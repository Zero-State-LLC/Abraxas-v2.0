from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt import (
    READY_STATUS,
    RECEIPT_JSON_PATH,
    RECOMMENDED_OPERATOR_REVIEW_GATE,
    build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt,
    render_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_markdown,
    write_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt,
)
from scripts import run_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt.v1.schema.json"
)
SOURCE_PHASE6_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_promotion_closure_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_phase2_subsystem_selection_receipt_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT
    )

    assert first["selection_receipt_hash"] == second["selection_receipt_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["selection_receipt_ready"] is True
    assert first["phase1_stabilization_advisory_complete_observed"] is True
    assert first["phase1_promotion_readiness_classification"] == (
        "ADVISORY_COMPLETE_NOT_CANON_PROMOTED"
    )
    assert first["recommended_next_lane"] == RECOMMENDED_OPERATOR_REVIEW_GATE
    assert first["candidate_next_lane_count"] == 5
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["valid_for_writeback"] is False
    assert first["valid_for_promotion"] is False
    assert first["valid_for_activation"] is False
    assert first["valid_for_execution"] is False
    assert first["safe_to_auto_continue"] is False


def test_phase2_subsystem_selection_receipt_missing_source_fails_closed(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT,
        source_phase6_promotion_closure_receipt_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE2_NEXT_STABILIZATION_SUBSYSTEM_SELECTION_RECEIPT_BLOCKED"
    )
    assert packet["selection_receipt_ready"] is False
    assert "required_phase6_promotion_closure_receipt_missing" in packet[
        "source_blockers"
    ]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["candidate_next_lane_count"] == 0


def test_phase2_subsystem_selection_receipt_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    phase6 = _read_json(SOURCE_PHASE6_PATH)
    phase6["runtime_activation_authorized"] = True
    phase6["authority_locks"]["activation"] = True
    source = _write_source(tmp_path, "authorizing_phase6.json", phase6)

    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT,
        source_phase6_promotion_closure_receipt_path=source,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE2_NEXT_STABILIZATION_SUBSYSTEM_SELECTION_RECEIPT_BLOCKED"
    )
    assert "phase6_closure_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "phase6_closure_receipt_authority_expanding_field:runtime_activation_authorized"
        in packet["source_blockers"]
    )
    assert "phase6_closure_receipt_authority_lock_true:activation" in packet[
        "source_blockers"
    ]
    assert packet["selection_receipt_ready"] is False
    assert packet["runtime_activation_authorized"] is False


def test_phase2_subsystem_selection_receipt_unfinalized_source_claim_blocks(
    tmp_path: Path,
) -> None:
    phase6 = _read_json(SOURCE_PHASE6_PATH)
    claim = phase6["promotion_closure_contract"]["closure_claims"][0]
    claim["claim_finalized"] = False
    claim["closure_status"] = "BLOCKED"
    source = _write_source(tmp_path, "unfinalized_phase6.json", phase6)

    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT,
        source_phase6_promotion_closure_receipt_path=source,
    )

    assert "phase6_closure_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert "phase6_closure_claim_not_finalized" in packet["source_blockers"]
    assert packet["selection_receipt_ready"] is False
    assert packet["phase1_stabilization_advisory_complete_observed"] is False


def test_phase2_subsystem_selection_receipt_contract_shape() -> None:
    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT
    )
    contract = packet["next_stabilization_subsystem_selection_contract"]
    candidates = packet["candidate_next_lane_matrix"]
    brier_contract = packet["brier_scoring_contract"]
    rune_mapping = packet["rune_governance_mapping"]

    assert contract["phase1_source_hash"] == (
        "3f40995d73afb860bd78396e94c8a5f1d34ba9a63fec269327c8a4c8a3879e01"
    )
    assert contract["phase1_stabilization_advisory_complete"] is True
    assert contract["recommended_operator_review_gate"] == RECOMMENDED_OPERATOR_REVIEW_GATE
    assert contract["candidate_count"] == 5
    assert len(candidates) == 5
    assert {candidate["candidate_id"] for candidate in candidates} == {
        "writeback_authorization",
        "canon_promotion_authorization",
        "runtime_activation_planning",
        "package_lock_dependency_hygiene",
        "broader_subsystem_readiness_audit",
    }
    assert all(candidate["authority_granted"] is False for candidate in candidates)
    assert all(
        candidate["risk_level"] in {"LOW", "MEDIUM", "HIGH"} for candidate in candidates
    )
    assert all(value is False for value in contract["authority_denials"].values())
    assert brier_contract["telemetry_only"] is True
    assert brier_contract["resolution_allowed"] is False
    assert brier_contract["promotion_authorized"] is False
    assert brier_contract["brier_resolution_authorized"] is False
    assert len(brier_contract["telemetry_hooks"]) == 5
    assert all(
        hook["binary_outcome"] == "NOT_COMPUTABLE"
        for hook in brier_contract["telemetry_hooks"]
    )
    assert {item["rune"] for item in rune_mapping} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in rune_mapping)


def test_phase2_subsystem_selection_receipt_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT
    )

    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["canon_promotion_authorized"] is False
    assert packet["runtime_activation_authorized"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["forecast_routing_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["brier_resolution_authorized"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_phase2_subsystem_selection_receipt_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("selection_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_phase2_subsystem_selection_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["selection_receipt_hash"] == packet["selection_receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_phase2_subsystem_selection_receipt_markdown() -> None:
    packet = build_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt(
        REPO_ROOT
    )
    markdown = (
        render_v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_markdown(
            packet
        )
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 2 Next Stabilization Subsystem Selection Receipt"
    )
    assert any("## Candidate Next-Lane Matrix" in line for line in markdown)
    assert any("package_lock_dependency_hygiene" in line for line in markdown)
    assert any("promotion_authorized: False" in line for line in markdown)
