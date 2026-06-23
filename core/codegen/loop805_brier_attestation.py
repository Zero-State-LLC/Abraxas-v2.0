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
