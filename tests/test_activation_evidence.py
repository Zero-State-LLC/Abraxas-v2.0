"""Independent INTERNAL_CANARY evidence (core/governance/activation_evidence.py)."""

from __future__ import annotations

import base64
import json
from datetime import UTC, datetime, timedelta

import pytest

pytest.importorskip("cryptography")

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from core.governance.activation_evidence import (
    ActivationEvidencePayload,
    EvidenceStatus,
    TrustStore,
    verify_activation_evidence,
    verify_evidence_files,
)

NOW = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
REVISION = "a" * 40
CONFIG = "b" * 64
ISSUER = {"issuer_id": "ci.zero-state.abraxas-release", "kind": "signed_ci"}
KEY = Ed25519PrivateKey.generate()
OTHER_KEY = Ed25519PrivateKey.generate()


def _b64_public(key: Ed25519PrivateKey) -> str:
    raw = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode()


TRUST = TrustStore.model_validate(
    {
        "schema_version": "ActivationEvidenceTrustStore.v1",
        "required_checks": ["fast_ci", "pawl_ratchet"],
        "issuers": [{**ISSUER, "key_id": "ci-2026", "public_key": _b64_public(KEY)}],
    }
)


def _evidence(key=KEY, key_id="ci-2026", **overrides):
    payload = {
        "schema_version": "ActivationEvidence.v1",
        "lane": "INTERNAL_CANARY",
        "candidate_revision": REVISION,
        "config_digest": CONFIG,
        "checks": {"fast_ci": "PASS", "pawl_ratchet": "PASS"},
        "issuer": ISSUER,
        "issued_at": (NOW - timedelta(hours=1)).isoformat(),
        "expires_at": (NOW + timedelta(days=1)).isoformat(),
        **overrides,
    }
    message = ActivationEvidencePayload.model_validate(payload).signing_bytes()
    signature = base64.b64encode(key.sign(message)).decode()
    return {"payload": payload, "key_id": key_id, "signature": signature}


def _verify(evidence, **kwargs):
    params = {
        "trust_store": TRUST,
        "expected_revision": REVISION,
        "expected_config_digest": CONFIG,
        "now": NOW,
        **kwargs,
    }
    return verify_activation_evidence(evidence, **params)


def test_valid_independent_evidence_verifies():
    result = _verify(_evidence())
    assert result.status is EvidenceStatus.VERIFIED
    assert result.issuer_id == ISSUER["issuer_id"]


@pytest.mark.parametrize(
    "case, expected",
    [
        ("absent", EvidenceStatus.ABSENT),
        ("no_trust_store", EvidenceStatus.UNVERIFIABLE),
        ("no_expected_revision", EvidenceStatus.UNVERIFIABLE),
        ("malformed", EvidenceStatus.MALFORMED),
        ("unknown_key", EvidenceStatus.UNTRUSTED_ISSUER),
        ("issuer_swapped", EvidenceStatus.UNTRUSTED_ISSUER),
        ("forged_signature", EvidenceStatus.UNVERIFIABLE),
        ("tampered_payload", EvidenceStatus.UNVERIFIABLE),
        ("other_revision", EvidenceStatus.MISMATCHED),
        ("other_config", EvidenceStatus.MISMATCHED),
        ("missing_check", EvidenceStatus.MISMATCHED),
        ("expired", EvidenceStatus.STALE),
        ("future", EvidenceStatus.STALE),
        ("too_long", EvidenceStatus.STALE),
        ("failed_check", EvidenceStatus.FAILED),
        ("self_asserted", EvidenceStatus.SELF_ASSERTED),
    ],
)
def test_every_defect_blocks(case, expected):
    kwargs = {}
    evidence = _evidence()
    if case == "absent":
        evidence = None
    elif case == "no_trust_store":
        kwargs["trust_store"] = None
    elif case == "no_expected_revision":
        kwargs["expected_revision"] = None
    elif case == "malformed":
        evidence = {"payload": {"lane": "INTERNAL_CANARY"}, "key_id": "x", "signature": "y"}
    elif case == "unknown_key":
        evidence = _evidence(key_id="someone-else")
    elif case == "issuer_swapped":
        evidence = _evidence(issuer={"issuer_id": "operator.luna", "kind": "operator_receipt"})
    elif case == "forged_signature":
        evidence = _evidence(key=OTHER_KEY)
    elif case == "tampered_payload":
        evidence["payload"] = {**evidence["payload"], "checks": {"fast_ci": "PASS", "pawl_ratchet": "PASS", "extra": "PASS"}}
    elif case == "other_revision":
        kwargs["expected_revision"] = "c" * 40
    elif case == "other_config":
        kwargs["expected_config_digest"] = "d" * 64
    elif case == "missing_check":
        evidence = _evidence(checks={"fast_ci": "PASS"})
    elif case == "expired":
        kwargs["now"] = NOW + timedelta(days=2)
    elif case == "future":
        evidence = _evidence(issued_at=(NOW + timedelta(hours=1)).isoformat())
    elif case == "too_long":
        evidence = _evidence(expires_at=(NOW + timedelta(days=30)).isoformat())
    elif case == "failed_check":
        evidence = _evidence(checks={"fast_ci": "PASS", "pawl_ratchet": "FAIL"})
    elif case == "self_asserted":
        kwargs["candidate_identity"] = ISSUER["issuer_id"]
    assert _verify(evidence, **kwargs).status is expected


def test_files_loader_and_api_canary_path(tmp_path):
    from fastapi.testclient import TestClient

    from apps.api.main import create_app
    from apps.api.settings import AppSettings, configure_settings, get_settings

    evidence_path = tmp_path / "evidence.json"
    trust_path = tmp_path / "trust.json"
    trust_path.write_text(TRUST.model_dump_json())
    assert verify_evidence_files(
        evidence_path, trust_path, expected_revision=REVISION, expected_config_digest=CONFIG, now=NOW
    ).status is EvidenceStatus.ABSENT

    body = {"run_id": "canary", "enable_alembic": False, "activation_lane": "INTERNAL_CANARY"}
    previous = get_settings()
    try:
        settings = AppSettings(
            api_token="t",
            canary_evidence_path=evidence_path,
            canary_trust_store_path=trust_path,
            candidate_revision=REVISION,
            candidate_config_digest=CONFIG,
        )
        client = TestClient(create_app(settings), headers={"X-ABX-Token": "t"})
        denied = client.post("/analyze", json=body).json()
        assert denied["status"] == "DENIED"
        assert "independent_evidence:ABSENT" in denied["activation"]["missing_controls"]

        # Real-time path: issue evidence valid around the actual clock.
        now = datetime.now(UTC)
        evidence = _evidence(
            issued_at=(now - timedelta(minutes=1)).isoformat(),
            expires_at=(now + timedelta(hours=1)).isoformat(),
        )
        evidence_path.write_text(json.dumps(evidence))
        allowed = client.post("/analyze", json=body).json()
        assert allowed["status"] == "OK", allowed
    finally:
        configure_settings(previous)
