from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_dependency_hygiene_package_lock_receipt import (
    HELD_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt,
    render_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_markdown,
    write_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt,
)
from scripts.hygiene import run_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_dependency_hygiene_package_lock_receipt.v1.schema.json"
)
SOURCE_PHASE8_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_dependency_hygiene_receipt_holds_package_lock_tracking() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(REPO_ROOT)

    assert packet["status"] == HELD_STATUS
    assert packet["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert packet["source_blockers"] == []
    assert packet["dependency_hygiene_receipt_ready"] is True
    assert packet["phase8_operator_review_gate_hash_verified"] is True
    assert packet["recommended_next_lane"] == (
        "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_ROOT_CAUSE_RECEIPT_001"
    )
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["package_lock_resolution_ready"] is False
    assert packet["package_lock_resolution_held"] is True
    assert packet["package_lock_tracking_authorized"] is False
    assert packet["valid_for_package_lock_tracking"] is False
    assert packet["valid_for_execution"] is False


def test_dependency_hygiene_receipt_records_lockfile_diagnostics() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(REPO_ROOT)
    diagnostics = packet["package_lock_diagnostics"]
    resolution = packet["resolution_contract"]

    assert diagnostics["package_json_file_observed"] is True
    assert diagnostics["package_lock_file_observed"] is True
    assert diagnostics["metadata_consistent_with_package_json"] is True
    assert diagnostics["empty_version_entry_count"] == 0
    assert diagnostics["package_lock_hash_unchanged_after_validation_attempt"] is True
    assert diagnostics["package_lock_tracked_in_git"] is False
    assert resolution["preferred_disposition"] == "COMMIT_AND_TRACK_IF_VALIDATED"
    assert resolution["actual_disposition"] == "HOLD_VALIDATION_FAILED"
    assert resolution["package_lock_tracking_authorized"] is False
    assert resolution["fail_closed_blocker"] == (
        "npm_install_package_lock_only_failed_invalid_version"
    )


def test_dependency_hygiene_receipt_toolchain_and_validation_evidence() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(REPO_ROOT)

    toolchains = {item["toolchain_id"]: item for item in packet["toolchain_observations"]}
    assert toolchains["system_node_npm"]["node_version"] == "v26.0.0"
    assert toolchains["system_node_npm"]["npm_version"] == "11.17.0"
    assert toolchains["homebrew_node20"]["observed"] is False
    assert toolchains["codex_bundled_node"]["npm_version"] == "NOT_COMPUTABLE"
    assert any(
        item["command"] == "npm install --package-lock-only --ignore-scripts --legacy-peer-deps"
        and item["status"] == "FAILED_INVALID_VERSION"
        and item["observed_error"] == "Invalid Version"
        for item in packet["validation_evidence"]
    )
    assert packet["root_cause_classification"]["classification"] == (
        "TOOLCHAIN_LOCKFILE_DEDUPE_COMPATIBILITY_HOLD"
    )


def test_dependency_hygiene_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(
        REPO_ROOT,
        source_phase8_operator_review_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_BLOCKED"
    )
    assert packet["dependency_hygiene_receipt_ready"] is False
    assert "required_phase8_operator_review_gate_missing" in packet["source_blockers"]
    assert packet["phase8_operator_review_gate_hash_verified"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_dependency_hygiene_source_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    phase8 = _read_json(SOURCE_PHASE8_PATH)
    phase8["package_lock_tracking_authorized"] = True
    phase8["authority_locks"]["package_lock_tracking"] = True
    source = _write_source(tmp_path, "authorizing_phase8.json", phase8)

    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(
        REPO_ROOT,
        source_phase8_operator_review_gate_path=source,
    )

    assert packet["dependency_hygiene_receipt_ready"] is False
    assert "phase8_operator_review_gate_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "phase8_operator_review_gate_authority_expanding_field:package_lock_tracking_authorized"
        in packet["source_blockers"]
    )
    assert "phase8_operator_review_gate_authority_lock_true:package_lock_tracking" in packet[
        "source_blockers"
    ]
    assert packet["package_lock_tracking_authorized"] is False


def test_dependency_hygiene_contracts_preserve_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(REPO_ROOT)
    brier = packet["brier_scoring_contract"]
    runes = packet["rune_governance_mapping"]

    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["promotion_authorized"] is False
    assert brier["brier_resolution_authorized"] is False
    assert {item["rune"] for item in runes} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in runes)
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["canon_promotion_authorized"] is False
    assert packet["runtime_activation_authorized"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["package_json_mutation_authorized"] is False
    assert packet["npmrc_mutation_authorized"] is False
    assert packet["gitignore_mutation_authorized"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_dependency_hygiene_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(REPO_ROOT)
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("dependency_hygiene_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_dependency_hygiene_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["dependency_hygiene_receipt_hash"] == packet[
        "dependency_hygiene_receipt_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_dependency_hygiene_markdown() -> None:
    packet = build_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt(REPO_ROOT)
    markdown = render_v2_hygiene_phase1_dependency_hygiene_package_lock_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Dependency Hygiene Package-Lock Receipt"
    )
    assert any("## Package-Lock Diagnostics" in line for line in markdown)
    assert any("HOLD_VALIDATION_FAILED" in line for line in markdown)
    assert any("brier_resolution_authorized: False" in line for line in markdown)
