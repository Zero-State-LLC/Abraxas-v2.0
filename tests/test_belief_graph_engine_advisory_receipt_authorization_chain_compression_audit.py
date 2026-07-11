from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_advisory_receipt_authorization_chain_compression_audit import (
    DENIED_AUTHORITY,
    REJECTED_RECURSIVE_NEXT_LANE,
    build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit,
    render_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_markdown,
)
from core.canonical.json import canonical_hash
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "belief_graph_engine_advisory_receipt_authorization_chain_compression_audit.v1.schema.json"
)
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit.py",
    "local_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_runner",
)


def test_compression_audit_rejects_redundant_recursive_lane() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
        repo_root=REPO_ROOT
    )

    assert (
        packet["artifact_type"]
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainCompressionAudit.v1"
    )
    assert (
        packet["compression_audit_status"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_READY"
    )
    assert packet["recursive_pattern_observed"] is True
    assert packet["rejected_recursive_next_lane"] == REJECTED_RECURSIVE_NEXT_LANE
    assert packet["further_recursive_lane_recommended"] is False
    assert packet["chain_recommendation"] == "SEAL_RECURSIVE_AUTHORIZATION_CHAIN"
    assert packet["compression_recommendation"] == "COMPRESS_TO_GENERIC_TEMPLATE"
    assert (
        packet["recommended_next_lane"]
        == "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN"
    )


def test_compression_audit_denies_authority() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
        repo_root=REPO_ROOT
    )

    for authority in DENIED_AUTHORITY:
        assert authority in packet["denied_authority"]
    assert packet["authorization_chain_continuation_allowed"] is False
    assert packet["authorization_record_creation_record_creation_allowed"] is False
    assert packet["authorization_record_created"] is False
    assert packet["authorization_token_created"] is False
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_compression_audit_fails_closed_without_source(tmp_path: Path) -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
        repo_root=tmp_path
    )

    assert packet["compression_audit_status"] == "NOT_COMPUTABLE"
    assert packet["recursive_pattern_observed"] is False
    assert packet["chain_recommendation"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["source_record_creation_record_plan"]["source_ready"] is False


def test_compression_audit_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_compression_audit_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json"
    )
    out_md = (
        tmp_path
        / "out/audit/"
        "belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.md"
    )

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_compression_audit_markdown_and_registry_entries() -> None:
    packet = build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
        repo_root=REPO_ROOT
    )
    markdown = render_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_markdown(
        packet
    )

    assert (
        markdown[0]
        == "# Belief Graph Engine Advisory Receipt Authorization Chain Compression Audit"
    )
    assert any("further_recursive_lane_recommended: False" in line for line in markdown)
    assert any("AUTHORIZATION_CHAIN_CONTINUATION" in line for line in markdown)

    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
