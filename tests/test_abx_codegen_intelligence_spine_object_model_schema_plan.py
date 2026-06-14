from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_object_model_schema_plan import (
    build_abx_codegen_intelligence_spine_object_model_schema_plan,
    render_abx_codegen_intelligence_spine_object_model_schema_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_object_model_schema_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_object_model_schema_plan.v1.schema.json"
)


def test_codegen_object_model_schema_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["object_model_schema_plan_status"]
        == "ABX_CODEGEN_OBJECT_MODEL_SCHEMA_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_canon_shadow_formalization_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_object_model_schema_plan_names_all_candidate_schemas() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=REPO_ROOT
    )

    schemas = {item["schema_name"]: item for item in packet["schema_plans"]}
    assert set(schemas) == {
        "PatchContract.v1",
        "CodeDropEnvelope.v1",
        "PolicyReviewPacket.v1",
        "CodegenHandoffPacket.v1",
    }
    assert schemas["PatchContract.v1"]["planned_path"] == (
        "contracts/codegen/patch_contract.v1.schema.json"
    )
    assert all(item["schema_creation_authorized"] is False for item in schemas.values())


def test_codegen_object_model_schema_plan_denies_namespace_and_file_creation() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=REPO_ROOT
    )

    namespace = packet["planned_contract_namespace"]
    assert namespace["preferred_directory"] == "contracts/codegen"
    assert namespace["namespace_creation_authorized"] is False
    assert namespace["schema_file_creation_authorized"] is False


def test_codegen_object_model_schema_plan_preserves_shared_invariants() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=REPO_ROOT
    )

    invariants = {item["invariant"] for item in packet["shared_invariants"]}
    assert "advisory_only_true" in invariants
    assert "operator_review_required_true" in invariants
    assert "autonomous_patch_application_false" in invariants
    assert "execution_authority_false" in invariants


def test_codegen_object_model_schema_plan_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
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


def test_codegen_object_model_schema_plan_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=tmp_path
    )

    assert packet["object_model_schema_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_canon_shadow_formalization_plan"]["source_ready"] is False
    assert all(item["schema_status"] == "NOT_COMPUTABLE" for item in packet["schema_plans"])


def test_codegen_object_model_schema_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_object_model_schema_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_object_model_schema_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_object_model_schema_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_object_model_schema_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_object_model_schema_plan_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_object_model_schema_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_object_model_schema_plan_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Object Model Schema Plan"
    assert any("PatchContract.v1" in line for line in markdown)
    assert any("schema_creation_authorized=False" in line for line in markdown)
