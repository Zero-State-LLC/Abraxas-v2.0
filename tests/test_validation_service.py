"""Tests for Validation Service v1 (WP-B)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.services.validation_service import (
    REQUEST_SCHEMA_VERSION,
    SERVICE_ID,
    SERVICE_VERSION,
    validate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/stabilization_readiness/interface_registry.v1.schema.json"
)


def _req(payload: object, schema_ref: str = SCHEMA_PATH, **extra: object) -> dict:
    body: dict = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "service_id": SERVICE_ID,
        "service_version": SERVICE_VERSION,
        "execution_id": "test-exec-001",
        "schema_ref": schema_ref,
        "payload": payload,
    }
    body.update(extra)
    return body


def test_valid_payload_ok() -> None:
    # Minimal interface registry-shaped payload may fail schema; use a simple schema
    schema_ref = "contracts/services/validation_service.request.v1.schema.json"
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "service_id": SERVICE_ID,
        "schema_ref": "contracts/services/validation_service.request.v1.schema.json",
        "payload": {"x": 1},
    }
    resp = validate(_req(payload, schema_ref=schema_ref), repo_root=REPO_ROOT)
    assert resp["status"] == "OK"
    assert resp["valid"] is True
    assert resp["provenance"]["validator"] == "jsonschema"
    assert len(resp["provenance"]["payload_sha256"]) == 64


def test_invalid_payload_ok_status_with_errors() -> None:
    schema_ref = "contracts/services/validation_service.request.v1.schema.json"
    resp = validate(_req({"not": "a request"}, schema_ref=schema_ref), repo_root=REPO_ROOT)
    assert resp["status"] == "OK"
    assert resp["valid"] is False
    assert len(resp["errors"]) >= 1


def test_path_traversal_denied() -> None:
    resp = validate(
        _req({}, schema_ref="contracts/../pyproject.toml"),
        repo_root=REPO_ROOT,
    )
    assert resp["status"] == "ERROR"
    assert resp["error_class"] == "SCHEMA_REF_INVALID"


def test_non_contracts_ref_denied() -> None:
    resp = validate(_req({}, schema_ref="README.md"), repo_root=REPO_ROOT)
    assert resp["status"] == "ERROR"
    assert resp["error_class"] == "SCHEMA_REF_INVALID"


def test_request_schema_version_required() -> None:
    resp = validate(
        {
            "schema_version": "wrong",
            "service_id": SERVICE_ID,
            "schema_ref": SCHEMA_PATH,
            "payload": {},
        },
        repo_root=REPO_ROOT,
    )
    assert resp["status"] == "ERROR"
    assert resp["error_class"] == "REQUEST_INVALID"


def test_deterministic_payload_hash() -> None:
    schema_ref = "contracts/services/validation_service.request.v1.schema.json"
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "service_id": SERVICE_ID,
        "schema_ref": schema_ref,
        "payload": {"b": 1, "a": 2},
    }
    r1 = validate(_req(payload, schema_ref=schema_ref), repo_root=REPO_ROOT)
    r2 = validate(_req(payload, schema_ref=schema_ref), repo_root=REPO_ROOT)
    assert r1["status"] == "OK" and r2["status"] == "OK"
    assert r1["provenance"]["payload_sha256"] == r2["provenance"]["payload_sha256"]
    assert r1["provenance"]["schema_sha256"] == r2["provenance"]["schema_sha256"]


def test_response_matches_response_schema_for_ok() -> None:
    schema_ref = "contracts/services/validation_service.request.v1.schema.json"
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "service_id": SERVICE_ID,
        "schema_ref": schema_ref,
        "payload": {},
    }
    resp = validate(_req(payload, schema_ref=schema_ref), repo_root=REPO_ROOT)
    response_schema = json.loads(
        (
            REPO_ROOT
            / "contracts/services/validation_service.response.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=resp, schema=response_schema)


def test_error_response_matches_response_schema() -> None:
    resp = validate(_req({}, schema_ref="not/under/contracts.json"), repo_root=REPO_ROOT)
    response_schema = json.loads(
        (
            REPO_ROOT
            / "contracts/services/validation_service.response.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=resp, schema=response_schema)
