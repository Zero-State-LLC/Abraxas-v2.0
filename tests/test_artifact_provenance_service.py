"""Tests for Artifact & Provenance Service v0 (WP-J)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.canonical.json import canonical_hash
from core.services.artifact_provenance_service import (
    REQUEST_SCHEMA_VERSION,
    SERVICE_ID,
    execute,
)


REPO = Path(__file__).resolve().parents[1]


def _req(operation: str, payload: object, path: str | None = None) -> dict:
    body = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "service_id": SERVICE_ID,
        "service_version": "0.1.0",
        "execution_id": "test-art-001",
        "operation": operation,
        "payload": payload,
    }
    if path is not None:
        body["path"] = path
    return body


def test_hash_matches_canonical() -> None:
    payload = {"b": 1, "a": 2}
    resp = execute(_req("hash", payload), repo_root=REPO)
    assert resp["status"] == "OK"
    assert resp["result"]["canonical_hash"] == canonical_hash(payload)


def test_write_under_out(tmp_path: Path, monkeypatch) -> None:
    # use real repo out/ tmp subdir
    rel = "out/production_readiness/ws3/_artifact_service_test.json"
    target = REPO / rel
    if target.exists():
        target.unlink()
    resp = execute(
        _req("write", {"k": "v"}, path=rel),
        repo_root=REPO,
    )
    assert resp["status"] == "OK"
    assert resp["result"]["written"] is True
    assert target.is_file()
    target.unlink(missing_ok=True)


def test_path_outside_out_denied() -> None:
    resp = execute(
        _req("write", {"k": 1}, path="contracts/services/x.json"),
        repo_root=REPO,
    )
    assert resp["status"] == "ERROR"
    assert resp["error_class"] == "PATH_DENIED"


def test_path_traversal_denied() -> None:
    resp = execute(
        _req("write", {"k": 1}, path="out/../pyproject.toml"),
        repo_root=REPO,
    )
    assert resp["status"] == "ERROR"
    assert resp["error_class"] == "PATH_DENIED"


def test_response_schema_ok() -> None:
    resp = execute(_req("hash", {"x": 1}), repo_root=REPO)
    schema = json.loads(
        (
            REPO
            / "contracts/services/artifact_provenance_service.response.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=resp, schema=schema)
