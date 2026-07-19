"""Script: emit FOURTH_OPERATOR_SELECTION_BUNDLE — four advisory-only artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.metric_operator_rank4_candidate_audit import (
    build_metric_operator_rank4_candidate_audit,
    default_candidate_entries,
    default_output_contract as audit_output_contract,
    serialize_metric_operator_rank4_candidate_audit,
)
from core.metric_operator_rank4_selection_plan import (
    build_metric_operator_rank4_selection_plan,
    default_implementation_gates,
    default_output_contract as plan_output_contract,
    serialize_metric_operator_rank4_selection_plan,
)
from core.norm_geometry_distance_implementation_readiness_dossier import (
    build_norm_geometry_distance_implementation_readiness_dossier,
    default_output_contract as dossier_output_contract,
    serialize_norm_geometry_distance_implementation_readiness_dossier,
)
from core.norm_geometry_test_vector_schema_plan import (
    build_norm_geometry_test_vector_schema_plan,
    default_output_contract as schema_plan_output_contract,
    default_schema_constraints,
    default_schema_layout_plan,
    default_validation_plan,
    serialize_norm_geometry_test_vector_schema_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "FOURTH_OPERATOR_SELECTION_BUNDLE_001"
_LOCKED_FALSE_FLAGS = {
    "production_activation": False, "canon_promotion": False,
    "scheduler_mutation": False, "runtime_authority": False,
    "runtime_mutation": False, "forecast_influence": False,
    "execution_authority": False, "token_minting_allowed": False,
    "valid_for_execution": False, "activation_approved": False,
    "authorization_granted": False,
}

_PATHS = RuntimePaths.from_env()
AUDIT_OUT    = _PATHS.metric_operator_rank4_candidate_audit_latest
PLAN_OUT     = _PATHS.metric_operator_rank4_selection_plan_latest
DOSSIER_OUT  = _PATHS.norm_geometry_distance_implementation_readiness_dossier_latest
SCHEMA_OUT   = _PATHS.norm_geometry_test_vector_schema_plan_latest

_PARITY_RECEIPT_002_HASH = (
    "6a4d05e6147009d04f3e666da719473451396513e99ace5a9f789783bd618185"
)
_REGISTRY_STAB_002_HASH = (
    "c281a21492dfac3c6f2c5c9ac7af1749609aa0f9a2842b7100b506caf139b901"
)
_FRONTIER_002_HASH = (
    "a49b6326750e5021d0d4840f450ec0470939fb5f61250339c48471c699a7d620"
)

_AUDIT_PAYLOAD: dict = {
    "audit_id": "metric_operator_rank4_candidate_audit_001",
    "audit_status": "RANK4_CANDIDATE_SELECTED",
    "completed_operators": ["CHAMFER_DISTANCE", "GEODESIC", "WASSERSTEIN"],
    "candidate_entries": default_candidate_entries(),
    "recommended_rank4": "NORM_GEOMETRY",
    "output_contract": audit_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_rank4_candidate_audit.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorCrossOperatorParityReceipt.v1:metric_operator_cross_operator_parity_receipt_002",
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
            "MetricOperatorFrontierRecommendation.v1:metric_operator_frontier_recommendation_002",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_PLAN_PAYLOAD: dict = {
    "plan_id": "metric_operator_rank4_selection_plan_001",
    "selected_operator_id": "NORM_GEOMETRY",
    "selection_scope": {
        "intended_lane": "SHADOW",
        "selection_family": "RANK4_OPERATOR_SELECTION",
        "selection_stage": "SELECTION_PLAN_ONLY",
    },
    "source_audit_refs": [
        "MetricOperatorRank4CandidateAudit.v1:metric_operator_rank4_candidate_audit_001",
    ],
    "source_registry_stabilization_refs": [
        "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
    ],
    "source_frontier_recommendation_refs": [
        "MetricOperatorFrontierRecommendation.v1:metric_operator_frontier_recommendation_002",
    ],
    "implementation_gates": default_implementation_gates(),
    "output_contract": plan_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_rank4_selection_plan.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorRank4CandidateAudit.v1:metric_operator_rank4_candidate_audit_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_DOSSIER_PAYLOAD: dict = {
    "dossier_id": "norm_geometry_distance_implementation_readiness_dossier_001",
    "implementation_scope": "NORM_GEOMETRY_DISTANCE_READINESS_ONLY",
    "output_contract": dossier_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/norm_geometry_distance_implementation_readiness_dossier.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorRank4SelectionPlan.v1:metric_operator_rank4_selection_plan_001",
            "MetricOperatorRank4CandidateAudit.v1:metric_operator_rank4_candidate_audit_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}

_SCHEMA_PLAN_PAYLOAD: dict = {
    "plan_id": "norm_geometry_test_vector_schema_plan_001",
    "schema_scope": {
        "schema_family": "MIXED_SCHEMA_PLAN",
        "intended_lane": "SHADOW",
        "schema_stage": "SCHEMA_PLAN_ONLY",
    },
    "source_dossier_refs": [
        "NormGeometryDistanceImplementationReadinessDossier.v1:"
        "norm_geometry_distance_implementation_readiness_dossier_001",
    ],
    "source_metric_registry_refs": [
        "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_002",
    ],
    "source_baseline_vector_pack_refs": [
        "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
    ],
    "schema_layout_plan": default_schema_layout_plan(),
    "schema_constraints": default_schema_constraints(),
    "validation_plan": default_validation_plan(),
    "output_contract": schema_plan_output_contract(),
    "governance_flags": dict(_LOCKED_FALSE_FLAGS),
    "provenance": {
        "source": "FOURTH_OPERATOR_SELECTION_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/norm_geometry_test_vector_schema_plan.v1.schema.json",
        ],
        "evidence_refs": [
            "NormGeometryDistanceImplementationReadinessDossier.v1:"
            "norm_geometry_distance_implementation_readiness_dossier_001",
            "MetricOperatorRank4SelectionPlan.v1:metric_operator_rank4_selection_plan_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "fourth_operator_selection_bundle",
        artifact_path=AUDIT_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(logger, "INFO", "fourth_operator_selection_bundle_started",
              correlation_id=correlation_id)

    AUDIT_OUT.parent.mkdir(parents=True, exist_ok=True)

    audit = build_metric_operator_rank4_candidate_audit(_AUDIT_PAYLOAD)
    AUDIT_OUT.write_text(
        serialize_metric_operator_rank4_candidate_audit(audit), encoding="utf-8"
    )
    log_event(logger, "INFO", "rank4_candidate_audit_emitted",
              canonical_hash=audit.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"rank4_candidate_audit  canonical_hash={audit.get('canonical_hash','?')}")
    print(f"  recommended_rank4={audit.get('recommended_rank4','?')}")
    print(f"  wrote={AUDIT_OUT.as_posix()}")

    plan = build_metric_operator_rank4_selection_plan(_PLAN_PAYLOAD)
    PLAN_OUT.write_text(
        serialize_metric_operator_rank4_selection_plan(plan), encoding="utf-8"
    )
    log_event(logger, "INFO", "rank4_selection_plan_emitted",
              canonical_hash=plan.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"rank4_selection_plan   canonical_hash={plan.get('canonical_hash','?')}")
    print(f"  selected_operator_id={plan.get('selected_operator_id','?')}")
    print(f"  wrote={PLAN_OUT.as_posix()}")

    dossier = build_norm_geometry_distance_implementation_readiness_dossier(
        _DOSSIER_PAYLOAD
    )
    DOSSIER_OUT.write_text(
        serialize_norm_geometry_distance_implementation_readiness_dossier(dossier),
        encoding="utf-8",
    )
    log_event(logger, "INFO", "norm_geometry_readiness_dossier_emitted",
              canonical_hash=dossier.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"norm_geometry_dossier  canonical_hash={dossier.get('canonical_hash','?')}")
    print(f"  wrote={DOSSIER_OUT.as_posix()}")

    schema_plan = build_norm_geometry_test_vector_schema_plan(_SCHEMA_PLAN_PAYLOAD)
    SCHEMA_OUT.write_text(
        serialize_norm_geometry_test_vector_schema_plan(schema_plan), encoding="utf-8"
    )
    log_event(logger, "INFO", "norm_geometry_schema_plan_emitted",
              canonical_hash=schema_plan.get("canonical_hash", "?"),
              correlation_id=correlation_id)
    print(f"norm_geometry_schema   canonical_hash={schema_plan.get('canonical_hash','?')}")
    print(f"  wrote={SCHEMA_OUT.as_posix()}")

    log_event(logger, "INFO", "fourth_operator_selection_bundle_completed",
              correlation_id=correlation_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
