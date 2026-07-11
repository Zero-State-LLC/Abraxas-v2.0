from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run import (
    build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run,
    render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_markdown,
)
from core.canonical.json import canonical_hash
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run.v1.schema.json"
)
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run.py",
    "local_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_runner",
)


def test_seal_receipt_dry_run_is_validation_only() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptDryRun.v1"
    )
    assert (
        packet["seal_receipt_dry_run_status"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY"
    )
    assert packet["source_seal_receipt_plan"]["source_ready"] is True
    assert packet["validation_passed"] is True
    assert packet["seal_receipt_dry_run_only"] is True
    assert packet["seal_receipt_creation_allowed"] is False
    assert packet["seal_receipt_created"] is False
    assert packet["recursive_chain_sealed"] is False
    assert packet["recursive_chain_continuation_allowed"] is False
    assert (
        packet["recommended_next_lane"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW"
    )


def test_seal_receipt_dry_run_denies_authority() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
        repo_root=REPO_ROOT
    )

    assert packet["authorization_chain_continuation_allowed"] is False
    assert packet["authorization_record_creation_record_creation_allowed"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_token_created"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_seal_receipt_dry_run_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
        repo_root=tmp_path
    )

    assert packet["seal_receipt_dry_run_status"] == "NOT_COMPUTABLE"
    assert packet["validation_passed"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["source_seal_receipt_plan"]["source_ready"] is False


def test_seal_receipt_dry_run_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_seal_receipt_dry_run_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json"
    )
    out_md = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.md"
    )

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_seal_receipt_dry_run_markdown_and_registry_entries() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
        repo_root=REPO_ROOT
    )
    markdown = render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Dry Run"
    )
    assert any("validation_passed: True" in line for line in markdown)
    assert any("seal_receipt_creation_allowed: False" in line for line in markdown)

    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
