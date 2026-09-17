"""Neon Genie SHADOW mount: honest scores, FAMILIAR ingest, not a specialist model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "abx-neon-genie"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SKILL))

import neon_genie_kernel as kernel  # noqa: E402
import neon_genie_router as router  # noqa: E402
import neon_genie_score as score_mod  # noqa: E402
from core.alembic.adapters import DEFAULT_ADAPTERS  # noqa: E402


def test_score_vector_is_honest_not_stub_ranks():
    scored = score_mod.score(
        [{"recombined_description": "synthetic seed"}],
        {"status": "PROMPT_ONLY", "evidence_density": 0.35, "commercial_claims_blocked": True},
    )
    vec = scored[0]["score_vector"]
    assert vec["schema_version"] == "NeonGenieScoreVector.v1"
    assert vec["ranker"] == "none"
    assert vec["overall"]["value"] is None
    assert vec["overall"]["register"] == "NOT_COMPUTABLE"
    assert vec["novelty"]["value"] is None
    assert vec["evidence_density"]["value"] == 0.35
    assert vec["evidence_density"]["register"] == "COMPUTED"
    assert vec["features"]["commercial_claims_blocked"] is True


def test_cycle_does_not_emit_measured_overall():
    result = router.run_venture_cycle({"mode": "PROMPT_LED", "seed": "synthetic test"})
    vec = result["venture_packet"]["score_vector"]
    assert vec["ranker"] == "none"
    assert vec["overall"]["register"] == "NOT_COMPUTABLE"
    assert result["not_a_specialist_model"] is True
    assert result["authority"]["forecast_routing_authorized"] is False


def test_shadow_kernel_ingests_without_queue_write():
    run = kernel.run_shadow_kernel(
        {"mode": "PROMPT_LED", "seed": "synthetic neon mount"},
        request_id="test-ng",
        repo_root=ROOT,
    )
    assert run["lane"] == "SHADOW"
    assert run["not_a_specialist_model"] is True
    assert run["pack_validation_errors"] == []
    assert run["ingestion_receipt"]["status"] == "INGESTED_SHADOW"
    assert run["spine_touchpoint"]["route"] == "ORACLE_SHADOW_CANDIDATE"
    assert run["oracle_belief_bridge"]["status"] == "BRIDGED_SHADOW"
    intake = run["oracle_belief_bridge"]["oracle_shadow_intake"]
    assert intake["queue_write_authorized"] is False
    assert intake["runtime_invoke_authorized"] is False
    env = run["envelope"]
    assert env["schema_version"] == "NeonGenieIngestEnvelope.v1"
    assert env["ranker"] == "none"
    assert env["score_vector"]["usefulness"]["value"] is None
    assert env["score_vector"]["overall"]["value"] is None


def test_neon_genie_is_not_on_live_alembic_or_specialist_stack():
    live_ids = [a.descriptor().architecture_id for a in DEFAULT_ADAPTERS]
    assert not any("neon" in i.lower() and "rank" in i.lower() for i in live_ids)
    stack = json.loads(
        (ROOT / "contracts" / "specialist_models" / "stack.v1.json").read_text(
            encoding="utf-8"
        )
    )
    ids = [row["id"] for row in stack["specialists"]]
    assert "neon-genie" not in ids
    router_row = stack["invention_router"]
    assert router_row["not_a_specialist_model"] is True
    assert router_row["ranker"] == "none"
    assert "Neon Genie as a trained specialist model" in " ".join(stack["non_goals"])
