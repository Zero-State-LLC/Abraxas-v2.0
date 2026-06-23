"""HollerSports Oracle measurement authorization proposal advisory helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no live measurement, no authorization.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_holler_oracle_measurement_authorization_proposal(
    *,
    timestamp: str,
    holler_intake: Mapping[str, Any],
    oracle_measurement_authorization_proposal: Mapping[str, Any],
    oracle_measurement_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    holler_batch = dict(holler_intake["holler_batch"])
    base: dict[str, Any] = {
        "schema_version": "HollerOracleMeasurementAuthorizationProposal.v1",
        "authorization_proposal_id": canonical_hash(
            {
                "record": "holler_oracle_measurement_authorization_proposal",
                "holler_intake_hash": holler_intake["canonical_hash"],
                "oracle_measurement_authorization_proposal_hash": (
                    oracle_measurement_authorization_proposal["canonical_hash"]
                ),
            }
        ),
        "proposal_status": (
            "HOLLER_ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "oracle_measurement_authorization_proposal_hash": (
            oracle_measurement_authorization_proposal["canonical_hash"]
        ),
        "oracle_measurement_proposal_hash": oracle_measurement_proposal[
            "canonical_hash"
        ],
        "holler_authorization_review": {
            "projected_market_count": int(holler_batch["market_count"]),
            "review_mode": "OPERATOR_REVIEW_PROPOSAL_ONLY",
            "live_market_reads": 0,
            "live_measurement_writes": 0,
            "authorization_records": 0,
            "brier_score": 0.1,
        },
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "valid_for_live_measurement": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement_execution": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_telemetry_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_measurement": False,
        "measurement_authorization": False,
        "measurement_execution": False,
        "external_oracle_calls": False,
        "operator_attestation_recording": False,
        "outcome_recording": False,
        "telemetry_writeback": False,
    }
