from __future__ import annotations

from core.governance.brier_provenance import (
    NOT_COMPUTABLE,
    build_brier_provenance_hook,
    build_brier_provenance_packet,
    validate_adversarial_calibration,
)
from core.governance.signal_forager_brier_hook import (
    build_signal_forager_brier_contract,
    emit_signal_forager_brier_hook,
)
from core.scoring.brier import compute_brier_score


def test_brier_provenance_hook_hash_stability() -> None:
    first = build_brier_provenance_packet()
    second = build_brier_provenance_packet()
    assert first["brier_provenance_hash"] == second["brier_provenance_hash"]
    assert first["telemetry_only"] is True
    assert first["resolution_allowed"] is False
    assert first["brier_resolution_authorized"] is False


def test_brier_provenance_denies_resolution_authority() -> None:
    hook = build_brier_provenance_hook(
        claim_id="deny_resolution",
        forecast_probability=0.8,
    )
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False
    assert hook["binary_outcome"] == NOT_COMPUTABLE
    assert hook["brier_score"] == NOT_COMPUTABLE


def test_brier_provenance_computes_score_when_outcome_present() -> None:
    hook = build_brier_provenance_hook(
        claim_id="resolved_fixture",
        forecast_probability=0.8,
        binary_outcome=1.0,
    )
    assert hook["brier_score"] == compute_brier_score(0.8, 1.0)


def test_adversarial_empty_outcome_blocked() -> None:
    hook = build_brier_provenance_hook(
        claim_id="empty_outcome",
        forecast_probability=0.5,
        binary_outcome="",
    )
    blockers = validate_adversarial_calibration(hook)
    assert "empty_outcome_not_scorable" in blockers


def test_adversarial_conflicting_settlement_blocked() -> None:
    hook = build_brier_provenance_hook(
        claim_id="conflict",
        forecast_probability=0.5,
        binary_outcome=1.0,
    )
    hook["settlement_decision"] = "CONFLICTING"
    blockers = validate_adversarial_calibration(hook)
    assert "conflicting_settlement_with_binary_outcome" in blockers


def test_signal_forager_hook_matches_hygiene_contract_shape() -> None:
    contract = build_signal_forager_brier_contract()
    hook = emit_signal_forager_brier_hook(
        claim_id="shape_check",
        forecast_probability=0.6,
    )

    assert contract["telemetry_only"] is True
    assert contract["resolution_allowed"] is False
    assert contract["brier_resolution_authorized"] is False
    assert contract["decomposition_mode"] == "MURPHY_AND_YATES"
    assert set(hook) >= {
        "claim_id",
        "forecast_probability",
        "binary_outcome",
        "brier_score",
        "resolution_source",
        "resolution_allowed",
        "decomposition",
    }
    assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"


def test_brier_provenance_packet_includes_decomposition() -> None:
    packet = build_brier_provenance_packet()
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert "murphy" in hook["decomposition"]
        assert "yates" in hook["decomposition"]
