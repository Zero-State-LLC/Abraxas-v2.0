from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_gap_analysis_plan import (
    OUT_JSON as BELIEF_GRAPH_ENGINE_GAP_ANALYSIS_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisorySpecPlan.v1"
PLAN_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_001"
OUT_JSON = "out/audit/belief_graph_engine_advisory_spec_plan_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_advisory_spec_plan_001.latest.md"

BLOCKED_ACTIONS = [
    "BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_RUNTIME_CREATION",
    "TRUTH_ASSIGNMENT",
    "BELIEF_PROMOTION",
    "FORECAST_ROUTING",
    "RUNTIME_DISPATCH_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "ACTIVATION_OR_EXECUTION",
]


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _contract_boundaries() -> list[dict[str, Any]]:
    return [
        {
            "boundary_id": "contract_boundary_001_input_packet",
            "surface": "belief_graph_packet_input",
            "planned_status": "SPEC_ONLY",
            "allowed_semantics": [
                "consume existing BeliefGraphPacket-style evidence",
                "preserve source object hashes and relationship provenance",
            ],
            "denied_semantics": [
                "truth assignment",
                "belief promotion",
                "forecast authority",
            ],
        },
        {
            "boundary_id": "contract_boundary_002_engine_receipt",
            "surface": "belief_graph_engine_advisory_receipt",
            "planned_status": "SPEC_ONLY",
            "allowed_semantics": [
                "summarize graph evidence readiness",
                "emit deterministic validation findings",
            ],
            "denied_semantics": [
                "runtime graph creation",
                "dispatch routing",
                "canon mutation",
            ],
        },
        {
            "boundary_id": "contract_boundary_003_authority_locks",
            "surface": "belief_graph_authority_lock_set",
            "planned_status": "SPEC_ONLY",
            "allowed_semantics": [
                "record denied authority classes",
                "route any future implementation through a separate operator gate",
            ],
            "denied_semantics": [
                "auto-approval",
                "auto-execution",
                "writeback automation",
            ],
        },
    ]


def _route_binding_reviews() -> list[dict[str, Any]]:
    return [
        {
            "review_id": "route_binding_review_001_yggdrasil_advisory",
            "source_family": "contracts/yggdrasil/routes/*.route.v1.json",
            "planned_status": "REVIEW_REQUIRED_BEFORE_IMPLEMENTATION",
            "binding_question": "which advisory routes may reference Belief Graph evidence packets",
            "mutation_allowed": False,
        },
        {
            "review_id": "route_binding_review_002_pipeline_contracts",
            "source_family": "contracts/pipelines/*.v1_1.json",
            "planned_status": "REVIEW_REQUIRED_BEFORE_IMPLEMENTATION",
            "binding_question": "which pipeline contracts may declare Belief Graph evidence as read-only input",
            "mutation_allowed": False,
        },
        {
            "review_id": "route_binding_review_003_operator_surfaces",
            "source_family": "out/operator_review/*",
            "planned_status": "REVIEW_REQUIRED_BEFORE_IMPLEMENTATION",
            "binding_question": "which operator gates are required before any engine implementation PR",
            "mutation_allowed": False,
        },
    ]


def _fixture_plan() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "fixture_plan_001_minimal_packet",
            "fixture_status": "PLANNED_ONLY",
            "purpose": "validate a minimal evidence packet without assigning truth",
            "requires_implementation": False,
        },
        {
            "fixture_id": "fixture_plan_002_conflicting_evidence",
            "fixture_status": "PLANNED_ONLY",
            "purpose": "validate that conflicts remain advisory and non-authoritative",
            "requires_implementation": False,
        },
        {
            "fixture_id": "fixture_plan_003_missing_provenance",
            "fixture_status": "PLANNED_ONLY",
            "purpose": "validate fail-closed behavior when provenance is incomplete",
            "requires_implementation": False,
        },
    ]


def _operator_gates() -> list[dict[str, Any]]:
    return [
        {
            "gate_id": "operator_gate_001_spec_review",
            "gate_status": "FUTURE_REVIEW_REQUIRED",
            "required_before": "Belief Graph engine contract authoring",
            "authority_granted": False,
        },
        {
            "gate_id": "operator_gate_002_implementation_authorization",
            "gate_status": "FUTURE_REVIEW_REQUIRED",
            "required_before": "Belief Graph engine implementation PR",
            "authority_granted": False,
        },
        {
            "gate_id": "operator_gate_003_activation_authorization",
            "gate_status": "FUTURE_REVIEW_REQUIRED",
            "required_before": "any runtime activation or dispatch integration",
            "authority_granted": False,
        },
    ]


def build_belief_graph_engine_advisory_spec_plan(
    *,
    repo_root: str | Path,
    gap_analysis_plan_path: str | Path = BELIEF_GRAPH_ENGINE_GAP_ANALYSIS_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    gap_plan = _read_json(root / gap_analysis_plan_path)
    source_ready = (
        gap_plan.get("artifact_type") == "BeliefGraphEngineGapAnalysisPlan.v1"
        and gap_plan.get("plan_status") == "BELIEF_GRAPH_ENGINE_GAP_ANALYSIS_PLAN_READY"
        and gap_plan.get("recommended_next_lane") == "BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN"
        and gap_plan.get("valid_for_implementation") is False
        and gap_plan.get("execution_authority") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN_READY" if source_ready else "NOT_COMPUTABLE"
        ),
        "target_surface": "BELIEF_GRAPH_ENGINE_001",
        "source_plan": {
            "path": Path(gap_analysis_plan_path).as_posix(),
            "hash": _sha256(root / gap_analysis_plan_path),
            "plan_status": str(gap_plan.get("plan_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(gap_plan.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "source_gap_summary": {
            "engine_missing_paths": int(gap_plan.get("gap_summary", {}).get("engine_missing_paths", 0))
            if isinstance(gap_plan.get("gap_summary"), dict)
            else 0,
            "primitive_observed_paths": int(
                gap_plan.get("gap_summary", {}).get("primitive_observed_paths", 0)
            )
            if isinstance(gap_plan.get("gap_summary"), dict)
            else 0,
            "primitive_equivalent_observed": bool(
                gap_plan.get("primitive_scaffold_evidence", {}).get(
                    "belief_graph_equivalent_observed",
                    False,
                )
            )
            if isinstance(gap_plan.get("primitive_scaffold_evidence"), dict)
            else False,
        },
        "spec_scope": "ADVISORY_SPEC_PLAN_ONLY",
        "contract_boundaries": _contract_boundaries(),
        "route_binding_reviews": _route_binding_reviews(),
        "fixture_and_test_plan": _fixture_plan(),
        "operator_gates": _operator_gates(),
        "required_future_delivery_surfaces": [
            "contracts/canon/belief_graph_engine_advisory_receipt.v1.schema.json",
            "core/belief_graph_engine_advisory_receipt.py",
            "scripts/run_belief_graph_engine_advisory_receipt.py",
            "tests/test_belief_graph_engine_advisory_receipt.py",
            "out/audit/belief_graph_engine_advisory_receipt_001.latest.json",
            "out/audit/belief_graph_engine_advisory_receipt_001.latest.md",
        ],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "recommended_next_lane": "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CONTRACT_PLAN",
        "recommended_next_action": (
            "prepare a separate advisory receipt contract plan; do not implement the engine "
            "or wire runtime dispatch without a future explicit operator gate"
        ),
        "belief_graph_engine_implementation_authorized": False,
        "belief_graph_engine_implementation_performed": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "forecast_routing_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": {
            "belief_promotion": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "truth_assignment": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_engine_advisory_spec_plan(path: str | Path, packet: Mapping[str, Any]) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_spec_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Spec Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- spec_scope: {packet['spec_scope']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- belief_graph_engine_implementation_authorized: {packet['belief_graph_engine_implementation_authorized']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Contract Boundaries",
    ]
    for boundary in packet.get("contract_boundaries", []):
        if isinstance(boundary, dict):
            lines.append(f"- {boundary['boundary_id']}: {boundary['surface']}")
    lines.extend(["", "## Route Binding Reviews"])
    for review in packet.get("route_binding_reviews", []):
        if isinstance(review, dict):
            lines.append(f"- {review['review_id']}: {review['planned_status']}")
    lines.extend(["", "## Operator Gates"])
    for gate in packet.get("operator_gates", []):
        if isinstance(gate, dict):
            lines.append(f"- {gate['gate_id']}: {gate['gate_status']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_belief_graph_engine_advisory_spec_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_belief_graph_engine_advisory_spec_plan_markdown(packet)) + "\n",
        encoding="utf-8",
    )
