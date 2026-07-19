from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan import (
    build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan,
    render_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan.v1.schema.json"
)


def test_codegen_aal_viz_projection_bindings_plan_ready() -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=REPO_ROOT
    )

    assert (
        packet["projection_bindings_plan_status"]
        == "ABX_CODEGEN_AAL_VIZ_PROJECTION_BINDINGS_PLAN_READY"
    )
    assert packet["source_rune_yggdrasil_plan"]["source_ready"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_aal_viz_projection_bindings_are_display_only() -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=REPO_ROOT
    )

    assert [item["artifact_type"] for item in packet["recommended_projection_bindings"]] == [
        "ImprovementProposal.v1",
        "ShadowImprovementReceipt.v1",
        "CodegenOperatorDecisionRecord",
        "MetaGate*",
    ]
    assert all(
        item["recommended_viz_mode"] == "display_only"
        for item in packet["recommended_projection_bindings"]
    )
    assert all(
        item["projection_binding_authorized"] is False
        for item in packet["recommended_projection_bindings"]
    )
    assert all(
        item["execution_trigger_authorized"] is False
        for item in packet["recommended_projection_bindings"]
    )


def test_codegen_aal_viz_visualization_needs_are_not_implementation_authority() -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=REPO_ROOT
    )

    assert [item["view_id"] for item in packet["visualization_needs"]] == [
        "proposal_dashboard",
        "replay_metrics_view",
        "meta_gate_monitor",
        "lineage_graph",
    ]
    assert all(item["display_only"] is True for item in packet["visualization_needs"])
    assert all(
        item["implementation_authorized"] is False for item in packet["visualization_needs"]
    )
    assert (
        packet["projection_constraints"]["meta_gate_paths_require_elevated_scrutiny_label"]
        is True
    )


def test_codegen_aal_viz_projection_bindings_preserve_authority_locks() -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=REPO_ROOT
    )

    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["display_only"] is True
    assert packet["non_authoritative"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_aal_viz_projection_bindings_fail_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=tmp_path
    )

    assert packet["projection_bindings_plan_status"] == "NOT_COMPUTABLE"
    assert packet["source_rune_yggdrasil_plan"]["source_ready"] is False
    assert all(
        item["binding_status"] == "NOT_COMPUTABLE"
        for item in packet["recommended_projection_bindings"]
    )
    assert all(item["need_status"] == "NOT_COMPUTABLE" for item in packet["visualization_needs"])


def test_codegen_aal_viz_projection_bindings_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_aal_viz_projection_bindings_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_aal_viz_projection_bindings_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_aal_viz_projection_bindings_plan_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# ABX Codegen Intelligence Spine AAL-Viz Projection Bindings Plan"
    )
    assert any("ImprovementProposal.v1: display_only" in line for line in markdown)
    assert any("meta_gate_monitor: PLANNING_ONLY" in line for line in markdown)
