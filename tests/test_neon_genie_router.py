"""Tests for skills/abx-neon-genie/neon_genie_router.py + evidence_pack path wiring."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "abx-neon-genie"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SKILL))

import evidence_pack as ep
import neon_genie_router as r

LIVE_PACK = (
    ROOT
    / "out"
    / "signal_forage"
    / "2026-07-27_hermes-agent-skill-os-patterns"
    / "evidence_pack.v0.json"
)
FIXTURE_PACK = (
    ROOT
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)


def test_classify_mode():
    assert r.classify_mode({}) == "PROMPT_LED"
    assert r.classify_mode({"mode": "market_led"}) == "MARKET_LED"
    assert r.classify_mode({"mode": "trend_led"}) == "TREND_LED"


def test_require_evidence():
    assert r.require_evidence("MARKET_LED", {}) is True
    assert r.require_evidence("PROMPT_LED", {}) is False
    assert r.require_evidence("PROMPT_LED", {"require_evidence": True}) is True


def test_run_venture_cycle_basic():
    req = {"mode": "prompt_led"}
    result = r.run_venture_cycle(req)
    assert "schema_version" in result
    assert result["input_mode"] == "PROMPT_LED"
    assert "venture_packet" in result
    assert "route_decision" in result
    assert result["evidence_status"] == "PROMPT_ONLY"
    assert result["authority"]["execution_authority"] is False


def test_run_venture_cycle_with_legacy_evidence():
    req = {"mode": "market_led", "evidence_pack": {"status": "ACQUIRED"}}
    result = r.run_venture_cycle(req)
    assert result["evidence_status"] == "ACQUIRED"
    assert "overlap_classification" in result


def test_market_led_without_pack_is_not_computable():
    result = r.run_venture_cycle({"mode": "MARKET_LED", "seed": "widget saas"})
    assert result["evidence_status"] == "NOT_COMPUTABLE"
    assert result["commercial_claims_blocked"] is True
    vp = result["venture_packet"]
    assert vp["commercial_claims_status"] == "NOT_COMPUTABLE"
    assert vp["market_model"]["status"] == "NOT_COMPUTABLE"


def test_normalize_evidence_pack_v0_fixture(tmp_path: Path):
    pack = {
        "schema_version": "EvidencePack.v0",
        "pack_id": "ep_test_001",
        "topic": "t",
        "intent": "tech",
        "must_answer": ["q"],
        "sources": [
            {
                "source_id": "S1",
                "url_or_path": "https://example.com",
                "title": "Ex",
                "source_class": "primary",
                "excerpt": "hi",
            }
        ],
        "claims": [
            {
                "claim_id": "C1",
                "text": "observed thing",
                "register": "OBSERVED",
                "source_ids": ["S1"],
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
        "register_counts": {"OBSERVED": 1, "INFERRED": 0, "SPECULATIVE": 0, "NOT_COMPUTABLE": 0},
        "observed_source_count": 1,
    }
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(pack), encoding="utf-8")
    normalized = ep.resolve_evidence_for_request(
        {"evidence_pack_path": str(path)}, needs_evidence=True
    )
    assert normalized["status"] == "EVIDENCE_PACK"
    assert normalized["pack_id"] == "ep_test_001"
    assert normalized["evidence_density"] > 0.1
    assert normalized["pack_ref"]


@pytest.mark.skipif(not LIVE_PACK.is_file(), reason="live forage pack not present")
def test_run_venture_cycle_with_live_forage_pack_path():
    pack_path = LIVE_PACK if LIVE_PACK.is_file() else FIXTURE_PACK
    req = {
        "mode": "TREND_LED",
        "seed": "governed agent skill OS",
        "evidence_pack_path": str(pack_path),
        "require_evidence": True,
    }
    result = r.run_venture_cycle(req)
    assert result["evidence_status"] == "EVIDENCE_PACK"
    assert result["evidence_pack_ref"]
    assert result["evidence_density"] >= 0.55
    # Live pack marks market TAM NOT_COMPUTABLE → commercial gate on
    assert result["commercial_claims_blocked"] is True
    vp = result["venture_packet"]
    assert vp["evidence_basis"] == "EVIDENCE_PACK"
    assert vp["seed_evidence"]["pack_id"] == "ep_20260727_hermes_skill_os_001"
    assert vp["market_model"]["status"] == "NOT_COMPUTABLE"


def test_run_venture_cycle_with_fixture_pack_path():
    assert FIXTURE_PACK.is_file()
    result = r.run_venture_cycle({
        "mode": "TREND_LED",
        "seed": "governed agent skill OS",
        "evidence_pack_path": str(FIXTURE_PACK),
    })
    assert result["evidence_status"] == "EVIDENCE_PACK"
    assert result["venture_packet"]["seed_evidence"]["pack_id"] == "ep_20260727_hermes_skill_os_001"
    assert result["commercial_claims_blocked"] is True
    assert result["venture_packet"]["market_model"]["status"] == "NOT_COMPUTABLE"
