#!/usr/bin/env python3
"""
AAL-Viz Operator Action Packet Adapter — projection/copy-only packet builder.

Reads:
  apps/aal-viz-live-console/public/projection-bundle.json
  out/metric_operator/metric_operator_frontier_recommendation_006.latest.json
  out/metric_operator/transport_computation_implementation_gate_001.latest.json
  out/metric_operator/transport_fixture_corpus_creation_receipt_001.latest.json
  out/metric_operator/transport_implementation_authorization_decision_record_001.latest.json
  out/metric_operator/transport_baseline_promotion_complete_001.latest.json

Writes:
  apps/aal-viz-live-console/public/operator-action-packets.json

Authority constraints (always enforced):
  execution_allowed              = false
  runtime_mutation_allowed       = false
  promotion_allowed              = false
  production_activation_allowed  = false
  metric_emission_allowed        = false
  forecast_influence_allowed     = false
  p43_lanes_allowed              = false

All generated packets are COPY-ONLY. No auto-apply. No execution.
Fails closed on missing provenance or invalid authority.
Never reads research_canary. Never writes to out/.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "apps" / "aal-viz-live-console" / "public" / "operator-action-packets.json"
SCHEMA_VERSION = "AALViz.OperatorActionPackets.v0.1"
GENERATED_BY = "BUILD_AAL_VIZ_OPERATOR_ACTION_PACKETS_001"

AUTHORITY: dict[str, bool] = {
    "execution_allowed": False,
    "runtime_mutation_allowed": False,
    "promotion_allowed": False,
    "production_activation_allowed": False,
    "metric_emission_allowed": False,
    "forecast_influence_allowed": False,
    "p43_lanes_allowed": False,
}

STANDARD_BLOCKED_SCOPES: list[str] = [
    "METRIC_EMISSION",
    "FORECAST_INFLUENCE",
    "P43_SURFACE_LANES",
    "PRODUCTION_ACTIVATION",
    "CANON_PROMOTION",
    "RUNTIME_MUTATION",
    "EXECUTION_AUTHORITY",
    "LP_SOLVER_INVOCATION_OUTSIDE_TEST_VECTOR_SCOPE",
]

# ── Source artifact paths ─────────────────────────────────────────────────────

_SRC_FRONTIER = "out/metric_operator/metric_operator_frontier_recommendation_006.latest.json"
_SRC_IMPL_GATE = "out/metric_operator/transport_computation_implementation_gate_001.latest.json"
_SRC_CORPUS_RECEIPT = "out/metric_operator/transport_fixture_corpus_creation_receipt_001.latest.json"
_SRC_AUTH_RECORD = "out/metric_operator/transport_implementation_authorization_decision_record_001.latest.json"
_SRC_PACK_VECTOR_UPDATE = "out/metric_operator/wasserstein_cpu_baseline_pack_vector_update_001.latest.json"
_SRC_PROMOTION_COMPLETE = "out/metric_operator/wasserstein_baseline_promotion_complete_001.latest.json"
_SRC_TRANSPORT_COMPUTATION_RECEIPT = "out/metric_operator/transport_computation_receipt_001.latest.json"
_SRC_TRANSPORT_PROMOTION_COMPLETE = "out/metric_operator/transport_baseline_promotion_complete_001.latest.json"
_SRC_CHAMFER_PROMOTION_COMPLETE = "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json"
_SRC_BUNDLE = "apps/aal-viz-live-console/public/projection-bundle.json"
_SRC_RANK6_SELECTION = "out/metric_operator/rank6_operator_selection_001.latest.json"

# ── Helpers ───────────────────────────────────────────────────────────────────


def _guard_no_research_canary(path: Path) -> None:
    for part in path.parts:
        if part.startswith("research_canary"):
            raise ValueError(f"Forbidden: research_canary access blocked: {path}")


def _load_safe(path: Path) -> dict[str, Any] | None:
    _guard_no_research_canary(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"WARN malformed JSON in {path.relative_to(ROOT)}: {exc}\n")
        return None


def _require(path: Path, label: str) -> dict[str, Any]:
    data = _load_safe(path)
    if data is None:
        raise ValueError(f"FAIL_CLOSED: required source artifact missing: {label} ({path.relative_to(ROOT)})")
    return data


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _h(d: dict[str, Any]) -> str:
    return str(d.get("canonical_hash", "UNKNOWN"))[:16] + "…"


# ── Packet builders ───────────────────────────────────────────────────────────

_TRANSPORT_COMPUTATION_PROMPT = """\
TRANSPORT COMPUTATION IMPLEMENTATION — BOUNDED SCOPE AUTHORIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gate:     transport_computation_implementation_gate_001
          hash: a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0

Auth:     transport_implementation_authorization_decision_record_001
          hash: 2cd378187842043c93d4a66ed6e0f6a83b59cc1a3a8415c259abd70e5e1cb935

Frontier: metric_operator_frontier_recommendation_006
          hash: bdedd43c2a87d13c54a2f352e45c13effbfa48aa827898a308877f38cb18896e

━━━ AUTHORIZED SCOPE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Algorithm:    DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH
Computation:  TEST_VECTOR_COMPUTATION_ONLY
Lane:         SHADOW
Bounded:      true (4×4 max, 16 transport variables max)

━━━ SEVEN LOCKED CONSTANTS (all sealed in gate artifact) ━━━━━━━━━

1  LP solver variant:            DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH
2  Max problem size:             supply_len ≤ 4, demand_len ≤ 4
3  Balance tolerance:            epsilon_abs = 0.0, epsilon_rel = 0.0
4  Cost matrix magnitude bound:  1,000,000.0
5  Pivot rule:                   LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR
6  Tie-breaking rule:            ROW_MAJOR_THEN_COLUMN_MAJOR
7  NOT_COMPUTABLE branches:      9 branches (enumerated below)

━━━ NOT_COMPUTABLE BRANCHES (9, all sealed) ━━━━━━━━━━━━━━━━━━━━━━

  COST_MATRIX_SHAPE_MISMATCH
  EMPTY_DEMAND_VECTOR
  EMPTY_SUPPLY_VECTOR
  NEGATIVE_COST_VALUE
  NEGATIVE_SUPPLY_VALUE
  NON_FINITE_COST_VALUE
  NON_FINITE_DEMAND_VALUE
  NON_FINITE_SUPPLY_VALUE
  UNBALANCED_SUPPLY_DEMAND

━━━ FIXTURE CORPUS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Corpus hash: 971a9bbc23850a6a4e9fffb16b6de1b48dfb8e060bb61d127c2d27d2454bb78e
Location:    input/fixtures/transport/ (15 fixtures)

  VALID (6):          tv-valid-001 … tv-valid-006
  INVALID (4):        reject expected — no LP invocation
  NOT_COMPUTABLE (5): NOT_COMPUTABLE expected

━━━ TASK ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Produce: out/metric_operator/transport_computation_receipt_001.latest.json

Required receipt fields:
  canonical_hash             — sha256 of deterministic canonical JSON
  computation_executed: true
  operator_id: "TRANSPORT"
  fixture_results            — list of {fixture_id, expected, actual, matched}
  all_valid_passed: bool
  all_invalid_rejected: bool
  all_not_computable_routed: bool
  authority_locks:
    computation_executed: true
    emits_metric_values: false
    forecast_influence: false
    p43_surface_lanes_authorized: false
    canon_promotion: false
    production_activation: false

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  This is a COPY_PROMPT packet only.
  The operator reads, adapts if needed, and implements manually.
  No auto-execution. No auto-merge. No out/ mutation from this console.
  Doctrine validator must pass before any PR is created.\
"""

_TRANSPORT_VALIDATION_CHECKLIST: list[str] = [
    "[ ] 1.  Gate artifact verified: transport_computation_implementation_gate_001",
    "[ ]     gate hash: a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0",
    "[ ] 2.  All 7 locked constants confirmed sealed before implementation begins",
    "[ ] 3.  LP solver variant = DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH only",
    "[ ] 4.  Problem size does not exceed 4×4 (max 16 transport variables)",
    "[ ] 5.  Balance tolerance exactly: epsilon_abs=0.0, epsilon_rel=0.0",
    "[ ] 6.  Pivot rule = LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR",
    "[ ] 7.  Tie-breaking rule = ROW_MAJOR_THEN_COLUMN_MAJOR",
    "[ ] 8.  All 9 NOT_COMPUTABLE branches handled and return NOT_COMPUTABLE",
    "[ ] 9.  All 6 VALID fixtures pass (tv-valid-001 through tv-valid-006)",
    "[ ] 10. All 4 INVALID fixtures are rejected (no LP invocation)",
    "[ ] 11. All 5 NOT_COMPUTABLE fixtures return NOT_COMPUTABLE",
    "[ ] 12. No metric values emitted from computation",
    "[ ] 13. Forecast influence remains blocked",
    "[ ] 14. No P43 surface lanes opened",
    "[ ] 15. No canon mutation of any kind",
    "[ ] 16. Receipt produced at out/metric_operator/transport_computation_receipt_001.latest.json",
    "[ ] 17. Receipt includes: canonical_hash, computation_executed: true, fixture_results",
    "[ ] 18. Receipt authority_locks confirm all governance flags false",
    "[ ] 19. python scripts/run_doctrine_validator.py passes",
    "[ ] 20. Canon validation CI passes",
]

_AAL_VIZ_NEXT_ADAPTER_CHECKLIST: list[str] = [
    "Current adapters active: (1) Artifact Index Adapter, (2) Operator Action Packet Adapter",
    "",
    "COMPLETED (no adapter action required):",
    "[x] A. TRANSPORT COMPUTATION RECEIPT ADAPTER — DONE",
    "[x]    transport_computation_receipt_001 present; TRANSPORT was READY/95%",
    "[x] B. WASSERSTEIN BASELINE PROMOTION ADAPTER — DONE",
    "[x]    wasserstein_baseline_promotion_complete_001 present; WASSERSTEIN is READY_SHADOW_STUB_CLOSED/100%",
    "[x] C. TRANSPORT BASELINE PROMOTION FOLLOW-THROUGH ADAPTER — DONE",
    "[x]    transport_baseline_promotion_complete_001 present; TRANSPORT is READY_SHADOW_STUB_CLOSED/100%",
    "[x] D. CHAMFER BASELINE PROMOTION FOLLOW-THROUGH ADAPTER — DONE",
    "[x]    chamfer_baseline_promotion_complete_001 present; CHAMFER is READY_SHADOW_STUB_CLOSED/100%",
    "[x] E. FIVE-OPERATOR SHADOW STUB PARITY RECEIPT — DONE (BATCH_B)",
    "[x]    five_operator_shadow_stub_parity_receipt_001 present; all five SHADOW_STUB_ONLY",
    "[x] F. RANK6_OPERATOR_SELECTION ADAPTER — DONE (BATCH_C)",
    "[x]    rank6_operator_selection_001 present; HEAVY_TAIL selected (42/45)",
    "[x]    HEAVY_TAIL projection: RANK6_SELECTED/10%",
    "",
    "NEXT STEP — HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION_AUTHORIZATION",
    "[ ] G1. Produce HEAVY_TAIL implementation authorization artifact",
    "[ ] G2. Authorization must explicitly grant: fixture_creation_authorized=true,",
    "[ ]     baseline_pack_update_authorized=true, shadow_stub_only posture preserved",
    "[ ] G3. Do NOT grant: metric emission, forecast influence, P43 lanes,",
    "[ ]     runtime mutation, production activation, canon promotion, execution authority",
    "[ ] G4. Wire HEAVY_TAIL to OPERATOR_DEFS in projection bundle builder",
    "[ ] G5. Re-run both builders and verify HEAVY_TAIL advances",
    "",
    "AUTHORITY REMINDERS FOR ALL ADAPTERS:",
    "[ ] projection_only: true",
    "[ ] Mutation of any out/ artifact: blocked",
    "[ ] research_canary access: blocked",
    "[ ] Fail closed on missing provenance",
    "[ ] Doctrine validator must pass before any PR",
]

_SEALED_PAUSE_BODY = """\
SEALED PAUSE / NO-OP — RANK 1 FRONTIER OPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontier ref: metric_operator_frontier_recommendation_006
Frontier hash: bdedd43c2a87d13c54a2f352e45c13effbfa48aa827898a308877f38cb18896e
Option rank:  1 (highest ranked)
Posture:      ADVISORY_ONLY

This option records that no immediate action is taken.
All governance flags remain false.
All authority locks remain enforced.
The frontier state is preserved as-is.
No computation is initiated.
No canon mutation occurs.

Use when: the operator needs time to review frontier state before
deciding which bounded action to authorize next.

Evidence refs:
  TransportImplementationAuthorizationDecisionRecord.v1:
    transport_implementation_authorization_decision_record_001
  MetricOperatorCrossOperatorParityReceipt.v1:
    metric_operator_cross_operator_parity_receipt_003
  MetricOperatorFrontierRecommendation.v1:
    metric_operator_frontier_recommendation_005\
"""


def _build_transport_computation_prompt(
    gate: dict[str, Any],
    receipt: dict[str, Any],
    auth: dict[str, Any],
    frontier: dict[str, Any],
) -> dict[str, Any]:
    gate_hash = gate.get("canonical_hash", "UNKNOWN")
    receipt_hash = receipt.get("canonical_hash", "UNKNOWN")
    auth_hash = auth.get("canonical_hash", "UNKNOWN")
    frontier_hash = frontier.get("canonical_hash", "UNKNOWN")

    return {
        "packet_id": "pkt-transport-computation-bounded-prompt-001",
        "source_frontier_ref": "metric_operator_frontier_recommendation_006",
        "action_title": "TRANSPORT Bounded Computation Implementation Prompt",
        "action_type": "COPY_PROMPT",
        "operator_id": "transport",
        "recommended_next_step": "TRANSPORT_COMPUTATION_IMPLEMENTATION",
        "authority_required": "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_001",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _TRANSPORT_COMPUTATION_PROMPT,
        "validation_checklist": _TRANSPORT_VALIDATION_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"transport_computation_implementation_gate_001:{gate_hash}",
            f"transport_fixture_corpus_creation_receipt_001:{receipt_hash}",
            f"transport_implementation_authorization_decision_record_001:{auth_hash}",
            f"metric_operator_frontier_recommendation_006:{frontier_hash}",
        ],
        "fail_closed_reason": None,
    }


def _build_transport_validation_checklist(
    gate: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    gate_hash = gate.get("canonical_hash", "UNKNOWN")
    receipt_hash = receipt.get("canonical_hash", "UNKNOWN")

    return {
        "packet_id": "pkt-transport-validation-checklist-001",
        "source_frontier_ref": "metric_operator_frontier_recommendation_006",
        "action_title": "TRANSPORT Test Vector Validation Checklist",
        "action_type": "COPY_CHECKLIST",
        "operator_id": "transport",
        "recommended_next_step": "TRANSPORT_VALIDATION",
        "authority_required": "TRANSPORT_COMPUTATION_IMPLEMENTATION_GATE_001",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": (
            "Run this checklist against transport computation receipt before PR creation.\n"
            f"Gate hash: {gate_hash}\n"
            f"Corpus hash: {receipt_hash}"
        ),
        "validation_checklist": _TRANSPORT_VALIDATION_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"transport_computation_implementation_gate_001:{gate_hash}",
            f"transport_fixture_corpus_creation_receipt_001:{receipt_hash}",
        ],
        "fail_closed_reason": None,
    }


def _build_aal_viz_next_adapter_checklist() -> dict[str, Any]:
    return {
        "packet_id": "pkt-aal-viz-next-adapter-checklist-001",
        "source_frontier_ref": None,
        "action_title": "AAL-Viz Next Adapter Development Checklist",
        "action_type": "COPY_CHECKLIST",
        "subsystem_id": "aal_viz",
        "recommended_next_step": "AAL_VIZ_NEXT_ADAPTER",
        "authority_required": "OPERATOR_INSTRUCTION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": (
            "Three candidate next adapters based on current frontier state.\n"
            "Pick the one whose preconditions are met, implement manually, then re-run builders."
        ),
        "validation_checklist": _AAL_VIZ_NEXT_ADAPTER_CHECKLIST,
        "blocked_scopes": [
            "METRIC_EMISSION",
            "FORECAST_INFLUENCE",
            "P43_SURFACE_LANES",
            "PRODUCTION_ACTIVATION",
            "CANON_PROMOTION",
            "RUNTIME_MUTATION",
            "EXECUTION_AUTHORITY",
        ],
        "provenance_refs": [
            "build_aal_viz_projection_bundle.py:ARTIFACT_INDEX_ADAPTER",
            "build_aal_viz_operator_action_packets.py:OPERATOR_ACTION_PACKET_ADAPTER",
        ],
        "fail_closed_reason": None,
    }


_WASSERSTEIN_BASELINE_PROMOTION_CHECKLIST: list[str] = [
    "[ ] 1.  Verify pack vector update present: wasserstein_cpu_baseline_pack_vector_update_001",
    "[ ]     pack_vector_update hash: b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134",
    "[ ] 2.  Verify operator closure present: wasserstein_cpu_baseline_computation_operator_closure_001",
    "[ ]     operator_closure hash: 36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd",
    "[ ] 3.  Confirm cpu_baseline_computation_phase_status == COMPUTATION_PHASE_CLOSED",
    "[ ] 4.  Confirm baseline_promotion_authorized == false in closure artifact",
    "[ ] 5.  Operator decision: approve or defer WASSERSTEIN baseline promotion",
    "[ ] 6.  If approving: produce a new authorization decision artifact granting baseline_promotion_authorized=true",
    "[ ] 7.  If deferring: record SEALED_PAUSE and preserve current authority state",
    "[ ] 8.  No metric values may be emitted regardless of promotion decision",
    "[ ] 9.  No forecast influence regardless of promotion decision",
    "[ ] 10. No P43 surface lanes regardless of promotion decision",
    "[ ] 11. python scripts/run_doctrine_validator.py passes",
    "[ ] 12. git diff HEAD -- out/research_canary* is empty",
]

_WASSERSTEIN_BASELINE_PROMOTION_BODY = """\
WASSERSTEIN BASELINE PROMOTION DECISION — OPERATOR REVIEW REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current state:
  Pack vector update:   wasserstein_cpu_baseline_pack_vector_update_001
  Pack vector hash:     b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134
  CPU baseline status:  COMPUTATION_PHASE_CLOSED
  Operator closure:     wasserstein_cpu_baseline_computation_operator_closure_001
  Closure hash:         36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd

━━━ CURRENT AUTHORITY STATE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  baseline_promotion_authorized:  false (BLOCKED — explicit governance hold)
  emits_metric_values:            false
  forecast_influence:             false
  p43_surface_lanes_authorized:   false
  production_activation:          false
  canon_promotion:                false
  runtime_mutation:               false

━━━ WHAT CLOSED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  5/5 valid fixtures matched (WASSERSTEIN CPU baseline computation)
  5/5 invalid fixtures rejected as INVALID_INPUT
  4/4 NOT_COMPUTABLE fixtures closed
  Helper kernels scoped to TEST_VECTOR_FIXTURE_HELPER_KERNELS_ONLY

━━━ WHAT REMAINS BLOCKED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Baseline promotion requires a new explicit operator authorization decision.
  The existing closure artifact does NOT authorize promotion.
  No further chain progress without an explicit WASSERSTEIN_BASELINE_PROMOTION_DECISION.

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  This is a COPY_PROMPT packet only. No auto-apply. No auto-promotion.
  No out/ mutation from this console.
  Doctrine validator must pass before any PR is created.\
"""


def _build_wasserstein_baseline_promotion_packet(
    pack_vector: dict[str, Any],
) -> dict[str, Any]:
    pack_hash = pack_vector.get("canonical_hash", "UNKNOWN")
    return {
        "packet_id": "pkt-wasserstein-baseline-promotion-decision-001",
        "source_frontier_ref": "wasserstein_cpu_baseline_pack_vector_update_001",
        "action_title": "WASSERSTEIN Baseline Promotion Decision — Operator Review Required",
        "action_type": "REVIEW_REQUIRED",
        "operator_id": "wasserstein",
        "recommended_next_step": "WASSERSTEIN_BASELINE_PROMOTION_DECISION",
        "authority_required": "OPERATOR_DECISION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _WASSERSTEIN_BASELINE_PROMOTION_BODY,
        "validation_checklist": _WASSERSTEIN_BASELINE_PROMOTION_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"wasserstein_cpu_baseline_pack_vector_update_001:{pack_hash}",
            "wasserstein_cpu_baseline_computation_operator_closure_001:"
            "36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd",
        ],
        "fail_closed_reason": None,
    }


def _build_sealed_pause_packet(frontier: dict[str, Any]) -> dict[str, Any]:
    frontier_hash = frontier.get("canonical_hash", "UNKNOWN")
    ranked = frontier.get("ranked_options", [])
    sealed_pause = next(
        (r for r in ranked if r.get("option_id") == "G_SEALED_PAUSE"), None
    )
    rank = sealed_pause.get("rank", 1) if sealed_pause else 1

    return {
        "packet_id": "pkt-sealed-pause-review-001",
        "source_frontier_ref": "metric_operator_frontier_recommendation_006",
        "action_title": f"Sealed Pause / No-Op (Rank {rank} Frontier Option)",
        "action_type": "REVIEW_REQUIRED",
        "subsystem_id": "global",
        "recommended_next_step": "OPERATOR_REVIEW_REQUIRED",
        "authority_required": "OPERATOR_DECISION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _SEALED_PAUSE_BODY,
        "validation_checklist": [
            "[ ] 1. Operator has reviewed all frontier options",
            "[ ] 2. Sealed pause is the correct choice for current session",
            "[ ] 3. All authority locks remain enforced",
            "[ ] 4. No out/ artifact mutations have occurred",
            "[ ] 5. research_canary artifacts remain untouched",
        ],
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"metric_operator_frontier_recommendation_006:{frontier_hash}",
        ],
        "fail_closed_reason": None,
    }


_TRANSPORT_COMPUTATION_COMPLETE_BODY = """\
TRANSPORT COMPUTATION COMPLETE — FOLLOW-THROUGH REVIEW REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Computation receipt confirmed:
  transport_computation_receipt_001
  receipt_status: TRANSPORT_COMPUTATION_RECEIPT_COMPLETE
  computation_executed: true
  all_valid_passed:     true

Current TRANSPORT projection state:
  status:         READY
  completion_pct: 95
  ceiling:        95  (no promotion artifact wired to projection builder)

━━━ WHAT CLOSED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  6/6 VALID fixtures passed (tv-valid-001 through tv-valid-006)
  4/4 INVALID fixtures rejected (no LP invocation)
  5/5 NOT_COMPUTABLE fixtures routed correctly
  7 locked constants confirmed sealed
  Algorithm: DETERMINISTIC_ENUMERATED_BASIC_FEASIBLE_SEARCH
  Pivot rule: LEXICOGRAPHIC_MIN_COST_THEN_ROW_MAJOR
  Tie-breaking: ROW_MAJOR_THEN_COLUMN_MAJOR

━━━ WHAT REMAINS OPEN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  TRANSPORT projection capped at 95% until a follow-through
  promotion artifact is produced and wired to promotion_key.

  Candidate follow-through action:
    1. Produce transport_baseline_promotion_gate (or closure record)
    2. Wire to OPERATOR_DEFS['transport']['promotion_key']
       in scripts/build_aal_viz_projection_bundle.py
    3. Re-run: python scripts/build_aal_viz_projection_bundle.py
    4. Verify TRANSPORT advances: READY/95% → READY/100%
    5. Rebuild action packets: python scripts/build_aal_viz_operator_action_packets.py
    6. Full validation sequence passes

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No auto-execution. No auto-promotion. No out/ mutation.
  Doctrine validator must pass before any PR is created.\
"""

_TRANSPORT_FOLLOW_THROUGH_CHECKLIST: list[str] = [
    "[ ] 1.  Verify transport_computation_receipt_001 is present",
    "[ ]     receipt_status: TRANSPORT_COMPUTATION_RECEIPT_COMPLETE",
    "[ ]     canonical_hash: a1fa0921830bbab5e4c68f7975d056e80788f0a079b26739d1ad6d4f0d9d3831",
    "[ ] 2.  Confirm computation_executed == true",
    "[ ] 3.  Confirm all_valid_passed == true",
    "[ ] 4.  Decide: produce transport_baseline_promotion_gate artifact",
    "[ ]     OR: produce transport_chain_closure_record if no promotion is warranted",
    "[ ] 5.  If producing promotion gate: wire promotion_key in OPERATOR_DEFS['transport']",
    "[ ]     in scripts/build_aal_viz_projection_bundle.py",
    "[ ] 6.  Re-run: python scripts/build_aal_viz_projection_bundle.py",
    "[ ] 7.  Verify TRANSPORT advances: READY/95% → READY/100%",
    "[ ] 8.  Re-run: python scripts/build_aal_viz_operator_action_packets.py",
    "[ ] 9.  python -m pytest passes",
    "[ ] 10. python scripts/run_doctrine_validator.py passes",
    "[ ] 11. No metric values emitted regardless of decision",
    "[ ] 12. No forecast influence regardless of decision",
    "[ ] 13. No P43 surface lanes regardless of decision",
    "[ ] 14. No canon mutation of any kind",
    "[ ] 15. git diff HEAD -- out/research_canary* is empty",
]

_CHAMFER_BASELINE_PROMOTION_BODY = """\
CHAMFER BASELINE PROMOTION — FOLLOW-THROUGH REVIEW REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current CHAMFER projection state:
  status:         READY
  completion_pct: 95
  ceiling:        95  (baseline promotion gate not yet wired)

━━━ WHAT CLOSED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Advisory phase closed (frontier bundle: PR #329)
  Artifacts: RegistryStabilization, ParityReceipt, FrontierRecommendation
  Baseline promoted to SHADOW_STUB_ONLY (PR #328)
  Advisory-only planning bundle complete (PR #330)

━━━ WHAT REMAINS OPEN ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CHAMFER projection capped at 95% until a baseline promotion
  gate artifact is produced and wired to promotion_key.

  Candidate follow-through action:
    1. Produce chamfer_baseline_promotion_gate artifact
    2. Wire to OPERATOR_DEFS['chamfer_distance']['promotion_key']
       in scripts/build_aal_viz_projection_bundle.py
    3. Re-run: python scripts/build_aal_viz_projection_bundle.py
    4. Verify CHAMFER advances: READY/95% → READY/100%
    5. Rebuild action packets: python scripts/build_aal_viz_operator_action_packets.py
    6. Full validation sequence passes

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No auto-execution. No auto-promotion. No out/ mutation.
  Doctrine validator must pass before any PR is created.\
"""

_CHAMFER_FOLLOW_THROUGH_CHECKLIST: list[str] = [
    "[ ] 1.  Verify CHAMFER advisory phase is closed",
    "[ ]     Last ledger event: CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT_001",
    "[ ] 2.  Verify CHAMFER baseline_promotion_phase_complete flag if present",
    "[ ] 3.  Decide: produce chamfer_baseline_promotion_gate artifact",
    "[ ] 4.  Wire promotion_key in OPERATOR_DEFS['chamfer_distance']",
    "[ ]     in scripts/build_aal_viz_projection_bundle.py",
    "[ ] 5.  Re-run: python scripts/build_aal_viz_projection_bundle.py",
    "[ ] 6.  Verify CHAMFER advances: READY/95% → READY/100%",
    "[ ] 7.  Re-run: python scripts/build_aal_viz_operator_action_packets.py",
    "[ ] 8.  python -m pytest passes",
    "[ ] 9.  python scripts/run_doctrine_validator.py passes",
    "[ ] 10. No metric values emitted regardless of decision",
    "[ ] 11. No forecast influence regardless of decision",
    "[ ] 12. No P43 surface lanes regardless of decision",
    "[ ] 13. No canon mutation of any kind",
    "[ ] 14. git diff HEAD -- out/research_canary* is empty",
]


def _build_transport_computation_complete_packet(
    transport_receipt: dict[str, Any],
) -> dict[str, Any]:
    receipt_hash = transport_receipt.get("canonical_hash", "UNKNOWN")
    return {
        "packet_id": "pkt-transport-computation-complete-review-001",
        "source_frontier_ref": "transport_computation_receipt_001",
        "action_title": "TRANSPORT Computation Complete — Follow-Through Review Required",
        "action_type": "REVIEW_REQUIRED",
        "operator_id": "transport",
        "recommended_next_step": "TRANSPORT_PROMOTION_OR_CLOSURE_FOLLOW_THROUGH",
        "authority_required": "OPERATOR_DECISION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _TRANSPORT_COMPUTATION_COMPLETE_BODY,
        "validation_checklist": _TRANSPORT_FOLLOW_THROUGH_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"transport_computation_receipt_001:{receipt_hash}",
            "transport_computation_implementation_gate_001:"
            "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0",
        ],
        "fail_closed_reason": None,
    }


_TRANSPORT_BASELINE_PROMOTION_CLOSED_BODY = """\
TRANSPORT BASELINE PROMOTION COMPLETE — PHASE CLOSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Artifact confirmed:
  transport_baseline_promotion_complete_001
  complete_status: TRANSPORT_BASELINE_PROMOTION_COMPLETE
  canonical_hash:  92ece46ca0eb538eb12acdc0a11a8a1c8c74f3729db34a1ce43d30866dbb4c1f

TRANSPORT projection state:
  status:         READY_SHADOW_STUB_CLOSED
  completion_pct: 100
  posture:        VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY

━━━ WHAT CLOSED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  TRANSPORT promoted from NOT_IMPLEMENTED → SHADOW_STUB_ONLY (PR #399)
  Baseline pack hash updated to 05a72025… (PR #400)
  Five-operator parity confirmed:
    WASSERSTEIN, CHAMFER_DISTANCE, GEODESIC, NORM_GEOMETRY, TRANSPORT
    all VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY

━━━ WHAT REMAINS BLOCKED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Metric emission:         blocked
  Forecast influence:      blocked
  P43 surface lanes:       blocked
  Production activation:   blocked
  Canon promotion:         blocked
  Runtime mutation:        blocked
  Execution authority:     blocked

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Advisory/shadow-only posture preserved.
  No auto-execution. No auto-promotion. No out/ mutation.
  Doctrine validator must pass before any PR is created.\
"""

_TRANSPORT_PROMOTION_CLOSED_CHECKLIST: list[str] = [
    "[x] 1.  transport_baseline_promotion_complete_001 present",
    "[x]     complete_status: TRANSPORT_BASELINE_PROMOTION_COMPLETE",
    "[x]     canonical_hash: 92ece46ca0eb538eb12acdc0a11a8a1c8c74f3729db34a1ce43d30866dbb4c1f",
    "[x] 2.  TRANSPORT vector: VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY",
    "[x] 3.  Baseline pack hash: 05a72025… (post-promotion)",
    "[x] 4.  Five-operator parity confirmed in pack",
    "[x] 5.  CHAMFER_BASELINE_PROMOTION_FOLLOW_THROUGH — DONE",
    "[x]     chamfer_baseline_promotion_complete_001 present; CHAMFER is READY_SHADOW_STUB_CLOSED/100%",
    "[ ] 6.  Review remaining frontier options (RANK6_OPERATOR_SELECTION or SEALED_PAUSE)",
    "[ ] 6.  All authority locks remain false",
    "[ ] 7.  No out/ artifact mutations",
    "[ ] 8.  research_canary artifacts untouched",
    "[ ] 9.  python scripts/run_doctrine_validator.py passes",
]


def _build_transport_baseline_promotion_closed_packet(
    promotion_complete: dict[str, Any],
    transport_receipt: dict[str, Any],
) -> dict[str, Any]:
    promo_hash = promotion_complete.get("canonical_hash", "UNKNOWN")
    receipt_hash = transport_receipt.get("canonical_hash", "UNKNOWN")
    return {
        "packet_id": "pkt-transport-baseline-promotion-closed-001",
        "source_frontier_ref": "transport_baseline_promotion_complete_001",
        "action_title": "TRANSPORT Baseline Promotion Complete — Phase Closed",
        "action_type": "REVIEW_REQUIRED",
        "operator_id": "transport",
        "recommended_next_step": "CHAMFER_BASELINE_PROMOTION_FOLLOW_THROUGH",
        "authority_required": "OPERATOR_DECISION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _TRANSPORT_BASELINE_PROMOTION_CLOSED_BODY,
        "validation_checklist": _TRANSPORT_PROMOTION_CLOSED_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"transport_baseline_promotion_complete_001:{promo_hash}",
            f"transport_computation_receipt_001:{receipt_hash}",
        ],
        "fail_closed_reason": None,
    }


_CHAMFER_BASELINE_PROMOTION_CLOSED_BODY = """\
CHAMFER BASELINE PROMOTION COMPLETE — PHASE CLOSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Artifact confirmed:
  chamfer_baseline_promotion_complete_001
  complete_status: CHAMFER_BASELINE_PROMOTION_COMPLETE
  canonical_hash:  89a8a59cf0791b87148baef87fbb75b8a2ebb5e0dd804b93af1448ad8fade2b1

CHAMFER projection state:
  status:         READY_SHADOW_STUB_CLOSED
  completion_pct: 100
  posture:        VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY

━━━ WHAT CLOSED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CHAMFER was already promoted to SHADOW_STUB_ONLY (PR #328)
  Follow-through audit completed (PR #402)
  Baseline promotion review completed (PR #403)
  Baseline promotion complete governance closure (PR #404)
  No pack re-promotion was performed or required

━━━ WHAT REMAINS BLOCKED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Metric emission:         blocked
  Forecast influence:      blocked
  P43 surface lanes:       blocked
  Production activation:   blocked
  Canon promotion:         blocked
  Runtime mutation:        blocked
  Execution authority:     blocked

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Advisory/shadow-only posture preserved.
  No auto-execution. No auto-promotion. No out/ mutation.
  Doctrine validator must pass before any PR is created.\
"""

_CHAMFER_PROMOTION_CLOSED_CHECKLIST: list[str] = [
    "[x] 1.  chamfer_baseline_promotion_complete_001 present",
    "[x]     complete_status: CHAMFER_BASELINE_PROMOTION_COMPLETE",
    "[x]     canonical_hash: 89a8a59cf0791b87148baef87fbb75b8a2ebb5e0dd804b93af1448ad8fade2b1",
    "[x] 2.  CHAMFER vector: VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY",
    "[x] 3.  Pack re-promotion not required; pack unchanged",
    "[x] 4.  All 9 governance sections confirmed (review, audit, complete_review, ev_receipt,",
    "[x]     baseline_state, no_repromotion, wiring_pending, authority_locks, blocked_scopes)",
    "[ ] 5.  Review remaining frontier options (RANK6_OPERATOR_SELECTION, SEALED_PAUSE)",
    "[ ] 6.  All authority locks remain false",
    "[ ] 7.  No out/ artifact mutations",
    "[ ] 8.  research_canary artifacts untouched",
    "[ ] 9.  python scripts/run_doctrine_validator.py passes",
]


_HEAVY_TAIL_IMPL_AUTH_BODY = """\
HEAVY_TAIL SHADOW-STUB IMPLEMENTATION — AUTHORIZATION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Selection confirmed:
  rank6_operator_selection_001
  selection_status: RANK6_OPERATOR_SELECTION_COMPLETE
  selected_operator: HEAVY_TAIL
  score: 42 / 45
  canonical_hash: 46a4ef4eaf696feb53d53d82476ae302e1f83c7a0fe6bd5cc2b70245ce403619

Parity receipt source:
  five_operator_shadow_stub_parity_receipt_001
  canonical_hash: 28c481fdeed3463ae9509820b987cc1ff10e9351969ece4c9f1bbe75b1d8d2ed

Current HEAVY_TAIL state:
  vector_type:               VALID_METADATA_VECTOR
  computation_status:        NOT_IMPLEMENTED
  projection_status:         RANK6_SELECTED / 10%
  implementation_authorized: false (this packet does NOT authorize implementation)

━━━ WHAT SELECTION AUTHORIZED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Selection only: HEAVY_TAIL designated as Rank-6 operator (BATCH_C)
  No implementation performed in selection artifact

━━━ WHAT REMAINS BLOCKED (until explicit authorization artifact) ━━

  HEAVY_TAIL implementation:       BLOCKED
  Fixture corpus creation:         BLOCKED
  Baseline pack update:            BLOCKED
  Metric emission:                 BLOCKED
  Forecast influence:              BLOCKED
  P43 surface lanes:               BLOCKED
  Runtime mutation:                BLOCKED
  Production activation:           BLOCKED
  Canon promotion:                 BLOCKED
  Execution authority:             BLOCKED
  Inference authority:             BLOCKED

━━━ REQUIRED AUTHORIZATION ARTIFACT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To authorize HEAVY_TAIL shadow-stub implementation, produce a new
governance artifact that explicitly grants:
  fixture_creation_authorized:      true
  baseline_pack_update_authorized:  true
  shadow_stub_only_posture:         preserved (no metric emission)
  implementation_authorized:        true
  rank6_implementation_authorized:  true

And explicitly keeps blocked:
  emits_metric_values:              false
  forecast_influence:               false
  p43_surface_lanes_authorized:     false
  runtime_mutation:                 false
  production_activation:            false
  canon_promotion:                  false
  execution_authority:              false
  inference_authority:              false

━━━ SELECTION RATIONALE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HEAVY_TAIL scores 42/45 across nine deterministic criteria:
  fixture_feasibility:              5/5
  schema_complexity_score:          5/5
  numerical_risk_score:             5/5
  deterministic_fixture_generation: 5/5
  governance_risk_score:            5/5
  implementation_dependency_risk:   5/5
  shadow_stub_feasibility:          5/5
  proximity_to_cohort:              3/5
  aal_viz_projection_usefulness:    4/5

Schema: alpha (shape exponent), sample_count, expected_tail_threshold
Fixtures: analytically bounded integer sequences with closed-form moments
No external operator dependency. Fully shadow-stub-able.

━━━ AUTHORITY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  This is a REVIEW_REQUIRED packet only. No auto-execution.
  No auto-implementation. No out/ mutation from this console.
  Doctrine validator must pass before any PR is created.\
"""

_HEAVY_TAIL_IMPL_AUTH_CHECKLIST: list[str] = [
    "[ ] 1.  Verify rank6_operator_selection_001 is present",
    "[ ]     selection_status: RANK6_OPERATOR_SELECTION_COMPLETE",
    "[ ]     selected_operator: HEAVY_TAIL",
    "[ ]     canonical_hash: 46a4ef4eaf696feb53d53d82476ae302e1f83c7a0fe6bd5cc2b70245ce403619",
    "[ ] 2.  Verify five_operator_shadow_stub_parity_receipt_001 is present",
    "[ ]     canonical_hash: 28c481fdeed3463ae9509820b987cc1ff10e9351969ece4c9f1bbe75b1d8d2ed",
    "[ ] 3.  Produce HEAVY_TAIL implementation authorization artifact",
    "[ ]     Explicitly grant: fixture_creation_authorized=true",
    "[ ]     Explicitly grant: baseline_pack_update_authorized=true",
    "[ ]     Explicitly grant: rank6_implementation_authorized=true",
    "[ ]     Preserve: shadow_stub_only_posture=true",
    "[ ] 4.  Keep all emission/mutation/activation flags false",
    "[ ] 5.  Wire HEAVY_TAIL to OPERATOR_DEFS in projection bundle builder",
    "[ ] 6.  Re-run: python scripts/build_aal_viz_projection_bundle.py",
    "[ ] 7.  Re-run: python scripts/build_aal_viz_operator_action_packets.py",
    "[ ] 8.  Verify HEAVY_TAIL advances from RANK6_SELECTED to PARTIAL or higher",
    "[ ] 9.  python -m pytest passes",
    "[ ] 10. python scripts/run_doctrine_validator.py passes",
    "[ ] 11. No metric values emitted",
    "[ ] 12. No forecast influence",
    "[ ] 13. No P43 surface lanes opened",
    "[ ] 14. No canon mutation of any kind",
    "[ ] 15. git diff HEAD -- out/research_canary* is empty",
]


def _build_heavy_tail_implementation_authorization_packet(
    rank6: dict[str, Any],
) -> dict[str, Any]:
    rank6_hash = rank6.get("canonical_hash", "UNKNOWN")
    return {
        "packet_id": "pkt-heavy-tail-shadow-stub-implementation-authorization-001",
        "source_frontier_ref": "rank6_operator_selection_001",
        "action_title": "HEAVY_TAIL Shadow-Stub Implementation — Authorization Required",
        "action_type": "REVIEW_REQUIRED",
        "operator_id": "heavy_tail",
        "recommended_next_step": "HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION",
        "authority_required": "OPERATOR_AUTHORIZATION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "implementation_authorized": False,
        "fixture_creation_authorized": False,
        "baseline_pack_update_authorized": False,
        "prompt_body": _HEAVY_TAIL_IMPL_AUTH_BODY,
        "validation_checklist": _HEAVY_TAIL_IMPL_AUTH_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES + [
            "HEAVY_TAIL_IMPLEMENTATION",
            "FIXTURE_CREATION",
            "BASELINE_PACK_UPDATE",
        ],
        "provenance_refs": [
            f"rank6_operator_selection_001:{rank6_hash}",
            "five_operator_shadow_stub_parity_receipt_001:"
            "28c481fdeed3463ae9509820b987cc1ff10e9351969ece4c9f1bbe75b1d8d2ed",
        ],
        "fail_closed_reason": None,
    }


def _build_chamfer_baseline_promotion_closed_packet(
    chamfer_promotion_complete: dict[str, Any],
) -> dict[str, Any]:
    promo_hash = chamfer_promotion_complete.get("canonical_hash", "UNKNOWN")
    return {
        "packet_id": "pkt-chamfer-baseline-promotion-closed-001",
        "source_frontier_ref": "chamfer_baseline_promotion_complete_001",
        "action_title": "CHAMFER Baseline Promotion Complete — Phase Closed",
        "action_type": "REVIEW_REQUIRED",
        "operator_id": "chamfer_distance",
        "recommended_next_step": "HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION_AUTHORIZATION",
        "authority_required": "OPERATOR_DECISION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _CHAMFER_BASELINE_PROMOTION_CLOSED_BODY,
        "validation_checklist": _CHAMFER_PROMOTION_CLOSED_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            f"chamfer_baseline_promotion_complete_001:{promo_hash}",
            "chamfer_distance_computation_complete_review_001:"
            "676ea1c55da5e3d2f0771fbbe6065795248016d53a8cda16778733f95461867b",
        ],
        "fail_closed_reason": None,
    }


def _build_chamfer_baseline_promotion_packet() -> dict[str, Any]:
    return {
        "packet_id": "pkt-chamfer-baseline-promotion-follow-through-001",
        "source_frontier_ref": "chamfer_expected_values_addition_receipt_001",
        "action_title": "CHAMFER Baseline Promotion Follow-Through — Operator Review Required",
        "action_type": "REVIEW_REQUIRED",
        "operator_id": "chamfer_distance",
        "recommended_next_step": "CHAMFER_BASELINE_PROMOTION_FOLLOW_THROUGH",
        "authority_required": "OPERATOR_DECISION",
        "allowed": True,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "promotion_allowed": False,
        "prompt_body": _CHAMFER_BASELINE_PROMOTION_BODY,
        "validation_checklist": _CHAMFER_FOLLOW_THROUGH_CHECKLIST,
        "blocked_scopes": STANDARD_BLOCKED_SCOPES,
        "provenance_refs": [
            "chamfer_expected_values_addition_receipt_001:"
            "c84fff6b939645c4a31ecad111be0d662da9001f12ed8f8a9d26860c6756c724",
            "chamfer_expected_values_gate_001:"
            "a0952c077acb489a77ab9c5c15bab02ee10887a009a44d43e3207913bbee4045",
        ],
        "fail_closed_reason": None,
    }


# ── Main bundle builder ───────────────────────────────────────────────────────


def build_packets() -> dict[str, Any]:
    frontier = _require(ROOT / _SRC_FRONTIER, "frontier_recommendation_006")
    gate = _require(ROOT / _SRC_IMPL_GATE, "transport_computation_implementation_gate_001")
    corpus_receipt = _require(ROOT / _SRC_CORPUS_RECEIPT, "transport_fixture_corpus_creation_receipt_001")
    auth = _require(ROOT / _SRC_AUTH_RECORD, "transport_implementation_authorization_decision_record_001")
    pack_vector_update = _load_safe(ROOT / _SRC_PACK_VECTOR_UPDATE)
    promotion_complete = _load_safe(ROOT / _SRC_PROMOTION_COMPLETE)
    transport_computation_receipt = _load_safe(ROOT / _SRC_TRANSPORT_COMPUTATION_RECEIPT)
    transport_promotion_complete = _load_safe(ROOT / _SRC_TRANSPORT_PROMOTION_COMPLETE)
    chamfer_promotion_complete = _load_safe(ROOT / _SRC_CHAMFER_PROMOTION_COMPLETE)
    rank6_selection = _load_safe(ROOT / _SRC_RANK6_SELECTION)

    projection_bundle = _load_safe(ROOT / _SRC_BUNDLE)
    bundle_hash: str | None = None
    if projection_bundle:
        systems = projection_bundle.get("systems", [])
        transport_sys = next((s for s in systems if s.get("system_id") == "transport"), None)
        if transport_sys:
            receipts = transport_sys.get("ledger_receipts", [])
            if receipts:
                bundle_hash = receipts[-1].get("canonical_hash")

    packets: list[dict[str, Any]] = []

    # TRANSPORT packets: emit closed packet when promotion complete; suppress prior packets.
    # If promotion not yet complete but computation done: emit follow-through review.
    # If computation not yet done: emit implementation prompt.
    if transport_promotion_complete is not None and transport_computation_receipt is not None:
        packets.append(
            _build_transport_baseline_promotion_closed_packet(
                transport_promotion_complete, transport_computation_receipt
            )
        )
    elif transport_computation_receipt is not None:
        packets.append(_build_transport_computation_complete_packet(transport_computation_receipt))
    else:
        packets.append(_build_transport_computation_prompt(gate, corpus_receipt, auth, frontier))
        packets.append(_build_transport_validation_checklist(gate, corpus_receipt))

    # CHAMFER: emit closed packet when promotion complete is present; otherwise follow-through
    if chamfer_promotion_complete is not None:
        packets.append(_build_chamfer_baseline_promotion_closed_packet(chamfer_promotion_complete))
    else:
        packets.append(_build_chamfer_baseline_promotion_packet())

    if rank6_selection is not None:
        packets.append(_build_heavy_tail_implementation_authorization_packet(rank6_selection))

    packets.append(_build_aal_viz_next_adapter_checklist())
    packets.append(_build_sealed_pause_packet(frontier))

    # WASSERSTEIN baseline promotion packet: only when phase is closed but not yet complete
    if pack_vector_update is not None and promotion_complete is None:
        phase_record = pack_vector_update.get("cpu_baseline_phase_record", {})
        phase_closed = (
            phase_record.get("cpu_baseline_computation_phase_status")
            == "COMPUTATION_PHASE_CLOSED"
        )
        if phase_closed:
            packets.append(_build_wasserstein_baseline_promotion_packet(pack_vector_update))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_now(),
        "generated_by": GENERATED_BY,
        "authority": AUTHORITY,
        "source_projection_bundle_hash": bundle_hash,
        "fail_closed_reason": None,
        "packets": packets,
    }


def _validate_bundle(bundle: dict[str, Any]) -> None:
    auth = bundle.get("authority", {})
    if auth.get("execution_allowed") is not False:
        raise ValueError("FAIL_CLOSED: authority.execution_allowed must be false")
    if auth.get("runtime_mutation_allowed") is not False:
        raise ValueError("FAIL_CLOSED: authority.runtime_mutation_allowed must be false")
    if auth.get("promotion_allowed") is not False:
        raise ValueError("FAIL_CLOSED: authority.promotion_allowed must be false")
    for pkt in bundle.get("packets", []):
        if pkt.get("execution_allowed") is not False:
            raise ValueError(
                f"FAIL_CLOSED: packet {pkt.get('packet_id')} has execution_allowed != false"
            )
        if pkt.get("runtime_mutation_allowed") is not False:
            raise ValueError(
                f"FAIL_CLOSED: packet {pkt.get('packet_id')} has runtime_mutation_allowed != false"
            )


def main() -> int:
    try:
        bundle = build_packets()
        _validate_bundle(bundle)
    except ValueError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        fail_closed: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": _utc_now(),
            "generated_by": GENERATED_BY,
            "authority": AUTHORITY,
            "source_projection_bundle_hash": None,
            "fail_closed_reason": str(exc),
            "packets": [],
        }
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(fail_closed, indent=2, sort_keys=True), encoding="utf-8"
        )
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8"
    )
    sys.stdout.write(
        f"OK: wrote {len(bundle['packets'])} action packets → {OUTPUT_PATH.relative_to(ROOT)}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
