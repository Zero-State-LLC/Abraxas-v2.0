from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.rune_equivalent_surface_audit import build_rune_equivalent_surface_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/rune_equivalent_surface_audit.v1.schema.json"


def _load_runner():
    try:
        from scripts.operator import run_rune_equivalent_surface_audit

        return run_rune_equivalent_surface_audit
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_rune_equivalent_surface_audit.py"
        spec = importlib.util.spec_from_file_location("run_rune_equivalent_surface_audit", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_rune_equivalent_surface_audit_is_advisory_only() -> None:
    packet = build_rune_equivalent_surface_audit(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "RuneEquivalentSurfaceAudit.v1"
    assert packet["audit_status"] == "EMITTED_ADVISORY_ONLY"
    assert packet["rune_registration_performed"] is False
    assert packet["execution_dispatch_changed"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_rune_equivalent_surface_audit_records_required_and_candidate_runes() -> None:
    packet = build_rune_equivalent_surface_audit(repo_root=REPO_ROOT)
    records = {record["rune_id"]: record for record in packet["surface_records"]}

    assert packet["catalog_rune_count"] == 29
    assert packet["required_rune_count"] == 29
    assert packet["unrequired_rune_count"] == 0
    assert records["RUNE.PIPELINE.PARSE"]["equivalence_status"] == "OBSERVED_REQUIRED"
    assert records["RUNE.PIPELINE.PARSE"]["pipeline_requirement_count"] == 10
    assert records["RUNE.PIPELINE.OPERATOR_REVIEW"]["candidate_only"] is False
    # operator_review_queue + drift_scan (2); alembic_spine (03dc6028) and eight
    # Track B contracts (cc173aab) also require operator review -> 11.
    assert records["RUNE.PIPELINE.OPERATOR_REVIEW"]["pipeline_requirement_count"] == 11
    assert records["RUNE.YGGDRASIL.ROUTE_RECEIPT"]["duplicate_risk"] == "LOW"
    assert all(record["catalog_authority_locked"] for record in packet["surface_records"])


def test_rune_equivalent_surface_audit_schema_and_hash_are_stable() -> None:
    packet = build_rune_equivalent_surface_audit(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_rune_equivalent_surface_audit_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/rune_equivalent_surface_audit_001.latest.json"
    out_md = tmp_path / "out/audit/rune_equivalent_surface_audit_001.latest.md"
    run_rune_equivalent_surface_audit = _load_runner()

    first = run_rune_equivalent_surface_audit.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_rune_equivalent_surface_audit.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
