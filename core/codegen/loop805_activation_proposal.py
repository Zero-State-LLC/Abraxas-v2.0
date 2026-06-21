from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID


LOOP_805_ACTIVATION_PROPOSAL_SCHEMA_VERSION = "AbxLoop805ActivationProposal.v1"


ACTIVATION_GATES: tuple[dict[str, Any], ...] = (
    {
        "gate_id": "GATE_1_LIVE_MCP_EXPOSURE_REVIEW",
        "target_capability": "read_only_mcp_exposure",
        "current_status": "STUB_READY_NOT_LIVE",
        "required_attestation": "Operator confirms read-only MCP exposure scope.",
        "activation_authorized": False,
        "brier_score": 0.1,
    },
    {
        "gate_id": "GATE_2_HELD_OUT_BRIER_BOUNDING_REVIEW",
        "target_capability": "held_out_brier_measurement",
        "current_status": "STATIC_FIXTURE_READY_NOT_RESOLVING",
        "required_attestation": "Operator binds held-out set and outcome policy.",
        "activation_authorized": False,
        "brier_score": 0.11,
    },
    {
        "gate_id": "GATE_3_TOKEN_OPTIMIZER_ENFORCEMENT_REVIEW",
        "target_capability": "token_optimizer_ci_gate",
        "current_status": "ADVISORY_MATH_READY_NOT_ENFORCED",
        "required_attestation": "Operator approves token optimizer as review gate only.",
        "activation_authorized": False,
        "brier_score": 0.1,
    },
    {
        "gate_id": "GATE_4_SELF_PR_WRITEBACK_REVIEW",
        "target_capability": "self_generated_pr_proposal_writeback",
        "current_status": "PROPOSAL_TEMPLATE_READY_NOT_WRITING",
        "required_attestation": "Operator grants explicit scoped GitHub writeback.",
        "activation_authorized": False,
        "brier_score": 0.12,
    },
)


def build_loop805_activation_proposal(
    *,
    timestamp: str,
    slice2_receipt_hashes: Mapping[str, str],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_805_ACTIVATION_PROPOSAL_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "proposal_id": "ABX_LOOP805_SLICE3_ACTIVATION_PROPOSAL",
        "proposal_status": "SLICE3_FULL_ACTIVATION_PROPOSAL_READY_OPERATOR_GATE_REQUIRED",
        "timestamp": timestamp,
        "slice2_receipt_hashes": dict(slice2_receipt_hashes),
        "activation_gates": [dict(gate) for gate in ACTIVATION_GATES],
        "operator_gate": {
            "required": True,
            "exact_confirmation": "yes",
            "attestation_note_required": True,
            "approval_template": (
                "I approve reviewing Loop 805 Slice 3 activation gates. "
                "This does not authorize live MCP, Brier resolution, token "
                "enforcement, runtime activation, or GitHub/Notion writeback."
            ),
            "brier_score": 0.09,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_brier_resolution": False,
        "valid_for_ci_enforcement": False,
        "valid_for_token_rewrite": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice3_prompt_packet(
    *,
    timestamp: str,
    activation_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 3 activation proposal.",
            "- All locks remain explicitly false until operator attestation.",
            "",
            "EVIDENCE PACKET",
            "- Slice 2 MCP/Brier/token/self-PR stubs are merged and receipt-backed.",
            f"- Activation proposal hash: {activation_proposal['canonical_hash']}",
            "",
            "TASK",
            "- Review live MCP, held-out Brier, token optimizer, and self-PR gates.",
            "- Do not activate any gate without exact operator approval.",
            "",
            "OUTPUT",
            "- Operator decision matrix for each gate.",
            "- Updated receipts only after explicit attestation.",
            "",
            "VALIDATION",
            "- Confirm all authority locks remain false before approval.",
            "- Confirm no GitHub, Notion, runtime, token rewrite, or MCP side effect.",
            "",
            "RESIDUAL RISKS",
            "- Activation remains impossible without external operator authority.",
            "- Held-out Brier quality depends on the future attested fixture set.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Operator reviews Slice 3 gates and chooses exactly one scoped gate.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_ACTIVATION_PROPOSAL_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE3_PROMPT_PACKET",
        "packet_status": "SLICE3_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "activation_proposal_hash": activation_proposal["canonical_hash"],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
