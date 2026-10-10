"""schema_ref resolution in the advisory spine is anchored to the configured repo root.

Regression: `analyze --schema-ref` resolved the schema against the process
working directory while `validate` used the client's repo_root, so the two
operations disagreed outside the repository directory.
"""

from __future__ import annotations

from pathlib import Path

from abraxas.client import AbraxasClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REF = "contracts/services/validation_service.request.v1.schema.json"
PAYLOAD = {
    "schema_version": "ValidationServiceRequest.v1",
    "service_id": "validation_service",
    "execution_id": "spine-repo-root",
    "schema_ref": SCHEMA_REF,
    "payload": {},
}


def _analyze(client: AbraxasClient) -> dict:
    return client.analyze(run_id="spine-repo-root", input_payload=PAYLOAD, schema_ref=SCHEMA_REF)


def test_analyze_schema_ref_ignores_working_directory(tmp_path, monkeypatch):
    client = AbraxasClient(repo_root=REPO_ROOT)

    monkeypatch.chdir(REPO_ROOT)
    from_repo = _analyze(client)
    monkeypatch.chdir(tmp_path)
    from_elsewhere = _analyze(client)

    assert from_elsewhere.get("error_class") != "VALIDATION_FAILED", from_elsewhere
    assert from_elsewhere == from_repo


def test_analyze_and_validate_agree_on_schema_ref(tmp_path, monkeypatch):
    client = AbraxasClient(repo_root=REPO_ROOT)
    monkeypatch.chdir(tmp_path)

    validated = client.validate(schema_ref=SCHEMA_REF, payload=PAYLOAD)
    analyzed = _analyze(client)

    assert validated["status"] == "OK", validated
    assert analyzed["status"] != "INVALID_INPUT", analyzed
