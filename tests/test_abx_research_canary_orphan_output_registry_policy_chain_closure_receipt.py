from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_research_canary_orphan_output_registry_policy_chain_closure_receipt import (
    RECEIPT_ID,
    build_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt,
    write_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt.py",
    "local_abx_research_canary_orphan_policy_chain_closure_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/"
    "abx_research_canary_orphan_output_registry_policy_chain_closure_receipt.v1.schema.json"
)


def test_chain_closure_is_deterministic() -> None:
    first = build_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(
        source_root=REPO_ROOT
    )
    second = build_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(
        source_root=REPO_ROOT
    )
    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["artifact_id"] == RECEIPT_ID


def test_chain_closure_blocked_without_upstream_artifacts(tmp_path: Path) -> None:
    packet = build_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(
        source_root=tmp_path
    )
    assert packet["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_BLOCKED"
    assert packet["chain_closure_status"] == "NOT_COMPUTABLE"


def test_chain_closure_emitted_when_chain_complete(tmp_path: Path) -> None:
    import shutil

    from core.abx_research_canary_orphan_output_registry_policy_operator_decision_record import (
        write_abx_research_canary_orphan_output_registry_policy_operator_decision_record,
    )
    from core.abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan import (
        write_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan,
    )
    from core.abx_research_canary_orphan_output_registry_policy_operator_decision_request import (
        write_abx_research_canary_orphan_output_registry_policy_operator_decision_request,
    )

    for name in (
        "abx_research_canary_orphan_output_registry_policy_review_001.latest.json",
        "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json",
    ):
        src = REPO_ROOT / "out/operator_review" / name
        dst = tmp_path / "out/operator_review" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)

    write_abx_research_canary_orphan_output_registry_policy_operator_decision_request(
        source_root=tmp_path, out_root=tmp_path
    )
    write_abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan(
        source_root=tmp_path, out_root=tmp_path
    )
    write_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
        source_root=tmp_path, out_root=tmp_path
    )

    packet = write_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(
        source_root=tmp_path,
        out_root=tmp_path,
    )
    assert packet["status"] == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_EMITTED"
    assert packet["chain_closure_status"] == "ORPHAN_POLICY_GOVERNANCE_SEALED"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
