from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan import (
    DECISION_RECORD_LANE,
    PLAN_ID,
    build_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan,
    write_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan.py",
    "local_abx_research_canary_orphan_policy_decision_record_plan_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan.v1.schema.json"
)


def test_plan_is_deterministic() -> None:
    first = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
        source_root=REPO_ROOT
    )
    assert first["decision_record_plan_hash"] == second["decision_record_plan_hash"]
    assert first["decision_record_plan_id"] == PLAN_ID


def test_plan_ready_when_prerequisites_observed() -> None:
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
        source_root=REPO_ROOT
    )
    assert packet["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_READY"
    assert packet["recommended_default_decision"] == "MAINTAIN_EXCLUDE_FROM_CANONICAL_REPAIR"
    assert packet["recommended_next_lane"] == DECISION_RECORD_LANE


def test_writer_runner_and_schema(tmp_path: Path) -> None:
    packet = write_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["decision_record_plan_hash"] == packet["decision_record_plan_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
