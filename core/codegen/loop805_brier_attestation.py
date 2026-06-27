from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID


LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION = "AbxLoop805BrierAttestation.v1"


DEFAULT_HELD_OUT_SET_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "requirement_id": "HELD_OUT_SET_ID",
        "description": "Operator names the held-out forecast set before scoring.",
        "satisfied": False,
        "brier_score": 0.08,
    },
    {
        "requirement_id": "OUTCOME_POLICY",
        "description": "Operator defines when and how outcomes may be bound.",
        "satisfied": False,
        "brier_score": 0.09,
    },
    {
        "requirement_id": "LEAKAGE_BOUNDARY",
        "description": "Operator confirms training/evidence leakage is excluded.",
        "satisfied": False,
        "brier_score": 0.1,
    },
    {
        "requirement_id": "SCORING_WINDOW",
        "description": "Operator defines forecast close and scoring timestamps.",
        "satisfied": False,
        "brier_score": 0.1,
    },
)


def build_loop805_brier_attestation_packet(
    *,
    timestamp: str,
    gate_selection_matrix: Mapping[str, Any],
    requirements: Sequence[Mapping[str, Any]] = DEFAULT_HELD_OUT_SET_REQUIREMENTS,
) -> dict[str, Any]:
    normalized_requirements = [_normalize_requirement(item) for item in requirements]
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE5_HELD_OUT_BRIER_ATTESTATION",
        "packet_status": "SLICE5_HELD_OUT_BRIER_ATTESTATION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "gate_selection_matrix_hash": gate_selection_matrix["canonical_hash"],
        "target_gate": "GATE_2_HELD_OUT_BRIER_BOUNDING_REVIEW",
        "held_out_set_requirements": normalized_requirements,
        "operator_attestation": {
            "required": True,
            "exact_confirmation": "yes",
            "attestation_note_required": True,
            "attestation_recorded": False,
            "approval_template": (
                "I attest the held-out forecast set, outcome policy, leakage "
                "boundary, and scoring window are ready for advisory Brier "
                "measurement review. This does not authorize Brier resolution."
            ),
            "brier_score": 0.09,
        },
        "scoring_authority": {
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "mode": "ATTESTATION_PACKET_ONLY",
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice5_prompt_packet(
    *,
    timestamp: str,
    brier_attestation_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 5 held-out Brier attestation.",
            "- This packet does not bind outcomes or resolve Brier scores.",
            "",
            "EVIDENCE PACKET",
            f"- Attestation packet hash: {brier_attestation_packet['canonical_hash']}",
            "- Slice 4 recommended held-out Brier as the first future gate.",
            "",
            "TASK",
            "- Review held-out set ID, outcome policy, leakage boundary, and scoring window.",
            "- Record operator attestation only in a future approval packet.",
            "",
            "OUTPUT",
            "- Attestation readiness decision.",
            "- List of missing held-out set requirements, if any.",
            "- No scoring, outcome binding, routing, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_brier_resolution remains false.",
            "- Confirm scoring_authority denies fixture and outcome binding.",
            "",
            "RESIDUAL RISKS",
            "- Real Brier uplift remains unproven until operator binds a held-out set.",
            "- Outcome timing and leakage boundaries require human review.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- If approved later, prepare Slice 6 held-out fixture binding dry run.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE5_PROMPT_PACKET",
        "packet_status": "SLICE5_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "brier_attestation_packet_hash": brier_attestation_packet["canonical_hash"],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_fixture_binding_dryrun(
    *,
    timestamp: str,
    brier_attestation_packet: Mapping[str, Any],
    fixture_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_rows = [_normalize_fixture_row(row) for row in fixture_rows]
    if not normalized_rows:
        raise ValueError("fixture binding dry run requires at least one fixture row")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "dryrun_id": "ABX_LOOP805_SLICE6_HELD_OUT_FIXTURE_BINDING_DRYRUN",
        "dryrun_status": "SLICE6_FIXTURE_BINDING_DRYRUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "brier_attestation_packet_hash": brier_attestation_packet["canonical_hash"],
        "fixture_rows": normalized_rows,
        "fixture_row_count": len(normalized_rows),
        "binding_mode": "DRYRUN_SHAPE_ONLY",
        "binding_authority": {
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice6_prompt_packet(
    *,
    timestamp: str,
    fixture_binding_dryrun: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 6 held-out fixture binding dry run.",
            "- This packet validates fixture shape only; it does not bind fixtures.",
            "",
            "EVIDENCE PACKET",
            f"- Fixture dry-run hash: {fixture_binding_dryrun['canonical_hash']}",
            "- Slice 5 defined held-out set attestation requirements.",
            "",
            "TASK",
            "- Review fixture row schema and provenance fields.",
            "- Confirm fixture rows remain dry-run-only placeholders.",
            "",
            "OUTPUT",
            "- Fixture shape review decision.",
            "- Missing row fields or provenance blockers.",
            "- No outcome binding, forecast routing, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_fixture_binding remains false.",
            "- Confirm valid_for_outcome_binding remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains unproven until attested data is bound.",
            "- Leakage and outcome policies still require operator approval.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 7 Brier scoring shadow-run packet after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE6_PROMPT_PACKET",
        "packet_status": "SLICE6_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "fixture_binding_dryrun_hash": fixture_binding_dryrun["canonical_hash"],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_brier_scoring_shadow_run(
    *,
    timestamp: str,
    fixture_binding_dryrun: Mapping[str, Any],
    shadow_outcomes: Mapping[str, int],
) -> dict[str, Any]:
    shadow_rows = [
        _build_shadow_scoring_row(row, shadow_outcomes)
        for row in fixture_binding_dryrun["fixture_rows"]
    ]
    if not shadow_rows:
        raise ValueError("Brier scoring shadow run requires at least one row")
    mean_shadow_brier = round(
        sum(float(row["shadow_brier_component"]) for row in shadow_rows)
        / len(shadow_rows),
        6,
    )
    missing_outcomes = [
        row["forecast_id"]
        for row in fixture_binding_dryrun["fixture_rows"]
        if row["forecast_id"] not in shadow_outcomes
    ]
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "shadow_run_id": "ABX_LOOP805_SLICE7_BRIER_SCORING_SHADOW_RUN",
        "shadow_run_status": "SLICE7_BRIER_SCORING_SHADOW_RUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "fixture_binding_dryrun_hash": fixture_binding_dryrun["canonical_hash"],
        "shadow_rows": shadow_rows,
        "shadow_row_count": len(shadow_rows),
        "missing_shadow_outcomes": missing_outcomes,
        "mean_shadow_brier_score": mean_shadow_brier,
        "scoring_mode": "SHADOW_REHEARSAL_ONLY",
        "shadow_scoring_authority": {
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice7_prompt_packet(
    *,
    timestamp: str,
    brier_scoring_shadow_run: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 7 Brier scoring shadow run.",
            "- This packet rehearses scoring math only; it does not resolve Brier.",
            "",
            "EVIDENCE PACKET",
            f"- Shadow-run hash: {brier_scoring_shadow_run['canonical_hash']}",
            "- Slice 6 validated fixture row shape without binding fixtures.",
            "",
            "TASK",
            "- Review shadow Brier math, missing outcomes, and provenance shape.",
            "- Confirm shadow outcomes are rehearsal-only and not bound outcomes.",
            "",
            "OUTPUT",
            "- Shadow scoring review decision.",
            "- Mean shadow Brier score for rehearsal only.",
            "- No fixture binding, outcome binding, routing, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_brier_resolution remains false.",
            "- Confirm valid_for_outcome_binding remains false.",
            "- Confirm shadow_scoring_authority denies resolution.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains unproven until outcomes are attested.",
            "- Shadow outcomes can validate arithmetic but not forecast quality.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 8 outcome policy review packet after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE7_PROMPT_PACKET",
        "packet_status": "SLICE7_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "brier_scoring_shadow_run_hash": brier_scoring_shadow_run["canonical_hash"],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_outcome_policy_review_packet(
    *,
    timestamp: str,
    brier_scoring_shadow_run: Mapping[str, Any],
    policy_requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_requirements = [
        _normalize_outcome_policy_requirement(item) for item in policy_requirements
    ]
    if not normalized_requirements:
        raise ValueError("outcome policy review requires at least one requirement")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE8_OUTCOME_POLICY_REVIEW",
        "packet_status": "SLICE8_OUTCOME_POLICY_REVIEW_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "brier_scoring_shadow_run_hash": brier_scoring_shadow_run["canonical_hash"],
        "policy_requirements": normalized_requirements,
        "policy_requirement_count": len(normalized_requirements),
        "review_mode": "OUTCOME_POLICY_REVIEW_ONLY",
        "operator_attestation": {
            "required": True,
            "exact_confirmation": "yes",
            "attestation_note_required": True,
            "attestation_recorded": False,
            "approval_template": (
                "I approve reviewing the Loop 805 outcome policy requirements. "
                "This does not bind outcomes or authorize Brier resolution."
            ),
            "brier_score": 0.09,
        },
        "policy_authority": {
            "outcome_policy_binding_allowed": False,
            "outcome_binding_allowed": False,
            "fixture_binding_allowed": False,
            "brier_resolution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice8_prompt_packet(
    *,
    timestamp: str,
    outcome_policy_review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 8 outcome policy review.",
            "- This packet reviews outcome policy requirements only; it binds nothing.",
            "",
            "EVIDENCE PACKET",
            f"- Outcome policy review hash: {outcome_policy_review_packet['canonical_hash']}",
            "- Slice 7 rehearsed Brier scoring math without resolving Brier.",
            "",
            "TASK",
            "- Review close timestamps, source of truth, conflict rules, and leakage checks.",
            "- Confirm all policy requirements remain not satisfied in repo receipts.",
            "",
            "OUTPUT",
            "- Outcome policy review decision.",
            "- Missing policy requirement list.",
            "- No outcome binding, forecast routing, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_outcome_policy_binding remains false.",
            "- Confirm valid_for_outcome_binding remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Outcome policy quality remains unproven until operator attestation.",
            "- Real Brier measurement remains blocked until outcomes are bound later.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 9 held-out set lockfile proposal after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE8_PROMPT_PACKET",
        "packet_status": "SLICE8_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "outcome_policy_review_hash": outcome_policy_review_packet["canonical_hash"],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_held_out_set_lockfile_proposal(
    *,
    timestamp: str,
    outcome_policy_review_packet: Mapping[str, Any],
    held_out_set_id: str,
    forecast_ids: Sequence[str],
) -> dict[str, Any]:
    normalized_forecast_ids = [str(item) for item in forecast_ids]
    if not held_out_set_id:
        raise ValueError("held-out set lockfile proposal requires a set id")
    if not normalized_forecast_ids:
        raise ValueError("held-out set lockfile proposal requires forecast ids")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "proposal_id": "ABX_LOOP805_SLICE9_HELD_OUT_SET_LOCKFILE_PROPOSAL",
        "proposal_status": "SLICE9_HELD_OUT_SET_LOCKFILE_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "outcome_policy_review_hash": outcome_policy_review_packet["canonical_hash"],
        "held_out_set_id": held_out_set_id,
        "forecast_ids": normalized_forecast_ids,
        "forecast_count": len(normalized_forecast_ids),
        "lockfile_mode": "PROPOSAL_ONLY_NOT_LOCKED",
        "lockfile_authority": {
            "held_out_set_lock_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_policy_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "operator_attestation": {
            "required": True,
            "exact_confirmation": "yes",
            "attestation_note_required": True,
            "attestation_recorded": False,
            "approval_template": (
                "I approve reviewing the proposed Loop 805 held-out set lockfile. "
                "This does not lock the set, bind fixtures, bind outcomes, or "
                "authorize Brier resolution."
            ),
            "brier_score": 0.09,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice9_prompt_packet(
    *,
    timestamp: str,
    held_out_set_lockfile_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 9 held-out set lockfile proposal.",
            "- This packet proposes a lockfile only; it does not lock the set.",
            "",
            "EVIDENCE PACKET",
            f"- Lockfile proposal hash: {held_out_set_lockfile_proposal['canonical_hash']}",
            "- Slice 8 reviewed outcome policy requirements without binding outcomes.",
            "",
            "TASK",
            "- Review proposed held-out set ID and forecast IDs.",
            "- Confirm the proposal remains not locked and not bound.",
            "",
            "OUTPUT",
            "- Held-out set lockfile review decision.",
            "- Missing forecast IDs or provenance blockers.",
            "- No held-out set lock, fixture binding, outcome binding, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_held_out_set_lock remains false.",
            "- Confirm valid_for_fixture_binding remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Forecast IDs are still proposed and not authoritative.",
            "- Real held-out measurement remains blocked until the set is attested later.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 10 held-out set attestation gate after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE9_PROMPT_PACKET",
        "packet_status": "SLICE9_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "held_out_set_lockfile_proposal_hash": held_out_set_lockfile_proposal[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_held_out_set_attestation_gate(
    *,
    timestamp: str,
    held_out_set_lockfile_proposal: Mapping[str, Any],
    attestation_requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_requirements = [
        _normalize_held_out_attestation_requirement(item)
        for item in attestation_requirements
    ]
    if not normalized_requirements:
        raise ValueError("held-out set attestation gate requires at least one item")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "gate_id": "ABX_LOOP805_SLICE10_HELD_OUT_SET_ATTESTATION_GATE",
        "gate_status": "SLICE10_HELD_OUT_SET_ATTESTATION_GATE_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "held_out_set_lockfile_proposal_hash": held_out_set_lockfile_proposal[
            "canonical_hash"
        ],
        "held_out_set_id": held_out_set_lockfile_proposal["held_out_set_id"],
        "forecast_count": held_out_set_lockfile_proposal["forecast_count"],
        "attestation_requirements": normalized_requirements,
        "attestation_requirement_count": len(normalized_requirements),
        "attestation_mode": "GATE_REVIEW_ONLY_NOT_ATTESTED",
        "operator_gate": {
            "required": True,
            "exact_confirmation": "yes",
            "attestation_note_required": True,
            "attestation_recorded": False,
            "approval_template": (
                "I approve reviewing the Loop 805 held-out set attestation gate. "
                "This does not attest, lock, bind, route, score, or resolve Brier."
            ),
            "brier_score": 0.09,
        },
        "gate_authority": {
            "held_out_set_attestation_allowed": False,
            "held_out_set_lock_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_policy_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice10_prompt_packet(
    *,
    timestamp: str,
    held_out_set_attestation_gate: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 10 held-out set attestation gate.",
            "- This packet reviews attestation readiness only; it does not attest.",
            "",
            "EVIDENCE PACKET",
            f"- Attestation gate hash: {held_out_set_attestation_gate['canonical_hash']}",
            "- Slice 9 proposed a held-out set lockfile without locking the set.",
            "",
            "TASK",
            "- Review held-out set attestation requirements.",
            "- Confirm all requirements remain unsatisfied until operator evidence exists.",
            "",
            "OUTPUT",
            "- Held-out set attestation gate review decision.",
            "- Missing attestation evidence list.",
            "- No held-out set lock, fixture binding, outcome binding, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_held_out_set_attestation remains false.",
            "- Confirm valid_for_held_out_set_lock remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains blocked until attestation is recorded later.",
            "- Forecast quality remains unproven without bound outcomes.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 11 measurement readiness review after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE10_PROMPT_PACKET",
        "packet_status": "SLICE10_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "held_out_set_attestation_gate_hash": held_out_set_attestation_gate[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_readiness_review(
    *,
    timestamp: str,
    held_out_set_attestation_gate: Mapping[str, Any],
    readiness_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_measurement_readiness_check(item) for item in readiness_checks
    ]
    if not normalized_checks:
        raise ValueError("measurement readiness review requires at least one check")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE11_MEASUREMENT_READINESS_REVIEW",
        "review_status": "SLICE11_MEASUREMENT_READINESS_REVIEW_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "held_out_set_attestation_gate_hash": held_out_set_attestation_gate[
            "canonical_hash"
        ],
        "held_out_set_id": held_out_set_attestation_gate["held_out_set_id"],
        "readiness_checks": normalized_checks,
        "readiness_check_count": len(normalized_checks),
        "measurement_mode": "READINESS_REVIEW_ONLY_NOT_MEASURING",
        "measurement_authority": {
            "measurement_allowed": False,
            "held_out_set_attestation_allowed": False,
            "held_out_set_lock_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice11_prompt_packet(
    *,
    timestamp: str,
    measurement_readiness_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 11 measurement readiness review.",
            "- This packet reviews readiness only; it does not measure or resolve Brier.",
            "",
            "EVIDENCE PACKET",
            f"- Measurement readiness hash: {measurement_readiness_review['canonical_hash']}",
            "- Slice 10 prepared held-out set attestation gate without attesting.",
            "",
            "TASK",
            "- Review measurement prerequisites and unresolved blockers.",
            "- Confirm all readiness checks remain unsatisfied in repo receipts.",
            "",
            "OUTPUT",
            "- Measurement readiness review decision.",
            "- Missing readiness evidence list.",
            "- No measurement, routing, fixture binding, outcome binding, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement remains false.",
            "- Confirm valid_for_outcome_binding remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains unproven until all gates are attested.",
            "- Brier uplift remains hypothetical until outcomes are bound later.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 12 measurement authorization proposal after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE11_PROMPT_PACKET",
        "packet_status": "SLICE11_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_readiness_review_hash": measurement_readiness_review[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_authorization_proposal(
    *,
    timestamp: str,
    measurement_readiness_review: Mapping[str, Any],
    authorization_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_authorization_item(item)
        for item in authorization_items
    ]
    if not normalized_items:
        raise ValueError("measurement authorization proposal requires at least one item")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "proposal_id": "ABX_LOOP805_SLICE12_MEASUREMENT_AUTHORIZATION_PROPOSAL",
        "proposal_status": "SLICE12_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_readiness_review_hash": measurement_readiness_review[
            "canonical_hash"
        ],
        "held_out_set_id": measurement_readiness_review["held_out_set_id"],
        "authorization_items": normalized_items,
        "authorization_item_count": len(normalized_items),
        "proposal_mode": "AUTHORIZATION_PROPOSAL_ONLY_NOT_AUTHORIZED",
        "operator_gate": {
            "required": True,
            "exact_confirmation": "yes",
            "attestation_note_required": True,
            "attestation_recorded": False,
            "approval_template": (
                "I approve reviewing the Loop 805 measurement authorization "
                "proposal. This does not authorize measurement, bind fixtures, "
                "bind outcomes, route forecasts, or resolve Brier."
            ),
            "brier_score": 0.09,
        },
        "authorization_authority": {
            "measurement_authorization_allowed": False,
            "measurement_allowed": False,
            "held_out_set_attestation_allowed": False,
            "held_out_set_lock_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_policy_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_held_out_set_attestation": False,
        "valid_for_held_out_set_lock": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice12_prompt_packet(
    *,
    timestamp: str,
    measurement_authorization_proposal: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 12 measurement authorization proposal.",
            "- This packet proposes an operator gate only; it does not authorize measurement.",
            "",
            "EVIDENCE PACKET",
            f"- Measurement authorization proposal hash: {measurement_authorization_proposal['canonical_hash']}",
            "- Slice 11 reviewed measurement readiness without measuring or resolving Brier.",
            "",
            "TASK",
            "- Review proposed authorization items and unresolved operator gates.",
            "- Confirm the proposal remains not authorized in repo receipts.",
            "",
            "OUTPUT",
            "- Measurement authorization proposal review decision.",
            "- Missing attestation or binding evidence list.",
            "- No measurement, fixture binding, outcome binding, routing, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_authorization remains false.",
            "- Confirm valid_for_measurement remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains blocked until operator authorization exists.",
            "- Bound outcomes and Brier resolution remain future-gated.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 13 authorization evidence packet after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE12_PROMPT_PACKET",
        "packet_status": "SLICE12_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_authorization_proposal_hash": (
            measurement_authorization_proposal["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_authorization_evidence_packet(
    *,
    timestamp: str,
    measurement_authorization_proposal: Mapping[str, Any],
    evidence_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_authorization_evidence_item(item) for item in evidence_items
    ]
    if not normalized_items:
        raise ValueError("authorization evidence packet requires at least one item")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE13_AUTHORIZATION_EVIDENCE_PACKET",
        "packet_status": "SLICE13_AUTHORIZATION_EVIDENCE_PACKET_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_authorization_proposal_hash": (
            measurement_authorization_proposal["canonical_hash"]
        ),
        "held_out_set_id": measurement_authorization_proposal["held_out_set_id"],
        "evidence_items": normalized_items,
        "evidence_item_count": len(normalized_items),
        "evidence_mode": "EVIDENCE_PACKET_SHAPE_ONLY_NOT_RECORDED",
        "evidence_authority": {
            "authorization_evidence_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_authorization_allowed": False,
            "measurement_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_authorization_evidence_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice13_prompt_packet(
    *,
    timestamp: str,
    authorization_evidence_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 13 authorization evidence packet.",
            "- This packet validates evidence shape only; it does not record evidence.",
            "",
            "EVIDENCE PACKET",
            f"- Authorization evidence packet hash: {authorization_evidence_packet['canonical_hash']}",
            "- Slice 12 proposed measurement authorization without granting it.",
            "",
            "TASK",
            "- Review required authorization evidence fields and missing evidence.",
            "- Confirm every evidence item remains unrecorded and unattested.",
            "",
            "OUTPUT",
            "- Authorization evidence packet review decision.",
            "- Missing authorization evidence list.",
            "- No evidence recording, measurement authorization, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_authorization_evidence_recording remains false.",
            "- Confirm valid_for_measurement_authorization remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Measurement remains blocked until external operator evidence is recorded.",
            "- Evidence shape can be reviewed, but no repo receipt is an attestation.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 14 fixture/outcome binding authorization review after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE13_PROMPT_PACKET",
        "packet_status": "SLICE13_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "authorization_evidence_packet_hash": authorization_evidence_packet[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_authorization_evidence_recording": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_fixture_outcome_binding_review(
    *,
    timestamp: str,
    authorization_evidence_packet: Mapping[str, Any],
    binding_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_fixture_outcome_binding_check(item) for item in binding_checks
    ]
    if not normalized_checks:
        raise ValueError("fixture/outcome binding review requires at least one check")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE14_FIXTURE_OUTCOME_BINDING_REVIEW",
        "review_status": "SLICE14_FIXTURE_OUTCOME_BINDING_REVIEW_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "authorization_evidence_packet_hash": authorization_evidence_packet[
            "canonical_hash"
        ],
        "held_out_set_id": authorization_evidence_packet["held_out_set_id"],
        "binding_checks": normalized_checks,
        "binding_check_count": len(normalized_checks),
        "review_mode": "FIXTURE_OUTCOME_BINDING_REVIEW_ONLY_NOT_BOUND",
        "binding_authority": {
            "fixture_binding_review_allowed": False,
            "outcome_binding_review_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_policy_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "measurement_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_fixture_binding_review": False,
        "valid_for_outcome_binding_review": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice14_prompt_packet(
    *,
    timestamp: str,
    fixture_outcome_binding_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 14 fixture/outcome binding review.",
            "- This packet reviews binding prerequisites only; it binds nothing.",
            "",
            "EVIDENCE PACKET",
            f"- Fixture/outcome binding review hash: {fixture_outcome_binding_review['canonical_hash']}",
            "- Slice 13 prepared authorization evidence shape without recording evidence.",
            "",
            "TASK",
            "- Review fixture binding and outcome binding prerequisites.",
            "- Confirm binding checks remain unsatisfied and unbound in repo receipts.",
            "",
            "OUTPUT",
            "- Fixture/outcome binding review decision.",
            "- Missing binding evidence and blocker list.",
            "- No fixture binding, outcome binding, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_fixture_binding remains false.",
            "- Confirm valid_for_outcome_binding remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains blocked until fixtures and outcomes are bound externally.",
            "- Review packets validate shape, not authority or factual outcomes.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 15 measurement dry-run authorization hold after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE14_PROMPT_PACKET",
        "packet_status": "SLICE14_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "fixture_outcome_binding_review_hash": fixture_outcome_binding_review[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_fixture_binding_review": False,
        "valid_for_outcome_binding_review": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_authorization_hold(
    *,
    timestamp: str,
    fixture_outcome_binding_review: Mapping[str, Any],
    hold_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_measurement_dryrun_authorization_hold_check(item)
        for item in hold_checks
    ]
    if not normalized_checks:
        raise ValueError(
            "measurement dry-run authorization hold requires at least one check"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "hold_id": "ABX_LOOP805_SLICE15_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD",
        "hold_status": (
            "SLICE15_MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "fixture_outcome_binding_review_hash": fixture_outcome_binding_review[
            "canonical_hash"
        ],
        "held_out_set_id": fixture_outcome_binding_review["held_out_set_id"],
        "hold_checks": normalized_checks,
        "hold_check_count": len(normalized_checks),
        "hold_mode": "MEASUREMENT_DRYRUN_AUTHORIZATION_HOLD_ONLY_NOT_AUTHORIZED",
        "authorization_authority": {
            "measurement_dryrun_authorization_hold_allowed": False,
            "measurement_dryrun_authorization_allowed": False,
            "measurement_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_policy_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_authorization_hold": False,
        "valid_for_measurement_dryrun_authorization": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice15_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_authorization_hold: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 15 measurement dry-run authorization hold.",
            "- This packet prepares a hold for operator review; it authorizes no dry-run measurement.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run authorization hold hash: "
                f"{measurement_dryrun_authorization_hold['canonical_hash']}"
            ),
            "- Slice 14 reviewed fixture/outcome binding prerequisites without binding anything.",
            "",
            "TASK",
            "- Review whether all prerequisites for a future measurement dry-run authorization are externally attested.",
            "- Confirm repo receipts still hold the line: no fixture binding, outcome binding, measurement, or Brier resolution.",
            "",
            "OUTPUT",
            "- Measurement dry-run authorization hold decision.",
            "- Missing operator evidence and unresolved blocker list.",
            "- No dry-run authorization, measurement execution, routing, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_authorization remains false.",
            "- Confirm valid_for_measurement remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real held-out measurement remains blocked until the operator separately authorizes a dry run.",
            "- This hold can stage review only; it cannot authorize or execute measurement.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 16 measurement dry-run preflight packet only after operator authorization evidence is recorded.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE15_PROMPT_PACKET",
        "packet_status": "SLICE15_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_authorization_hold_hash": (
            measurement_dryrun_authorization_hold["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_authorization_hold": False,
        "valid_for_measurement_dryrun_authorization": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_preflight_packet(
    *,
    timestamp: str,
    measurement_dryrun_authorization_hold: Mapping[str, Any],
    preflight_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_measurement_dryrun_preflight_check(item)
        for item in preflight_checks
    ]
    if not normalized_checks:
        raise ValueError("measurement dry-run preflight requires at least one check")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "preflight_id": "ABX_LOOP805_SLICE16_MEASUREMENT_DRYRUN_PREFLIGHT_PACKET",
        "preflight_status": (
            "SLICE16_MEASUREMENT_DRYRUN_PREFLIGHT_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_authorization_hold_hash": (
            measurement_dryrun_authorization_hold["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_authorization_hold["held_out_set_id"],
        "preflight_checks": normalized_checks,
        "preflight_check_count": len(normalized_checks),
        "preflight_mode": "PREFLIGHT_SHAPE_ONLY_NOT_EXECUTABLE",
        "preflight_authority": {
            "measurement_dryrun_preflight_allowed": False,
            "measurement_dryrun_authorization_allowed": False,
            "measurement_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_preflight": False,
        "valid_for_measurement_dryrun_authorization": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_policy_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice16_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_preflight_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 16 measurement dry-run preflight packet.",
            "- This packet validates preflight shape only; it cannot run measurement.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run preflight hash: "
                f"{measurement_dryrun_preflight_packet['canonical_hash']}"
            ),
            "- Slice 15 prepared a dry-run authorization hold without authorizing it.",
            "",
            "TASK",
            "- Review preflight blockers for a future measurement dry-run.",
            "- Confirm every preflight check remains unsatisfied and non-executable.",
            "",
            "OUTPUT",
            "- Measurement dry-run preflight review decision.",
            "- Missing preflight evidence and blocker list.",
            "- No measurement dry run, forecast routing, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_preflight remains false.",
            "- Confirm valid_for_measurement remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Dry-run execution remains blocked until a separate operator gate records authorization.",
            "- Preflight shape can reduce ambiguity but cannot prove held-out performance.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 17 measurement dry-run operator decision request only after preflight review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE16_PROMPT_PACKET",
        "packet_status": "SLICE16_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_preflight_packet_hash": (
            measurement_dryrun_preflight_packet["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_preflight": False,
        "valid_for_measurement_dryrun_authorization": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_decision_request(
    *,
    timestamp: str,
    measurement_dryrun_preflight_packet: Mapping[str, Any],
    decision_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_decision_item(item) for item in decision_items
    ]
    if not normalized_items:
        raise ValueError("measurement dry-run decision request requires one item")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "request_id": "ABX_LOOP805_SLICE17_MEASUREMENT_DRYRUN_DECISION_REQUEST",
        "request_status": (
            "SLICE17_MEASUREMENT_DRYRUN_DECISION_REQUEST_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_preflight_packet_hash": (
            measurement_dryrun_preflight_packet["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_preflight_packet["held_out_set_id"],
        "decision_items": normalized_items,
        "decision_item_count": len(normalized_items),
        "decision_mode": "OPERATOR_DECISION_REQUEST_ONLY_NOT_RECORDED",
        "decision_authority": {
            "measurement_dryrun_decision_request_allowed": False,
            "measurement_dryrun_decision_recording_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "measurement_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_request": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice17_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_decision_request: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 17 measurement dry-run decision request.",
            "- This packet requests a future operator decision; it records no decision and executes nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run decision request hash: "
                f"{measurement_dryrun_decision_request['canonical_hash']}"
            ),
            "- Slice 16 prepared a measurement dry-run preflight packet without executable authority.",
            "",
            "TASK",
            "- Review the dry-run decision request items and unresolved blockers.",
            "- Confirm no operator decision is recorded in this repo receipt.",
            "",
            "OUTPUT",
            "- Operator decision request packet for separate review.",
            "- Explicit go/no-go placeholders only.",
            "- No dry-run execution, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_decision_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator records a separate decision.",
            "- Decision request wording can prepare review but cannot authorize execution.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 18 measurement dry-run decision record template only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE17_PROMPT_PACKET",
        "packet_status": "SLICE17_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_decision_request_hash": (
            measurement_dryrun_decision_request["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_request": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_decision_record_template(
    *,
    timestamp: str,
    measurement_dryrun_decision_request: Mapping[str, Any],
    template_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_decision_record_template_item(item)
        for item in template_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run decision record template requires one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "template_id": (
            "ABX_LOOP805_SLICE18_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE"
        ),
        "template_status": (
            "SLICE18_MEASUREMENT_DRYRUN_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_decision_request_hash": (
            measurement_dryrun_decision_request["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_decision_request["held_out_set_id"],
        "template_items": normalized_items,
        "template_item_count": len(normalized_items),
        "template_mode": "DECISION_RECORD_TEMPLATE_ONLY_NOT_RECORDED",
        "decision_record_state": {
            "template_prepared": True,
            "decision_recorded": False,
            "operator_attested": False,
            "measurement_dryrun_authorized": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "decision_authority": {
            "measurement_dryrun_decision_record_template_allowed": False,
            "measurement_dryrun_decision_recording_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "measurement_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_record_template": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice18_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_decision_record_template: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 18 measurement dry-run decision record template.",
            "- This packet prepares an unfilled record template only; it records no decision and executes nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run decision record template hash: "
                f"{measurement_dryrun_decision_record_template['canonical_hash']}"
            ),
            "- Slice 17 requested a future operator decision without recording one.",
            "",
            "TASK",
            "- Review the unfilled decision record template fields.",
            "- Confirm the template is not an operator decision record.",
            "",
            "OUTPUT",
            "- Decision record template packet for future operator-only use.",
            "- Explicit field placeholders only.",
            "- No dry-run decision recording, execution, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_decision_record_template remains false.",
            "- Confirm valid_for_measurement_dryrun_decision_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator records a separate decision outside this template.",
            "- Template shape can reduce ambiguity but cannot authorize execution.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 19 measurement dry-run operator decision intake gate only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE18_PROMPT_PACKET",
        "packet_status": "SLICE18_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_decision_record_template_hash": (
            measurement_dryrun_decision_record_template["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_record_template": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_decision_intake_gate(
    *,
    timestamp: str,
    measurement_dryrun_decision_record_template: Mapping[str, Any],
    intake_requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_requirements = [
        _normalize_measurement_dryrun_operator_decision_intake_requirement(
            requirement
        )
        for requirement in intake_requirements
    ]
    if not normalized_requirements:
        raise ValueError(
            "measurement dry-run operator decision intake gate requires one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "gate_id": "ABX_LOOP805_SLICE19_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_GATE",
        "gate_status": (
            "SLICE19_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_GATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_decision_record_template_hash": (
            measurement_dryrun_decision_record_template["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_decision_record_template[
            "held_out_set_id"
        ],
        "intake_requirements": normalized_requirements,
        "intake_requirement_count": len(normalized_requirements),
        "intake_mode": "OPERATOR_DECISION_INTAKE_GATE_ONLY_NOT_OPENED",
        "intake_state": {
            "intake_gate_prepared": True,
            "operator_decision_intake_opened": False,
            "operator_decision_received": False,
            "operator_decision_recorded": False,
            "operator_attested": False,
            "measurement_dryrun_authorized": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "decision_authority": {
            "measurement_dryrun_operator_decision_intake_gate_allowed": False,
            "measurement_dryrun_operator_decision_intake_allowed": False,
            "measurement_dryrun_decision_recording_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "measurement_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_intake_gate": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice19_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_decision_intake_gate: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 19 measurement dry-run operator decision intake gate.",
            "- This packet prepares an intake gate only; it opens no intake, records no decision, and executes nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator decision intake gate hash: "
                f"{measurement_dryrun_operator_decision_intake_gate['canonical_hash']}"
            ),
            "- Slice 18 prepared an unfilled decision record template without recording a decision.",
            "",
            "TASK",
            "- Review the intake requirements before any future operator decision intake.",
            "- Confirm the gate is not a submitted decision, attestation, authorization, or execution record.",
            "",
            "OUTPUT",
            "- Operator decision intake gate packet for future review.",
            "- Explicit intake prerequisites only.",
            "- No intake opening, dry-run decision recording, execution, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_decision_intake_gate remains false.",
            "- Confirm valid_for_measurement_dryrun_operator_decision_intake remains false.",
            "- Confirm valid_for_measurement_dryrun_decision_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator separately opens intake and records a decision.",
            "- Intake gate shape can reduce operator ambiguity but cannot authorize execution.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 20 measurement dry-run operator decision intake packet only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE19_PROMPT_PACKET",
        "packet_status": "SLICE19_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_decision_intake_gate_hash": (
            measurement_dryrun_operator_decision_intake_gate["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_intake_gate": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_decision_intake_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_decision_intake_gate: Mapping[str, Any],
    intake_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_operator_decision_intake_item(item)
        for item in intake_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run operator decision intake packet requires one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "intake_packet_id": (
            "ABX_LOOP805_SLICE20_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_PACKET"
        ),
        "intake_packet_status": (
            "SLICE20_MEASUREMENT_DRYRUN_OPERATOR_DECISION_INTAKE_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_decision_intake_gate_hash": (
            measurement_dryrun_operator_decision_intake_gate["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_operator_decision_intake_gate[
            "held_out_set_id"
        ],
        "intake_items": normalized_items,
        "intake_item_count": len(normalized_items),
        "intake_packet_mode": "OPERATOR_DECISION_INTAKE_PACKET_ONLY_NOT_SUBMITTED",
        "intake_packet_state": {
            "intake_packet_prepared": True,
            "intake_opened": False,
            "intake_submitted": False,
            "decision_received": False,
            "decision_recorded": False,
            "operator_attested": False,
            "measurement_dryrun_authorized": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "decision_authority": {
            "measurement_dryrun_operator_decision_intake_packet_allowed": False,
            "measurement_dryrun_operator_decision_intake_allowed": False,
            "measurement_dryrun_decision_recording_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "measurement_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_intake_packet": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice20_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_decision_intake_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 20 measurement dry-run operator decision intake packet.",
            "- This packet prepares unsubmitted intake fields only; it records no decision and executes nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator decision intake packet hash: "
                f"{measurement_dryrun_operator_decision_intake_packet['canonical_hash']}"
            ),
            "- Slice 19 prepared an intake gate without opening intake.",
            "",
            "TASK",
            "- Review the operator decision intake packet fields.",
            "- Confirm the packet is not submitted, attested, recorded, or executable.",
            "",
            "OUTPUT",
            "- Operator decision intake packet for future operator-only review.",
            "- Explicit unsubmitted intake placeholders only.",
            "- No intake submission, dry-run decision recording, execution, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_decision_intake_packet remains false.",
            "- Confirm valid_for_measurement_dryrun_operator_decision_intake remains false.",
            "- Confirm valid_for_measurement_dryrun_decision_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator separately submits and records a decision.",
            "- Intake packet shape can prepare review but cannot authorize execution.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 21 measurement dry-run operator decision record candidate only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE20_PROMPT_PACKET",
        "packet_status": "SLICE20_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_decision_intake_packet_hash": (
            measurement_dryrun_operator_decision_intake_packet["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_intake_packet": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_decision_record_candidate(
    *,
    timestamp: str,
    measurement_dryrun_operator_decision_intake_packet: Mapping[str, Any],
    candidate_fields: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_fields = [
        _normalize_measurement_dryrun_operator_decision_record_candidate_field(
            field
        )
        for field in candidate_fields
    ]
    if not normalized_fields:
        raise ValueError(
            "measurement dry-run operator decision record candidate requires one field"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "candidate_id": (
            "ABX_LOOP805_SLICE21_MEASUREMENT_DRYRUN_OPERATOR_DECISION_RECORD_CANDIDATE"
        ),
        "candidate_status": (
            "SLICE21_MEASUREMENT_DRYRUN_OPERATOR_DECISION_RECORD_CANDIDATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_decision_intake_packet_hash": (
            measurement_dryrun_operator_decision_intake_packet["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_operator_decision_intake_packet[
            "held_out_set_id"
        ],
        "candidate_fields": normalized_fields,
        "candidate_field_count": len(normalized_fields),
        "candidate_mode": "OPERATOR_DECISION_RECORD_CANDIDATE_ONLY_NOT_RECORDED",
        "candidate_state": {
            "record_candidate_prepared": True,
            "intake_submitted": False,
            "decision_received": False,
            "decision_recorded": False,
            "operator_attested": False,
            "measurement_dryrun_authorized": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "decision_authority": {
            "measurement_dryrun_operator_decision_record_candidate_allowed": False,
            "measurement_dryrun_decision_recording_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "measurement_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_record_candidate": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice21_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_decision_record_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 21 measurement dry-run operator decision record candidate.",
            "- This packet prepares a candidate record only; it records no decision and executes nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator decision record candidate hash: "
                f"{measurement_dryrun_operator_decision_record_candidate['canonical_hash']}"
            ),
            "- Slice 20 prepared an unsubmitted decision intake packet.",
            "",
            "TASK",
            "- Review the operator decision record candidate fields.",
            "- Confirm the candidate is not a submitted decision, attestation, authorization, or execution record.",
            "",
            "OUTPUT",
            "- Operator decision record candidate for future operator-only review.",
            "- Explicit candidate placeholders only.",
            "- No dry-run decision recording, execution, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_decision_record_candidate remains false.",
            "- Confirm valid_for_measurement_dryrun_decision_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator separately records and attests a decision.",
            "- Record candidate shape can prepare review but cannot authorize execution.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 22 measurement dry-run decision record review packet only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE21_PROMPT_PACKET",
        "packet_status": "SLICE21_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_decision_record_candidate_hash": (
            measurement_dryrun_operator_decision_record_candidate["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_decision_record_candidate": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_decision_record_review(
    *,
    timestamp: str,
    measurement_dryrun_operator_decision_record_candidate: Mapping[str, Any],
    review_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_decision_record_review_item(item)
        for item in review_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run decision record review requires one review item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE22_MEASUREMENT_DRYRUN_DECISION_RECORD_REVIEW",
        "review_status": (
            "SLICE22_MEASUREMENT_DRYRUN_DECISION_RECORD_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_decision_record_candidate_hash": (
            measurement_dryrun_operator_decision_record_candidate["canonical_hash"]
        ),
        "held_out_set_id": measurement_dryrun_operator_decision_record_candidate[
            "held_out_set_id"
        ],
        "review_items": normalized_items,
        "review_item_count": len(normalized_items),
        "review_mode": "DECISION_RECORD_REVIEW_ONLY_NOT_RECORDED",
        "review_state": {
            "review_surface_prepared": True,
            "candidate_reviewed": False,
            "decision_recorded": False,
            "operator_attested": False,
            "measurement_dryrun_authorized": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "diff_preview_stub": {
            "enabled": False,
            "candidate_hash": measurement_dryrun_operator_decision_record_candidate[
                "canonical_hash"
            ],
            "preview_generated": False,
            "valid_for_decision_recording": False,
            "valid_for_measurement_dryrun_execution": False,
            "brier_score": 0.1,
        },
        "decision_authority": {
            "measurement_dryrun_decision_record_review_allowed": False,
            "measurement_dryrun_decision_recording_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "measurement_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_record_review": False,
        "valid_for_measurement_dryrun_operator_decision_record_candidate": False,
        "valid_for_measurement_dryrun_operator_decision_intake": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice22_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_decision_record_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 22 measurement dry-run decision record review.",
            "- This packet reviews a candidate record only; it records no decision and executes nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run decision record review hash: "
                f"{measurement_dryrun_decision_record_review['canonical_hash']}"
            ),
            "- Slice 21 prepared a decision record candidate that remains unrecorded.",
            "",
            "TASK",
            "- Review candidate completeness, diff-preview stubs, and recording boundaries.",
            "- Confirm the review is not a submitted decision, attestation, authorization, or execution record.",
            "",
            "OUTPUT",
            "- Decision record review packet for future operator-only review.",
            "- Explicit diff-preview stub and review checklist only.",
            "- No dry-run decision recording, held-out binding, execution, routing, measurement, or Brier resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_decision_record_review remains false.",
            "- Confirm valid_for_measurement_dryrun_decision_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator separately records and attests a decision.",
            "- Review shape can prepare operator inspection but cannot authorize execution.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 23 held-out set binding review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE22_PROMPT_PACKET",
        "packet_status": "SLICE22_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_decision_record_review_hash": (
            measurement_dryrun_decision_record_review["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_decision_record_review": False,
        "valid_for_measurement_dryrun_decision_recording": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_held_out_set_binding_review(
    *,
    timestamp: str,
    measurement_dryrun_decision_record_review: Mapping[str, Any],
    observability_dashboard: Mapping[str, Any],
    binding_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_held_out_set_binding_review_check(check)
        for check in binding_checks
    ]
    if not normalized_checks:
        raise ValueError("held-out set binding review requires one binding check")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE23_HELD_OUT_SET_BINDING_REVIEW",
        "review_status": "SLICE23_HELD_OUT_SET_BINDING_REVIEW_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_decision_record_review_hash": (
            measurement_dryrun_decision_record_review["canonical_hash"]
        ),
        "observability_dashboard_hash": observability_dashboard["canonical_hash"],
        "held_out_set_id": measurement_dryrun_decision_record_review[
            "held_out_set_id"
        ],
        "binding_checks": normalized_checks,
        "binding_check_count": len(normalized_checks),
        "review_mode": "HELD_OUT_SET_BINDING_REVIEW_ONLY_NOT_BOUND",
        "observability_integration": {
            "telemetry_source": "LOOP805_DAILY_OBSERVABILITY_DASHBOARD",
            "telemetry_hash": observability_dashboard["canonical_hash"],
            "telemetry_reviewed": False,
            "binding_validation_hooks_prepared": True,
            "fixtures_bound": False,
            "outcomes_bound": False,
            "brier_resolution_prepared": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "binding_authority": {
            "held_out_set_binding_review_allowed": False,
            "held_out_set_binding_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_resolution_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_held_out_set_binding_review": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice23_prompt_packet(
    *,
    timestamp: str,
    held_out_set_binding_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 23 held-out set binding review.",
            "- This packet reviews binding readiness only; it binds no held-out sets, fixtures, or outcomes.",
            "",
            "EVIDENCE PACKET",
            (
                "- Held-out set binding review hash: "
                f"{held_out_set_binding_review['canonical_hash']}"
            ),
            "- Slice 22 prepared a decision record review that remains non-recording.",
            "",
            "TASK",
            "- Review held-out set binding checklist and observability telemetry hooks.",
            "- Confirm no held-out set, fixture, outcome, forecast, dry-run execution, or Brier resolution is bound.",
            "",
            "OUTPUT",
            "- Held-out set binding review packet for future operator-only review.",
            "- Explicit telemetry and binding-validation hooks only.",
            "- No dry-run execution proposal, Brier shadow resolution, routing, measurement, or binding.",
            "",
            "VALIDATION",
            "- Confirm valid_for_held_out_set_binding_review remains false.",
            "- Confirm valid_for_fixture_binding remains false.",
            "- Confirm valid_for_outcome_binding remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- A real dry-run remains blocked until the operator separately records and attests a decision.",
            "- Binding review can prepare inspection but cannot bind held-out fixtures or outcomes.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 24 Brier shadow resolution review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE23_PROMPT_PACKET",
        "packet_status": "SLICE23_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "held_out_set_binding_review_hash": held_out_set_binding_review[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_held_out_set_binding_review": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_brier_resolution": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_brier_shadow_resolution_review(
    *,
    timestamp: str,
    held_out_set_binding_review: Mapping[str, Any],
    resolution_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_brier_shadow_resolution_review_check(check)
        for check in resolution_checks
    ]
    if not normalized_checks:
        raise ValueError("Brier shadow resolution review requires at least one check")
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE24_BRIER_SHADOW_RESOLUTION_REVIEW",
        "review_status": (
            "SLICE24_BRIER_SHADOW_RESOLUTION_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "held_out_set_binding_review_hash": held_out_set_binding_review[
            "canonical_hash"
        ],
        "held_out_set_id": held_out_set_binding_review["held_out_set_id"],
        "resolution_checks": normalized_checks,
        "resolution_check_count": len(normalized_checks),
        "review_mode": "BRIER_SHADOW_RESOLUTION_REVIEW_ONLY_NOT_RESOLVED",
        "shadow_resolution_state": {
            "review_surface_prepared": True,
            "held_out_set_bound": False,
            "fixtures_bound": False,
            "outcomes_bound": False,
            "shadow_resolution_reviewed": False,
            "shadow_resolution_computed": False,
            "live_brier_resolution_computed": False,
            "measurement_dryrun_executable": False,
            "brier_score": 0.1,
        },
        "resolution_authority": {
            "brier_shadow_resolution_review_allowed": False,
            "brier_shadow_resolution_allowed": False,
            "brier_resolution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_held_out_set_binding_review": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_shadow_resolution_review": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice24_prompt_packet(
    *,
    timestamp: str,
    brier_shadow_resolution_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 24 Brier shadow resolution review.",
            "- This packet reviews resolution readiness only; it resolves no Brier scores.",
            "",
            "EVIDENCE PACKET",
            (
                "- Brier shadow resolution review hash: "
                f"{brier_shadow_resolution_review['canonical_hash']}"
            ),
            "- Slice 23 reviewed held-out set binding readiness without binding.",
            "",
            "TASK",
            "- Review shadow-resolution criteria, fixture/outcome absence, and leakage boundaries.",
            "- Confirm no Brier shadow resolution, live Brier resolution, fixture binding, or outcome binding occurs.",
            "",
            "OUTPUT",
            "- Brier shadow resolution review packet for future operator-only inspection.",
            "- Explicit resolution-denial state and next dry-run execution proposal lane.",
            "- No scoring execution, routing, measurement, fixture binding, outcome binding, or resolution.",
            "",
            "VALIDATION",
            "- Confirm valid_for_brier_shadow_resolution_review remains false.",
            "- Confirm valid_for_brier_shadow_resolution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real Brier uplift remains unproven until fixtures, outcomes, and measurement execution are separately authorized.",
            "- Shadow-resolution review can inspect readiness but cannot compute or record outcomes.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 25 measurement dry-run execution proposal stub only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE24_PROMPT_PACKET",
        "packet_status": "SLICE24_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "brier_shadow_resolution_review_hash": brier_shadow_resolution_review[
            "canonical_hash"
        ],
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_brier_shadow_resolution_review": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_measurement": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_execution_proposal_stub(
    *,
    timestamp: str,
    brier_shadow_resolution_review: Mapping[str, Any],
    proposal_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_execution_proposal_item(item)
        for item in proposal_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run execution proposal stub requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "proposal_id": (
            "ABX_LOOP805_SLICE25_MEASUREMENT_DRYRUN_EXECUTION_PROPOSAL_STUB"
        ),
        "proposal_status": (
            "SLICE25_MEASUREMENT_DRYRUN_EXECUTION_PROPOSAL_STUB_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "brier_shadow_resolution_review_hash": brier_shadow_resolution_review[
            "canonical_hash"
        ],
        "held_out_set_id": brier_shadow_resolution_review["held_out_set_id"],
        "proposal_items": normalized_items,
        "proposal_item_count": len(normalized_items),
        "proposal_mode": "MEASUREMENT_DRYRUN_EXECUTION_PROPOSAL_ONLY_NOT_EXECUTABLE",
        "execution_proposal_state": {
            "proposal_surface_prepared": True,
            "operator_execution_gate_recorded": False,
            "operator_attestation_recorded": False,
            "held_out_set_bound": False,
            "fixtures_bound": False,
            "outcomes_bound": False,
            "brier_shadow_resolution_computed": False,
            "measurement_dryrun_executable": False,
            "measurement_dryrun_executed": False,
            "brier_score": 0.1,
        },
        "execution_authority": {
            "measurement_dryrun_execution_proposal_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "brier_shadow_resolution_allowed": False,
            "brier_resolution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_proposal": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice25_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_execution_proposal_stub: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 25 measurement dry-run execution proposal stub.",
            "- This packet proposes review structure only; it executes no measurement dry run.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run execution proposal stub hash: "
                f"{measurement_dryrun_execution_proposal_stub['canonical_hash']}"
            ),
            "- Slice 24 reviewed Brier shadow resolution readiness without resolving Brier.",
            "",
            "TASK",
            "- Review execution proposal prerequisites, operator gate requirements, and rollback criteria.",
            "- Confirm no measurement dry-run execution, fixture binding, outcome binding, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run execution proposal stub for future operator-only review.",
            "- Explicit execution-denial state and next operator execution gate lane.",
            "- No measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_execution_proposal remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "- Confirm valid_for_brier_resolution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Real measurement remains unproven until operator records a separate execution gate.",
            "- Proposal structure can document prerequisites but cannot authorize or run dry-run measurement.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 26 operator measurement execution gate review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE25_PROMPT_PACKET",
        "packet_status": "SLICE25_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_execution_proposal_stub_hash": (
            measurement_dryrun_execution_proposal_stub["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_proposal": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_operator_measurement_execution_gate_review(
    *,
    timestamp: str,
    measurement_dryrun_execution_proposal_stub: Mapping[str, Any],
    gate_review_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_operator_measurement_execution_gate_review_item(item)
        for item in gate_review_items
    ]
    if not normalized_items:
        raise ValueError(
            "operator measurement execution gate review requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE26_OPERATOR_MEASUREMENT_EXECUTION_GATE_REVIEW",
        "review_status": (
            "SLICE26_OPERATOR_MEASUREMENT_EXECUTION_GATE_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_execution_proposal_stub_hash": (
            measurement_dryrun_execution_proposal_stub["canonical_hash"]
        ),
        "gate_review_items": normalized_items,
        "gate_review_item_count": len(normalized_items),
        "review_mode": "OPERATOR_EXECUTION_GATE_REVIEW_ONLY_NOT_RECORDED",
        "operator_gate_state": {
            "review_surface_prepared": True,
            "operator_execution_gate_required": True,
            "operator_execution_gate_recorded": False,
            "operator_attestation_required": True,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_prepared": False,
            "measurement_dryrun_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_binding_authorized": False,
            "outcome_binding_authorized": False,
            "brier_shadow_resolution_authorized": False,
            "brier_resolution_authorized": False,
            "brier_score": 0.1,
        },
        "execution_authority": {
            "operator_gate_review_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_shadow_resolution_allowed": False,
            "brier_resolution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_operator_measurement_execution_gate_review": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_proposal": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice26_prompt_packet(
    *,
    timestamp: str,
    operator_measurement_execution_gate_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 26 operator measurement execution gate review.",
            "- This packet reviews gate prerequisites only; it records no operator gate or attestation.",
            "",
            "EVIDENCE PACKET",
            (
                "- Operator measurement execution gate review hash: "
                f"{operator_measurement_execution_gate_review['canonical_hash']}"
            ),
            "- Slice 25 prepared a non-executable measurement dry-run execution proposal stub.",
            "",
            "TASK",
            "- Review operator gate requirements, attestation language, rollback criteria, and denial boundaries.",
            "- Confirm no measurement dry-run packet, fixture binding, outcome binding, execution, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Operator measurement execution gate review packet for future operator-only decision handling.",
            "- Explicit gate-not-recorded and attestation-not-recorded state.",
            "- No measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_operator_measurement_execution_gate_review remains false.",
            "- Confirm valid_for_operator_measurement_execution_gate_recording remains false.",
            "- Confirm valid_for_operator_attestation_recording remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Operator gate review can identify prerequisites but cannot record authorization.",
            "- Real measurement remains future-gated until a separate operator gate is recorded outside this packet.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 27 measurement dry-run execution packet candidate only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE26_PROMPT_PACKET",
        "packet_status": "SLICE26_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "operator_measurement_execution_gate_review_hash": (
            operator_measurement_execution_gate_review["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_operator_measurement_execution_gate_review": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_execution_packet_candidate(
    *,
    timestamp: str,
    operator_measurement_execution_gate_review: Mapping[str, Any],
    packet_sections: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_sections = [
        _normalize_measurement_dryrun_execution_packet_candidate_section(section)
        for section in packet_sections
    ]
    if not normalized_sections:
        raise ValueError(
            "measurement dry-run execution packet candidate requires at least one section"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "candidate_id": (
            "ABX_LOOP805_SLICE27_MEASUREMENT_DRYRUN_EXECUTION_PACKET_CANDIDATE"
        ),
        "candidate_status": (
            "SLICE27_MEASUREMENT_DRYRUN_EXECUTION_PACKET_CANDIDATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "operator_measurement_execution_gate_review_hash": (
            operator_measurement_execution_gate_review["canonical_hash"]
        ),
        "packet_sections": normalized_sections,
        "packet_section_count": len(normalized_sections),
        "candidate_mode": "PACKET_CANDIDATE_ONLY_NOT_EXECUTABLE",
        "packet_candidate_state": {
            "candidate_surface_prepared": True,
            "operator_execution_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "held_out_set_bound": False,
            "fixtures_bound": False,
            "outcomes_bound": False,
            "brier_shadow_resolution_computed": False,
            "brier_resolution_computed": False,
            "brier_score": 0.1,
        },
        "execution_authority": {
            "measurement_dryrun_packet_candidate_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_shadow_resolution_allowed": False,
            "brier_resolution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_packet_candidate": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice27_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_execution_packet_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 27 measurement dry-run execution packet candidate.",
            "- This packet drafts candidate packet sections only; it creates no executable packet.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run execution packet candidate hash: "
                f"{measurement_dryrun_execution_packet_candidate['canonical_hash']}"
            ),
            "- Slice 26 reviewed operator execution gate prerequisites without recording a gate.",
            "",
            "TASK",
            "- Review candidate packet sections, execution denial fields, rollback posture, and evidence dependencies.",
            "- Confirm no measurement dry-run execution, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run execution packet candidate for future operator review.",
            "- Explicit candidate-only state and execution-denial fields.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_execution_packet_candidate remains false.",
            "- Confirm valid_for_measurement_dryrun_execution_packet remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Candidate sections can describe future execution posture but cannot create a runnable packet.",
            "- Real measurement remains future-gated until separate operator authorization and executable packet handling.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 28 measurement dry-run execution packet review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE27_PROMPT_PACKET",
        "packet_status": "SLICE27_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_execution_packet_candidate_hash": (
            measurement_dryrun_execution_packet_candidate["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_packet_candidate": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_execution_packet_review(
    *,
    timestamp: str,
    measurement_dryrun_execution_packet_candidate: Mapping[str, Any],
    review_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_measurement_dryrun_execution_packet_review_check(check)
        for check in review_checks
    ]
    if not normalized_checks:
        raise ValueError(
            "measurement dry-run execution packet review requires at least one check"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": "ABX_LOOP805_SLICE28_MEASUREMENT_DRYRUN_EXECUTION_PACKET_REVIEW",
        "review_status": (
            "SLICE28_MEASUREMENT_DRYRUN_EXECUTION_PACKET_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_execution_packet_candidate_hash": (
            measurement_dryrun_execution_packet_candidate["canonical_hash"]
        ),
        "review_checks": normalized_checks,
        "review_check_count": len(normalized_checks),
        "review_mode": "PACKET_REVIEW_ONLY_NOT_EXECUTABLE",
        "packet_review_state": {
            "review_surface_prepared": True,
            "candidate_sections_reviewed": False,
            "operator_execution_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "held_out_set_bound": False,
            "fixtures_bound": False,
            "outcomes_bound": False,
            "brier_shadow_resolution_computed": False,
            "brier_resolution_computed": False,
            "brier_score": 0.1,
        },
        "execution_authority": {
            "measurement_dryrun_packet_review_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_shadow_resolution_allowed": False,
            "brier_resolution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_packet_review": False,
        "valid_for_measurement_dryrun_execution_packet_candidate": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice28_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_execution_packet_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 28 measurement dry-run execution packet review.",
            "- This packet reviews candidate sections only; it creates no executable packet and runs nothing.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run execution packet review hash: "
                f"{measurement_dryrun_execution_packet_review['canonical_hash']}"
            ),
            "- Slice 27 prepared a non-executable measurement dry-run packet candidate.",
            "",
            "TASK",
            "- Review candidate packet sections, operator gate dependencies, rollback posture, and denial boundaries.",
            "- Confirm no executable measurement packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run execution packet review for future operator-only handling.",
            "- Explicit review-only state and execution-denial fields.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_execution_packet_review remains false.",
            "- Confirm valid_for_measurement_dryrun_execution_packet remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Review can identify candidate issues but cannot approve or execute a measurement dry run.",
            "- Real measurement remains future-gated until a separate operator gate and execution mechanism exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 29 measurement dry-run execution denial ledger only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE28_PROMPT_PACKET",
        "packet_status": "SLICE28_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_execution_packet_review_hash": (
            measurement_dryrun_execution_packet_review["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_packet_review": False,
        "valid_for_measurement_dryrun_execution_packet_candidate": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_execution_denial_ledger(
    *,
    timestamp: str,
    measurement_dryrun_execution_packet_review: Mapping[str, Any],
    denial_entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_entries = [
        _normalize_measurement_dryrun_execution_denial_entry(entry)
        for entry in denial_entries
    ]
    if not normalized_entries:
        raise ValueError(
            "measurement dry-run execution denial ledger requires at least one entry"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "ledger_id": "ABX_LOOP805_SLICE29_MEASUREMENT_DRYRUN_EXECUTION_DENIAL_LEDGER",
        "ledger_status": (
            "SLICE29_MEASUREMENT_DRYRUN_EXECUTION_DENIAL_LEDGER_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_execution_packet_review_hash": (
            measurement_dryrun_execution_packet_review["canonical_hash"]
        ),
        "denial_entries": normalized_entries,
        "denial_entry_count": len(normalized_entries),
        "ledger_mode": "DENIAL_LEDGER_ONLY_NO_EXECUTION_AUTHORITY",
        "denial_state": {
            "denial_surface_prepared": True,
            "operator_execution_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "held_out_set_bound": False,
            "fixtures_bound": False,
            "outcomes_bound": False,
            "brier_shadow_resolution_computed": False,
            "brier_resolution_computed": False,
            "execution_denied": True,
            "brier_score": 0.1,
        },
        "execution_authority": {
            "denial_ledger_recording_allowed": False,
            "measurement_dryrun_packet_review_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_shadow_resolution_allowed": False,
            "brier_resolution_allowed": False,
            "forecast_routing_allowed": False,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_denial_ledger": False,
        "valid_for_measurement_dryrun_execution_packet_review": False,
        "valid_for_measurement_dryrun_execution_packet_candidate": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_held_out_set_binding": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_measurement": False,
        "valid_for_forecast_routing": False,
        "valid_for_runtime_activation": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice29_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_execution_denial_ledger: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 29 measurement dry-run execution denial ledger.",
            "- This packet records denial posture only; it authorizes no execution and creates no executable packet.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run execution denial ledger hash: "
                f"{measurement_dryrun_execution_denial_ledger['canonical_hash']}"
            ),
            "- Slice 28 reviewed the packet candidate without making it executable.",
            "",
            "TASK",
            "- Review denial entries, missing gates, missing bindings, and remaining execution blockers.",
            "- Confirm no executable measurement packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run execution denial ledger for future operator review.",
            "- Explicit denial state and remaining gate list.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_execution_denial_ledger remains false.",
            "- Confirm valid_for_measurement_dryrun_execution_packet remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Denial ledger can document blockers but cannot approve execution.",
            "- Real measurement remains future-gated until separate operator authority and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 30 measurement dry-run operator action menu only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE29_PROMPT_PACKET",
        "packet_status": "SLICE29_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_execution_denial_ledger_hash": (
            measurement_dryrun_execution_denial_ledger["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_execution_denial_ledger": False,
        "valid_for_measurement_dryrun_execution_packet_review": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_brier_resolution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_measurement": False,
        "valid_for_runtime_activation": False,
        "valid_for_github_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_action_menu(
    *,
    timestamp: str,
    measurement_dryrun_execution_denial_ledger: Mapping[str, Any],
    action_entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_entries = [
        _normalize_measurement_dryrun_operator_action_menu_entry(entry)
        for entry in action_entries
    ]
    if not normalized_entries:
        raise ValueError(
            "measurement dry-run operator action menu requires at least one entry"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "menu_id": "ABX_LOOP805_SLICE30_MEASUREMENT_DRYRUN_OPERATOR_ACTION_MENU",
        "menu_status": (
            "SLICE30_MEASUREMENT_DRYRUN_OPERATOR_ACTION_MENU_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_execution_denial_ledger_hash": (
            measurement_dryrun_execution_denial_ledger["canonical_hash"]
        ),
        "action_entries": normalized_entries,
        "action_entry_count": len(normalized_entries),
        "menu_mode": "OPERATOR_ACTION_MENU_ONLY_NO_DECISION_RECORDING",
        "selected_action": None,
        "selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "execution_authority": {
            "action_menu_recording_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_action_menu": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE31_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_REVIEW"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 29 + "
            "Hash: b469156fc3648e10c451b3c664158aab49296efa8c3fdc4b585400a5bed1643e"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice30_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_action_menu: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 30 measurement dry-run operator action menu.",
            "- This packet offers future operator action lanes only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator action menu hash: "
                f"{measurement_dryrun_operator_action_menu['canonical_hash']}"
            ),
            "- Slice 29 recorded denial posture without creating an executable measurement packet.",
            "",
            "TASK",
            "- Review action entries, required gates, and fail-closed boundaries.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator action menu for future operator review.",
            "- Explicit non-selection state and remaining gate list.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_action_menu remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Action menu can frame options but cannot record an operator decision.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 31 measurement dry-run operator selection review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE30_PROMPT_PACKET",
        "packet_status": "SLICE30_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_action_menu_hash": (
            measurement_dryrun_operator_action_menu["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_action_menu": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_denial_ledger": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_selection_review(
    *,
    timestamp: str,
    measurement_dryrun_operator_action_menu: Mapping[str, Any],
    selection_review_checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_checks = [
        _normalize_measurement_dryrun_operator_selection_review_check(check)
        for check in selection_review_checks
    ]
    if not normalized_checks:
        raise ValueError(
            "measurement dry-run operator selection review requires at least one check"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": (
            "ABX_LOOP805_SLICE31_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_REVIEW"
        ),
        "review_status": (
            "SLICE31_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_action_menu_hash": (
            measurement_dryrun_operator_action_menu["canonical_hash"]
        ),
        "selection_review_checks": normalized_checks,
        "selection_review_check_count": len(normalized_checks),
        "review_mode": "SELECTION_REVIEW_ONLY_NO_SELECTION_RECORDING",
        "selected_action": None,
        "selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "review_state": {
            "selection_review_prepared": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "execution_authority": {
            "selection_review_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_review": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE32_MEASUREMENT_DRYRUN_SELECTION_DENIAL_RECEIPT"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 30 + "
            "Hash: 98caf9181423e309c067ec554706953ab0c9601b8c0021af97488076ef5aa94a"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice31_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 31 measurement dry-run operator selection review.",
            "- This packet reviews selection prerequisites only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator selection review hash: "
                f"{measurement_dryrun_operator_selection_review['canonical_hash']}"
            ),
            "- Slice 30 prepared an action menu without recording operator selection.",
            "",
            "TASK",
            "- Review selection checks, unresolved gates, and fail-closed denial posture.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator selection review for future operator handling.",
            "- Explicit no-selection state and remaining gate list.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_selection_review remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Selection review can frame missing prerequisites but cannot record an operator choice.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 32 measurement dry-run selection denial receipt only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE31_PROMPT_PACKET",
        "packet_status": "SLICE31_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_review_hash": (
            measurement_dryrun_operator_selection_review["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_review": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_operator_action_menu": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_selection_denial_receipt(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_review: Mapping[str, Any],
    denial_reasons: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_reasons = [
        _normalize_measurement_dryrun_selection_denial_reason(reason)
        for reason in denial_reasons
    ]
    if not normalized_reasons:
        raise ValueError(
            "measurement dry-run selection denial receipt requires at least one reason"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "receipt_id": (
            "ABX_LOOP805_SLICE32_MEASUREMENT_DRYRUN_SELECTION_DENIAL_RECEIPT"
        ),
        "receipt_status": (
            "SLICE32_MEASUREMENT_DRYRUN_SELECTION_DENIAL_RECEIPT_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_review_hash": (
            measurement_dryrun_operator_selection_review["canonical_hash"]
        ),
        "denial_reasons": normalized_reasons,
        "denial_reason_count": len(normalized_reasons),
        "receipt_mode": "SELECTION_DENIAL_RECEIPT_ONLY_NO_SELECTION_RECORDING",
        "selected_action": None,
        "selection_denied": True,
        "selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "denial_state": {
            "selection_denial_receipt_prepared": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "execution_authority": {
            "selection_denial_receipt_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_selection_denial_receipt": False,
        "valid_for_measurement_dryrun_operator_selection_review": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE33_MEASUREMENT_DRYRUN_DENIAL_RECONCILIATION_PACKET"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 31 + "
            "Hash: 0b28909cd4ab7762da283c8f5d1239d09370ef7d148f00289680a5634c0e615c"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice32_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_selection_denial_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 32 measurement dry-run selection denial receipt.",
            "- This packet records selection denial posture only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run selection denial receipt hash: "
                f"{measurement_dryrun_selection_denial_receipt['canonical_hash']}"
            ),
            "- Slice 31 reviewed operator-selection prerequisites without recording an operator choice.",
            "",
            "TASK",
            "- Review denial reasons, unresolved gates, and fail-closed posture.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run selection denial receipt for future operator review.",
            "- Explicit selection-denied state and remaining gate list.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_selection_denial_receipt remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Selection denial receipt can document blockers but cannot record an operator choice.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 33 measurement dry-run denial reconciliation packet only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE32_PROMPT_PACKET",
        "packet_status": "SLICE32_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_selection_denial_receipt_hash": (
            measurement_dryrun_selection_denial_receipt["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_selection_denial_receipt": False,
        "valid_for_measurement_dryrun_operator_selection_review": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_denial_reconciliation_packet(
    *,
    timestamp: str,
    measurement_dryrun_selection_denial_receipt: Mapping[str, Any],
    reconciliation_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_denial_reconciliation_item(item)
        for item in reconciliation_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run denial reconciliation packet requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": (
            "ABX_LOOP805_SLICE33_MEASUREMENT_DRYRUN_DENIAL_RECONCILIATION_PACKET"
        ),
        "packet_status": (
            "SLICE33_MEASUREMENT_DRYRUN_DENIAL_RECONCILIATION_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_selection_denial_receipt_hash": (
            measurement_dryrun_selection_denial_receipt["canonical_hash"]
        ),
        "reconciliation_items": normalized_items,
        "reconciliation_item_count": len(normalized_items),
        "reconciliation_mode": "DENIAL_RECONCILIATION_ONLY_NO_AUTHORITY_CHANGE",
        "reconciled_status": "MEASUREMENT_DRYRUN_REMAINS_DENIED",
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "denial_reconciliation_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_denial_reconciliation": False,
        "valid_for_measurement_dryrun_selection_denial_receipt": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE34_MEASUREMENT_DRYRUN_OPERATOR_HANDOFF_PACKET"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 32 + "
            "Hash: f2faecc382882478a1a0dd9eb729d526c05014dc55f394af34ae37f88c0dafbb"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice33_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_denial_reconciliation_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 33 measurement dry-run denial reconciliation packet.",
            "- This packet reconciles denial posture only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run denial reconciliation hash: "
                f"{measurement_dryrun_denial_reconciliation_packet['canonical_hash']}"
            ),
            "- Slice 32 recorded selection denial without changing execution authority.",
            "",
            "TASK",
            "- Review reconciled denial state across action menu, selection review, and selection denial receipt.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run denial reconciliation packet for future operator handoff.",
            "- Explicit measurement-dryrun-remains-denied state.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_denial_reconciliation remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Reconciliation packet can summarize blockers but cannot clear them.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 34 measurement dry-run operator handoff packet only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE33_PROMPT_PACKET",
        "packet_status": "SLICE33_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_denial_reconciliation_packet_hash": (
            measurement_dryrun_denial_reconciliation_packet["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_denial_reconciliation": False,
        "valid_for_measurement_dryrun_selection_denial_receipt": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_handoff_packet(
    *,
    timestamp: str,
    measurement_dryrun_denial_reconciliation_packet: Mapping[str, Any],
    handoff_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_operator_handoff_item(item)
        for item in handoff_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run operator handoff packet requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": (
            "ABX_LOOP805_SLICE34_MEASUREMENT_DRYRUN_OPERATOR_HANDOFF_PACKET"
        ),
        "packet_status": (
            "SLICE34_MEASUREMENT_DRYRUN_OPERATOR_HANDOFF_PACKET_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_denial_reconciliation_packet_hash": (
            measurement_dryrun_denial_reconciliation_packet["canonical_hash"]
        ),
        "handoff_items": normalized_items,
        "handoff_item_count": len(normalized_items),
        "handoff_mode": "OPERATOR_HANDOFF_PACKET_ONLY_NO_SELECTION_RECORDING",
        "handoff_state": {
            "operator_handoff_prepared": True,
            "denial_reconciliation_preserved": True,
            "measurement_dryrun_remains_denied": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "selected_action": None,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "operator_handoff_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_handoff": False,
        "valid_for_measurement_dryrun_denial_reconciliation": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE35_MEASUREMENT_DRYRUN_OPERATOR_HANDOFF_REVIEW"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 33 + "
            "Hash: ccce32991a6d2bf896c0797ff8bbe1afbdd5a54e51d4f3602f0c132f9b7b9ea5"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice34_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_handoff_packet: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 34 measurement dry-run operator handoff packet.",
            "- This packet frames operator handoff only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator handoff hash: "
                f"{measurement_dryrun_operator_handoff_packet['canonical_hash']}"
            ),
            "- Slice 33 reconciled denial posture without changing execution authority.",
            "",
            "TASK",
            "- Review handoff items, unresolved gates, and denial-preserving operator notes.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator handoff packet for future review.",
            "- Explicit measurement-dryrun-remains-denied state and no-selection posture.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_handoff remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Handoff packet can organize operator review context but cannot record a choice.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 35 measurement dry-run operator handoff review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE34_PROMPT_PACKET",
        "packet_status": "SLICE34_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_handoff_packet_hash": (
            measurement_dryrun_operator_handoff_packet["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_handoff": False,
        "valid_for_measurement_dryrun_denial_reconciliation": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_handoff_review(
    *,
    timestamp: str,
    measurement_dryrun_operator_handoff_packet: Mapping[str, Any],
    review_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_operator_handoff_review_item(item)
        for item in review_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run operator handoff review requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": (
            "ABX_LOOP805_SLICE35_MEASUREMENT_DRYRUN_OPERATOR_HANDOFF_REVIEW"
        ),
        "review_status": (
            "SLICE35_MEASUREMENT_DRYRUN_OPERATOR_HANDOFF_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_handoff_packet_hash": (
            measurement_dryrun_operator_handoff_packet["canonical_hash"]
        ),
        "review_items": normalized_items,
        "review_item_count": len(normalized_items),
        "review_mode": "OPERATOR_HANDOFF_REVIEW_ONLY_NO_SELECTION_RECORDING",
        "review_state": {
            "operator_handoff_review_prepared": True,
            "handoff_packet_reviewed": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "selected_action": None,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "operator_handoff_review_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_handoff_review": False,
        "valid_for_measurement_dryrun_operator_handoff": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE36_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_CANDIDATE"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 34 + "
            "Hash: b329515bfc9801f7052d5eb69c83ac6f6f365674dc620f9b12471a32cee36f26"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice35_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_handoff_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 35 measurement dry-run operator handoff review.",
            "- This packet reviews handoff posture only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator handoff review hash: "
                f"{measurement_dryrun_operator_handoff_review['canonical_hash']}"
            ),
            "- Slice 34 packaged operator handoff context without recording a selection.",
            "",
            "TASK",
            "- Review handoff readiness, unresolved selection gates, and denial-preserving boundaries.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator handoff review packet for future candidate routing.",
            "- Explicit no-selection, no-gate, no-attestation state.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_handoff_review remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Handoff review can summarize readiness gaps but cannot select an action.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 36 measurement dry-run operator selection packet candidate only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE35_PROMPT_PACKET",
        "packet_status": "SLICE35_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_handoff_review_hash": (
            measurement_dryrun_operator_handoff_review["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_handoff_review": False,
        "valid_for_measurement_dryrun_operator_handoff": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_selection_packet_candidate(
    *,
    timestamp: str,
    measurement_dryrun_operator_handoff_review: Mapping[str, Any],
    candidate_fields: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_fields = [
        _normalize_measurement_dryrun_operator_selection_candidate_field(field)
        for field in candidate_fields
    ]
    if not normalized_fields:
        raise ValueError(
            "measurement dry-run operator selection packet candidate requires at least one field"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "candidate_id": (
            "ABX_LOOP805_SLICE36_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_CANDIDATE"
        ),
        "candidate_status": (
            "SLICE36_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_CANDIDATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_handoff_review_hash": (
            measurement_dryrun_operator_handoff_review["canonical_hash"]
        ),
        "candidate_fields": normalized_fields,
        "candidate_field_count": len(normalized_fields),
        "candidate_mode": "SELECTION_PACKET_CANDIDATE_ONLY_NO_SELECTION_RECORDING",
        "candidate_state": {
            "selection_packet_candidate_prepared": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "selected_action": None,
        "selection_recorded": False,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "selection_packet_candidate_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_measurement_dryrun_operator_handoff_review": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE37_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_REVIEW"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 35 + "
            "Hash: 4110e1d59fbb4c4e5e7606102b35cd3b5f2401a3a012b9553f902b0169242126"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice36_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_packet_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 36 measurement dry-run operator selection packet candidate.",
            "- This packet drafts a future selection packet shape only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator selection packet candidate hash: "
                f"{measurement_dryrun_operator_selection_packet_candidate['canonical_hash']}"
            ),
            "- Slice 35 reviewed handoff posture without recording an operator choice.",
            "",
            "TASK",
            "- Review candidate fields, required future gates, and fail-closed no-selection posture.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator selection packet candidate for future review.",
            "- Explicit selected_action null and selection_recorded false state.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_selection_packet_candidate remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Candidate packet can define fields but cannot select or authorize an action.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 37 measurement dry-run operator selection packet review only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE36_PROMPT_PACKET",
        "packet_status": "SLICE36_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_packet_candidate_hash": (
            measurement_dryrun_operator_selection_packet_candidate["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_measurement_dryrun_operator_handoff_review": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_selection_packet_review(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_packet_candidate: Mapping[str, Any],
    review_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_operator_selection_packet_review_item(item)
        for item in review_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run operator selection packet review requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "review_id": (
            "ABX_LOOP805_SLICE37_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_REVIEW"
        ),
        "review_status": (
            "SLICE37_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_REVIEW_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_packet_candidate_hash": (
            measurement_dryrun_operator_selection_packet_candidate["canonical_hash"]
        ),
        "review_items": normalized_items,
        "review_item_count": len(normalized_items),
        "review_mode": "SELECTION_PACKET_REVIEW_ONLY_NO_SELECTION_RECORDING",
        "review_state": {
            "selection_packet_review_prepared": True,
            "selection_packet_candidate_reviewed": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "selected_action": None,
        "selection_recorded": False,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "selection_packet_review_allowed": False,
            "selection_packet_candidate_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE38_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_DENIAL"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 36 + "
            "Hash: 9976bb8e2fd2c75561e8ffc689459d66efb69cee0ad2ffeb44a24fe6bb56203e"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice37_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_packet_review: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 37 measurement dry-run operator selection packet review.",
            "- This packet reviews a selection packet candidate only; it records no selected action and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator selection packet review hash: "
                f"{measurement_dryrun_operator_selection_packet_review['canonical_hash']}"
            ),
            "- Slice 36 prepared a selection packet candidate without recording an operator choice.",
            "",
            "TASK",
            "- Review candidate fields, selection prerequisites, and fail-closed no-selection posture.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator selection packet review for future denial/reconciliation routing.",
            "- Explicit selected_action null, selection_recorded false, and review-only state.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_selection_packet_review remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Review packet can evaluate candidate fields but cannot choose or authorize an action.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 38 measurement dry-run operator selection packet denial only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE37_PROMPT_PACKET",
        "packet_status": "SLICE37_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_packet_review_hash": (
            measurement_dryrun_operator_selection_packet_review["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_selection_packet_denial(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_packet_review: Mapping[str, Any],
    denial_reasons: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_reasons = [
        _normalize_measurement_dryrun_selection_denial_reason(reason)
        for reason in denial_reasons
    ]
    if not normalized_reasons:
        raise ValueError(
            "measurement dry-run operator selection packet denial requires at least one reason"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "receipt_id": (
            "ABX_LOOP805_SLICE38_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_DENIAL"
        ),
        "receipt_status": (
            "SLICE38_MEASUREMENT_DRYRUN_OPERATOR_SELECTION_PACKET_DENIAL_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_packet_review_hash": (
            measurement_dryrun_operator_selection_packet_review["canonical_hash"]
        ),
        "denial_reasons": normalized_reasons,
        "denial_reason_count": len(normalized_reasons),
        "receipt_mode": "SELECTION_PACKET_DENIAL_ONLY_NO_SELECTION_RECORDING",
        "selected_action": None,
        "selection_packet_denied": True,
        "selection_recorded": False,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "denial_state": {
            "selection_packet_denial_prepared": True,
            "selection_packet_reviewed": True,
            "operator_selection_recorded": False,
            "operator_gate_recorded": False,
            "operator_attestation_recorded": False,
            "measurement_dryrun_packet_created": False,
            "measurement_dryrun_packet_executable": False,
            "measurement_dryrun_executed": False,
            "fixture_bound": False,
            "outcome_bound": False,
            "brier_resolution_computed": False,
        },
        "execution_authority": {
            "selection_packet_denial_allowed": False,
            "selection_packet_review_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_packet_denial": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE39_MEASUREMENT_DRYRUN_SELECTION_PACKET_DENIAL_RECONCILIATION"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 37 + "
            "Hash: 10e6fd6a0f05a9dc200a366d945f092b5095d69258cc6878c442b1f27c5242ad"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice38_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_packet_denial: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 38 measurement dry-run operator selection packet denial.",
            "- This receipt preserves denial posture only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator selection packet denial hash: "
                f"{measurement_dryrun_operator_selection_packet_denial['canonical_hash']}"
            ),
            "- Slice 37 reviewed the selection packet candidate without recording an operator choice.",
            "",
            "TASK",
            "- Review denial reasons, unresolved gates, and fail-closed measurement posture.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator selection packet denial receipt for future reconciliation.",
            "- Explicit selection_packet_denied true with selected_action null.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_selection_packet_denial remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Denial receipt can document blockers but cannot record an operator choice.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 39 measurement dry-run selection packet denial reconciliation only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE38_PROMPT_PACKET",
        "packet_status": "SLICE38_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_packet_denial_hash": (
            measurement_dryrun_operator_selection_packet_denial["canonical_hash"]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_selection_packet_denial": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_selection_packet_denial_reconciliation(
    *,
    timestamp: str,
    measurement_dryrun_operator_selection_packet_denial: Mapping[str, Any],
    reconciliation_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_denial_reconciliation_item(item)
        for item in reconciliation_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run selection packet denial reconciliation requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": (
            "ABX_LOOP805_SLICE39_MEASUREMENT_DRYRUN_SELECTION_PACKET_DENIAL_RECONCILIATION"
        ),
        "packet_status": (
            "SLICE39_MEASUREMENT_DRYRUN_SELECTION_PACKET_DENIAL_RECONCILIATION_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_operator_selection_packet_denial_hash": (
            measurement_dryrun_operator_selection_packet_denial["canonical_hash"]
        ),
        "reconciliation_items": normalized_items,
        "reconciliation_item_count": len(normalized_items),
        "reconciliation_mode": (
            "SELECTION_PACKET_DENIAL_RECONCILIATION_ONLY_NO_AUTHORITY_CHANGE"
        ),
        "reconciled_status": "MEASUREMENT_DRYRUN_SELECTION_PACKET_REMAINS_DENIED",
        "selected_action": None,
        "selection_recorded": False,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "selection_packet_denial_reconciliation_allowed": False,
            "selection_packet_denial_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_selection_packet_denial_reconciliation": False,
        "valid_for_measurement_dryrun_operator_selection_packet_denial": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE40_MEASUREMENT_DRYRUN_OPERATOR_PACKET_HANDOFF_RECONCILIATION"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 38 + "
            "Hash: d19334bdc629201cfe6adee1ae925b056e6a5e7481b81848df3e47c77be5b117"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice39_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_selection_packet_denial_reconciliation: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 39 measurement dry-run selection packet denial reconciliation.",
            "- This packet reconciles denial posture only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run selection packet denial reconciliation hash: "
                f"{measurement_dryrun_selection_packet_denial_reconciliation['canonical_hash']}"
            ),
            "- Slice 38 recorded selection packet denial without changing execution authority.",
            "",
            "TASK",
            "- Review reconciled denial state across candidate, review, and denial receipts.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run selection packet denial reconciliation for future operator packet handoff.",
            "- Explicit measurement-dryrun-selection-packet-remains-denied state.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_selection_packet_denial_reconciliation remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Reconciliation packet can summarize blockers but cannot clear them.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 40 measurement dry-run operator packet handoff reconciliation only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE39_PROMPT_PACKET",
        "packet_status": "SLICE39_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_selection_packet_denial_reconciliation_hash": (
            measurement_dryrun_selection_packet_denial_reconciliation[
                "canonical_hash"
            ]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_selection_packet_denial_reconciliation": False,
        "valid_for_measurement_dryrun_operator_selection_packet_denial": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_measurement_dryrun_operator_packet_handoff_reconciliation(
    *,
    timestamp: str,
    measurement_dryrun_selection_packet_denial_reconciliation: Mapping[str, Any],
    handoff_reconciliation_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    normalized_items = [
        _normalize_measurement_dryrun_denial_reconciliation_item(item)
        for item in handoff_reconciliation_items
    ]
    if not normalized_items:
        raise ValueError(
            "measurement dry-run operator packet handoff reconciliation "
            "requires at least one item"
        )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": (
            "ABX_LOOP805_SLICE40_MEASUREMENT_DRYRUN_OPERATOR_PACKET_HANDOFF_RECONCILIATION"
        ),
        "packet_status": (
            "SLICE40_MEASUREMENT_DRYRUN_OPERATOR_PACKET_HANDOFF_RECONCILIATION_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "measurement_dryrun_selection_packet_denial_reconciliation_hash": (
            measurement_dryrun_selection_packet_denial_reconciliation[
                "canonical_hash"
            ]
        ),
        "handoff_reconciliation_items": normalized_items,
        "handoff_reconciliation_item_count": len(normalized_items),
        "handoff_reconciliation_mode": (
            "OPERATOR_PACKET_HANDOFF_RECONCILIATION_ONLY_NO_AUTHORITY_CHANGE"
        ),
        "reconciled_status": (
            "MEASUREMENT_DRYRUN_OPERATOR_PACKET_HANDOFF_REMAINS_DENIED"
        ),
        "operator_packet_handoff_ready": True,
        "selected_action": None,
        "selection_recorded": False,
        "operator_selection_recorded": False,
        "operator_gate_recorded": False,
        "operator_attestation_recorded": False,
        "operator_packet_handoff_recorded": False,
        "measurement_dryrun_packet_created": False,
        "measurement_dryrun_packet_executable": False,
        "measurement_dryrun_executed": False,
        "fixture_bound": False,
        "outcome_bound": False,
        "brier_resolution_computed": False,
        "execution_authority": {
            "operator_packet_handoff_reconciliation_allowed": False,
            "selection_packet_denial_reconciliation_allowed": False,
            "operator_action_selection_allowed": False,
            "operator_gate_recording_allowed": False,
            "operator_attestation_recording_allowed": False,
            "measurement_dryrun_packet_creation_allowed": False,
            "measurement_dryrun_execution_allowed": False,
            "fixture_binding_allowed": False,
            "outcome_binding_allowed": False,
            "brier_resolution_allowed": False,
            "github_writeback_allowed": False,
            "notion_writeback_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_packet_handoff_reconciliation": False,
        "valid_for_measurement_dryrun_selection_packet_denial_reconciliation": False,
        "valid_for_measurement_dryrun_operator_selection_packet_denial": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_operator_packet_handoff_recording": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "recommended_next_gate": (
            "PREPARE_SLICE41_MEASUREMENT_DRYRUN_OPERATOR_PACKET_HANDOFF_DENIAL_LEDGER"
        ),
        "provenance": (
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice 39 + "
            "Hash: 85f4685eb96ad1c847f7816c5940c809d66225015b0552a1c47805d1ee23a84f"
        ),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_loop805_slice40_prompt_packet(
    *,
    timestamp: str,
    measurement_dryrun_operator_packet_handoff_reconciliation: Mapping[str, Any],
) -> dict[str, Any]:
    prompt = "\n".join(
        [
            "BOUNDARY",
            "- Advisory-only Loop 805 Slice 40 measurement dry-run operator packet handoff reconciliation.",
            "- This packet reconciles operator packet handoff posture only; it records no selection and authorizes no execution.",
            "",
            "EVIDENCE PACKET",
            (
                "- Measurement dry-run operator packet handoff reconciliation hash: "
                f"{measurement_dryrun_operator_packet_handoff_reconciliation['canonical_hash']}"
            ),
            "- Slice 39 reconciled selection packet denial without changing execution authority.",
            "",
            "TASK",
            "- Review operator packet handoff posture and confirm the handoff remains non-recording.",
            "- Confirm no operator selection, executable packet, fixture binding, outcome binding, forecast routing, or Brier resolution occurs.",
            "",
            "OUTPUT",
            "- Measurement dry-run operator packet handoff reconciliation for future denial ledger preparation.",
            "- Explicit operator-packet-handoff-remains-denied state.",
            "- No executable packet, measurement execution, external calls, routing, Brier resolution, or writeback.",
            "",
            "VALIDATION",
            "- Confirm valid_for_measurement_dryrun_operator_packet_handoff_reconciliation remains false.",
            "- Confirm valid_for_operator_action_selection remains false.",
            "- Confirm valid_for_measurement_dryrun_execution remains false.",
            "- Confirm valid_for_execution remains false.",
            "",
            "RESIDUAL RISKS",
            "- Handoff reconciliation can summarize operator packet blockers but cannot record a handoff.",
            "- Measurement remains future-gated until separate operator selection, attestation, and execution mechanics exist.",
            "",
            "RECOMMENDED NEXT ADVISORY ACTION",
            "- Prepare Slice 41 measurement dry-run operator packet handoff denial ledger only after operator review.",
        ]
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_BRIER_ATTESTATION_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "packet_id": "ABX_LOOP805_SLICE40_PROMPT_PACKET",
        "packet_status": "SLICE40_PROMPT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "measurement_dryrun_operator_packet_handoff_reconciliation_hash": (
            measurement_dryrun_operator_packet_handoff_reconciliation[
                "canonical_hash"
            ]
        ),
        "prompt": prompt,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_measurement_dryrun_operator_packet_handoff_reconciliation": False,
        "valid_for_measurement_dryrun_selection_packet_denial_reconciliation": False,
        "valid_for_measurement_dryrun_operator_selection_packet_denial": False,
        "valid_for_measurement_dryrun_operator_selection_packet_review": False,
        "valid_for_measurement_dryrun_operator_selection_packet_candidate": False,
        "valid_for_operator_action_selection": False,
        "valid_for_measurement_dryrun_execution_packet": False,
        "valid_for_measurement_dryrun_execution": False,
        "valid_for_operator_measurement_execution_gate_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_operator_packet_handoff_recording": False,
        "valid_for_brier_shadow_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _normalize_requirement(requirement: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(requirement)
    normalized["satisfied"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_readiness_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [field for field in required_fields if field not in check]
    if missing:
        raise ValueError(f"measurement readiness check missing fields: {missing}")
    normalized = dict(check)
    normalized["satisfied"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_authorization_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("authorization_id", "description")
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise ValueError(f"measurement authorization item missing fields: {missing}")
    normalized = dict(item)
    normalized["requested"] = True
    normalized["authorized"] = False
    normalized["valid_for_measurement_authorization"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_authorization_evidence_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("evidence_id", "description")
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise ValueError(f"authorization evidence item missing fields: {missing}")
    normalized = dict(item)
    normalized["required"] = True
    normalized["recorded"] = False
    normalized["attested"] = False
    normalized["valid_for_authorization_evidence_recording"] = False
    normalized["valid_for_measurement_authorization"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_fixture_outcome_binding_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [field for field in required_fields if field not in check]
    if missing:
        raise ValueError(f"fixture/outcome binding check missing fields: {missing}")
    normalized = dict(check)
    normalized["satisfied"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["valid_for_fixture_binding_review"] = False
    normalized["valid_for_outcome_binding_review"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_authorization_hold_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [field for field in required_fields if field not in check]
    if missing:
        raise ValueError(
            f"measurement dry-run authorization hold check missing fields: {missing}"
        )
    normalized = dict(check)
    normalized["satisfied"] = False
    normalized["externally_attested"] = False
    normalized["valid_for_measurement_dryrun_authorization_hold"] = False
    normalized["valid_for_measurement_dryrun_authorization"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_preflight_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [field for field in required_fields if field not in check]
    if missing:
        raise ValueError(
            f"measurement dry-run preflight check missing fields: {missing}"
        )
    normalized = dict(check)
    normalized["satisfied"] = False
    normalized["executable"] = False
    normalized["valid_for_measurement_dryrun_preflight"] = False
    normalized["valid_for_measurement_dryrun_authorization"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_decision_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("decision_id", "description")
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise ValueError(f"measurement dry-run decision item missing fields: {missing}")
    normalized = dict(item)
    normalized["requested"] = True
    normalized["decision_recorded"] = False
    normalized["operator_attested"] = False
    normalized["valid_for_measurement_dryrun_decision_request"] = False
    normalized["valid_for_measurement_dryrun_decision_recording"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_decision_record_template_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("field_id", "description")
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise ValueError(
            f"measurement dry-run decision record template item missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["required"] = True
    normalized["filled"] = False
    normalized["decision_recorded"] = False
    normalized["operator_attested"] = False
    normalized["valid_for_measurement_dryrun_decision_record_template"] = False
    normalized["valid_for_measurement_dryrun_decision_recording"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_decision_intake_requirement(
    requirement: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("requirement_id", "description")
    missing = [field for field in required_fields if field not in requirement]
    if missing:
        raise ValueError(
            "measurement dry-run operator decision intake requirement "
            f"missing fields: {missing}"
        )
    normalized = dict(requirement)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["intake_opened"] = False
    normalized["decision_received"] = False
    normalized["decision_recorded"] = False
    normalized["operator_attested"] = False
    normalized["valid_for_measurement_dryrun_operator_decision_intake_gate"] = False
    normalized["valid_for_measurement_dryrun_operator_decision_intake"] = False
    normalized["valid_for_measurement_dryrun_decision_recording"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_decision_intake_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise ValueError(
            "measurement dry-run operator decision intake item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["required"] = True
    normalized["submitted"] = False
    normalized["decision_received"] = False
    normalized["decision_recorded"] = False
    normalized["operator_attested"] = False
    normalized["valid_for_measurement_dryrun_operator_decision_intake_packet"] = False
    normalized["valid_for_measurement_dryrun_operator_decision_intake"] = False
    normalized["valid_for_measurement_dryrun_decision_recording"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_decision_record_candidate_field(
    field: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("field_id", "description")
    missing = [name for name in required_fields if name not in field]
    if missing:
        raise ValueError(
            "measurement dry-run operator decision record candidate field "
            f"missing fields: {missing}"
        )
    normalized = dict(field)
    normalized["candidate_only"] = True
    normalized["filled"] = False
    normalized["decision_received"] = False
    normalized["decision_recorded"] = False
    normalized["operator_attested"] = False
    normalized[
        "valid_for_measurement_dryrun_operator_decision_record_candidate"
    ] = False
    normalized["valid_for_measurement_dryrun_decision_recording"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_decision_record_review_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("review_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "measurement dry-run decision record review item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["reviewed"] = False
    normalized["decision_recorded"] = False
    normalized["operator_attested"] = False
    normalized["valid_for_measurement_dryrun_decision_record_review"] = False
    normalized["valid_for_measurement_dryrun_decision_recording"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_held_out_set_binding_review_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [name for name in required_fields if name not in check]
    if missing:
        raise ValueError(
            "held-out set binding review check "
            f"missing fields: {missing}"
        )
    normalized = dict(check)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["reviewed"] = False
    normalized["binding_hook_prepared"] = True
    normalized["held_out_set_bound"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["valid_for_held_out_set_binding_review"] = False
    normalized["valid_for_held_out_set_binding"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_brier_shadow_resolution_review_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [name for name in required_fields if name not in check]
    if missing:
        raise ValueError(
            "Brier shadow resolution review check "
            f"missing fields: {missing}"
        )
    normalized = dict(check)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["reviewed"] = False
    normalized["shadow_resolution_computed"] = False
    normalized["live_resolution_computed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["valid_for_brier_shadow_resolution_review"] = False
    normalized["valid_for_brier_shadow_resolution"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_measurement"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_execution_proposal_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "measurement dry-run execution proposal item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["reviewed"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["valid_for_measurement_dryrun_execution_proposal"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_operator_measurement_execution_gate_review_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "operator measurement execution gate review item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["reviewed"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_prepared"] = False
    normalized["measurement_dryrun_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["valid_for_operator_measurement_execution_gate_review"] = False
    normalized["valid_for_operator_measurement_execution_gate_recording"] = False
    normalized["valid_for_operator_attestation_recording"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_execution_packet_candidate_section(
    section: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("section_id", "description")
    missing = [name for name in required_fields if name not in section]
    if missing:
        raise ValueError(
            "measurement dry-run execution packet candidate section "
            f"missing fields: {missing}"
        )
    normalized = dict(section)
    normalized["required"] = True
    normalized["prepared"] = True
    normalized["reviewed"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_execution_packet_candidate"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_execution_packet_review_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [name for name in required_fields if name not in check]
    if missing:
        raise ValueError(
            "measurement dry-run execution packet review check "
            f"missing fields: {missing}"
        )
    normalized = dict(check)
    normalized["required"] = True
    normalized["satisfied"] = False
    normalized["reviewed"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_execution_packet_review"] = False
    normalized["valid_for_measurement_dryrun_execution_packet_candidate"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_execution_denial_entry(
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("denial_id", "description")
    missing = [name for name in required_fields if name not in entry]
    if missing:
        raise ValueError(
            "measurement dry-run execution denial entry "
            f"missing fields: {missing}"
        )
    normalized = dict(entry)
    normalized["active"] = True
    normalized["resolved"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_execution_denial_ledger"] = False
    normalized["valid_for_measurement_dryrun_execution_packet_review"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_action_menu_entry(
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("action_id", "description", "next_gate")
    missing = [name for name in required_fields if name not in entry]
    if missing:
        raise ValueError(
            "measurement dry-run operator action menu entry "
            f"missing fields: {missing}"
        )
    normalized = dict(entry)
    normalized["available_for_review"] = True
    normalized["selected"] = False
    normalized["selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_operator_action_menu"] = False
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_selection_review_check(
    check: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("check_id", "description")
    missing = [name for name in required_fields if name not in check]
    if missing:
        raise ValueError(
            "measurement dry-run operator selection review check "
            f"missing fields: {missing}"
        )
    normalized = dict(check)
    normalized["required"] = True
    normalized["reviewed"] = False
    normalized["satisfied"] = False
    normalized["selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_operator_selection_review"] = False
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_selection_denial_reason(
    reason: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("reason_id", "description")
    missing = [name for name in required_fields if name not in reason]
    if missing:
        raise ValueError(
            "measurement dry-run selection denial reason "
            f"missing fields: {missing}"
        )
    normalized = dict(reason)
    normalized["active"] = True
    normalized["resolved"] = False
    normalized["selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_selection_denial_receipt"] = False
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_denial_reconciliation_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "measurement dry-run denial reconciliation item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["reconciled"] = True
    normalized["resolved"] = False
    normalized["operator_selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_denial_reconciliation"] = False
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_handoff_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "measurement dry-run operator handoff item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["handoff_ready"] = True
    normalized["operator_selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_operator_handoff"] = False
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_handoff_review_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "measurement dry-run operator handoff review item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["reviewed"] = True
    normalized["approved"] = False
    normalized["operator_selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_operator_handoff_review"] = False
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_selection_candidate_field(
    field: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("field_id", "description")
    missing = [name for name in required_fields if name not in field]
    if missing:
        raise ValueError(
            "measurement dry-run operator selection candidate field "
            f"missing fields: {missing}"
        )
    normalized = dict(field)
    normalized["required"] = True
    normalized["populated"] = False
    normalized["selected"] = False
    normalized["operator_selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["valid_for_measurement_dryrun_operator_selection_packet_candidate"] = (
        False
    )
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_measurement_dryrun_operator_selection_packet_review_item(
    item: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("item_id", "description")
    missing = [name for name in required_fields if name not in item]
    if missing:
        raise ValueError(
            "measurement dry-run operator selection packet review item "
            f"missing fields: {missing}"
        )
    normalized = dict(item)
    normalized["reviewed"] = True
    normalized["approved"] = False
    normalized["selected"] = False
    normalized["operator_selection_recorded"] = False
    normalized["operator_gate_recorded"] = False
    normalized["operator_attested"] = False
    normalized["measurement_dryrun_packet_created"] = False
    normalized["measurement_dryrun_packet_executable"] = False
    normalized["measurement_dryrun_executed"] = False
    normalized["fixture_bound"] = False
    normalized["outcome_bound"] = False
    normalized["brier_resolution_computed"] = False
    normalized["valid_for_measurement_dryrun_operator_selection_packet_review"] = (
        False
    )
    normalized["valid_for_measurement_dryrun_operator_selection_packet_candidate"] = (
        False
    )
    normalized["valid_for_operator_action_selection"] = False
    normalized["valid_for_measurement_dryrun_execution_packet"] = False
    normalized["valid_for_measurement_dryrun_execution"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_held_out_attestation_requirement(
    requirement: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("requirement_id", "description")
    missing = [field for field in required_fields if field not in requirement]
    if missing:
        raise ValueError(f"held-out attestation requirement missing fields: {missing}")
    normalized = dict(requirement)
    normalized["satisfied"] = False
    normalized["valid_for_held_out_set_attestation"] = False
    normalized["valid_for_held_out_set_lock"] = False
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _normalize_outcome_policy_requirement(
    requirement: Mapping[str, Any],
) -> dict[str, Any]:
    required_fields = ("requirement_id", "description")
    missing = [field for field in required_fields if field not in requirement]
    if missing:
        raise ValueError(f"outcome policy requirement missing fields: {missing}")
    normalized = dict(requirement)
    normalized["satisfied"] = False
    normalized["valid_for_outcome_policy_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized


def _build_shadow_scoring_row(
    row: Mapping[str, Any],
    shadow_outcomes: Mapping[str, int],
) -> dict[str, Any]:
    forecast_id = str(row["forecast_id"])
    if forecast_id not in shadow_outcomes:
        raise ValueError(f"shadow outcome missing for forecast_id: {forecast_id}")
    shadow_outcome = int(shadow_outcomes[forecast_id])
    if shadow_outcome not in (0, 1):
        raise ValueError("shadow outcome must be 0 or 1")
    probability = float(row["probability"])
    return {
        "forecast_id": forecast_id,
        "question": row["question"],
        "probability": probability,
        "shadow_outcome": shadow_outcome,
        "shadow_brier_component": round((probability - shadow_outcome) ** 2, 6),
        "provenance": row["provenance"],
        "valid_for_fixture_binding": False,
        "valid_for_outcome_binding": False,
        "valid_for_brier_resolution": False,
        "brier_score": 0.1,
    }


def _normalize_fixture_row(row: Mapping[str, Any]) -> dict[str, Any]:
    required_fields = ("forecast_id", "question", "probability", "provenance")
    missing = [field for field in required_fields if field not in row]
    if missing:
        raise ValueError(f"fixture row missing required fields: {missing}")
    probability = float(row["probability"])
    if probability < 0 or probability > 1:
        raise ValueError("fixture row probability must be between 0 and 1")
    normalized = dict(row)
    normalized["probability"] = probability
    normalized["outcome"] = None
    normalized["valid_for_fixture_binding"] = False
    normalized["valid_for_outcome_binding"] = False
    normalized["valid_for_brier_resolution"] = False
    normalized.setdefault("brier_score", 0.1)
    return normalized
