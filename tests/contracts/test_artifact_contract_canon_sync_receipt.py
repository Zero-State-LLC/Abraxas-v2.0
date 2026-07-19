from pathlib import Path

from scripts.artifact import run_artifact_contract_canon_sync_receipt as canon


def test_reads_sources() -> None:
    payload, _, _ = canon.build()
    assert payload["source_closure_status"] in {"passed", "missing"}
    assert payload["source_operator_receipt_status"] in {"passed", "missing"}


def test_source_status_classification() -> None:
    """'failed' must never propagate to source_*_status fields.
    Unavailable sources must be reported as 'missing'; 'failed' is reserved
    for artifacts that are present but contain malformed or blocking data."""
    payload, _, _ = canon.build()
    assert payload["source_operator_receipt_status"] != "failed", (
        "source_operator_receipt_status must be 'passed' or 'missing', not 'failed'"
    )
    assert payload["source_closure_status"] != "failed", (
        "source_closure_status must be 'passed' or 'missing', not 'failed'"
    )


def test_human_nonexecuting_and_viz_projection() -> None:
    payload, _, _ = canon.build()
    if payload["status"] == "passed":
        assert payload["human_approval_nonexecuting"] is True
        assert payload["aal_viz_posture"]["projection_only"] is True


def test_ready_and_notion_semantics() -> None:
    payload, _, _ = canon.build()
    assert payload["notion_sync_performed"] is False
    if payload["source_closure_status"] == "passed" and payload["source_operator_receipt_status"] == "passed":
        assert payload["canon_reflection_ready"] is True


def test_action_lists() -> None:
    payload, _, _ = canon.build()
    assert "notion_canon_index_update_manual" in payload["allowed_next_actions"]
    assert "unverified_notion_write" in payload["forbidden_actions"]


def test_hash_and_newline() -> None:
    a, _, _ = canon.build()
    b, _, _ = canon.build()
    assert a["canon_sync_hash"] == b["canon_sync_hash"]
    canon.main()
    assert Path("out/contracts/artifact_contract_canon_sync_receipt.latest.json").read_bytes().endswith(b"\n")
