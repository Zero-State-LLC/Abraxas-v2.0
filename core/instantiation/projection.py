"""Projection-only instantiation state/transition/lineage view (RDI-4).

Builds the read-only view AAL-Viz consumes: per-construct state timelines,
transition lineage edges, dimension epistemic labels, causal exposure, and
contamination flags — plus an optional SHADOW findings overlay.

Projection displays; it never decides. The view invents no scores, no
aggregate depth, no thresholds, and grants no authority
(`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md` section 11).
Pure and deterministic; no disk writes — runners publish.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.canonical.json import canonical_hash

from .contracts import (
    DIMENSIONS,
    validate_instantiation_state,
    validate_instantiation_transition,
)
from .shadow import validate_instantiation_shadow_report

SCHEMA_VERSION = "InstantiationProjectionView.v1"

PROJECTION_AUTHORITY = {
    "advisory_only": True,
    "projection_only": True,
    "non_authoritative": True,
    "forecast_authority": False,
    "intervention_authority": False,
    "execution_authority": False,
    "canon_mutation": False,
    "runtime_mutation": False,
}


def _state_tile(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "state_id": state["state_id"],
        "state_hash": state["state_hash"],
        "observation_window": dict(state["observation_window"]),
        "causal_exposure": state["causal_exposure"],
        "aggregate_instantiation_depth": state["aggregate_instantiation_depth"],
        "dimensions": [
            {
                "name": d["name"],
                "epistemic_status": d["epistemic_status"],
                "evidence_count": len(d["evidence_refs"]),
                "not_computable_reason": d["not_computable_reason"],
            }
            for d in state["dimensions"]
        ],
    }


def _lineage_edge(transition: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "transition_id": transition["transition_id"],
        "transition_hash": transition["transition_hash"],
        "from_state_id": transition["prior_state_ref"]["object_id"],
        "to_state_id": transition["later_state_ref"]["object_id"],
        "causal_exposure": transition["causal_exposure"],
        "feedback_contaminated": transition["contamination"]["feedback_contaminated"],
        "independent_confirmation_eligible": transition["contamination"][
            "independent_confirmation_eligible"
        ],
        "dimension_changes": [
            {
                "dimension": c["dimension"],
                "change_kind": c["change_kind"],
                "epistemic_status": c["epistemic_status"],
            }
            for c in transition["dimension_changes"]
        ],
        "linked_refs": {
            name: (dict(transition[name]) if transition.get(name) else None)
            for name in ("forecast_ref", "intervention_ref", "settlement_ref")
        },
    }


def build_instantiation_projection(
    states: Sequence[Mapping[str, Any]],
    transitions: Sequence[Mapping[str, Any]] = (),
    *,
    view_id: str,
    shadow_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic InstantiationProjectionView.v1 payload.

    States group by construct into hash-linked timelines; transitions become
    lineage edges. When a shadow report is provided its findings are overlaid
    verbatim — projection repeats detections, it does not re-detect or judge.
    """
    for state in states:
        validate_instantiation_state(state)
    for transition in transitions:
        validate_instantiation_transition(transition)
    if shadow_report is not None:
        validate_instantiation_shadow_report(shadow_report)

    states_by_id = {state["state_id"]: state for state in states}
    if len(states_by_id) != len(states):
        raise ValueError("states must have unique state_id values")

    constructs: dict[str, list[Mapping[str, Any]]] = {}
    construct_hashes: dict[str, str] = {}
    for state in states:
        construct_id = state["construct_ref"]["object_id"]
        constructs.setdefault(construct_id, []).append(state)
        construct_hashes[construct_id] = state["construct_ref"]["canonical_hash"]

    timelines = [
        {
            "construct_ref": {
                "object_id": construct_id,
                "canonical_hash": construct_hashes[construct_id],
            },
            "states": [
                _state_tile(state)
                for state in sorted(
                    constructs[construct_id],
                    key=lambda s: (
                        s["observation_window"]["start"],
                        s["observation_window"]["end"],
                        s["state_id"],
                    ),
                )
            ],
        }
        for construct_id in sorted(constructs)
    ]

    edges = [
        _lineage_edge(t) for t in sorted(transitions, key=lambda t: t["transition_id"])
    ]
    unresolved = sorted(
        {
            edge[key]
            for edge in edges
            for key in ("from_state_id", "to_state_id")
            if edge[key] not in states_by_id
        }
    )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "view_id": view_id,
        "lane": "PROJECTION",
        "dimension_order": list(DIMENSIONS),
        "construct_timelines": timelines,
        "lineage_edges": edges,
        "unresolved_state_ids": unresolved,
        "shadow_overlay": (
            {
                "report_id": shadow_report["report_id"],
                "report_hash": shadow_report["report_hash"],
                "findings": [dict(f) for f in shadow_report["findings"]],
            }
            if shadow_report is not None
            else None
        ),
        "authority": dict(PROJECTION_AUTHORITY),
        "view_hash": "",
    }
    body = {key: value for key, value in payload.items() if key != "view_hash"}
    payload["view_hash"] = canonical_hash(body)
    return payload


def validate_instantiation_projection(payload: Mapping[str, Any]) -> None:
    """Fail-closed structural validation of a projection view payload."""
    data = dict(payload)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("lane") != "PROJECTION":
        raise ValueError("lane must be PROJECTION")
    if data.get("authority") != PROJECTION_AUTHORITY:
        raise ValueError("projection authority boundary violated")
    if data.get("dimension_order") != list(DIMENSIONS):
        raise ValueError("dimension_order must match canonical dimensions")
    expected = canonical_hash({k: v for k, v in data.items() if k != "view_hash"})
    if data.get("view_hash") != expected:
        raise ValueError("view_hash does not match canonical payload")
