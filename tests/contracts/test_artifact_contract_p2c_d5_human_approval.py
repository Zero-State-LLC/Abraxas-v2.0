from pathlib import Path

from scripts import run_artifact_contract_p2c_d5_approval_repair_reverify as reverify
from scripts import run_artifact_contract_p2c_d5_human_approval as d5h


def test_exact_d5_target_selection() -> None:
    payload, report, actions = d5h.build()
    from scripts.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    expected_targets = sorted([i["target"] for i in triage["items"] if i.get("classification") == "requires_operator_decision" and i.get("recommended_batch") == "P2C-D5"])
    assert payload["source_d5_count"] == len(expected_targets)
    assert payload["exact_d5_target"] == expected_targets
    assert report["source_d5_count"] == len(expected_targets)
    assert len(actions) == len(expected_targets)


def test_deterministic_approval_hash() -> None:
    a, _, _ = d5h.build()
    b, _, _ = d5h.build()
    assert a["approval_hash"] == b["approval_hash"]


def test_one_approval_per_target() -> None:
    payload, _, _ = d5h.build()
    assert len(payload["approvals"]) == payload["source_d5_count"]


def test_explicit_human_approval_and_no_authority_escalation() -> None:
    payload, report, _ = d5h.build()
    row = payload["approvals"][0]
    assert row["human_approval"] is True
    assert payload["autonomous_approval"] is False
    assert payload["execution_authority"] is False
    assert payload["runtime_mutation_authority"] is False
    assert payload["doctrine_mutation_authority"] is False
    assert payload["inventory_suppression_authority"] is False
    assert report["autonomous_approval"] is False
    assert report["execution_authority"] is False


def test_cleared_queues_preserved_and_authority_lock() -> None:
    payload, report, _ = d5h.build()
    assert payload["cleared_queues_preserved"]["P1A"] == 0
    assert payload["cleared_queues_preserved"]["P1C"] == 0
    assert payload["cleared_queues_preserved"]["P2A"] == 0
    assert payload["cleared_queues_preserved"]["P2C-A"] == 0
    assert payload["cleared_queues_preserved"]["P2C-B"] == 0
    assert report["authority_invariants_ok"] is True


def test_canonical_json_newline() -> None:
    d5h.main()
    assert Path("out/contracts/artifact_contract_p2c_d5_human_approval.latest.json").read_bytes().endswith(b"\n")


def test_failure_when_unresolved_exists() -> None:
    payload, _, _ = d5h.build()
    fake = dict(payload)
    fake["approvals"] = [dict(fake["approvals"][0], result="unresolved")]
    unresolved = [r for r in fake["approvals"] if r["result"] in {"unresolved", "not_computable"}]
    assert bool(unresolved)


def test_reverify_hash_deterministic() -> None:
    a, _, _ = reverify.build()
    b, _, _ = reverify.build()
    assert a["repair_hash"] == b["repair_hash"]
