from __future__ import annotations

import json
from pathlib import Path

from core.temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review import (
    build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review,
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review,
)

_STATUS_REVIEW_READY = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW_READY"
)
_STATUS_BLOCKED = (
    "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
)
_STATUS_FAILED = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW_FAILED"
)
_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"

_NEXT_P104 = (
    "P104_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION"
)
_NEXT_P102 = (
    "P102_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
)

_P102_SOURCE = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution/latest.json"
)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def _make_valid_sim_record() -> dict[str, object]:
    return {
        "simulated_finalization_id": "SIMULATED_FINALIZATION_ONLY",
        "simulated_finalization_hash": "SIMULATED_FINALIZATION_HASH_ONLY",
        "simulated_finalization_token": "SIMULATED_FINALIZATION_TOKEN_ONLY",
        "simulated_finalization_signature": "SIMULATED_FINALIZATION_SIGNATURE_ONLY",
        "simulated_finalization_completed_at": "SIMULATED_ONLY",
        "simulated_operator_id": "SIMULATED_OPERATOR",
        "simulated_operator_attestation": "SIMULATED_ATTESTED",
        "simulated_only": True,
        "actual_finalization_executed": False,
        "approval_record_sealed": False,
        "finalization_authorized": False,
        "authorization_granted": False,
        "approval_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
    }


def _make_valid_chain_ver() -> list[dict[str, object]]:
    return [
        {"check_id": "p96_seal_operator_decision_approved", "passed": True,
         "source": "out/.../seal_operator_decision/latest.json",
         "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD",
         "observed_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION_APPROVED_RECORD"},
        {"check_id": "p97_seal_execution_plan_ready", "passed": True,
         "source": "out/.../seal_execution_plan/latest.json",
         "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY",
         "observed_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_PLAN_READY"},
        {"check_id": "p98_seal_execution_simulated_complete", "passed": True,
         "source": "out/.../seal_execution/latest.json",
         "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE",
         "observed_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_EXECUTION_SIMULATED_COMPLETE"},
        {"check_id": "p99_finalization_authorization_eligible", "passed": True,
         "source": "out/.../seal_finalization_authorization/latest.json",
         "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE",
         "observed_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_ELIGIBLE"},
        {"check_id": "p100_finalization_authorization_record_authorized", "passed": True,
         "source": "out/.../seal_finalization_authorization_record/latest.json",
         "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD",
         "observed_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_AUTHORIZATION_RECORD_AUTHORIZED_RECORD"},
        {"check_id": "p101_finalization_plan_ready", "passed": True,
         "source": "out/.../seal_finalization_plan/latest.json",
         "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_READY",
         "observed_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN_READY"},
    ]


def _make_valid_invariant_checks() -> list[dict[str, object]]:
    lanes = [
        "p96_seal_operator_decision_approved",
        "p97_seal_execution_plan_ready",
        "p98_seal_execution_simulated_complete",
        "p99_finalization_authorization_eligible",
        "p100_finalization_authorization_record_authorized",
        "p101_finalization_plan_ready",
    ]
    fields = ["approval_granted", "approval_record_sealed", "authorization_granted",
              "finalization_authorized", "execution_authority", "token_minting_allowed",
              "valid_for_execution"]
    checks = []
    for lane in lanes:
        for field in fields:
            checks.append({"check_id": f"{lane}__{field}_is_false", "passed": True})
    return checks


def _make_valid_prov_chain() -> dict[str, object]:
    return {
        "autonomous_approval": False,
        "decision_id": "P96_OPERATOR_DECISION_2026_05_28_001",
        "decision_value": "approve_seal_record",
        "operator_id": "Daniel Meyer",
        "p96_seal_operator_decision_hash": "1d9fb64f294609748f75eefb6510731041f43c982e0922c20cb6ade64dfa1d73",
        "p97_seal_execution_plan_hash": "8a7894653c3382c4f7026425bc98712fa309fef53761222a20f7cea8daeeb8b1",
        "p98_seal_execution_hash": "459fed62649b15e3887ce1a1999de4e10f5d838e25a60f01dbd9bb16eb2f2d62",
        "p100_authorization_record_hash": "22fa2e3d8ed1c4e9decbfe5cbbb3e78e612ab11d4749693a462cc84534ae3afc",
        "p101_finalization_plan_hash": "cb02017477114ba8534def93b779995d6f127eb231061b9bf6e86d6e849c967f",
        "p101_finalization_plan_file_hash": "7a30ccf4a322fe60453ed57d24caf5dfb98821cedc7c1eeaca6d8b3cc767c140",
    }


def _seed_p102(
    root: Path,
    *,
    status: str = "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION_SIMULATED_COMPLETE",
    finalization_recorded: bool = True,
    sim_record: dict | None = None,
    chain_ver: list | None = None,
    inv_checks: list | None = None,
    prov_chain: dict | None = None,
    inject: dict[str, object] | None = None,
) -> Path:
    p102_path = root / _P102_SOURCE
    base: dict[str, object] = {
        "finalization_execution_status": status,
        "finalization_recorded": finalization_recorded,
        "simulated_finalization_only": True,
        "actual_finalization_executed": False,
        "approval_record_seal_finalization_execution_hash": (
            "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737"
        ),
        "simulated_finalization_record": sim_record if sim_record is not None else _make_valid_sim_record(),
        "simulated_sentinel_check": {
            "check_passed": True,
            "sentinel_strings_all_contain_simulated_marker": True,
            "simulated_only_flag_set": True,
            "actual_finalization_executed_is_false": True,
            "approval_record_sealed_is_false": True,
            "finalization_authorized_is_false": True,
        },
        "finalization_chain_verification": chain_ver if chain_ver is not None else _make_valid_chain_ver(),
        "finalization_authority_invariant_checks": inv_checks if inv_checks is not None else _make_valid_invariant_checks(),
        "finalization_provenance_chain": prov_chain if prov_chain is not None else _make_valid_prov_chain(),
        "simulated_finalization_summary": {
            "simulated_only": True,
            "actual_finalization_executed": False,
            "approval_record_sealed": False,
            "finalization_authority_granted": False,
            "step_count_verified": 6,
        },
        "advisory_only": True,
        "projection_only": True,
        "finalization_execution_only": True,
        "approval_record_seal_finalization_execution_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "execution_authority": False,
        "authorization_authority": False,
        "plan_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "governance_authority_mutation": False,
    }
    if inject:
        for k, v in inject.items():
            base[k] = v
    _write_json(p102_path, base)
    return p102_path


def _build(root: Path) -> dict:
    return build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review(
        repo_root=root,
    )


def test_missing_p102_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_NOT_COMPUTABLE
    assert packet["review_passed"] is False
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["actual_finalization_executed"] is False
    assert packet["advisory_only"] is True
    assert packet["review_only"] is True
    assert packet["finalization_review_only"] is True
    assert len(packet["finalization_review_checklist"]) == 5
    assert _NEXT_P102 in packet["recommended_next_lane"]
    h = packet["approval_record_seal_finalization_review_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_blocked_wrong_status(tmp_path: Path) -> None:
    _seed_p102(
        tmp_path,
        status="BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_PLAN",
        finalization_recorded=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_BLOCKED
    assert packet["review_passed"] is False
    assert _NEXT_P102 in packet["recommended_next_lane"]


def test_blocked_finalization_not_recorded(tmp_path: Path) -> None:
    _seed_p102(
        tmp_path,
        status="OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION_SIMULATED_COMPLETE",
        finalization_recorded=False,
    )
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_BLOCKED
    assert packet["review_passed"] is False
    assert any("finalization_recorded" in b for b in packet["review_blockers"])


def test_review_ready_valid_p102(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_REVIEW_READY
    assert packet["review_passed"] is True
    assert packet["review_blockers"] == []
    assert _NEXT_P104 in packet["recommended_next_lane"]
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["actual_finalization_executed"] is False
    assert packet["advisory_only"] is True
    assert packet["review_only"] is True


def test_review_checklist_always_present(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    cl = packet["finalization_review_checklist"]
    assert len(cl) == 5
    assert all(item["review_only"] is True for item in cl)
    ids = [item["item_id"] for item in cl]
    assert "finalization_simulation_advisory_confirmed" in ids
    assert "finalization_provenance_chain_intact" in ids
    assert "sentinel_strings_confirmed" in ids
    assert "authority_locks_all_false_confirmed" in ids
    assert "finalization_not_executed_confirmed" in ids


def test_chain_review_echoed(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    chain = packet["finalization_chain_review"]
    assert len(chain) == 6
    assert all(c["passed"] is True for c in chain)
    assert {c["check_id"] for c in chain} == {
        "p96_seal_operator_decision_approved",
        "p97_seal_execution_plan_ready",
        "p98_seal_execution_simulated_complete",
        "p99_finalization_authorization_eligible",
        "p100_finalization_authorization_record_authorized",
        "p101_finalization_plan_ready",
    }


def test_authority_invariant_review_echoed(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    inv = packet["finalization_authority_invariant_review"]
    assert len(inv) == 42
    assert all(c["passed"] is True for c in inv)


def test_simulated_finalization_review_passes(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    sfr = packet["simulated_finalization_review"]
    assert sfr["review_passed"] is True
    assert sfr["authority_fields_all_false"] is True
    assert sfr["sentinel_strings_contain_simulated_marker"] is True
    assert sfr["simulated_only_flag_set"] is True
    assert sfr["actual_finalization_executed_is_false"] is True
    assert sfr["finalization_authorized_is_false"] is True


def test_finalization_sentinel_check_review_passes(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    scr = packet["finalization_sentinel_check_review"]
    assert scr["source_check_passed"] is True
    assert scr["sentinel_strings_all_contain_simulated_marker"] is True
    assert scr["actual_finalization_executed_is_false"] is True
    assert scr["finalization_authorized_is_false"] is True


def test_finalization_provenance_review_passes(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    prov = packet["finalization_provenance_review"]
    assert len(prov) == 6
    assert all(c["passed"] is True for c in prov)


def test_finalization_check_summary(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    s = packet["finalization_check_summary"]
    assert s["failed"] == 0
    assert s["passed"] > 0
    assert s["total"] == s["passed"] + s["failed"]


def test_p102_anchors_embedded(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    assert packet["p102_finalization_execution_hash_anchor"] == (
        "904c85d365c1c7ca1a348e1f0a5f117d0a87fcd655cbf0e35afcc35f91ee6737"
    )
    assert packet["p102_simulated_finalization_only_anchor"] is True
    assert packet["p102_actual_finalization_executed_anchor"] is False
    assert packet["p102_finalization_recorded_anchor"] is True


def test_failed_sentinel_string_not_simulated(tmp_path: Path) -> None:
    bad_rec = _make_valid_sim_record()
    bad_rec["simulated_finalization_id"] = "NOT_REAL_VALUE"
    _seed_p102(tmp_path, sim_record=bad_rec)
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert packet["review_passed"] is False
    sfr = packet["simulated_finalization_review"]
    assert sfr["sentinel_strings_contain_simulated_marker"] is False


def test_failed_sim_record_authority_lock(tmp_path: Path) -> None:
    bad_rec = _make_valid_sim_record()
    bad_rec["authorization_granted"] = True
    _seed_p102(tmp_path, sim_record=bad_rec)
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert packet["review_passed"] is False
    sfr = packet["simulated_finalization_review"]
    assert sfr["authority_fields_all_false"] is False
    assert packet["authorization_granted"] is False


def test_failed_chain_check_not_passed(tmp_path: Path) -> None:
    bad_chain = _make_valid_chain_ver()
    bad_chain[2] = {**bad_chain[2], "passed": False, "observed_status": "BLOCKED"}
    _seed_p102(tmp_path, chain_ver=bad_chain)
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert packet["review_passed"] is False
    assert any("p98_seal_execution_simulated_complete" in b for b in packet["review_blockers"])


def test_failed_provenance_autonomous_approval(tmp_path: Path) -> None:
    bad_prov = dict(_make_valid_prov_chain())
    bad_prov["autonomous_approval"] = True
    _seed_p102(tmp_path, prov_chain=bad_prov)
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert any("autonomous" in b for b in packet["review_blockers"])


def test_failed_p102_authority_lock_in_source(tmp_path: Path) -> None:
    _seed_p102(tmp_path, inject={"authorization_granted": True})
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert packet["review_passed"] is False
    assert packet["authorization_granted"] is False


def test_failed_p102_finalization_authorized_in_source(tmp_path: Path) -> None:
    _seed_p102(tmp_path, inject={"finalization_authorized": True})
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert packet["finalization_authorized"] is False


def test_authority_locks_hardcoded_regardless_of_source(tmp_path: Path) -> None:
    _seed_p102(tmp_path, inject={
        "authorization_granted": True,
        "finalization_authorized": True,
        "approval_record_sealed": True,
        "valid_for_execution": True,
        "execution_authority": True,
        "token_minting_allowed": True,
        "actual_finalization_executed": True,
        "production_activation": True,
    })
    packet = _build(tmp_path)
    assert packet["finalization_review_status"] == _STATUS_FAILED
    assert packet["authorization_granted"] is False
    assert packet["finalization_authorized"] is False
    assert packet["approval_record_sealed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert packet["token_minting_allowed"] is False
    assert packet["actual_finalization_executed"] is False
    assert packet["production_activation"] is False
    assert packet["canon_promotion"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["baseline_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["governance_authority_mutation"] is False


def test_schema_and_id(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    assert packet["schema_version"] == (
        "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationReview.v1"
    )
    assert packet["approval_record_seal_finalization_review_id"] == (
        "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review_001"
    )


def test_hash_validation(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    h = packet["approval_record_seal_finalization_review_hash"]
    assert isinstance(h, str) and len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)
    from core.canonical.json import canonical_hash
    packet_base = {k: v for k, v in packet.items() if k != "approval_record_seal_finalization_review_hash"}
    assert canonical_hash(packet_base) == h


def test_determinism(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    p1 = _build(tmp_path)
    p2 = _build(tmp_path)
    assert json.dumps(p1, sort_keys=True) == json.dumps(p2, sort_keys=True)
    assert p1["approval_record_seal_finalization_review_hash"] == p2["approval_record_seal_finalization_review_hash"]


def test_write_function(tmp_path: Path) -> None:
    _seed_p102(tmp_path)
    packet = _build(tmp_path)
    out = (
        tmp_path
        / "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review/latest.json"
    )
    write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review(
        out, packet
    )
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["approval_record_seal_finalization_review_hash"] == packet["approval_record_seal_finalization_review_hash"]
    assert loaded["finalization_review_status"] == packet["finalization_review_status"]


def test_doctrine_validator_nonregression() -> None:
    import subprocess
    result = subprocess.run(
        ["python", "scripts/run_doctrine_validator.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "seal" in result.stdout
