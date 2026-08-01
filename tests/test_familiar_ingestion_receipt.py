"""Tests for familiar_ingestion receipt (AI OS Slice B)."""

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.ingest.familiar_ingestion_receipt import (
    SCHEMA_VERSION,
    build_familiar_ingestion_receipt,
    build_familiar_ingestion_receipt_from_path,
    write_familiar_ingestion_receipt,
)
from core.signal.evidence_pack import assert_valid_evidence_pack

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
SCHEMA = ROOT / "contracts" / "ingest" / "familiar_ingestion_receipt.v0.schema.json"


def test_schema_file_exists():
    assert SCHEMA.is_file()
    data = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert data["title"] == "FamiliarIngestionReceipt.v0"


def test_receipt_from_fixture_pack():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert_valid_evidence_pack(pack, repo_root=ROOT)
    r1 = build_familiar_ingestion_receipt(
        pack, pack_ref=str(FIXTURE), repo_root=ROOT
    )
    r2 = build_familiar_ingestion_receipt(
        pack, pack_ref=str(FIXTURE), repo_root=ROOT
    )
    assert r1 == r2
    assert r1["schema_version"] == SCHEMA_VERSION
    assert r1["pipeline_id"] == "familiar_ingestion"
    assert r1["status"] == "INGESTED_SHADOW"
    assert r1["validation_status"] == "PASS"
    assert r1["advisory_only"] is True
    assert r1["lane"] == "SHADOW"
    assert r1["authority"]["execution_authority"] is False
    assert r1["pack_id"] == "ep_20260727_hermes_skill_os_001"
    assert r1["pack_hash"] == canonical_hash(pack)
    assert r1["observed_claim_count"] >= 1
    assert r1["source_count"] >= 1
    assert r1["commercial_claims_blocked"] is True
    # receipt_hash seals body without circularity
    body = dict(r1)
    rh = body.pop("receipt_hash")
    assert rh == canonical_hash(body)


def test_receipt_from_path_helper():
    receipt = build_familiar_ingestion_receipt_from_path(FIXTURE, repo_root=ROOT)
    assert receipt["status"] == "INGESTED_SHADOW"
    assert "hermes" in receipt["pack_ref"].lower() or receipt["pack_ref"].endswith(
        FIXTURE.name
    )


def test_invalid_pack_rejected():
    bad = {
        "schema_version": "EvidencePack.v0",
        "pack_id": "ep_bad_xx",
        "topic": "t",
        "intent": "tech",
        "must_answer": ["q"],
        "sources": [],
        "claims": [
            {
                "claim_id": "C1",
                "text": "orphan",
                "register": "OBSERVED",
                "source_ids": [],
            }
        ],
        "authority": {
            "execution_authority": False,
            "promotion_authorized": False,
            "forecast_routing_authorized": False,
            "canon_mutation_allowed": False,
        },
        "provenance": {
            "producer_system": "HERMES",
            "skill_id": "abx-familiar-signal-forager",
            "tool_trace_summary": "t",
        },
    }
    receipt = build_familiar_ingestion_receipt(bad, pack_ref="mem://bad", repo_root=ROOT)
    assert receipt["status"] == "REJECTED_INVALID_PACK"
    assert receipt["validation_status"] == "FAIL"
    assert receipt["blockers"] == ["invalid_evidence_pack"]


def test_no_input():
    receipt = build_familiar_ingestion_receipt(None)
    assert receipt["status"] == "NO_INPUT"
    assert receipt["validation_status"] == "NOT_COMPUTABLE"


def test_write_receipt(tmp_path: Path):
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    receipt = build_familiar_ingestion_receipt(
        pack, pack_ref=str(FIXTURE), repo_root=ROOT
    )
    out = tmp_path / "receipt.json"
    write_familiar_ingestion_receipt(out, receipt, out_root=tmp_path)
    assert out.is_file()
    assert out.with_suffix(".md").is_file()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["receipt_id"] == receipt["receipt_id"]
    assert loaded["schema_version"] == SCHEMA_VERSION
    assert loaded["status"] == "INGESTED_SHADOW"

def test_jsonschema_validates_fixture_receipt():
    from jsonschema import Draft7Validator

    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    receipt = build_familiar_ingestion_receipt(
        pack, pack_ref=str(FIXTURE), repo_root=ROOT
    )
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(receipt)
