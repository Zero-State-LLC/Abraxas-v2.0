from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_module_surface_plan import (
    build_abx_codegen_intelligence_spine_module_surface_plan,
    render_abx_codegen_intelligence_spine_module_surface_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_module_surface_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_module_surface_plan.v1.schema.json"
)


def test_codegen_module_surface_plan_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)

    assert (
        packet["module_surface_plan_status"]
        == "ABX_CODEGEN_MODULE_SURFACE_PLAN_HELD_FOR_OPERATOR"
    )
    assert packet["source_object_model_schema_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_module_surface_plan_names_core_codegen_namespace_without_creating_it() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)

    namespace = packet["planned_module_namespace"]
    assert namespace["preferred_directory"] == "core/codegen"
    assert namespace["namespace_creation_authorized"] is False
    assert namespace["module_file_creation_authorized"] is False


def test_codegen_module_surface_plan_names_expected_modules() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)

    modules = {item["module"]: item for item in packet["planned_modules"]}
    assert "core/codegen/patch_contract.py" in modules
    assert "core/codegen/code_drop_envelope.py" in modules
    assert "core/codegen/policy_reviewer.py" in modules
    assert "core/codegen/repo_state_binder.py" in modules
    assert "core/codegen/seal_validator.py" in modules
    assert "core/codegen/handoff_packet.py" in modules
    assert all(item["module_creation_authorized"] is False for item in modules.values())


def test_codegen_module_surface_plan_denies_scripts_and_tests() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)

    assert [item["script"] for item in packet["planned_scripts"]] == [
        "scripts/run_codegen_contract_audit.py",
        "scripts/run_codegen_handoff_packet.py",
    ]
    assert all(
        item["script_creation_authorized"] is False
        for item in packet["planned_scripts"]
    )
    assert all(item["test_creation_authorized"] is False for item in packet["planned_tests"])


def test_codegen_module_surface_plan_preserves_validation_groups() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)

    groups = {item["group"] for item in packet["validation_groups"]}
    assert "deterministic_patch_contracts" in groups
    assert "incremental_patch_enforcement" in groups
    assert "adversarial_authority_drift_detection" in groups
    assert "no_execution_authority" in groups


def test_codegen_module_surface_plan_preserves_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)

    assert packet["advisory_only"] is True
    assert packet["shadow_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_module_surface_plan_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=tmp_path)

    assert packet["module_surface_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_object_model_schema_plan"]["source_ready"] is False
    assert all(item["module_status"] == "NOT_COMPUTABLE" for item in packet["planned_modules"])


def test_codegen_module_surface_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_module_surface_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_module_surface_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_module_surface_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_module_surface_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_module_surface_plan_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_module_surface_plan(repo_root=REPO_ROOT)
    markdown = render_abx_codegen_intelligence_spine_module_surface_plan_markdown(packet)

    assert markdown[0] == "# ABX Codegen Intelligence Spine Module Surface Plan"
    assert any("core/codegen/patch_contract.py" in line for line in markdown)
    assert any("module_file_creation_denied" in line for line in markdown)
