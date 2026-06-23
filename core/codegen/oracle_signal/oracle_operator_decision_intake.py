"""Oracle operator decision-intake advisory packet builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no operator attestation recording.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_operator_decision_intake(
    *,
    timestamp: str,
    oracle_shadow_dryrun: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleOperatorDecisionIntake.v1",
        "intake_id": canonical_hash(
            {
                "record": "oracle_operator_decision_intake",
                "oracle_shadow_dryrun_hash": oracle_shadow_dryrun["canonical_hash"],
            }
        ),
        "intake_status": "ORACLE_OPERATOR_DECISION_INTAKE_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "oracle_shadow_dryrun_hash": oracle_shadow_dryrun["canonical_hash"],
        "template": {
            "template_id": "ORACLE_MEASUREMENT_READINESS_OPERATOR_INTAKE_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "review_questions": [
            {
                "question_id": "Q1_SHADOW_DRYRUN_SCOPE",
                "question": "Does the operator accept the shadow dry-run receipt as advisory evidence only?",
                "records_decision": False,
                "brier_score": 0.1,
            },
            {
                "question_id": "Q2_MEASUREMENT_BOUNDARY",
                "question": "Does the operator confirm no live measurement is authorized by this packet?",
                "records_decision": False,
                "brier_score": 0.1,
            },
        ],
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_authorization": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_measurement": False,
        "operator_attestation_recording": False,
        "github_writeback": False,
        "notion_writeback": False,
    }
