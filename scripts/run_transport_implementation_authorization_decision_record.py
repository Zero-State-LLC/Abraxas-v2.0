"""Script: emit TransportImplementationAuthorizationDecisionRecord.v1 and frontier _006."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import canonical_hash
from core.transport_implementation_authorization_decision_record import (
    build_transport_implementation_authorization_decision_record,
    default_authority_locks,
    default_blocked_scopes,
    default_output_contract,
    serialize_transport_implementation_authorization_decision_record,
    _build_blocked_scope_acknowledgement_review,
    _build_decision_validation_review,
    _build_implementation_gate_prerequisite_review,
    _build_locked_constants_record,
)
from core.metric_operator_frontier_recommendation import (
    build_metric_operator_frontier_recommendation,
    default_governance_flags as front_governance_flags,
    default_output_contract as front_output_contract,
    serialize_metric_operator_frontier_recommendation,
    transport_implementation_gate_ranked_options,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_001"

_PATHS = RuntimePaths.from_env()

DECISION_INPUT = Path(
    "input/transport_implementation_authorization_operator_decision.json"
)
RECORD_OUT   = _PATHS.transport_implementation_authorization_decision_record_001_latest
FRONTIER_OUT = _PATHS.metric_operator_frontier_recommendation_006_latest


def _load_operator_decision(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"operator decision file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("operator_decision_not_a_dict")
    return data


def _build_record_payload(decision_data: dict) -> dict:
    source_hash = canonical_hash(decision_data)
    locked_constants = decision_data.get("locked_constants", {})
    return {
        "record_id": "transport_implementation_authorization_decision_record_001",
        "source_operator_decision_hash": source_hash,
        "decision_id": decision_data.get(
            "decision_id",
            "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_2026_05_29_001",
        ),
        "locked_constants_record": _build_locked_constants_record(locked_constants),
        "decision_validation_review": _build_decision_validation_review(decision_data),
        "blocked_scope_acknowledgement_review": _build_blocked_scope_acknowledgement_review(
            decision_data
        ),
        "implementation_gate_prerequisite_review": _build_implementation_gate_prerequisite_review(),
        "authority_locks": default_authority_locks(),
        "blocked_scopes": default_blocked_scopes(),
        "recommended_next_step": "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE",
        "output_contract": default_output_contract(),
        "provenance": {
            "source": "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_RUN",
            "advisory_only": True,
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/transport_implementation_authorization_decision_record.v1.schema.json",
            ],
            "evidence_refs": [
                "TransportImplementationAuthorizationOperatorDecision.v1"
                ":transport_implementation_authorization_operator_decision",
                "MetricOperatorCrossOperatorParityReceipt.v1"
                ":metric_operator_cross_operator_parity_receipt_003",
                "MetricOperatorRegistryStabilization.v1"
                ":metric_operator_registry_stabilization_003",
                "MetricOperatorFrontierRecommendation.v1"
                ":metric_operator_frontier_recommendation_005",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


_FRONTIER_PAYLOAD: dict = {
    "recommendation_id": "metric_operator_frontier_recommendation_006",
    "recommendation_status": "ADVISORY_ONLY",
    "ranked_options": transport_implementation_gate_ranked_options(),
    "recommended_next_step": "G_SEALED_PAUSE",
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "TRANSPORT implementation authorization decision recorded. "
        "Seven locked constants sealed. "
        "No self-authorizing advancement step exists from TEST_VECTOR_COMPUTATION_ONLY posture. "
        "TRANSPORT computation implementation gate is advisory-only. "
        "All implementation PRs require explicit operator instruction. "
        "Metric emission, forecast influence, and P43 surface lanes remain blocked."
    ),
    "output_contract": front_output_contract(),
    "governance_flags": front_governance_flags(),
    "provenance": {
        "source": "TRANSPORT_IMPLEMENTATION_AUTHORIZATION_DECISION_RECORD_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_frontier_recommendation.v1.schema.json",
            "contracts/canon/transport_implementation_authorization_decision_record.v1.schema.json",
        ],
        "evidence_refs": [
            "TransportImplementationAuthorizationDecisionRecord.v1"
            ":transport_implementation_authorization_decision_record_001",
            "MetricOperatorCrossOperatorParityReceipt.v1"
            ":metric_operator_cross_operator_parity_receipt_003",
            "MetricOperatorFrontierRecommendation.v1"
            ":metric_operator_frontier_recommendation_005",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "transport_implementation_authorization_decision_record",
        artifact_path=RECORD_OUT,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "transport_implementation_authorization_decision_record_started",
        correlation_id=correlation_id,
    )

    decision_data = _load_operator_decision(DECISION_INPUT)
    log_event(
        logger,
        "INFO",
        "operator_decision_loaded",
        decision_id=decision_data.get("decision_id"),
        correlation_id=correlation_id,
    )

    RECORD_OUT.parent.mkdir(parents=True, exist_ok=True)

    payload = _build_record_payload(decision_data)
    record = build_transport_implementation_authorization_decision_record(payload)
    RECORD_OUT.write_text(
        serialize_transport_implementation_authorization_decision_record(record),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "decision_record_001_emitted",
        canonical_hash=record.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"decision_record_001  canonical_hash={record.get('canonical_hash', '?')}")
    print(f"  wrote={RECORD_OUT.as_posix()}")

    frontier = build_metric_operator_frontier_recommendation(_FRONTIER_PAYLOAD)
    FRONTIER_OUT.write_text(
        serialize_metric_operator_frontier_recommendation(frontier),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "frontier_recommendation_006_emitted",
        canonical_hash=frontier.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"frontier_recommendation_006  canonical_hash={frontier.get('canonical_hash', '?')}")
    print(f"  wrote={FRONTIER_OUT.as_posix()}")

    log_event(
        logger,
        "INFO",
        "transport_implementation_authorization_decision_record_completed",
        correlation_id=correlation_id,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
