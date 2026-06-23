"""HollerSports-specific Oracle schema validation helpers.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live ingest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.codegen.oracle_signal.oracle_schema_validator import validate_oracle_packet


HOLLER_SCHEMA_PATH = "contracts/canon/oracle/oracle_holler_intake.v1.schema.json"


def validate_holler_oracle_batch_evolution(
    *,
    holler_intake: Mapping[str, Any],
    timestamp: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    schema_result = validate_oracle_packet(
        packet_key="oracle_holler_intake",
        packet=holler_intake,
        schema_path=HOLLER_SCHEMA_PATH,
        timestamp=timestamp,
        repo_root=repo_root,
    )
    holler_batch = dict(holler_intake.get("holler_batch", {}))
    specialized_errors = []
    if holler_batch.get("calibration_policy") != "SHADOW_CALIBRATION_REPORT_ONLY":
        specialized_errors.append(
            {
                "path": "holler_batch.calibration_policy",
                "message": "HollerSports validation remains shadow calibration only",
                "brier_score": 0.1,
            }
        )
    if bool(holler_intake.get("shadow_replay", {}).get("valid_for_execution")):
        specialized_errors.append(
            {
                "path": "shadow_replay.valid_for_execution",
                "message": "HollerSports shadow replay cannot be executable",
                "brier_score": 0.1,
            }
        )
    base: dict[str, Any] = {
        "schema_version": "HollerOracleSchemaValidationResult.v1",
        "validation_id": canonical_hash(
            {
                "record": "holler_oracle_schema_validation",
                "schema_result_hash": schema_result["canonical_hash"],
            }
        ),
        "validation_status": (
            "VALID_ADVISORY_ONLY"
            if schema_result["validation_status"] == "VALID_ADVISORY_ONLY"
            and not specialized_errors
            else "INVALID_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "schema_result_hash": schema_result["canonical_hash"],
        "specialized_errors": specialized_errors,
        "holler_batch_id": holler_batch.get("batch_id", ""),
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "live_signal_ingest": False,
            "marketplace_ingest": False,
            "schema_writeback": False,
        },
        "advisory_only": True,
        "valid_for_live_ingest": False,
        "valid_for_execution": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
