"""POST /analyze access policy (apps/api/boundaries.py): authenticated by default."""

from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

pytest.importorskip("fastapi.testclient")

from fastapi.testclient import TestClient  # noqa: E402

from apps.api.boundaries import SlidingWindowRateLimiter  # noqa: E402
from apps.api.main import create_app  # noqa: E402
from apps.api.settings import AppSettings, configure_settings, get_settings  # noqa: E402

TOKEN = "s3cret-test-token-value"
BODY = {"run_id": "access-policy", "enable_alembic": False}
LOOPBACK = ("127.0.0.1", 50000)
REMOTE = ("203.0.113.7", 50000)


@pytest.fixture(autouse=True)
def _restore_settings():
    previous = get_settings()
    yield
    configure_settings(previous)


def _client(client_addr=REMOTE, **settings) -> TestClient:
    return TestClient(create_app(AppSettings(**settings)), client=client_addr)


def test_default_settings_fail_closed_without_token():
    response = _client().post("/analyze", json=BODY)
    assert response.status_code == 503
    assert response.json()["detail"] == "api_auth_not_configured"


def test_default_settings_reject_anonymous_even_from_loopback():
    response = _client(LOOPBACK).post("/analyze", json=BODY)
    assert response.status_code == 503


def test_missing_and_wrong_token_are_rejected():
    client = _client(api_token=TOKEN)
    assert client.post("/analyze", json=BODY).status_code == 401
    wrong = client.post("/analyze", json=BODY, headers={"X-ABX-Token": "nope"})
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "invalid_credentials"


def test_valid_token_is_accepted():
    response = _client(api_token=TOKEN).post("/analyze", json=BODY, headers={"X-ABX-Token": TOKEN})
    assert response.status_code == 200, response.text


def test_anonymous_flag_refused_outside_local_profile():
    with pytest.raises(ValidationError):
        AppSettings(allow_anonymous_local_dev=True)
    with pytest.raises(ValidationError):
        AppSettings(allow_anonymous_local_dev=True, deployment_profile="deployed")


def test_anonymous_local_dev_only_for_loopback_clients():
    settings = {"allow_anonymous_local_dev": True, "deployment_profile": "local"}
    assert _client(LOOPBACK, **settings).post("/analyze", json=BODY).status_code == 200
    remote = _client(REMOTE, **settings).post("/analyze", json=BODY)
    assert remote.status_code == 401
    assert remote.json()["detail"] == "authentication_required"


def test_rate_limit_per_principal():
    client = _client(api_token=TOKEN, analyze_rate_limit_per_minute=2)
    headers = {"X-ABX-Token": TOKEN}
    assert [client.post("/analyze", json=BODY, headers=headers).status_code for _ in range(2)] == [200, 200]
    limited = client.post("/analyze", json=BODY, headers=headers)
    assert limited.status_code == 429
    assert int(limited.headers["Retry-After"]) >= 1


def test_rate_limiter_window_slides():
    now = [0.0]
    limiter = SlidingWindowRateLimiter(1, window_seconds=60, clock=lambda: now[0])
    assert limiter.acquire("p") is None
    assert limiter.acquire("p") == pytest.approx(60)
    assert limiter.acquire("other") is None
    now[0] = 60.0
    assert limiter.acquire("p") is None


def test_oversized_body_rejected_before_parsing():
    client = _client(api_token=TOKEN, max_request_bytes=1024)
    big = {"run_id": "big", "input_payload": {"x": "a" * 4096}}
    response = client.post("/analyze", json=big, headers={"X-ABX-Token": TOKEN})
    assert response.status_code == 413
    assert response.json()["detail"] == "request_body_too_large"


def test_invalid_alembic_mode_is_client_error():
    client = _client(api_token=TOKEN)
    response = client.post(
        "/analyze", json={**BODY, "alembic_mode": "bogus"}, headers={"X-ABX-Token": TOKEN}
    )
    assert response.status_code == 422


def test_credentials_never_echoed_in_responses_or_logs(caplog):
    caplog.set_level(logging.DEBUG)
    client = _client(api_token=TOKEN)
    for headers in ({"X-ABX-Token": TOKEN}, {"X-ABX-Token": TOKEN + "x"}):
        response = client.post("/analyze", json=BODY, headers=headers)
        assert TOKEN not in response.text
        assert all(TOKEN not in value for value in response.headers.values())
    assert TOKEN not in caplog.text
    diagnostics = get_settings().redacted_diagnostics()
    assert TOKEN not in str(diagnostics)
    assert diagnostics["api_token_configured"] is True
