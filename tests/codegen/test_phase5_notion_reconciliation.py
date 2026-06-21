from __future__ import annotations

from core.canonical.json import canonical_hash
from core.codegen.notion_reconciliation import build_notion_reconciliation_dryrun


def test_notion_reconciliation_dryrun_is_no_writeback() -> None:
    packet = build_notion_reconciliation_dryrun(
        timestamp="2026-06-21T00:00:00Z",
        phase_statuses={
            "PHASE_1_CONTRACTS_CODEGEN_SCHEMAS": "MERGED",
            "PHASE_2_CORE_CODEGEN_HARNESS": "MERGED",
            "PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY": "MERGED",
            "PHASE_4_META_GATE_OPERATOR_PROMOTION": "MERGED",
        },
        merge_shas={
            "PHASE_1_CONTRACTS_CODEGEN_SCHEMAS": "ee183d1d",
            "PHASE_2_CORE_CODEGEN_HARNESS": "c730750d",
            "PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY": "a69f87b0",
            "PHASE_4_META_GATE_OPERATOR_PROMOTION": "0cc01902",
        },
    )

    assert packet["status"] == "NOTION_RECONCILIATION_DRYRUN_READY"
    assert packet["notion_writeback"] is False
    assert packet["github_writeback"] is False
    assert packet["execution_authority"] is False
    assert "paste-ready text only" in packet["sync_text"]
    assert "Brier Score: 0.10" in packet["sync_text"]


def test_notion_reconciliation_dryrun_hash_is_stable() -> None:
    packet = build_notion_reconciliation_dryrun(
        timestamp="2026-06-21T00:00:00Z",
        phase_statuses={"PHASE_5_NOTION_RECONCILIATION_DRYRUN": "READY"},
        merge_shas={"PHASE_5_NOTION_RECONCILIATION_DRYRUN": "NOT_MERGED"},
    )

    assert packet["canonical_hash"] == canonical_hash(
        {key: value for key, value in packet.items() if key != "canonical_hash"}
    )
