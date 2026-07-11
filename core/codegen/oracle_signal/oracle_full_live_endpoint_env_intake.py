"""Oracle full-live endpoint environment intake builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records redacted operator configuration intake for runtime preflight blockers.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


REQUIRED_ENDPOINT_ENV_VARS = (
    "ORACLE_SIGNAL_ENDPOINT_URL",
    "HOLLERSPORTS_BATCH_ENDPOINT_URL",
)


def build_oracle_full_live_endpoint_env_intake(
    *,
    timestamp: str,
    oracle_full_live_runtime_preflight_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    missing_env = list(
        oracle_full_live_runtime_preflight_receipt.get(
            "missing_endpoint_env_vars",
            REQUIRED_ENDPOINT_ENV_VARS,
        )
    )
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveEndpointEnvIntake.v1",
        "intake_id": canonical_hash(
            {
                "record": "oracle_full_live_endpoint_env_intake",
                "runtime_preflight_receipt": (
                    oracle_full_live_runtime_preflight_receipt["canonical_hash"]
                ),
                "missing_env": missing_env,
            }
        ),
        "intake_status": "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_READY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_full_live_runtime_preflight_receipt": (
                oracle_full_live_runtime_preflight_receipt["canonical_hash"]
            ),
        },
        "endpoint_env_requirements": [
            _endpoint_requirement(
                "ORACLE_SIGNAL_PRIMARY_ENDPOINT",
                "ORACLE_SIGNAL_ENDPOINT_URL",
                "Primary Oracle signal endpoint URL",
                "missing" if "ORACLE_SIGNAL_ENDPOINT_URL" in missing_env else "present",
            ),
            _endpoint_requirement(
                "HOLLERSPORTS_PRIMARY_ENDPOINT",
                "HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "HollerSports batch endpoint URL",
                (
                    "missing"
                    if "HOLLERSPORTS_BATCH_ENDPOINT_URL" in missing_env
                    else "present"
                ),
            ),
        ],
        "operator_configuration_checklist": [
            _checklist_item(
                "SET_ORACLE_SIGNAL_ENDPOINT_URL",
                "Configure ORACLE_SIGNAL_ENDPOINT_URL in the operator runtime environment.",
            ),
            _checklist_item(
                "SET_HOLLERSPORTS_BATCH_ENDPOINT_URL",
                "Configure HOLLERSPORTS_BATCH_ENDPOINT_URL in the operator runtime environment.",
            ),
            _checklist_item(
                "CONFIRM_NO_SECRET_VALUES_IN_REPO",
                "Verify endpoint values are not committed, logged, or copied into receipts.",
            ),
            _checklist_item(
                "RERUN_PREFLIGHT_UNDER_OPERATOR_MONITORING",
                "Run the full-live runtime preflight after environment setup.",
            ),
        ],
        "rerun_plan": {
            "command": (
                "python scripts/abx_loop.py "
                "--emit-oracle-full-live-runtime-preflight "
                "--validate-oracle-schemas"
            ),
            "expected_ready_status_after_configuration": (
                "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
            ),
            "continue_to_runtime_command_only_after_ready": True,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_full_live_endpoint_env_intake"),
        "authority_locks": _authority_locks(),
        "stores_endpoint_values": False,
        "external_calls_made": 0,
        "valid_for_external_oracle_calls": False,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_persistent_telemetry": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_autonomous_outcome_recording": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_endpoint_env_intake_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_full_live_endpoint_env_intake: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveEndpointEnvIntakeReceipt.v1",
        "receipt_id": "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_RECEIPT_001",
        "receipt_status": "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_READY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_full_live_endpoint_env_intake": (
                oracle_full_live_endpoint_env_intake["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "missing_endpoint_env_vars": [
            requirement["endpoint_env_var"]
            for requirement in oracle_full_live_endpoint_env_intake[
                "endpoint_env_requirements"
            ]
            if requirement["observed_preflight_state"] == "missing"
        ],
        "recommended_next_advisory_action": (
            "Configure endpoint environment outside git, then rerun the full-live "
            "runtime preflight under operator monitoring."
        ),
        "provenance": _provenance("oracle_full_live_endpoint_env_intake_receipt"),
        "authority_locks": _authority_locks(),
        "stores_endpoint_values": False,
        "external_calls_made": 0,
        "valid_for_external_oracle_calls": False,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_persistent_telemetry": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _endpoint_requirement(
    connection_id: str,
    endpoint_env_var: str,
    operator_label: str,
    observed_preflight_state: str,
) -> dict[str, Any]:
    return {
        "connection_id": connection_id,
        "endpoint_env_var": endpoint_env_var,
        "operator_label": operator_label,
        "observed_preflight_state": observed_preflight_state,
        "secret_material_embedded": False,
        "endpoint_value_recorded": False,
        "required_before_runtime_command": True,
        "brier_score": 0.1,
    }


def _checklist_item(item_id: str, instruction: str) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "instruction": instruction,
        "operator_action_required": True,
        "records_secret": False,
        "external_call_made": False,
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": True,
        "actual_external_oracle_calls": True,
        "actual_live_data_ingestion": True,
        "persistent_production_runtime_activation": True,
        "mcp_exposure": False,
        "unreviewed_production_deployment": False,
        "autonomous_outcome_recording": False,
        "github_writeback": False,
        "notion_writeback": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "operator_gate": "FULL_LIVE_EXECUTION_GATE",
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "stores_endpoint_values": False,
        "external_calls_made": 0,
        "brier_score": 0.1,
    }
