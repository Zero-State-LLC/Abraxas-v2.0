#!/usr/bin/env python3
"""
AAL-Viz Operator Action Packet Adapter — projection/copy-only packet builder.

Reads:
  apps/aal-viz-live-console/public/projection-bundle.json
  out/metric_operator/metric_operator_frontier_recommendation_006.latest.json
  out/metric_operator/transport_computation_implementation_gate_001.latest.json
  out/metric_operator/transport_fixture_corpus_creation_receipt_001.latest.json
  out/metric_operator/transport_implementation_authorization_decision_record_001.latest.json

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
_SRC_BUNDLE = "apps/aal-viz-live-console/public/projection-bundle.json"

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
    "OPTION A — TRANSPORT COMPUTATION RECEIPT ADAPTER",
    "[ ] A1. After transport computation receipt produced, add to OPERATOR_DEFS sequence",
    "[ ]     path: out/metric_operator/transport_computation_receipt_001.latest.json",
    "[ ] A2. Update computation_receipt_key for transport in build_aal_viz_projection_bundle.py",
    "[ ] A3. Re-run: python scripts/build_aal_viz_projection_bundle.py",
    "[ ] A4. Verify transport status changes from PARTIAL → READY",
    "",
    "OPTION B — WASSERSTEIN GATE-COND-005 UNLOCK ADAPTER",
    "[ ] B1. Obtain operator authorization for WASSERSTEIN CPU baseline implementation",
    "[ ] B2. Add authorization artifact to WASSERSTEIN sequence when present",
    "[ ] B3. Re-run projection bundle builder",
    "[ ] B4. Verify WASSERSTEIN status advances past SHADOW_STUB_ONLY",
    "",
    "OPTION C — CHAMFER BASELINE PROMOTION ADAPTER",
    "[ ] C1. CHAMFER is READY (95%); baseline promotion gate is next step",
    "[ ] C2. Produce chamfer_baseline_promotion_gate artifact",
    "[ ] C3. Add to sequence and re-run bundle builder",
    "[ ] C4. Verify CHAMFER advances to 100%",
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


# ── Main bundle builder ───────────────────────────────────────────────────────


def build_packets() -> dict[str, Any]:
    frontier = _require(ROOT / _SRC_FRONTIER, "frontier_recommendation_006")
    gate = _require(ROOT / _SRC_IMPL_GATE, "transport_computation_implementation_gate_001")
    receipt = _require(ROOT / _SRC_CORPUS_RECEIPT, "transport_fixture_corpus_creation_receipt_001")
    auth = _require(ROOT / _SRC_AUTH_RECORD, "transport_implementation_authorization_decision_record_001")
    pack_vector_update = _load_safe(ROOT / _SRC_PACK_VECTOR_UPDATE)

    projection_bundle = _load_safe(ROOT / _SRC_BUNDLE)
    bundle_hash: str | None = None
    if projection_bundle:
        systems = projection_bundle.get("systems", [])
        transport_sys = next((s for s in systems if s.get("system_id") == "transport"), None)
        if transport_sys:
            receipts = transport_sys.get("ledger_receipts", [])
            if receipts:
                bundle_hash = receipts[-1].get("canonical_hash")

    packets: list[dict[str, Any]] = [
        _build_transport_computation_prompt(gate, receipt, auth, frontier),
        _build_transport_validation_checklist(gate, receipt),
        _build_aal_viz_next_adapter_checklist(),
        _build_sealed_pause_packet(frontier),
    ]

    if pack_vector_update is not None:
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
