"""Oracle persistent execution + secret vault planning builders.

Provenance: Notion Sprint 001 + Loop 805 Oracle Runtime Mirror + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no secret persistence, no live execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


ISSUE_881_TITLE = "v2.7.2 - Persistent Execution + Secret Vault (sandbox-gated)"
PR_880_MERGE_SHA = "ddf08c456e82cb5d0af71e3d90fd0c0210c0c0b6"
RUNTIME_MIRROR_PACKET_HASH = (
    "5526667f4677854c94a0afce5359f08b956f47276f3db96c11635615d4866c6c"
)
RUNTIME_EXECUTION_ATTEMPT_BLOCKED_HASH = (
    "922e97a2b990554f35d5c1a4ada6a51a798545e81017a6f5c4f799f8e86e3ca6"
)


def build_oracle_persistent_execution_secret_vault_plan(
    *,
    timestamp: str,
    oracle_full_live_endpoint_env_intake_receipt: Mapping[str, Any],
    oracle_full_live_runtime_preflight_receipt: Mapping[str, Any],
    oracle_full_live_runtime_execution_attempt_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a sandbox-gated planning packet for #881 without persisting secrets."""

    base: dict[str, Any] = {
        "schema_version": "OraclePersistentExecutionSecretVaultPlan.v1",
        "plan_id": canonical_hash(
            {
                "record": "oracle_persistent_execution_secret_vault_plan",
                "issue": ISSUE_881_TITLE,
                "runtime_execution_attempt_receipt": (
                    oracle_full_live_runtime_execution_attempt_receipt[
                        "canonical_hash"
                    ]
                ),
                "mirror_packet_hash": RUNTIME_MIRROR_PACKET_HASH,
            }
        ),
        "plan_status": (
            "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "source_packet_hashes": {
            "pr_880_merge_sha": PR_880_MERGE_SHA,
            "runtime_mirror_packet": RUNTIME_MIRROR_PACKET_HASH,
            "runtime_execution_attempt_blocked": (
                RUNTIME_EXECUTION_ATTEMPT_BLOCKED_HASH
            ),
            "oracle_full_live_endpoint_env_intake_receipt": (
                oracle_full_live_endpoint_env_intake_receipt["canonical_hash"]
            ),
            "oracle_full_live_runtime_preflight_receipt": (
                oracle_full_live_runtime_preflight_receipt["canonical_hash"]
            ),
            "oracle_full_live_runtime_execution_attempt_receipt": (
                oracle_full_live_runtime_execution_attempt_receipt[
                    "canonical_hash"
                ]
            ),
        },
        "secret_handling_requirements": [
            _requirement(
                "SECRET_MATERIAL_NEVER_IN_REPO_LOGS_OR_NOTION",
                "Secret material must never enter repo files, generated receipts, logs, PR bodies, or Notion closeout blocks.",
            ),
            _requirement(
                "ENDPOINT_CONFIG_EXTERNAL_ONLY",
                "Endpoint configuration must use an ignored local env file or an external secret store controlled by the operator.",
            ),
            _requirement(
                "RECEIPT_BEFORE_SANDBOX_PROBE",
                "Runtime receipts must be emitted and reviewed before any sandbox-gated probe command is requested.",
            ),
            _requirement(
                "ROLLBACK_PATH_DOCUMENTED",
                "Every future persistent execution lane must include a documented rollback path before enabling persistence.",
            ),
        ],
        "persistent_execution_boundaries": {
            "runtime_mode": "SANDBOX_GATED_PLANNING_ONLY",
            "persistent_execution_enabled": False,
            "external_calls_allowed": False,
            "secret_material_allowed_in_repo": False,
            "telemetry_writeback_allowed": False,
            "allowed_next_surface": (
                "operator-reviewed persistent sandbox design proposal"
            ),
            "brier_score": 0.1,
        },
        "runtime_receipt_gate": {
            "gate_status": "RECEIPT_REQUIRED_BEFORE_ANY_SANDBOX_PROBE",
            "required_prior_receipts": [
                "oracle_full_live_runtime_preflight_receipt_001",
                "oracle_full_live_endpoint_env_intake_receipt_001",
                "oracle_full_live_runtime_execution_attempt_receipt_001",
            ],
            "current_execution_attempt_status": (
                oracle_full_live_runtime_execution_attempt_receipt[
                    "receipt_status"
                ]
            ),
            "current_execution_attempt_expected": (
                "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
            ),
            "sandbox_probe_authorized_by_this_packet": False,
            "brier_score": 0.1,
        },
        "rollback_plan": {
            "rollback_status": "PLANNING_STUB_READY",
            "minimum_steps": [
                "Disable sandbox-gated scheduler route.",
                "Unset endpoint environment outside git.",
                "Retain blocked/no-call receipts for audit trail.",
                "Append Notion closeout manually only after operator review.",
            ],
            "requires_operator_confirmation": True,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_persistent_execution_secret_vault_plan"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": False,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_persistent_telemetry": False,
        "valid_for_secret_material_persistence": False,
        "valid_for_payload_persistence": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_persistent_execution_secret_vault_plan_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_persistent_execution_secret_vault_plan: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OraclePersistentExecutionSecretVaultPlanReceipt.v1",
        "receipt_id": "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_RECEIPT_001",
        "receipt_status": (
            "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "issue": {
            "issue_number": 881,
            "issue_title": ISSUE_881_TITLE,
            "milestone_status": "OPERATOR_MANAGED_MILESTONE_UNSET_IF_ABSENT",
            "brier_score": 0.1,
        },
        "surface_hashes": {
            "oracle_persistent_execution_secret_vault_plan": (
                oracle_persistent_execution_secret_vault_plan["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "acceptance_criteria": [
            "Secret material never enters repo, logs, PR body, or Notion.",
            "Endpoint configuration uses ignored local env or external secret store.",
            "Runtime receipts emit before any sandbox probe.",
            "Rollback path is documented before persistence is enabled.",
        ],
        "recommended_next_advisory_action": (
            "Review #881 persistent sandbox design, then decide whether to add "
            "ignored local env examples and scheduler queue stubs in a separate PR."
        ),
        "provenance": _provenance(
            "oracle_persistent_execution_secret_vault_plan_receipt"
        ),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": False,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_persistent_telemetry": False,
        "valid_for_secret_material_persistence": False,
        "valid_for_payload_persistence": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _requirement(requirement_id: str, instruction: str) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "instruction": instruction,
        "operator_action_required": True,
        "stores_secret_material": False,
        "external_call_made": False,
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "actual_external_oracle_calls": False,
        "actual_live_data_ingestion": False,
        "persistent_production_runtime_activation": False,
        "secret_material_persistence": False,
        "payload_persistence": False,
        "telemetry_writeback": False,
        "mcp_exposure": False,
        "unreviewed_production_deployment": False,
        "autonomous_outcome_recording": False,
        "github_writeback": False,
        "notion_writeback": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + Loop 805 Oracle Runtime Mirror",
        "issue": ISSUE_881_TITLE,
        "parent_pr": "PR #880",
        "parent_merge_sha": PR_880_MERGE_SHA,
        "runtime_mirror_packet_hash": RUNTIME_MIRROR_PACKET_HASH,
        "blocked_runtime_attempt_receipt_hash": (
            RUNTIME_EXECUTION_ATTEMPT_BLOCKED_HASH
        ),
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
