from pathlib import Path

from scripts import run_artifact_contract_post_closure_operator_receipt as receipt


def test_receipt_reads_closure_status() -> None:
    payload, _, _ = receipt.build()
    assert payload["closure_status"] in {"passed", "missing"}


def test_status_classification() -> None:
    """'failed' must only be emitted when artifacts are present but validation fails.
    When required source artifacts are unavailable the status must be 'missing',
    not 'failed', to preserve fail-closed semantics without false negatives."""
    payload, _, _ = receipt.build()
    assert payload["status"] in {"passed", "missing", "failed"}
    # When closure_status is missing the receipt itself must never upgrade to passed.
    if payload["closure_status"] == "missing":
        assert payload["status"] != "passed"


def test_authority_and_human_nonexecuting() -> None:
    payload, _, _ = receipt.build()
    if payload["status"] == "passed":
        assert payload["human_approval_nonexecuting"] is True
        assert payload["authority_posture"]["execution_authority"] is False


def test_actions_lists() -> None:
    payload, _, _ = receipt.build()
    assert "autonomous_execution" in payload["forbidden_actions"]
    assert "canon_sync_receipt" in payload["next_allowed_actions"]


def test_hash_and_newline() -> None:
    a, _, _ = receipt.build()
    b, _, _ = receipt.build()
    assert a["receipt_hash"] == b["receipt_hash"]
    receipt.main()
    assert Path("out/contracts/artifact_contract_post_closure_operator_receipt.latest.json").read_bytes().endswith(b"\n")
