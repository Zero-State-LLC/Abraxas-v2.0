from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_canon_shadow_formalization_plan import (
    build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan,
    render_abx_codegen_intelligence_spine_canon_shadow_formalization_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_canon_shadow_formalization_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_canon_shadow_formalization_plan.v1.schema.json"
)


def test_codegen_canon_shadow_formalization_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["canon_shadow_formalization_plan_status"]
        == "ABX_CODEGEN_CANON_SHADOW_FORMALIZATION_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_governance_decision_vocabulary_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_canon_shadow_formalization_places_codegen_outside_runtime_stack() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )

    placement = packet["architectural_placement"]
    assert placement["placement"] == "outside_five_layer_runtime_stack"
    assert placement["five_layer_stack"] == ["INGEST", "BELIEF", "REPLAY", "PHASE", "VIZ"]
    assert placement["runtime_layer_authority_granted"] is False


def test_codegen_canon_shadow_formalization_names_candidate_models_without_creating_them() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )

    models = {item["object_model"]: item for item in packet["candidate_object_models"]}
    assert set(models) == {
        "PatchContract.v1",
        "CodeDropEnvelope.v1",
        "PolicyReviewPacket.v1",
        "CodegenHandoffPacket.v1",
    }
    assert all(item["schema_creation_authorized"] is False for item in models.values())


def test_codegen_canon_shadow_formalization_allows_only_advisory_statuses() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )

    assert "PATCH_CONTRACT_READY_ADVISORY_ONLY" in packet["allowed_final_statuses"]
    assert "NOT_COMPUTABLE" in packet["allowed_final_statuses"]
    assert "PATCH_APPLIED" in packet["forbidden_final_statuses"]
    assert "EXECUTION_READY" in packet["forbidden_final_statuses"]
    assert "CANON_PROMOTED" in packet["forbidden_final_statuses"]


def test_codegen_canon_shadow_formalization_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["shadow_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_canon_shadow_formalization_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=tmp_path
    )

    assert packet["canon_shadow_formalization_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_governance_decision_vocabulary_plan"]["source_ready"] is False
    assert all(
        item["status"] == "NOT_COMPUTABLE" for item in packet["subsystem_responsibilities"]
    )


def test_codegen_canon_shadow_formalization_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_canon_shadow_formalization_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_canon_shadow_formalization_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_canon_shadow_formalization_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_canon_shadow_formalization_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_canon_shadow_formalization_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_canon_shadow_formalization_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_canon_shadow_formalization_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Canon Shadow Formalization Plan"
    assert any("PatchContract.v1" in line for line in markdown)
    assert any("PATCH_APPLIED" in line for line in markdown)
