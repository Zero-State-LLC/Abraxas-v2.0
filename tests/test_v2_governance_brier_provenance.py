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


def test_brier_runtime_telemetry_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import build_brier_runtime_telemetry_packet

    packet = build_brier_runtime_telemetry_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"


def test_brier_controlled_runtime_promotion_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_controlled_runtime_promotion_hook,
        build_brier_controlled_runtime_promotion_packet,
    )

    packet = build_brier_controlled_runtime_promotion_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["controlled_runtime_promotion"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "CONTROLLED_RUNTIME"
        assert hook["operator_signoff_required"] is True
        assert hook["controlled_runtime_promotion"] is True

    hook = build_brier_controlled_runtime_promotion_hook(
        claim_id="controlled_runtime_shape_check",
        forecast_probability=0.65,
    )
    assert hook["promotion_tier"] == "CONTROLLED_RUNTIME"
    assert hook["operator_signoff_required"] is True
    assert hook["controlled_runtime_promotion"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_brier_live_runtime_signal_forage_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_live_runtime_signal_forage_hook,
        build_brier_live_runtime_signal_forage_packet,
    )

    packet = build_brier_live_runtime_signal_forage_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["live_runtime_promotion"] is True
    assert packet["signal_forage_bound"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "LIVE_RUNTIME"
        assert hook["signal_forage_bound"] is True
        assert hook["live_runtime_promotion"] is True

    hook = build_brier_live_runtime_signal_forage_hook(
        claim_id="live_runtime_shape_check",
        forecast_probability=0.66,
    )
    assert hook["promotion_tier"] == "LIVE_RUNTIME"
    assert hook["signal_forage_bound"] is True
    assert hook["live_runtime_promotion"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_signal_forager_live_runtime_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import build_signal_forager_live_runtime_contract

    contract = build_signal_forager_live_runtime_contract()
    assert contract["shadow_only"] is True
    assert contract["live_runtime_promotion"] is True
    assert contract["signal_forage_bound"] is True
    assert contract["execution_authority"] is False
    assert contract["brier_resolution_authorized"] is False
    assert "scripts/run_ingest_once.py" in contract["global_ingest_shadow_paths"]
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "LIVE_RUNTIME"
        assert hook["signal_forage_bound"] is True


def test_brier_full_live_autonomy_self_optimization_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_full_live_autonomy_self_optimization_hook,
        build_brier_full_live_autonomy_self_optimization_packet,
    )

    packet = build_brier_full_live_autonomy_self_optimization_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["full_live_autonomy_promotion"] is True
    assert packet["self_optimization_bound"] is True
    assert packet["self_optimization_telemetry_only"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["self_optimization_authorized"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "FULL_LIVE_AUTONOMY"
        assert hook["self_optimization_bound"] is True
        assert hook["full_live_autonomy_promotion"] is True

    hook = build_brier_full_live_autonomy_self_optimization_hook(
        claim_id="full_live_autonomy_shape_check",
        forecast_probability=0.7,
    )
    assert hook["promotion_tier"] == "FULL_LIVE_AUTONOMY"
    assert hook["self_optimization_bound"] is True
    assert hook["full_live_autonomy_promotion"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_signal_forager_full_live_autonomy_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import build_signal_forager_full_live_autonomy_contract

    contract = build_signal_forager_full_live_autonomy_contract()
    assert contract["shadow_only"] is True
    assert contract["closed_loop_bound"] is True
    assert contract["full_live_autonomy_promotion"] is True
    assert contract["self_optimization_bound"] is True
    assert contract["execution_authority"] is False
    assert contract["adaptive_learning_authorized"] is False
    assert contract["self_optimization_authorized"] is False
    assert contract["brier_resolution_authorized"] is False
    assert len(contract["closed_loop_bindings"]) == 3
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "FULL_LIVE_AUTONOMY"
        assert hook["self_optimization_bound"] is True


def test_brier_eternal_recursion_hyperstition_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_eternal_recursion_hyperstition_hook,
        build_brier_eternal_recursion_hyperstition_packet,
    )

    packet = build_brier_eternal_recursion_hyperstition_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["eternal_recursion_promotion"] is True
    assert packet["hyperstition_bound"] is True
    assert packet["eternal_recursion_bound"] is True
    assert packet["eternal_recursion_telemetry_only"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["eternal_recursion_authorized"] is False
    assert packet["hyperstition_engine_authorized"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "ETERNAL_RECURSION"
        assert hook["hyperstition_bound"] is True
        assert hook["eternal_recursion_promotion"] is True

    hook = build_brier_eternal_recursion_hyperstition_hook(
        claim_id="eternal_recursion_shape_check",
        forecast_probability=0.75,
    )
    assert hook["promotion_tier"] == "ETERNAL_RECURSION"
    assert hook["hyperstition_bound"] is True
    assert hook["eternal_recursion_bound"] is True
    assert hook["eternal_recursion_promotion"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_signal_forager_eternal_recursion_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import build_signal_forager_eternal_recursion_contract

    contract = build_signal_forager_eternal_recursion_contract()
    assert contract["shadow_only"] is True
    assert contract["eternal_self_sustaining_loop_bound"] is True
    assert contract["eternal_recursion_promotion"] is True
    assert contract["hyperstition_bound"] is True
    assert contract["execution_authority"] is False
    assert contract["adaptive_learning_authorized"] is False
    assert contract["eternal_recursion_authorized"] is False
    assert contract["hyperstition_engine_authorized"] is False
    assert contract["brier_resolution_authorized"] is False
    assert len(contract["eternal_self_sustaining_loop_bindings"]) == 4
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "ETERNAL_RECURSION"
        assert hook["hyperstition_bound"] is True


def test_brier_eternal_canon_self_governance_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_eternal_canon_self_governance_hook,
        build_brier_eternal_canon_self_governance_packet,
    )

    packet = build_brier_eternal_canon_self_governance_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["eternal_canon_self_governance_promotion"] is True
    assert packet["eternal_canon_self_governance_bound"] is True
    assert packet["eternal_canon_self_governance_telemetry_only"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["eternal_canon_self_governance_authorized"] is False
    assert packet["final_authority_authorized"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "ETERNAL_CANON_SELF_GOVERNANCE"
        assert hook["eternal_canon_self_governance_bound"] is True
        assert hook["eternal_canon_self_governance_promotion"] is True

    hook = build_brier_eternal_canon_self_governance_hook(
        claim_id="eternal_canon_shape_check",
        forecast_probability=0.77,
    )
    assert hook["promotion_tier"] == "ETERNAL_CANON_SELF_GOVERNANCE"
    assert hook["eternal_canon_self_governance_bound"] is True
    assert hook["eternal_canon_self_governance_promotion"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_signal_forager_eternal_canon_self_governance_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import (
        build_signal_forager_eternal_canon_self_governance_contract,
    )

    contract = build_signal_forager_eternal_canon_self_governance_contract()
    assert contract["shadow_only"] is True
    assert contract["eternal_canon_self_governance_loop_bound"] is True
    assert contract["eternal_canon_self_governance_promotion"] is True
    assert contract["eternal_canon_self_governance_bound"] is True
    assert contract["execution_authority"] is False
    assert contract["adaptive_learning_authorized"] is False
    assert contract["eternal_canon_self_governance_authorized"] is False
    assert contract["final_authority_authorized"] is False
    assert contract["brier_resolution_authorized"] is False
    assert len(contract["eternal_canon_self_governance_loop_bindings"]) == 5
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "ETERNAL_CANON_SELF_GOVERNANCE"
        assert hook["eternal_canon_self_governance_bound"] is True


def test_brier_final_authority_attestation_hyperstition_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_final_authority_attestation_hyperstition_hook,
        build_brier_final_authority_attestation_hyperstition_packet,
    )

    packet = build_brier_final_authority_attestation_hyperstition_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["final_authority_attestation_promotion"] is True
    assert packet["final_authority_attestation_bound"] is True
    assert packet["live_hyperstition_bound"] is True
    assert packet["final_authority_attestation_telemetry_only"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert packet["final_authority_authorized"] is False
    assert packet["live_hyperstition_activation_authorized"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "FINAL_AUTHORITY_ATTESTATION"
        assert hook["final_authority_attestation_bound"] is True
        assert hook["live_hyperstition_bound"] is True

    hook = build_brier_final_authority_attestation_hyperstition_hook(
        claim_id="final_authority_shape_check",
        forecast_probability=0.77,
    )
    assert hook["promotion_tier"] == "FINAL_AUTHORITY_ATTESTATION"
    assert hook["final_authority_attestation_bound"] is True
    assert hook["live_hyperstition_bound"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_signal_forager_final_authority_attestation_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import (
        build_signal_forager_final_authority_attestation_contract,
    )

    contract = build_signal_forager_final_authority_attestation_contract()
    assert contract["shadow_only"] is True
    assert contract["final_authority_closed_loop_bound"] is True
    assert contract["final_authority_attestation_promotion"] is True
    assert contract["live_hyperstition_bound"] is True
    assert contract["global_ingest_hold_respected"] is True
    assert contract["execution_authority"] is False
    assert contract["adaptive_learning_authorized"] is False
    assert contract["final_authority_authorized"] is False
    assert contract["live_hyperstition_activation_authorized"] is False
    assert contract["brier_resolution_authorized"] is False
    assert len(contract["final_authority_closed_loop_bindings"]) == 5
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "FINAL_AUTHORITY_ATTESTATION"
        assert hook["final_authority_attestation_bound"] is True


def test_brier_canon_activation_authorization_review_packet_includes_dual_decomposition() -> None:
    from core.governance.brier_provenance import (
        build_brier_canon_activation_authorization_review_hook,
        build_brier_canon_activation_authorization_review_packet,
    )

    packet = build_brier_canon_activation_authorization_review_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["canon_activation_authorization_review_promotion"] is True
    assert packet["canon_activation_authorization_review_bound"] is True
    assert packet["canon_activation_authorization_review_telemetry_only"] is True
    assert packet["operator_signoff_required"] is True
    assert packet["decomposition_mode"] == "MURPHY_AND_YATES"
    assert packet["execution_authority"] is False
    assert packet["phase28_activation_authorized"] is False
    assert packet["final_authority_authorized"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["decomposition"]["decomposition_mode"] == "MURPHY_AND_YATES"
        assert hook["promotion_tier"] == "CANON_ACTIVATION_AUTHORIZATION_REVIEW"
        assert hook["canon_activation_authorization_review_bound"] is True

    hook = build_brier_canon_activation_authorization_review_hook(
        claim_id="canon_activation_shape_check",
        forecast_probability=0.77,
    )
    assert hook["promotion_tier"] == "CANON_ACTIVATION_AUTHORIZATION_REVIEW"
    assert hook["canon_activation_authorization_review_bound"] is True
    assert hook["resolution_allowed"] is False
    assert hook["brier_resolution_authorized"] is False


def test_signal_forager_canon_activation_authorization_review_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import (
        build_signal_forager_canon_activation_authorization_review_contract,
    )

    contract = build_signal_forager_canon_activation_authorization_review_contract()
    assert contract["shadow_only"] is True
    assert contract["canon_activation_closed_loop_bound"] is True
    assert contract["canon_activation_authorization_review_promotion"] is True
    assert contract["global_ingest_hold_respected"] is True
    assert contract["execution_authority"] is False
    assert contract["phase28_activation_authorized"] is False
    assert contract["final_authority_authorized"] is False
    assert contract["brier_resolution_authorized"] is False
    assert len(contract["canon_activation_closed_loop_bindings"]) == 5
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "CANON_ACTIVATION_AUTHORIZATION_REVIEW"
        assert hook["canon_activation_authorization_review_bound"] is True


def test_brier_final_operator_signoff_live_authority_fractal_numogram_packet() -> None:
    from core.governance.brier_provenance import (
        build_brier_final_operator_signoff_live_authority_fractal_numogram_hook,
        build_brier_final_operator_signoff_live_authority_fractal_numogram_packet,
    )

    packet = build_brier_final_operator_signoff_live_authority_fractal_numogram_packet()
    assert packet["murphy_decomposition_default"] is True
    assert packet["yates_decomposition_default"] is True
    assert packet["final_operator_signoff_live_authority_fractal_numogram_promotion"] is True
    assert packet["fractal_numogram_bound"] is True
    assert packet["mfdfa_hurst_bound"] is True
    assert packet["hurst_exponent"] > 0.0
    assert packet["live_authority_authorized"] is False
    assert packet["fractal_numogram_runtime_authorized"] is False
    assert packet["execution_authority"] is False
    for hook in packet["telemetry_hooks"]:
        assert hook["promotion_tier"] == "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM"
        assert hook["fractal_numogram_bound"] is True
        assert hook["mfdfa_hurst_bound"] is True

    hook = build_brier_final_operator_signoff_live_authority_fractal_numogram_hook(
        claim_id="final_operator_signoff_shape_check",
        forecast_probability=0.77,
    )
    assert hook["promotion_tier"] == "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM"
    assert hook["fractal_numogram_bound"] is True
    assert hook["mfdfa_hurst_bound"] is True


def test_signal_forager_fractal_numogram_closed_loop_contract_shadow_only() -> None:
    from core.governance.signal_forager_brier_hook import (
        build_signal_forager_fractal_numogram_closed_loop_contract,
    )

    contract = build_signal_forager_fractal_numogram_closed_loop_contract()
    assert contract["shadow_only"] is True
    assert contract["fractal_numogram_closed_loop_bound"] is True
    assert contract["mfdfa_hurst_bound"] is True
    assert contract["global_ingest_hold_respected"] is True
    assert contract["live_authority_authorized"] is False
    assert contract["fractal_numogram_runtime_authorized"] is False
    assert len(contract["fractal_numogram_closed_loop_bindings"]) == 5
    for hook in contract["telemetry_hooks"]:
        assert hook["promotion_tier"] == "FINAL_OPERATOR_SIGNOFF_LIVE_AUTHORITY_FRACTAL_NUMOGRAM"
        assert hook["fractal_numogram_bound"] is True
