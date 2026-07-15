from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from core.aal_viz_temporal_diff import (
    TemporalDiffError,
    compare_operator_platform_projections,
    generation_id,
)

ROOT = Path(__file__).resolve().parents[1]
PROJECTION_SCHEMA = (
    ROOT / "contracts/canon/aal_viz_operator_platform_projection.v0.2.schema.json"
)
TEMPORAL_SCHEMA = ROOT / "contracts/canon/aal_viz_temporal_diff.v1.schema.json"
HASH = "a" * 64


def _source(source_key: str, path: str) -> dict[str, Any]:
    return {
        "source_key": source_key,
        "path": path,
        "declared_canonical_hash": HASH,
        "content_sha256": HASH,
        "integrity_state": "VERIFIED",
    }


def _section(payload: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "AVAILABLE",
        "provenance": "OBSERVED",
        "source_artifacts": [source],
        "payload": payload,
        "not_computable_reason": None,
        "validation_findings": [],
    }


def projection() -> dict[str, Any]:
    topology_source = _source("graph_render", "out/projections/graph.json")
    contract_source = _source("contract_inventory", "out/audit/contracts.json")
    evidence_source = _source("surface_receipt", "out/audit/surface_receipt.json")
    status_source = _source("operator_console", "out/audit/operator.json")
    production_source = _source("production_slice", "out/audit/production.json")
    temporal_source = _source("temporal_diff", "out/projections/temporal.json")
    return {
        "schema_version": "AALViz.OperatorPlatformProjection.v0.2",
        "generation": {
            "generated_at": "2026-07-15T00:00:00Z",
            "generated_by": "TEST",
            "source_bundle_schema_version": "AALViz.LiveConsoleProjectionBundle.v0.2",
        },
        "authority": {
            "projection_only": True,
            "runtime_mutation_allowed": False,
            "promotion_allowed": False,
            "production_activation_allowed": False,
        },
        "projection_only": True,
        "source_artifacts": sorted(
            [
                topology_source,
                contract_source,
                evidence_source,
                status_source,
                production_source,
                temporal_source,
            ],
            key=lambda item: item["source_key"],
        ),
        "system_status": _section(
            {
                "source_status": "OBSERVED",
                "stabilization_status": "READY",
                "production_slice_status": "OBSERVED",
                "system_count": 1,
                "ready_system_count": 1,
                "work_items": [
                    {
                        "id": "work:1",
                        "label": "Review",
                        "status": "OPEN",
                        "target": "aal-viz",
                    }
                ],
                "failures": [],
                "inherited_debt": [],
                "receipt_count": 1,
                "operator_summary": [],
            },
            status_source,
        ),
        "topology": _section(
            {
                "source_status": "OBSERVED",
                "nodes": [
                    {
                        "id": "node:1",
                        "label": "One",
                        "entity_type": "SYSTEM",
                        "status": "READY",
                        "source_ref": "one",
                        "provenance": "test",
                    }
                ],
                "edges": [],
            },
            topology_source,
        ),
        "production_slice": _section(
            {
                "source_status": "OBSERVED",
                "classification": "OBSERVED",
                "entrypoint": "scripts/test.py",
                "invocation": "python scripts/test.py",
                "orchestration": ["first", "second"],
                "validators": ["schema", "authority"],
                "execution_flow": ["load", "validate", "publish"],
                "artifacts": [],
                "receipts": [],
                "excluded_surfaces": [],
                "unresolved_links": [],
                "external_calls": False,
                "persistence_behavior": "OUTPUT_ONLY",
            },
            production_source,
        ),
        "contract_graph": _section(
            {
                "source_status": "OBSERVED",
                "contract_count": 1,
                "unowned_count": 1,
                "unvalidated_count": 1,
                "contracts": [
                    {
                        "id": "contract:1",
                        "language": "json",
                        "version": "1",
                        "owner": "UNRESOLVED",
                        "owner_resolved": False,
                        "validation_mode": "NONE",
                        "production_reachability": "OBSERVED",
                        "producers": ["p"],
                        "validators": [],
                        "consumers": ["c"],
                    }
                ],
            },
            contract_source,
        ),
        "evidence_index": _section(
            {
                "records": [
                    {
                        "id": "receipt:1",
                        "source_status": "OBSERVED",
                        "source_path": "out/audit/surface_receipt.json",
                        "canonical_hash": HASH,
                        "status": "READY",
                        "inputs": [],
                        "outputs": [],
                        "schemas": [],
                        "links": [],
                        "fail_closed_reason": None,
                    }
                ],
            },
            evidence_source,
        ),
        "temporal_diff": _section(
            {
                "source_status": "OBSERVED",
                "status": "NO_CHANGE",
                "prior_generation_id": None,
                "current_generation_id": None,
                "comparison_scope": [],
                "out_of_scope": ["LINEAGE", "QUEUE", "TRANSPORT"],
                "category_counts": {
                    "TOPOLOGY_NODE": 0,
                    "TOPOLOGY_EDGE": 0,
                    "CONTRACT_FIELD": 0,
                    "OWNERSHIP": 0,
                    "VALIDATOR_STATE": 0,
                    "RECEIPT": 0,
                    "PACKET": 0,
                    "SOURCE_INTEGRITY": 0,
                    "SECTION_STATUS": 0,
                },
                "total_change_count": 0,
                "not_computable_count": 0,
                "topology_change_count": 0,
                "lineage_shift_count": 0,
                "queue_delta_count": 0,
                "transport_delta_count": 0,
                "operator_summary": "stable",
                "entries": [],
                "remaining_blockers": [],
            },
            temporal_source,
        ),
    }


def compare(prior: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    return compare_operator_platform_projections(
        prior,
        current,
        prior_source_path="tests/fixtures/prior.json",
        current_source_path="tests/fixtures/current.json",
        prior_source_sha256="1" * 64,
        current_source_sha256="2" * 64,
        projection_schema_path=PROJECTION_SCHEMA,
        temporal_schema_path=TEMPORAL_SCHEMA,
    )


def test_no_change_is_deterministic_and_schema_valid() -> None:
    artifact = compare(projection(), projection())
    assert artifact == compare(projection(), projection())
    assert artifact["status"] == "NO_CHANGE"
    assert artifact["entries"] == []
    schema = json.loads(TEMPORAL_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(artifact)


def test_generation_identity_excludes_timestamp_and_temporal_section() -> None:
    prior = projection()
    current = copy.deepcopy(prior)
    current["generation"]["generated_at"] = "2026-07-16T00:00:00Z"
    current["temporal_diff"]["payload"]["operator_summary"] = "different"
    assert generation_id(prior) == generation_id(current)


def test_topology_addition_and_removal_are_typed() -> None:
    prior = projection()
    current = projection()
    current["topology"]["payload"]["nodes"] = [
        {
            "id": "node:2",
            "label": "Two",
            "entity_type": "PACKET",
            "status": "READY",
            "source_ref": "two",
            "provenance": "test",
        }
    ]
    entries = compare(prior, current)["entries"]
    assert {
        (entry["operation"], entry["category"])
        for entry in entries
        if entry["category"] == "TOPOLOGY_NODE"
    } == {("ADDED", "TOPOLOGY_NODE"), ("REMOVED", "TOPOLOGY_NODE")}


def test_contract_ownership_and_validator_evidence_impacts() -> None:
    prior = projection()
    current = projection()
    contract = current["contract_graph"]["payload"]["contracts"][0]
    contract["owner"] = "core.owner"
    contract["owner_resolved"] = True
    contract["validators"] = ["validate"]
    entries = compare(prior, current)["entries"]
    impacts = {
        (entry["category"], entry["field_path"].rsplit("/", 1)[-1]): entry["impact"]
        for entry in entries
    }
    assert impacts[("OWNERSHIP", "owner")] == "STRENGTHENED"
    assert impacts[("OWNERSHIP", "owner_resolved")] == "STRENGTHENED"
    assert impacts[("VALIDATOR_STATE", "validators")] == "STRENGTHENED"


def test_validation_mode_string_change_is_neutral() -> None:
    prior = projection()
    current = projection()
    current["contract_graph"]["payload"]["contracts"][0]["validation_mode"] = "CUSTOM"
    entry = next(
        entry
        for entry in compare(prior, current)["entries"]
        if entry["category"] == "VALIDATOR_STATE"
    )
    assert entry["impact"] == "NEUTRAL"


def test_receipt_changes_are_typed() -> None:
    prior = projection()
    current = projection()
    current["evidence_index"]["payload"]["records"][0]["status"] = "STALE"
    entry = next(
        entry
        for entry in compare(prior, current)["entries"]
        if entry["category"] == "RECEIPT"
    )
    assert entry["operation"] == "CHANGED"


def test_partial_evidence_never_implies_removal() -> None:
    prior = projection()
    current = projection()
    current["topology"]["status"] = "PARTIAL"
    current["topology"]["validation_findings"] = ["one excluded record"]
    current["topology"]["payload"]["nodes"] = []
    entries = compare(prior, current)["entries"]
    topology = [entry for entry in entries if entry["category"] == "TOPOLOGY_NODE"]
    assert {entry["operation"] for entry in topology} == {"NOT_COMPUTABLE"}
    assert all(entry["reason_code"] == "PARTIAL_EVIDENCE" for entry in topology)


def test_set_like_arrays_are_order_independent_but_flow_is_ordered() -> None:
    prior = projection()
    current = projection()
    current["production_slice"]["payload"]["validators"].reverse()
    assert generation_id(prior) == generation_id(current)
    current["production_slice"]["payload"]["execution_flow"].reverse()
    assert generation_id(prior) != generation_id(current)


def test_authority_and_absolute_path_fail_closed() -> None:
    bad = projection()
    bad["authority"]["runtime_mutation_allowed"] = True
    with pytest.raises(TemporalDiffError, match="schema violation|authority violation"):
        compare(bad, projection())
    with pytest.raises(TemporalDiffError, match="repository-relative"):
        compare_operator_platform_projections(
            projection(),
            projection(),
            prior_source_path="/tmp/prior.json",
            current_source_path="tests/current.json",
            prior_source_sha256="1" * 64,
            current_source_sha256="2" * 64,
            projection_schema_path=PROJECTION_SCHEMA,
            temporal_schema_path=TEMPORAL_SCHEMA,
        )


def test_entry_ids_and_canonical_hash_follow_locked_vectors() -> None:
    prior = projection()
    current = projection()
    current["contract_graph"]["payload"]["contracts"][0]["owner_resolved"] = True
    artifact = compare(prior, current)
    entry = next(
        entry for entry in artifact["entries"] if entry["category"] == "OWNERSHIP"
    )
    identity = [
        entry["operation"],
        entry["category"],
        entry["entity_id"],
        entry["field_path"],
    ]
    expected = hashlib.sha256(
        json.dumps(identity, separators=(",", ":")).encode()
    ).hexdigest()
    assert entry["id"] == expected
    unhashed = {
        key: value for key, value in artifact.items() if key != "canonical_hash"
    }
    expected_artifact_hash = hashlib.sha256(
        json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert artifact["canonical_hash"] == expected_artifact_hash


def test_no_research_canary_paths_are_used() -> None:
    assert "research_canary" not in json.dumps(compare(projection(), projection()))


def test_operator_runner_publishes_only_from_explicit_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.operator import run_temporal_diff_engine as runner

    prior_path = tmp_path / "prior.json"
    current_path = tmp_path / "current.json"
    output_path = tmp_path / "out.json"
    prior_path.write_text(json.dumps(projection()), encoding="utf-8")
    current = projection()
    current["topology"]["payload"]["nodes"].append(
        {
            "id": "node:2",
            "label": "Two",
            "entity_type": "PACKET",
            "status": "READY",
            "source_ref": "two",
            "provenance": "test",
        }
    )
    current_path.write_text(json.dumps(current), encoding="utf-8")
    paths = {"prior.json": prior_path, "current.json": current_path}
    monkeypatch.setattr(runner, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(runner, "_repository_path", lambda value: paths[value])
    assert runner.main(["--prior", "prior.json", "--current", "current.json"]) == 0
    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["status"] == "CHANGED"
    assert (
        artifact["prior_generation"]["source_sha256"]
        == hashlib.sha256(prior_path.read_bytes()).hexdigest()
    )


def test_operator_runner_missing_and_malformed_inputs_fail_as_specified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.operator import run_temporal_diff_engine as runner

    prior_path = tmp_path / "prior.json"
    current_path = tmp_path / "current.json"
    output_path = tmp_path / "out.json"
    prior_path.write_text(json.dumps(projection()), encoding="utf-8")
    paths = {"prior.json": prior_path, "current.json": current_path}
    monkeypatch.setattr(runner, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(runner, "_repository_path", lambda value: paths[value])
    assert runner.main(["--prior", "prior.json", "--current", "current.json"]) == 0
    missing = json.loads(output_path.read_text(encoding="utf-8"))
    assert missing["status"] == "NOT_COMPUTABLE"
    assert missing["summary"]["not_computable_count"] == 1
    assert missing["entries"][0]["operation"] == "NOT_COMPUTABLE"
    assert missing["prior_generation"]["generation_id"] == generation_id(projection())

    output_path.unlink()
    current_path.write_text("{malformed", encoding="utf-8")
    assert runner.main(["--prior", "prior.json", "--current", "current.json"]) == 1
    assert not output_path.exists()


def test_two_root_and_hash_seed_output_is_byte_identical(tmp_path: Path) -> None:
    roots = [tmp_path / "one", tmp_path / "two"]
    for root in roots:
        root.mkdir()
        (root / "prior.json").write_text(json.dumps(projection()), encoding="utf-8")
        current = projection()
        current["contract_graph"]["payload"]["contracts"][0]["owner_resolved"] = True
        (root / "current.json").write_text(json.dumps(current), encoding="utf-8")
    program = """
import json, sys
from pathlib import Path
from core.aal_viz_temporal_diff import canonical_json, compare_operator_platform_projections
root = Path(sys.argv[1])
repo = Path(sys.argv[2])
prior_raw = (root / 'prior.json').read_bytes()
current_raw = (root / 'current.json').read_bytes()
artifact = compare_operator_platform_projections(
    json.loads(prior_raw), json.loads(current_raw),
    prior_source_path='snapshots/prior.json', current_source_path='snapshots/current.json',
    prior_source_sha256=__import__('hashlib').sha256(prior_raw).hexdigest(),
    current_source_sha256=__import__('hashlib').sha256(current_raw).hexdigest(),
    projection_schema_path=repo / 'contracts/canon/aal_viz_operator_platform_projection.v0.2.schema.json',
    temporal_schema_path=repo / 'contracts/canon/aal_viz_temporal_diff.v1.schema.json',
)
sys.stdout.buffer.write(canonical_json(artifact))
"""
    outputs = []
    for root, seed in zip(roots, ("1", "987654"), strict=True):
        environment = {
            **os.environ,
            "PYTHONHASHSEED": seed,
            "SOURCE_DATE_EPOCH": "1784073600",
            "PYTHONPATH": str(ROOT),
        }
        result = subprocess.run(
            [sys.executable, "-c", program, str(root), str(ROOT)],
            check=True,
            capture_output=True,
            env=environment,
            cwd=ROOT,
        )
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1]
