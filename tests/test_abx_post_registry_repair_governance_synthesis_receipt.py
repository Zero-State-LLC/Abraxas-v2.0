from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_post_registry_repair_governance_synthesis_receipt import (
    RECEIPT_ID,
    SEALED_CHAINS,
    build_abx_post_registry_repair_governance_synthesis_receipt,
    write_abx_post_registry_repair_governance_synthesis_receipt,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_post_registry_repair_governance_synthesis_receipt.py",
    "local_abx_post_registry_repair_governance_synthesis_receipt_runner",
)
SCHEMA_PATH = (
    "contracts/operator_review/abx_post_registry_repair_governance_synthesis_receipt.v1.schema.json"
)


def test_synthesis_receipt_is_deterministic_and_sealed() -> None:
    first = build_abx_post_registry_repair_governance_synthesis_receipt(source_root=REPO_ROOT)
    second = build_abx_post_registry_repair_governance_synthesis_receipt(source_root=REPO_ROOT)

    assert first["receipt_hash"] == second["receipt_hash"]
    assert first["artifact_id"] == RECEIPT_ID
    assert first["status"] == "ABX_POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_RECEIPT_EMITTED"
    assert first["synthesis_status"] == "POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_SEALED"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["downstream_status"] == "NOT_COMPUTABLE"
    assert len(first["sealed_chain_records"]) == len(SEALED_CHAINS)
    assert all(record["chain_ready"] for record in first["sealed_chain_records"])


def test_synthesis_receipt_blocked_without_upstream_artifacts(tmp_path: Path) -> None:
    packet = build_abx_post_registry_repair_governance_synthesis_receipt(source_root=tmp_path)
    assert packet["status"] == "ABX_POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_RECEIPT_BLOCKED"
    assert packet["synthesis_status"] == "NOT_COMPUTABLE"


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_post_registry_repair_governance_synthesis_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = (
        tmp_path
        / "out/operator_review/abx_post_registry_repair_governance_synthesis_receipt_001.latest.json"
    )
    md_path = json_path.with_suffix(".md")
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_root=tmp_path)
    assert runner_packet["receipt_hash"] == packet["receipt_hash"]
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)
