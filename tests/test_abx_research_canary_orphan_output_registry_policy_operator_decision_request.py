from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_orphan_output_registry_policy_operator_decision_request import (
    DECISION_RECORD_PLAN_LANE,
    REQUEST_ID,
    build_abx_research_canary_orphan_output_registry_policy_operator_decision_request,
    render_abx_research_canary_orphan_output_registry_policy_operator_decision_request_markdown,
    write_abx_research_canary_orphan_output_registry_policy_operator_decision_request,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_research_canary_orphan_output_registry_policy_operator_decision_request.py",
    "local_abx_research_canary_orphan_policy_operator_decision_request_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_orphan_output_registry_policy_operator_decision_request.v1.schema.json"
)


def test_request_is_deterministic() -> None:
    first = build_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
        source_root=REPO_ROOT
    )
    assert first["request_hash"] == second["request_hash"]
    assert first["request_id"] == REQUEST_ID


def test_request_is_advisory_and_fail_closed() -> None:
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
        source_root=REPO_ROOT
    )
    assert packet["advisory_only"] is True
    assert packet["registry_mutation_performed"] is False
    assert packet["recommended_decision"] == "EXCLUDE_FROM_CANONICAL_REPAIR"


def test_request_emitted_when_policy_review_ready() -> None:
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
        source_root=REPO_ROOT
    )
    assert packet["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_EMITTED"
    assert packet["orphan_count"] == 10
    assert packet["recommended_next_lane"] == DECISION_RECORD_PLAN_LANE
    assert packet["downstream_status"] == "READY_FOR_OPERATOR_DECISION_RECORD_PLAN"


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
        source_root=REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_request_001.latest.json"
    )
    assert json_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["request_hash"] == packet["request_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
    markdown = render_abx_research_canary_orphan_output_registry_policy_operator_decision_request_markdown(packet)
    assert markdown[0].startswith("# ABX Research Canary Orphan")


def test_registry_includes_decision_request_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_request_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
