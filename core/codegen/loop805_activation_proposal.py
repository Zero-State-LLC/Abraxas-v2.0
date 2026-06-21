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


def build_loop805_gate_selection_matrix(
    *,
    timestamp: str,
    activation_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    ranked_gates = [
        {
            "rank": 1,
            "gate_id": "GATE_2_HELD_OUT_BRIER_BOUNDING_REVIEW",
            "recommended_next": "PREPARE_HELD_OUT_SET_ATTESTATION_PACKET",
            "reason": (
                "Held-out Brier measurement is the highest evidence-value gate "
                "because it can prove forecast-quality uplift without runtime or "
                "writeback authority."
            ),
            "requires_operator_attestation": True,
            "activation_authorized": False,
            "brier_score": 0.09,
        },
        {
            "rank": 2,
            "gate_id": "GATE_3_TOKEN_OPTIMIZER_ENFORCEMENT_REVIEW",
            "recommended_next": "PREPARE_NON_ENFORCING_CI_SHADOW_CHECK",
            "reason": (
                "Token optimizer enforcement should remain shadow-only until the "
                "Brier gate proves the measurement loop is stable."
            ),
            "requires_operator_attestation": True,
            "activation_authorized": False,
            "brier_score": 0.1,
        },
        {
            "rank": 3,
            "gate_id": "GATE_1_LIVE_MCP_EXPOSURE_REVIEW",
            "recommended_next": "PREPARE_LOCAL_READ_ONLY_MCP_DRYRUN_ONLY",
            "reason": (
                "MCP exposure has high leverage but should follow evidence and "
                "token gates to avoid widening the live surface prematurely."
            ),
            "requires_operator_attestation": True,
            "activation_authorized": False,
            "brier_score": 0.11,
        },
        {
            "rank": 4,
            "gate_id": "GATE_4_SELF_PR_WRITEBACK_REVIEW",
            "recommended_next": "DEFER_UNTIL_ALL_OTHER_GATES_ARE_STABLE",
            "reason": (
                "Self-PR writeback carries the most governance surface area and "
                "should stay proposal-only until the loop proves reliable."
            ),
            "requires_operator_attestation": True,
            "activation_authorized": False,
            "brier_score": 0.12,
        },
    ]
    base: dict[str, Any] = {
        "schema_version": LOOP_805_ACTIVATION_PROPOSAL_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "matrix_id": "ABX_LOOP805_SLICE4_GATE_SELECTION_MATRIX",
        "matrix_status": "SLICE4_GATE_SELECTION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "activation_proposal_hash": activation_proposal["canonical_hash"],
        "ranked_gates": ranked_gates,
        "selected_gate": None,
        "selection_authorized": False,
        "operator_gate": {
            "required": True,
            "attestation_note_required": True,
            "approval_template": (
                "I select one Loop 805 gate for the next advisory packet. "
                "This selection does not authorize activation or writeback."
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


def build_loop805_slice4_prompt_packet(
    *,
    timestamp: str,
    gate_selection_matrix: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 4 gate selection.",
            "- Selecting a gate does not activate that gate.",
            "",
            "EVIDENCE PACKET",
            f"- Gate selection matrix hash: {gate_selection_matrix['canonical_hash']}",
            "- Slice 3 activation proposal is merged and receipt-backed.",
            "",
            "TASK",
            "- Pick exactly one next gate for advisory packet preparation.",
            "- Recommended first gate: held-out Brier bounding review.",
            "",
            "OUTPUT",
            "- One selected gate ID.",
            "- Operator attestation note.",
            "- No runtime, MCP, Brier, token, GitHub, or Notion side effect.",
            "",
            "VALIDATION",
            "- Confirm selection_authorized remains false in repo receipts.",
            "- Confirm selected gate is used only for the next planning packet.",
            "",
            "RESIDUAL RISKS",
            "- Activation remains blocked until a later explicit approval packet.",
            "- Self-PR writeback should remain deferred until all other gates pass.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 5 held-out Brier attestation packet if operator agrees.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_ACTIVATION_PROPOSAL_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE4_PROMPT_PACKET",
        "packet_status": "SLICE4_GATE_SELECTION_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "gate_selection_matrix_hash": gate_selection_matrix["canonical_hash"],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
