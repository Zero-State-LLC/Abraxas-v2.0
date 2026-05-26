from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.research_fold_drop_spec_builder import build_research_fold_drop_spec_builder
from scripts import run_research_fold_drop_spec_builder

_VALID_P94_PACKET = {
    "artifact_type": "ResearchFoldCanonAlignmentPlan.v1",
    "lane_id": "P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN",
    "status": "PASS",
    "canon_alignment_status": "ALIGNED",
    "required_upstream_surfaces": [
        {"surface_id": "canon_drop_006_research_folds", "supplied": True},
        {"surface_id": "canon_drop_007_research_folds", "supplied": True},
    ],
}


def test_missing_p94_not_computable() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=None)
    assert packet["spec_builder_status"] == "NOT_COMPUTABLE"
    assert packet["specs_ready"] is False
    assert "p94_packet_missing" in packet["missing_or_invalid_inputs"]


def test_invalid_p94_not_aligned_not_computable() -> None:
    packet = build_research_fold_drop_spec_builder(
        p94_packet={**_VALID_P94_PACKET, "canon_alignment_status": "NOT_ALIGNED"}
    )
    assert packet["spec_builder_status"] == "NOT_COMPUTABLE"


def test_valid_p94_pass_and_two_specs() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    assert packet["spec_builder_status"] == "PASS"
    assert packet["specs_ready"] is True
    assert len(packet["built_specs"]) == 2
    assert packet["recommended_next_lane"] == "P96_RESEARCH_FOLD_VALIDATION_PLAN"


def test_built_specs_sorted_and_deterministic() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    spec_ids = [x["spec_id"] for x in packet["built_specs"]]
    assert spec_ids == sorted(spec_ids)


def test_determinism_packet_hash() -> None:
    a = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    b = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    assert a == b
    assert a["packet_hash"] == b["packet_hash"]


def test_authority_locks_forbidden_false() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    locks = packet["authority_locks"]
    for k in (
        "production_activation",
        "canon_promotion",
        "scheduler_mutation",
        "runtime_authority",
        "forecast_influence",
        "execution_authority",
        "repair_execution_authority",
        "regeneration_execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
    ):
        assert locks[k] is False


def test_runner_writes_output(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_fold_drop_spec_builder" / "latest.json"
    p = run_research_fold_drop_spec_builder.run(
        p94_packet=_VALID_P94_PACKET, repo_root=tmp_path, out_path=out_path
    )
    assert p["spec_builder_status"] == "PASS"
    assert out_path.exists()


def test_schema_validation_if_jsonschema_available() -> None:
    try:
        from jsonschema import validate
    except ModuleNotFoundError:
        pytest.skip("jsonschema not installed")

    schema = json.loads(
        Path("contracts/canon/research_fold_drop_spec_builder.v1.schema.json").read_text(encoding="utf-8")
    )
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    validate(packet, schema)
