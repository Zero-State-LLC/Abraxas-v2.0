from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_continuity_lane_conventions_plan import (
    build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan,
    render_abx_codegen_intelligence_spine_continuity_lane_conventions_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_continuity_lane_conventions_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_continuity_lane_conventions_plan.v1.schema.json"
)


def test_codegen_continuity_lane_conventions_plan_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["continuity_lane_conventions_plan_status"]
        == "ABX_CODEGEN_CONTINUITY_LANE_CONVENTIONS_PLAN_READY"
    )
    assert packet["source_projection_bindings_plan"]["source_ready"] is True
    assert packet["base_lane_prefix"] == "CODEGEN-"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_continuity_lane_conventions_preserve_naming_patterns() -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=REPO_ROOT
    )

    assert [item["naming_pattern"] for item in packet["lane_categories"]] == [
        "P102G+CODEGEN-SHADOW-###",
        "META-P102G+CODEGEN-META-###",
        "P102G+CODEGEN-ODR-###",
        "P102G+CODEGEN-AUTH-###",
        "P102G+CODEGEN-SEAL-###",
    ]
    assert all(
        item["convention_status"] == "PLANNING_ONLY"
        for item in packet["lane_categories"]
    )
    assert all(item["lane_creation_authorized"] is False for item in packet["lane_categories"])


def test_codegen_continuity_lane_creation_is_denied() -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=REPO_ROOT
    )
    rules = packet["lane_creation_rules"]
    relationship = packet["p102g_relationship"]

    assert rules["harness_lane_creation_observed_in_spec"] is True
    assert rules["meta_gate_lane_creation_observed_in_spec"] is True
    assert rules["lane_id_generation_authorized"] is False
    assert rules["harness_lane_creation_authorized"] is False
    assert rules["meta_gate_lane_creation_authorized"] is False
    assert relationship["p102g_extension_authorized_by_this_plan"] is False
    assert relationship["replaces_existing_p102_research_lanes"] is False


def test_codegen_continuity_lane_conventions_preserve_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_continuity_lane_conventions_fail_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=tmp_path
    )

    assert packet["continuity_lane_conventions_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_projection_bindings_plan"]["source_ready"] is False
    assert all(
        item["convention_status"] == "NOT_COMPUTABLE"
        for item in packet["lane_categories"]
    )


def test_codegen_continuity_lane_conventions_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_continuity_lane_conventions_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_continuity_lane_conventions_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_continuity_lane_conventions_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_continuity_lane_conventions_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_continuity_lane_conventions_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_continuity_lane_conventions_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_continuity_lane_conventions_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine Continuity Lane Conventions Plan"
    )
    assert any("P102G+CODEGEN-SHADOW-###" in line for line in markdown)
    assert any("harness_lane_creation_authorized: False" in line for line in markdown)
