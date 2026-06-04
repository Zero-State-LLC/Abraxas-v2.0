from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.rune_registry_formalization_plan import build_rune_registry_formalization_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/rune_registry_formalization_plan.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_rune_registry_formalization_plan

        return run_rune_registry_formalization_plan
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_rune_registry_formalization_plan.py"
        spec = importlib.util.spec_from_file_location("run_rune_registry_formalization_plan", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_rune_registry_formalization_plan_is_advisory_only() -> None:
    packet = build_rune_registry_formalization_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "RuneRegistryFormalizationPlan.v1"
    assert packet["plan_status"] == "PLAN_EMITTED_ADVISORY_ONLY"
    assert packet["rune_registration_performed"] is False
    assert packet["catalog_mutation_performed"] is False
    assert packet["pipeline_mutation_performed"] is False
    assert packet["route_mutation_performed"] is False
    assert packet["execution_dispatch_changed"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_rune_registry_formalization_plan_holds_candidate_runes() -> None:
    packet = build_rune_registry_formalization_plan(repo_root=REPO_ROOT)
    records = {record["rune_id"]: record for record in packet["plan_records"]}

    assert packet["catalog_rune_count"] == 24
    assert packet["required_rune_count"] == 20
    assert packet["candidate_hold_count"] == 4
    assert packet["belief_graph_equivalent_observed"] is True
    assert records["RUNE.PIPELINE.PARSE"]["formalization_action"] == "PRESERVE_REQUIRED_RUNE"
    assert records["RUNE.PIPELINE.OPERATOR_REVIEW"]["formalization_action"] == "HOLD_CANDIDATE_ONLY"
    assert records["RUNE.PIPELINE.OPERATOR_REVIEW"]["operator_authorization_required"] is True
    assert records["RUNE.YGGDRASIL.ROUTE_RECEIPT"]["catalog_change_required"] is False
    assert packet["formalization_summary"]["catalog_changes_planned"] == 0
    assert packet["formalization_summary"]["dispatch_changes_planned"] == 0


def test_rune_registry_formalization_plan_schema_and_hash_are_stable() -> None:
    packet = build_rune_registry_formalization_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_rune_registry_formalization_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/rune_registry_formalization_plan_001.latest.json"
    out_md = tmp_path / "out/audit/rune_registry_formalization_plan_001.latest.md"
    run_rune_registry_formalization_plan = _load_runner()

    first = run_rune_registry_formalization_plan.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_rune_registry_formalization_plan.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
