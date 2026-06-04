from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.belief_graph_gap_verification import build_belief_graph_gap_verification
from core.canonical.json import canonical_hash

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/belief_graph_gap_verification.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_belief_graph_gap_verification

        return run_belief_graph_gap_verification
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_belief_graph_gap_verification.py"
        spec = importlib.util.spec_from_file_location("run_belief_graph_gap_verification", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_belief_graph_gap_verification_is_advisory_only() -> None:
    packet = build_belief_graph_gap_verification(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "BeliefGraphGapVerification.v1"
    assert packet["verification_status"] == "GAP_VERIFICATION_EMITTED_ADVISORY_ONLY"
    assert packet["belief_graph_implementation_performed"] is False
    assert packet["graph_runtime_created"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_belief_graph_gap_verification_records_observed_components() -> None:
    packet = build_belief_graph_gap_verification(repo_root=REPO_ROOT)
    records = {record["component"]: record for record in packet["component_records"]}

    assert packet["belief_graph_equivalent_observed"] is True
    assert packet["summary"]["observed_components"] == packet["summary"]["total_components"]
    assert packet["summary"]["missing_components"] == 0
    assert records["ClaimObject"]["status"] == "OBSERVED"
    assert records["EvidenceObject"]["status"] == "OBSERVED"
    assert records["TheoryObject"]["status"] == "OBSERVED"
    assert records["SignalGraph"]["status"] == "OBSERVED"
    assert records["BeliefGraphPacket"]["status"] == "OBSERVED"
    assert records["IngestBeliefGraphBridge"]["status"] == "OBSERVED"
    assert packet["recommended_next_patch"] == "PATCH-ABX-RUNE-REGISTRY-FORMALIZATION-PLAN-001"


def test_belief_graph_gap_verification_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_gap_verification(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_belief_graph_gap_verification_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/belief_graph_gap_verification_001.latest.json"
    out_md = tmp_path / "out/audit/belief_graph_gap_verification_001.latest.md"
    run_belief_graph_gap_verification = _load_runner()

    first = run_belief_graph_gap_verification.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_belief_graph_gap_verification.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
