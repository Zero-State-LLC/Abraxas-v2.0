from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_orphan_output_registry_policy_operator_decision_record import (
    CHAIN_CLOSURE_LANE,
    DEFAULT_DECISION,
    RECORD_ID,
    build_abx_research_canary_orphan_output_registry_policy_operator_decision_record,
    write_abx_research_canary_orphan_output_registry_policy_operator_decision_record,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_orphan_output_registry_policy_operator_decision_record.py",
    "local_abx_research_canary_orphan_policy_decision_record_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_orphan_output_registry_policy_operator_decision_record.v1.schema.json"
)


def test_record_is_deterministic() -> None:
    first = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
        source_root=REPO_ROOT
    )
    assert first["decision_record_hash"] == second["decision_record_hash"]
    assert first["decision_record_id"] == RECORD_ID


def test_record_emitted_with_exclude_disposition() -> None:
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
        source_root=REPO_ROOT
    )
    assert packet["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_EMITTED"
    assert packet["selected_decision"] == DEFAULT_DECISION
    assert packet["orphan_count"] == 10
    assert packet["registry_mutation_performed"] is False
    assert len(packet["per_orphan_dispositions"]) == 10
    assert all(
        item["policy_disposition"] == DEFAULT_DECISION for item in packet["per_orphan_dispositions"]
    )
    assert packet["recommended_next_lane"] == CHAIN_CLOSURE_LANE


def test_writer_runner_and_schema(tmp_path: Path) -> None:
    packet = write_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["decision_record_hash"] == packet["decision_record_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
