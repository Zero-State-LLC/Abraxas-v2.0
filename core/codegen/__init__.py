from __future__ import annotations

from core.codegen.builder import (
    DEFAULT_LANE_SIGNALS,
    DEFAULT_PROVENANCE,
    build_code_drop_envelope,
    build_patch_contract,
)
from core.codegen.fixture_validation import (
    validate_shadow_replay_fixture,
    validate_shadow_replay_fixtures,
)
from core.codegen.forward_paths import build_forward_paths_receipt
from core.codegen.global_ingest_wiring import build_global_ingest_wiring_stub
from core.codegen.loop805_activation_proposal import (
    build_loop805_gate_selection_matrix,
    build_loop805_activation_proposal,
    build_loop805_slice3_prompt_packet,
    build_loop805_slice4_prompt_packet,
)
from core.codegen.loop805_brier_attestation import (
    build_loop805_authorization_evidence_packet,
    build_loop805_brier_attestation_packet,
    build_loop805_brier_scoring_shadow_run,
    build_loop805_fixture_binding_dryrun,
    build_loop805_fixture_outcome_binding_review,
    build_loop805_held_out_set_attestation_gate,
    build_loop805_held_out_set_lockfile_proposal,
    build_loop805_measurement_authorization_proposal,
    build_loop805_measurement_dryrun_authorization_hold,
    build_loop805_measurement_dryrun_decision_record_template,
    build_loop805_measurement_dryrun_decision_request,
    build_loop805_measurement_dryrun_operator_decision_intake_packet,
    build_loop805_measurement_dryrun_operator_decision_intake_gate,
    build_loop805_measurement_dryrun_preflight_packet,
    build_loop805_measurement_readiness_review,
    build_loop805_outcome_policy_review_packet,
    build_loop805_slice5_prompt_packet,
    build_loop805_slice6_prompt_packet,
    build_loop805_slice7_prompt_packet,
    build_loop805_slice8_prompt_packet,
    build_loop805_slice9_prompt_packet,
    build_loop805_slice10_prompt_packet,
    build_loop805_slice11_prompt_packet,
    build_loop805_slice12_prompt_packet,
    build_loop805_slice13_prompt_packet,
    build_loop805_slice14_prompt_packet,
    build_loop805_slice15_prompt_packet,
    build_loop805_slice16_prompt_packet,
    build_loop805_slice17_prompt_packet,
    build_loop805_slice18_prompt_packet,
    build_loop805_slice19_prompt_packet,
    build_loop805_slice20_prompt_packet,
)
from core.codegen.loop805_controller import build_loop805_controller_plan
from core.codegen.loop805_mcp_stub import (
    build_loop805_mcp_exposure_stub,
    default_loop805_mcp_tool_contracts,
)
from core.codegen.loop805_observability import (
    build_held_out_brier_fixture,
    build_held_out_brier_telemetry,
    build_loop805_daily_dashboard,
    build_loop805_regression_pr_proposal,
    build_spine_route_decision,
)
from core.codegen.loop805_operationalization import build_loop805_baseline_receipt
from core.codegen.loop805_token_optimizer import build_loop805_token_optimizer_stub
from core.codegen.meta_gate import build_meta_gate_review
from core.codegen.notion_reconciliation import build_notion_reconciliation_dryrun
from core.codegen.post_merge_reconciliation import (
    build_continuity_signal,
    build_post_merge_reconciliation_receipt,
)
from core.codegen.runner import (
    prepare_shadow_runtime_activation,
    run_codegen_harness,
    run_task_packet,
)
from core.codegen.shadow_activation_prep import build_shadow_runtime_activation_prep
from core.codegen.shadow_replay_harness import ShadowReplayHarness, run_shadow_replay
from core.codegen.spine_mcp_projection import (
    build_spine_audit_projection,
    build_spine_forecast_projection,
    build_spine_query_projection,
)
from core.codegen.spine_completion import build_codegen_spine_completion_receipt

__all__ = [
    "DEFAULT_LANE_SIGNALS",
    "DEFAULT_PROVENANCE",
    "ShadowReplayHarness",
    "build_codegen_spine_completion_receipt",
    "build_code_drop_envelope",
    "build_continuity_signal",
    "build_forward_paths_receipt",
    "build_global_ingest_wiring_stub",
    "build_loop805_gate_selection_matrix",
    "build_loop805_activation_proposal",
    "build_loop805_authorization_evidence_packet",
    "build_loop805_baseline_receipt",
    "build_loop805_brier_attestation_packet",
    "build_loop805_brier_scoring_shadow_run",
    "build_loop805_fixture_binding_dryrun",
    "build_loop805_fixture_outcome_binding_review",
    "build_loop805_held_out_set_attestation_gate",
    "build_loop805_held_out_set_lockfile_proposal",
    "build_loop805_measurement_authorization_proposal",
    "build_loop805_measurement_dryrun_authorization_hold",
    "build_loop805_measurement_dryrun_decision_record_template",
    "build_loop805_measurement_dryrun_decision_request",
    "build_loop805_measurement_dryrun_operator_decision_intake_packet",
    "build_loop805_measurement_dryrun_operator_decision_intake_gate",
    "build_loop805_measurement_dryrun_preflight_packet",
    "build_loop805_measurement_readiness_review",
    "build_loop805_outcome_policy_review_packet",
    "build_loop805_controller_plan",
    "build_loop805_daily_dashboard",
    "build_loop805_mcp_exposure_stub",
    "build_loop805_regression_pr_proposal",
    "build_loop805_slice3_prompt_packet",
    "build_loop805_slice4_prompt_packet",
    "build_loop805_slice5_prompt_packet",
    "build_loop805_slice6_prompt_packet",
    "build_loop805_slice7_prompt_packet",
    "build_loop805_slice8_prompt_packet",
    "build_loop805_slice9_prompt_packet",
    "build_loop805_slice10_prompt_packet",
    "build_loop805_slice11_prompt_packet",
    "build_loop805_slice12_prompt_packet",
    "build_loop805_slice13_prompt_packet",
    "build_loop805_slice14_prompt_packet",
    "build_loop805_slice15_prompt_packet",
    "build_loop805_slice16_prompt_packet",
    "build_loop805_slice17_prompt_packet",
    "build_loop805_slice18_prompt_packet",
    "build_loop805_slice19_prompt_packet",
    "build_loop805_slice20_prompt_packet",
    "build_loop805_token_optimizer_stub",
    "build_held_out_brier_fixture",
    "build_held_out_brier_telemetry",
    "build_meta_gate_review",
    "build_notion_reconciliation_dryrun",
    "build_patch_contract",
    "build_post_merge_reconciliation_receipt",
    "build_shadow_runtime_activation_prep",
    "build_spine_route_decision",
    "default_loop805_mcp_tool_contracts",
    "build_spine_audit_projection",
    "build_spine_forecast_projection",
    "build_spine_query_projection",
    "prepare_shadow_runtime_activation",
    "run_codegen_harness",
    "run_shadow_replay",
    "run_task_packet",
    "validate_shadow_replay_fixture",
    "validate_shadow_replay_fixtures",
]
