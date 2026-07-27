"""Tests for core.signal.evidence_pack (AI OS Slice A)."""

from __future__ import annotations

import json
from pathlib import Path

from core.signal.evidence_pack import (
    EVIDENCE_PACK_SCHEMA_VERSION,
    assert_valid_evidence_pack,
    commercial_claims_blocked,
    load_schema,
    normalize_evidence_pack,
    register_counts,
    resolve_evidence_for_request,
    schema_path,
    validate_evidence_pack,
    validate_path,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
SKILL_SCHEMA = (
    ROOT
    / "skills"
    / "abx-familiar-signal-forager"
    / "references"
    / "evidence_pack.v0.schema.json"
)
CONTRACT_SCHEMA = ROOT / "contracts" / "signal" / "evidence_pack.v0.schema.json"


def test_canonical_schema_exists_and_matches_skill_mirror():
    assert CONTRACT_SCHEMA.is_file()
    assert SKILL_SCHEMA.is_file()
    assert CONTRACT_SCHEMA.read_text(encoding="utf-8") == SKILL_SCHEMA.read_text(
        encoding="utf-8"
    )
    schema = load_schema(repo_root=ROOT)
    assert schema.get("title") == "EvidencePack.v0"
    assert schema_path(repo_root=ROOT) == CONTRACT_SCHEMA.resolve()


def test_fixture_pack_validates():
    assert FIXTURE.is_file()
    report = validate_path(FIXTURE, repo_root=ROOT)
    assert report["ok"] is True, report.get("errors")
    assert report["pack_id"] == "ep_20260727_hermes_skill_os_001"
    assert report["register_counts"]["OBSERVED"] >= 1
    assert report["authority"]["execution_authority"] is False
    assert report["commercial_claims_blocked"] is True


def test_assert_valid_fixture():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    out = assert_valid_evidence_pack(pack, repo_root=ROOT)
    assert out["schema_version"] == EVIDENCE_PACK_SCHEMA_VERSION


def test_observed_without_sources_fails(tmp_path: Path):
    pack = {
        "schema_version": "EvidencePack.v0",
        "pack_id": "ep_bad_001",
        "topic": "t",
        "intent": "tech",
        "must_answer": ["q"],
        "sources": [],
        "claims": [
            {
                "claim_id": "C1",
                "text": "orphan observed",
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
            "tool_trace_summary": "test",
        },
    }
    errs = validate_evidence_pack(pack, repo_root=ROOT)
    assert any("OBSERVED" in e for e in errs)


def test_execution_authority_true_fails():
    pack = json.loads(FIXTURE.read_text(encoding="utf-8"))
    pack = dict(pack)
    pack["authority"] = dict(pack["authority"])
    pack["authority"]["execution_authority"] = True
    errs = validate_evidence_pack(pack, repo_root=ROOT)
    assert any("execution_authority" in e for e in errs)


def test_normalize_and_resolve_path():
    normalized = normalize_evidence_pack(
        json.loads(FIXTURE.read_text(encoding="utf-8")),
        source_path=str(FIXTURE),
        validate=True,
        repo_root=ROOT,
    )
    assert normalized["status"] == "EVIDENCE_PACK"
    assert normalized["evidence_density"] >= 0.55
    resolved = resolve_evidence_for_request(
        {"evidence_pack_path": str(FIXTURE)},
        needs_evidence=True,
        validate=True,
        repo_root=ROOT,
    )
    assert resolved["status"] == "EVIDENCE_PACK"
    assert resolved["pack_id"] == "ep_20260727_hermes_skill_os_001"


def test_register_counts_from_claims():
    pack = {
        "claims": [
            {"register": "OBSERVED"},
            {"register": "OBSERVED"},
            {"register": "INFERRED"},
            {"register": "NOT_COMPUTABLE"},
        ]
    }
    assert register_counts(pack) == {
        "OBSERVED": 2,
        "INFERRED": 1,
        "SPECULATIVE": 0,
        "NOT_COMPUTABLE": 1,
    }


def test_commercial_blocked_on_empty():
    assert commercial_claims_blocked({"status": "NOT_COMPUTABLE"}) is True
    assert commercial_claims_blocked({"claims": [], "sources": []}) is True
