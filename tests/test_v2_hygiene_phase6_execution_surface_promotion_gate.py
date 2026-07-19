from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase6_execution_surface_promotion_gate import (
    EXECUTION_SURFACE_MATRIX,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase6_execution_surface_promotion_gate,
    render_v2_hygiene_phase6_execution_surface_promotion_gate_markdown,
    write_v2_hygiene_phase6_execution_surface_promotion_gate,
)
from scripts.hygiene import run_v2_hygiene_phase6_execution_surface_promotion_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase6_execution_surface_promotion_gate.v1.schema.json"
)
SOURCE_PHASE11_PATH = (
    "out/operator_review/v2_hygiene_phase5_controlled_writeback_activation_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_execution_surface_promotion_gate_ready() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)

    assert packet["status"] == READY_STATUS
    assert packet["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert packet["source_blockers"] == []
    assert packet["execution_surface_promotion_gate_ready"] is True
    assert packet["phase11_controlled_writeback_activation_gate_hash_verified"] is True
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["operator_review_posture"] == "ACTIVE"
    assert packet["valid_for_controlled_writeback"] is True
    assert packet["valid_for_execution"] is False


def test_execution_surface_matrix_promotes_all_surfaces() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)
    matrix = packet["execution_surface_promotion_contract"]["execution_surface_matrix"]
    expected_ids = {entry["surface_id"] for entry in EXECUTION_SURFACE_MATRIX}
    observed_ids = {surface["surface_id"] for surface in matrix}

    assert observed_ids == expected_ids
    assert all(surface["all_paths_observed"] is True for surface in matrix)
    assert all(surface["authority_granted"] is False for surface in matrix)
    promotion_classes = {surface["surface_id"]: surface["promotion_class"] for surface in matrix}
    assert promotion_classes["core_governance_modules"] == "PROMOTED_CONTROLLED_WRITE"
    assert promotion_classes["brier_engine"] == "PROMOTED_TELEMETRY_READ"
    assert promotion_classes["oracle_hooks"] == "PROMOTED_SHADOW_READ"
    assert promotion_classes["runtime_surface"] == "PROMOTED_READ_CONTROLLED_WRITE"
    assert promotion_classes["canon_surface"] == "PROMOTED_READ_CONTROLLED_WRITE"
    assert promotion_classes["queue_surface"] == "PROMOTED_READ_CONTROLLED_WRITE"
    assert promotion_classes["scheduler_surface"] == "PROMOTED_READ_CONTROLLED_WRITE"


def test_dependency_denials_preserved() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)
    denial = packet["dependency_denial_contract"]

    assert denial["package_lock_mutation_authorized"] is False
    assert denial["package_lock_tracking_authorized"] is False
    assert denial["toolchain_provisioning_authorized"] is False
    assert denial["dependency_mutation_authorized"] is False
    assert denial["npmrc_stabilization_observed"] is True
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["npmrc_mutation_authorized"] is False
    assert packet["package_json_mutation_authorized"] is False
    assert packet["toolchain_provisioning_authorized"] is False


def test_controlled_writeback_inheritance() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)
    inheritance = packet["controlled_writeback_inheritance_contract"]

    assert inheritance["controlled_writeback_enabled"] is True
    assert inheritance["surface_count"] == 5
    assert inheritance["uncontrolled_writeback_authorized"] is False
    assert inheritance["notion_writeback_allowed"] is False
    assert inheritance["github_writeback_allowed"] is False


def test_brier_and_rune_contracts_are_non_authoritative() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)
    brier = packet["brier_scoring_contract"]
    runes = packet["rune_governance_mapping"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["promotion_authorized"] is False
    assert brier["brier_resolution_authorized"] is False
    assert len(brier["telemetry_hooks"]) == len(EXECUTION_SURFACE_MATRIX)
    assert all(hook["resolution_allowed"] is False for hook in brier["telemetry_hooks"])
    assert {item["rune"] for item in runes} == {"Observe", "Bind", "Hold", "Weigh", "Seal"}
    assert all(item["authority_granted"] is False for item in runes)
    assert packet["execution_surface_promotion_authorized"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_missing_phase11_source_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(
        REPO_ROOT,
        source_phase11_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_BLOCKED"
    assert packet["execution_surface_promotion_gate_ready"] is False
    assert "required_phase11_controlled_writeback_gate_missing" in packet["source_blockers"]
    assert packet["phase11_controlled_writeback_activation_gate_hash_verified"] is False


def test_phase11_authority_mutation_fails_closed(tmp_path: Path) -> None:
    phase11 = _read_json(SOURCE_PHASE11_PATH)
    phase11["controlled_writeback_enabled"] = False
    source = _write_source(tmp_path, "mutated_phase11.json", phase11)

    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(
        REPO_ROOT,
        source_phase11_gate_path=source,
    )

    assert packet["execution_surface_promotion_gate_ready"] is False
    assert "phase11_controlled_writeback_activation_gate_self_hash_mismatch" in packet[
        "source_blockers"
    ]
    assert "phase11_controlled_writeback_not_enabled" in packet["source_blockers"]


def test_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("execution_surface_promotion_gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase6_execution_surface_promotion_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase6_execution_surface_promotion_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["execution_surface_promotion_gate_hash"] == packet[
        "execution_surface_promotion_gate_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_markdown() -> None:
    packet = build_v2_hygiene_phase6_execution_surface_promotion_gate(REPO_ROOT)
    markdown = render_v2_hygiene_phase6_execution_surface_promotion_gate_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Phase 6 Execution Surface Promotion Gate"
    assert any("## Execution Surface Matrix" in line for line in markdown)
    assert any("core_governance_modules" in line for line in markdown)
    assert any("brier_resolution_authorized: False" in line for line in markdown)
