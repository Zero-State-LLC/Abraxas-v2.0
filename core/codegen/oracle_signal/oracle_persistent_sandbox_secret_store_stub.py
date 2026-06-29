"""Oracle persistent sandbox secret-store stub builders.

Provenance: Notion Sprint 001 + Loop 805 Oracle Runtime Mirror + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no secret capture, no scheduler runtime.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


ISSUE_881_TITLE = "v2.7.2 - Persistent Execution + Secret Vault (sandbox-gated)"
PR_882_MERGE_SHA = "6750dffcc77ad6ec2dc58e3870d771187e8552f6"
PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_HASH = (
    "28fccc32396acab5f4ca7cb7f0f4c61675350aa0b9903240e530b3df87fc294a"
)


def build_oracle_persistent_sandbox_secret_store_stub(
    *,
    timestamp: str,
    oracle_persistent_execution_secret_vault_plan_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the next #881 sandbox stub without recording any secret material."""

    base: dict[str, Any] = {
        "schema_version": "OraclePersistentSandboxSecretStoreStub.v1",
        "stub_id": canonical_hash(
            {
                "record": "oracle_persistent_sandbox_secret_store_stub",
                "issue": ISSUE_881_TITLE,
                "plan_receipt": oracle_persistent_execution_secret_vault_plan_receipt[
                    "canonical_hash"
                ],
                "pr_882_merge_sha": PR_882_MERGE_SHA,
            }
        ),
        "stub_status": (
            "ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "source_packet_hashes": {
            "pr_882_merge_sha": PR_882_MERGE_SHA,
            "oracle_persistent_execution_secret_vault_plan_receipt": (
                oracle_persistent_execution_secret_vault_plan_receipt[
                    "canonical_hash"
                ]
            ),
            "expected_plan_hash": PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_HASH,
        },
        "ignored_env_examples": [
            _env_example("ORACLE_SIGNAL_ENDPOINT_URL"),
            _env_example("HOLLERSPORTS_BATCH_ENDPOINT_URL"),
            _env_example("ORACLE_RUNTIME_SECRET_REF"),
            _env_example("ORACLE_SANDBOX_PROBE_ATTEMPT_ID"),
        ],
        "external_secret_store_contract": {
            "contract_status": "STUB_ONLY_OPERATOR_MANAGED",
            "accepted_backends": [
                "operator-managed local ignored env",
                "external secret store reference",
            ],
            "disallowed_backends": [
                "repo file containing secret value",
                "Notion block containing endpoint secret",
                "GitHub issue or PR body containing secret value",
                "runtime receipt containing payload or secret value",
            ],
            "secret_values_stored_in_repo": False,
            "secret_values_stored_in_receipts": False,
            "rotation_required_before_probe": True,
            "brier_score": 0.1,
        },
        "persistent_execution_stub": {
            "stub_status": "SCHEDULER_QUEUE_CONTRACT_STUB_ONLY",
            "scheduler_enabled": False,
            "queue_enabled": False,
            "payload_persistence_enabled": False,
            "telemetry_writeback_enabled": False,
            "external_calls_allowed": False,
            "required_future_gate": "OPERATOR_SANDBOX_PROBE_GATE",
            "brier_score": 0.1,
        },
        "rollback_plan": {
            "rollback_status": "DOCUMENTED_NO_OP_ROLLBACK_STUB",
            "rollback_steps": [
                "Unset local ignored endpoint environment variables.",
                "Disable sandbox scheduler and queue route before first probe.",
                "Retain receipt-only audit trail with no payload persistence.",
                "Append manual Notion closeout only after operator review.",
            ],
            "rollback_verification": [
                "Confirm no endpoint values in git diff.",
                "Confirm receipts contain hashes and refs only.",
                "Confirm full-live execution attempt remains blocked/no-call by default.",
            ],
            "rollback_execution_authorized": False,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_persistent_sandbox_secret_store_stub"),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": False,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_persistent_telemetry": False,
        "valid_for_secret_material_persistence": False,
        "valid_for_payload_persistence": False,
        "valid_for_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_persistent_sandbox_secret_store_stub_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_persistent_sandbox_secret_store_stub: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OraclePersistentSandboxSecretStoreStubReceipt.v1",
        "receipt_id": "ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_RECEIPT_001",
        "receipt_status": (
            "ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "issue": {
            "issue_number": 881,
            "issue_title": ISSUE_881_TITLE,
            "brier_score": 0.1,
        },
        "surface_hashes": {
            "oracle_persistent_sandbox_secret_store_stub": (
                oracle_persistent_sandbox_secret_store_stub["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "delivered_stub_surfaces": [
            "ignored local env examples without values",
            "external secret-store contract stub",
            "scheduler/queue persistence stub held disabled",
            "documented rollback plan",
        ],
        "recommended_next_advisory_action": (
            "Operator review can choose a future sandbox probe gate; this receipt "
            "does not authorize a probe, scheduler, queue, external calls, or persistence."
        ),
        "provenance": _provenance(
            "oracle_persistent_sandbox_secret_store_stub_receipt"
        ),
        "authority_locks": _authority_locks(),
        "valid_for_external_oracle_calls": False,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_persistent_telemetry": False,
        "valid_for_secret_material_persistence": False,
        "valid_for_payload_persistence": False,
        "valid_for_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _env_example(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "storage_policy": "LOCAL_IGNORED_ENV_OR_EXTERNAL_SECRET_STORE_ONLY",
        "example_value": f"<{name}_SET_OUTSIDE_GIT>",
        "secret_material_present": False,
        "committable": False,
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
        "scheduler_queue_runtime": False,
        "secret_material_persistence": False,
        "payload_persistence": False,
        "telemetry_writeback": False,
        "mcp_exposure": False,
        "github_writeback": False,
        "notion_writeback": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + Loop 805 Oracle Runtime Mirror",
        "issue": ISSUE_881_TITLE,
        "parent_pr": "PR #882",
        "parent_merge_sha": PR_882_MERGE_SHA,
        "parent_receipt_hash": PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
