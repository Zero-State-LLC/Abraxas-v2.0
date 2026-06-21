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


def _normalize_requirement(requirement: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(requirement)
    normalized["satisfied"] = False
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
