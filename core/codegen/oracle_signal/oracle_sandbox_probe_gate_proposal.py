"""Oracle sandbox probe gate proposal builders.

Provenance: Notion Sprint 001 + Loop 805 Oracle Runtime Mirror + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no probe execution, no secret capture.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


ISSUE_881_TITLE = "v2.7.2 - Persistent Execution + Secret Vault (sandbox-gated)"
PR_884_MERGE_SHA = "07c9816e47c966c3772631b722cca4385f5dbe78"
PERSISTENT_SANDBOX_SECRET_STORE_STUB_HASH = (
    "1bde29ffc272f672d253a1edeb774cad48e91d00fd76eabd02bdaae5f358a6bf"
)
SCHEMA_VALIDATION_RECEIPT_HASH = (
    "b3436ef1d458a8482044a2ab46ce519a89132e84cf59a8ced6dbe3c3ad4eca6c"
)


def build_oracle_sandbox_probe_gate_proposal(
    *,
    timestamp: str,
    oracle_persistent_sandbox_secret_store_stub_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Build an operator gate proposal without authorizing a sandbox probe."""

    base: dict[str, Any] = {
        "schema_version": "OracleSandboxProbeGateProposal.v1",
        "proposal_id": canonical_hash(
            {
                "record": "oracle_sandbox_probe_gate_proposal",
                "issue": ISSUE_881_TITLE,
                "stub_receipt": oracle_persistent_sandbox_secret_store_stub_receipt[
                    "canonical_hash"
                ],
                "pr_884_merge_sha": PR_884_MERGE_SHA,
            }
        ),
        "proposal_status": "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "pr_884_merge_sha": PR_884_MERGE_SHA,
            "oracle_persistent_sandbox_secret_store_stub_receipt": (
                oracle_persistent_sandbox_secret_store_stub_receipt["canonical_hash"]
            ),
            "schema_validation_receipt": SCHEMA_VALIDATION_RECEIPT_HASH,
        },
        "operator_gate_template": {
            "required_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "attestation_note_required": True,
            "authorizes_probe_execution": False,
            "records_operator_attestation": False,
            "brier_score": 0.1,
        },
        "pre_probe_checklist": [
            _check("external secret reference configured outside git"),
            _check("runtime receipt emitted immediately before any future probe"),
            _check("logs routed to ignored local path with redaction review"),
            _check("rollback steps rehearsed without external calls"),
            _check("operator confirms no endpoint values in Notion or GitHub"),
        ],
        "probe_dry_run_plan": {
            "plan_status": "PROPOSAL_ONLY_NO_PROBE_EXECUTION",
            "external_calls_allowed_by_this_proposal": False,
            "scheduler_enabled_by_this_proposal": False,
            "queue_enabled_by_this_proposal": False,
            "payload_persistence_enabled_by_this_proposal": False,
            "telemetry_writeback_enabled_by_this_proposal": False,
            "required_future_command_shape": (
                "Scripts/abx_loop.py --emit-oracle-full-live-runtime-execution "
                "--oracle-full-live-execute --oracle-full-live-operator-attestation "
                "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED --validate-oracle-schemas"
            ),
            "command_shape_is_authorized_now": False,
            "brier_score": 0.1,
        },
        "rollback_plan": {
            "rollback_status": "OPERATOR_REVIEW_STUB_READY",
            "rollback_steps": [
                "Unset external endpoint references outside git.",
                "Delete ignored local probe log if it contains sensitive material.",
                "Re-emit blocked/no-call receipt to prove default state.",
                "Append manual Notion closeout only after operator review.",
            ],
            "rollback_execution_authorized": False,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_sandbox_probe_gate_proposal"),
        "authority_locks": _authority_locks(),
        "valid_for_sandbox_probe_execution": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_secret_material_persistence": False,
        "valid_for_payload_persistence": False,
        "valid_for_telemetry_writeback": False,
        "valid_for_mcp_exposure": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_sandbox_probe_gate_proposal_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_sandbox_probe_gate_proposal: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleSandboxProbeGateProposalReceipt.v1",
        "receipt_id": "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_RECEIPT_001",
        "receipt_status": "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "issue": {
            "issue_number": 881,
            "issue_title": ISSUE_881_TITLE,
            "brier_score": 0.1,
        },
        "surface_hashes": {
            "oracle_sandbox_probe_gate_proposal": (
                oracle_sandbox_probe_gate_proposal["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "gate_summary": {
            "required_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "probe_authorized_by_receipt": False,
            "external_calls_authorized_by_receipt": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Operator may review this gate proposal and issue a separate explicit "
            "sandbox probe gate before any probe command is run."
        ),
        "provenance": _provenance("oracle_sandbox_probe_gate_proposal_receipt"),
        "authority_locks": _authority_locks(),
        "valid_for_sandbox_probe_execution": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_scheduler_queue_runtime": False,
        "valid_for_secret_material_persistence": False,
        "valid_for_payload_persistence": False,
        "valid_for_telemetry_writeback": False,
        "valid_for_mcp_exposure": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _check(description: str) -> dict[str, Any]:
    return {
        "description": description,
        "required_before_future_probe": True,
        "completed_by_this_proposal": False,
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
        "sandbox_probe_execution": False,
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
        "parent_pr": "PR #884",
        "parent_merge_sha": PR_884_MERGE_SHA,
        "parent_receipt_hash": PERSISTENT_SANDBOX_SECRET_STORE_STUB_HASH,
        "schema_validation_receipt_hash": SCHEMA_VALIDATION_RECEIPT_HASH,
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
