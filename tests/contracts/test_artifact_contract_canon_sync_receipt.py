import hashlib
import json
from pathlib import Path

from core.canonical.json import canonical_dumps
from scripts import run_artifact_contract_canon_sync_receipt as canon


def test_reads_sources() -> None:
    payload, _, _ = canon.build()
    assert payload["source_closure_status"] in {"passed", "missing", "failed"}
    assert payload["source_operator_receipt_status"] in {"passed", "missing", "failed"}


def test_human_nonexecuting_and_viz_projection() -> None:
    payload, _, _ = canon.build()
    if payload["status"] == "passed":
        assert payload["human_approval_nonexecuting"] is True
        assert payload["aal_viz_posture"]["projection_only"] is True


def test_ready_and_notion_semantics() -> None:
    payload, _, _ = canon.build()
    assert payload["notion_sync_performed"] is False
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False
    assert payload["posture"] == "NOT_COMPUTABLE"
    assert payload["blocker"] == "live_notion_unavailable"
    assert payload["notion_reflection_ready"] is False
    assert payload["status"] != "passed"
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
    expected_hash = "sha256:" + hashlib.sha256(
        canonical_dumps({k: v for k, v in a.items() if k != "canon_sync_hash"}).encode("utf-8")
    ).hexdigest()
    assert a["canon_sync_hash"] == expected_hash
    for path in (
        "out/contracts/artifact_contract_canon_sync_receipt.latest.json",
        "out/contracts/artifact_contract_canon_sync_receipt_report.latest.json",
        "out/contracts/artifact_contract_canon_sync_receipt_actions.latest.json",
    ):
        data = Path(path).read_bytes()
        assert data.endswith(b"\n")
        _ = json.loads(data.decode("utf-8"))
