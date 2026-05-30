"""Script: emit IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE — four advisory-only artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.implementation_authorization_prep import (
    build_implementation_authorization_prep,
    default_locked_constants_required,
    default_readiness_comparison,
    default_recommendation_rationale,
    default_required_operator_decision_fields,
    default_output_contract as prep_output_contract,
    serialize_implementation_authorization_prep,
)
from core.norm_geometry_implementation_authorization_template import (
    build_norm_geometry_implementation_authorization_template,
    default_locked_constants_required as ng_locked_constants,
    default_output_contract as ng_template_output_contract,
    default_required_operator_decision_fields as ng_decision_fields,
    serialize_norm_geometry_implementation_authorization_template,
)
from core.transport_implementation_authorization_template import (
    build_transport_implementation_authorization_template,
    default_locked_constants_required as tr_locked_constants,
    default_output_contract as tr_template_output_contract,
    default_required_operator_decision_fields as tr_decision_fields,
    serialize_transport_implementation_authorization_template,
)
from core.metric_operator_frontier_recommendation import (
    authorization_prep_complete_ranked_options,
    build_metric_operator_frontier_recommendation,
    default_governance_flags,
    default_output_contract as frontier_output_contract,
    serialize_metric_operator_frontier_recommendation,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_001"
_LOCKED_FALSE_FLAGS = {
    "production_activation": False, "canon_promotion": False,
    "scheduler_mutation": False, "runtime_authority": False,
    "runtime_mutation": False, "forecast_influence": False,
    "execution_authority": False, "token_minting_allowed": False,
    "valid_for_execution": False, "activation_approved": False,
    "authorization_granted": False,
}

_PATHS = RuntimePaths.from_env()
PREP_OUT     = _PATHS.implementation_authorization_prep_latest
NG_TMPL_OUT  = _PATHS.norm_geometry_implementation_authorization_template_latest
TR_TMPL_OUT  = _PATHS.transport_implementation_authorization_template_latest
FRONTIER_OUT = _PATHS.metric_operator_frontier_recommendation_004_latest

_PREP_PAYLOAD: dict = {
    "prep_id": "implementation_authorization_prep_001",
    "operators_compared": ["NORM_GEOMETRY", "TRANSPORT"],
    "readiness_comparison": default_readiness_comparison(),
    "recommended_first_implementation_path": "NORM_GEOMETRY",
    "recommendation_rationale": default_recommendation_rationale(),
    "required_operator_decision_fields": default_required_operator_decision_fields(),
    "locked_constants_required": default_locked_constants_required(),
    "output_contract": prep_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/implementation_authorization_prep.v1.schema.json",
        ],
        "evidence_refs": [
            "NormGeometryCpuBaselineActualPrGateReview.v1:"
            "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
            "TransportCpuBaselineActualPrGateReview.v1:"
            "transport_cpu_baseline_actual_pr_gate_review_001",
            "NormGeometryCpuBaselineImplementationPlan.v1:"
            "norm_geometry_cpu_baseline_implementation_plan_001",
            "TransportCpuBaselineImplementationPlan.v1:"
            "transport_cpu_baseline_implementation_plan_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_NG_TEMPLATE_PAYLOAD: dict = {
    "template_id": "norm_geometry_implementation_authorization_template_001",
    "required_operator_decision_fields": ng_decision_fields(),
    "locked_constants_required": ng_locked_constants(),
    "activation_blocked_reason": (
        "Template only; explicit operator authorization instruction required. "
        "Five locked constants must be declared before any NORM_GEOMETRY "
        "implementation PR may be opened. This template does not constitute "
        "authorization."
    ),
    "output_contract": ng_template_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "norm_geometry_implementation_authorization_template.v1.schema.json",
        ],
        "evidence_refs": [
            "ImplementationAuthorizationPrep.v1:"
            "implementation_authorization_prep_001",
            "NormGeometryCpuBaselineActualPrGateReview.v1:"
            "norm_geometry_cpu_baseline_actual_pr_gate_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_TR_TEMPLATE_PAYLOAD: dict = {
    "template_id": "transport_implementation_authorization_template_001",
    "required_operator_decision_fields": tr_decision_fields(),
    "locked_constants_required": tr_locked_constants(),
    "activation_blocked_reason": (
        "Template only; explicit operator authorization instruction required. "
        "Seven locked constants must be declared before any TRANSPORT "
        "implementation PR may be opened, including LP solver variant, pivot "
        "rule, and tie-breaking strategy. This template does not constitute "
        "authorization."
    ),
    "output_contract": tr_template_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "transport_implementation_authorization_template.v1.schema.json",
        ],
        "evidence_refs": [
            "ImplementationAuthorizationPrep.v1:"
            "implementation_authorization_prep_001",
            "TransportCpuBaselineActualPrGateReview.v1:"
            "transport_cpu_baseline_actual_pr_gate_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_FRONTIER_PAYLOAD: dict = {
    "recommendation_id": "metric_operator_frontier_recommendation_004",
    "recommendation_status": "ADVISORY_ONLY",
    "ranked_options": authorization_prep_complete_ranked_options(),
    "recommended_next_step": (
        "Operator emits explicit NORM_GEOMETRY implementation authorization "
        "instruction with five locked constants as documented in "
        "NormGeometryImplementationAuthorizationTemplate.v1. "
        "This is the first recommended implementation path per "
        "ImplementationAuthorizationPrep.v1."
    ),
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "No self-authorizing advancement step exists. Both implementation "
        "authorization paths (J_NORM_GEOMETRY, K_TRANSPORT) require explicit "
        "operator instruction. NORM_GEOMETRY recommended first."
    ),
    "output_contract": frontier_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "IMPLEMENTATION_AUTHORIZATION_PREP_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
        ],
        "evidence_refs": [
            "ImplementationAuthorizationPrep.v1:"
            "implementation_authorization_prep_001",
            "NormGeometryImplementationAuthorizationTemplate.v1:"
            "norm_geometry_implementation_authorization_template_001",
            "TransportImplementationAuthorizationTemplate.v1:"
            "transport_implementation_authorization_template_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "implementation_authorization_prep_bundle",
        artifact_path=PREP_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "implementation_authorization_prep_bundle_started",
              correlation_id=correlation_id)

    PREP_OUT.parent.mkdir(parents=True, exist_ok=True)

    prep = build_implementation_authorization_prep(_PREP_PAYLOAD)
    PREP_OUT.write_text(
        serialize_implementation_authorization_prep(prep), encoding="utf-8"
    )
    log_event(logger, "INFO", "implementation_authorization_prep_emitted",
              canonical_hash=prep.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"impl_auth_prep  canonical_hash={prep.get('canonical_hash','?')}")
    print(f"  recommended_first={prep.get('recommended_first_implementation_path','?')}")
    print(f"  wrote={PREP_OUT.as_posix()}")

    ng_tmpl = build_norm_geometry_implementation_authorization_template(_NG_TEMPLATE_PAYLOAD)
    NG_TMPL_OUT.write_text(
        serialize_norm_geometry_implementation_authorization_template(ng_tmpl), encoding="utf-8"
    )
    log_event(logger, "INFO", "norm_geometry_authorization_template_emitted",
              canonical_hash=ng_tmpl.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"ng_template     canonical_hash={ng_tmpl.get('canonical_hash','?')}")
    print(f"  template_status={ng_tmpl.get('template_status','?')}")
    print(f"  wrote={NG_TMPL_OUT.as_posix()}")

    tr_tmpl = build_transport_implementation_authorization_template(_TR_TEMPLATE_PAYLOAD)
    TR_TMPL_OUT.write_text(
        serialize_transport_implementation_authorization_template(tr_tmpl), encoding="utf-8"
    )
    log_event(logger, "INFO", "transport_authorization_template_emitted",
              canonical_hash=tr_tmpl.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"tr_template     canonical_hash={tr_tmpl.get('canonical_hash','?')}")
    print(f"  template_status={tr_tmpl.get('template_status','?')}")
    print(f"  wrote={TR_TMPL_OUT.as_posix()}")

    frontier = build_metric_operator_frontier_recommendation(_FRONTIER_PAYLOAD)
    FRONTIER_OUT.write_text(
        serialize_metric_operator_frontier_recommendation(frontier), encoding="utf-8"
    )
    log_event(logger, "INFO", "frontier_recommendation_004_emitted",
              canonical_hash=frontier.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"frontier_004    canonical_hash={frontier.get('canonical_hash','?')}")
    opts = frontier.get("ranked_options", [])
    advisory = sum(1 for o in opts if o.get("authority_posture") == "ADVISORY_ONLY")
    blocked  = sum(1 for o in opts if o.get("authority_posture") == "BLOCKED")
    print(f"  options={len(opts)} advisory={advisory} blocked={blocked}")
    print(f"  wrote={FRONTIER_OUT.as_posix()}")

    log_event(logger, "INFO", "implementation_authorization_prep_bundle_completed",
              correlation_id=correlation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
