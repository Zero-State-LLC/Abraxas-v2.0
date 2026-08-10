"""SHADOW anomaly detection over instantiation states and transitions (RDI-4).

SHADOW detects only: anomaly, divergence, unexpected transition, missing
evidence, contamination, and unexplained decay. This module never explains why
a transition occurred, never issues a forecast, and never authorizes an
intervention (`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`
section 8). Findings are structural observations over already-validated
payloads; every judgment beyond detection is out of scope by contract.

Pure and deterministic: same states/transitions in, same report (and hash) out.
No disk writes; runners publish.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json_if_changed
from core.cfar import CFARRoute, ConstructPacket, ConstructStatus, VariableClass
from core.signal.evidence_pack import assert_valid_evidence_pack

from .contracts import (
    DIMENSIONS,
    validate_instantiation_state,
    validate_instantiation_transition,
)

SCHEMA_VERSION = "InstantiationShadowReport.v1"

# Detection-only severities. "anomaly" marks a structural irregularity worth
# operator attention; "observation" marks detected-but-expected conditions
# (e.g. declared contamination) that must stay visible without judgment.
SEVERITIES = ("anomaly", "observation")

SHADOW_AUTHORITY = {
    "explains_causality": False,
    "forecast_authority": False,
    "intervention_authority": False,
    "execution_authority": False,
    "canon_mutation": False,
}

# Consequence-bearing dimensions used by the reinforcement cross-check. The
# doctrine requires recursive reinforcement to rest on consequences
# attributable to the construct; observing it with zero consequence evidence
# is a detectable contradiction, not an interpretation.
_CONSEQUENCE_DIMENSIONS = (
    "behavioral_consequence",
    "network_propagation",
    "executable_embodiment",
    "economic_institutional_embodiment",
    "material_consequence",
)

RDI_LIVE_WIRE_SCHEMA_VERSION = "RDIInstantiationShadowLiveWire.v1"
RDI_LIVE_WIRE_KIND = "rdi_instantiation_shadow"
RDI_SCOPE_ASSUMPTIONS = (
    (
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: dimensions may coexist, regress, "
        "bifurcate, develop in different orders, or remain NOT_COMPUTABLE; they are "
        "not stages and are not ordered by maturity."
    ),
    (
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: an absent dimension is not zero "
        "and is not false; it is NOT_COMPUTABLE unless evidence supports another "
        "epistemically labeled value."
    ),
)


def _iso_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
        return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed
    except ValueError:
        return None


def _horizon_bounds(value: Any) -> tuple[datetime | None, datetime | None]:
    if not isinstance(value, str):
        return None, None
    parts = value.replace("..", "/").replace(" to ", "/").split("/")
    parsed = [_iso_timestamp(part.strip()) for part in parts]
    parsed = [item for item in parsed if item is not None]
    if len(parsed) == 1:
        return parsed[0], parsed[0]
    if len(parsed) >= 2:
        return min(parsed[0], parsed[1]), max(parsed[0], parsed[1])
    return None, None


def _claim_dimension(claim: Mapping[str, Any]) -> str | None:
    for key in ("dimension", "instantiation_dimension", "vector_dimension"):
        value = claim.get(key)
        if isinstance(value, str) and value in DIMENSIONS:
            return value
    return None


def derive_rdi_live_wire_window(
    pack: Mapping[str, Any], evidence_objects: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Derive the bounded window from the pack horizon and object timestamps."""
    start, end = _horizon_bounds(pack.get("time_horizon"))
    timestamps: list[str] = []
    for item in evidence_objects:
        timestamp = item.get("timestamp")
        parsed = _iso_timestamp(timestamp)
        if not isinstance(timestamp, str):
            continue
        if parsed is not None and start is not None and parsed < start:
            continue
        if parsed is not None and end is not None and parsed > end:
            continue
        timestamps.append(timestamp)
    return {
        "time_horizon": pack.get("time_horizon"),
        "start": start.isoformat() if start else None,
        "end": end.isoformat() if end else None,
        "evidence_object_timestamps": sorted(timestamps),
    }


def build_rdi_live_wire_artifact(
    pack: Mapping[str, Any],
    evidence_objects: Sequence[Mapping[str, Any]],
    *,
    artifact_id: str,
    out_root: str | Path = "out",
) -> dict[str, Any]:
    """Build and write a SANDBOX-only, detection-only live-wire artifact."""
    assert_valid_evidence_pack(pack)
    window = derive_rdi_live_wire_window(pack, evidence_objects)
    start, end = _horizon_bounds(pack.get("time_horizon"))
    by_source: dict[str, list[Mapping[str, Any]]] = {}
    for item in evidence_objects:
        source = item.get("source")
        if isinstance(source, str) and source:
            by_source.setdefault(source, []).append(item)

    selected: list[dict[str, Any]] = []
    for claim in pack.get("claims", []):
        if not isinstance(claim, Mapping):
            continue
        register = str(claim.get("register", "")).upper()
        dimension = _claim_dimension(claim)
        if register not in {"OBSERVED", "INFERRED"} or dimension is None:
            continue
        refs = sorted({str(ref) for ref in claim.get("source_ids", [])})
        objects = [obj for ref in refs for obj in by_source.get(ref, [])]
        objects = [
            obj
            for obj in objects
            if (timestamp := _iso_timestamp(obj.get("timestamp"))) is not None
            and (start is None or timestamp >= start)
            and (end is None or timestamp <= end)
        ]
        if not objects:
            continue
        selected.append({
            "claim_id": str(claim.get("claim_id", "")),
            "dimension": dimension,
            "register": register,
            "source_ids": refs,
            "evidence_object_timestamps": sorted(
                str(obj["timestamp"])
                for obj in objects
                if isinstance(obj.get("timestamp"), str)
            ),
        })
    selected.sort(key=lambda item: (DIMENSIONS.index(item["dimension"]), item["claim_id"]))

    query = "RDI instantiation vector H"
    input_hash = canonical_hash({"query": query})
    packet = ConstructPacket(
        schema_version="cfar.v1",
        object_id=f"cfar-{input_hash[:16]}",
        input_hash=input_hash,
        lane="SHADOW",
        status="VALID",
        provenance=("EvidencePack.v0", "REPRESENTATION_DRIVEN_INSTANTIATION_001"),
        query=query,
        construct=query,
        construct_status=ConstructStatus.EMERGENT,
        variable_class=VariableClass.HYBRID,
        dimensions=tuple(DIMENSIONS),
        assumptions=RDI_SCOPE_ASSUMPTIONS,
        abstraction_level=2,
        measurement_equivalence_required=False,
        route=CFARRoute.EVIDENCE_RETRIEVAL,
        rationale=("Operator-scoped RDI vector H is routed to evidence retrieval.",),
        authority={
            "truth_assignment": False,
            "forecast_routing": False,
            "canon_mutation": False,
            "execution_authority": False,
            "retrieval_authority": True,
        },
    ).to_dict()
    artifact: dict[str, Any] = {
        "schema_version": RDI_LIVE_WIRE_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "lane": "SHADOW",
        "dry_run": True,
        "source_pack_id": pack.get("pack_id"),
        "window": window,
        "construct_packet": packet,
        "selected_claims": selected,
        "authority": dict(SHADOW_AUTHORITY),
    }
    artifact["canonical_hash"] = canonical_hash(artifact)
    target = Path(out_root) / RDI_LIVE_WIRE_KIND / f"{artifact_id}.json"
    write_canonical_json_if_changed(target, artifact)
    return artifact


def _finding(code: str, severity: str, subject_id: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "subject_id": subject_id, "message": message}


def _dimension_status(state: Mapping[str, Any]) -> dict[str, str]:
    return {d["name"]: d["epistemic_status"] for d in state["dimensions"]}


def _state_findings(state: Mapping[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    state_id = state["state_id"]
    statuses = _dimension_status(state)

    for name in DIMENSIONS:
        if statuses[name] == "NOT_COMPUTABLE":
            findings.append(
                _finding(
                    "MISSING_EVIDENCE",
                    "observation",
                    state_id,
                    f"Dimension {name} is NOT_COMPUTABLE in state {state_id}.",
                )
            )

    if state["causal_exposure"] == "UNKNOWN":
        findings.append(
            _finding(
                "EXPOSURE_UNKNOWN",
                "observation",
                state_id,
                f"State {state_id} records UNKNOWN causal exposure.",
            )
        )

    if statuses["recursive_reinforcement"] in {"OBSERVED", "INFERRED"} and all(
        statuses[name] == "NOT_COMPUTABLE" for name in _CONSEQUENCE_DIMENSIONS
    ):
        findings.append(
            _finding(
                "REINFORCEMENT_WITHOUT_CONSEQUENCE_EVIDENCE",
                "anomaly",
                state_id,
                f"State {state_id} evidences recursive_reinforcement while every "
                "consequence dimension is NOT_COMPUTABLE.",
            )
        )
    return findings


def _transition_findings(
    transition: Mapping[str, Any],
    states_by_id: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    transition_id = transition["transition_id"]

    changed = {c["dimension"]: c for c in transition["dimension_changes"]}
    prior = states_by_id.get(transition["prior_state_ref"]["object_id"])
    later = states_by_id.get(transition["later_state_ref"]["object_id"])

    for ref_name, ref, state in (
        ("prior_state_ref", transition["prior_state_ref"], prior),
        ("later_state_ref", transition["later_state_ref"], later),
    ):
        if state is None:
            findings.append(
                _finding(
                    "STATE_REF_UNRESOLVED",
                    "anomaly",
                    transition_id,
                    f"Transition {transition_id} {ref_name} {ref['object_id']} is not "
                    "among the provided states.",
                )
            )
        elif state["state_hash"] != ref["canonical_hash"]:
            findings.append(
                _finding(
                    "STATE_REF_HASH_DIVERGENCE",
                    "anomaly",
                    transition_id,
                    f"Transition {transition_id} {ref_name} hash does not match state "
                    f"{ref['object_id']}.",
                )
            )

    for name, change in changed.items():
        if change["change_kind"] == "DECREASED":
            findings.append(
                _finding(
                    "DIMENSION_REGRESSION",
                    "anomaly",
                    transition_id,
                    f"Transition {transition_id} records DECREASED {name}.",
                )
            )
        if (
            later is not None
            and change["change_kind"] in {"INCREASED", "DECREASED", "BIFURCATED"}
            and _dimension_status(later)[name] == "NOT_COMPUTABLE"
        ):
            findings.append(
                _finding(
                    "CHANGE_WITHOUT_LATER_EVIDENCE",
                    "anomaly",
                    transition_id,
                    f"Transition {transition_id} declares {change['change_kind']} {name} "
                    "but the later state carries no evidence for that dimension.",
                )
            )

    if prior is not None and later is not None:
        prior_statuses = _dimension_status(prior)
        later_statuses = _dimension_status(later)
        for name in DIMENSIONS:
            if (
                prior_statuses[name] in {"OBSERVED", "INFERRED"}
                and later_statuses[name] == "NOT_COMPUTABLE"
                and name not in changed
            ):
                findings.append(
                    _finding(
                        "UNEXPLAINED_EVIDENCE_DECAY",
                        "anomaly",
                        transition_id,
                        f"Dimension {name} decayed from {prior_statuses[name]} to "
                        f"NOT_COMPUTABLE without a declared change in transition "
                        f"{transition_id}.",
                    )
                )

    contamination = transition["contamination"]
    if contamination["feedback_contaminated"]:
        findings.append(
            _finding(
                "CONTAMINATION_PRESENT",
                "observation",
                transition_id,
                f"Transition {transition_id} is feedback-contaminated; outcomes are not "
                "independent confirmation.",
            )
        )
        if transition["causal_exposure"] == "EXOGENOUS":
            findings.append(
                _finding(
                    "EXPOSURE_CONTAMINATION_CONFLICT",
                    "anomaly",
                    transition_id,
                    f"Transition {transition_id} claims EXOGENOUS exposure while flagged "
                    "feedback-contaminated.",
                )
            )
    if transition["causal_exposure"] == "UNKNOWN":
        findings.append(
            _finding(
                "EXPOSURE_UNKNOWN",
                "observation",
                transition_id,
                f"Transition {transition_id} records UNKNOWN causal exposure.",
            )
        )
    return findings


def detect_instantiation_anomalies(
    states: Sequence[Mapping[str, Any]],
    transitions: Sequence[Mapping[str, Any]] = (),
    *,
    report_id: str,
) -> dict[str, Any]:
    """Build a deterministic anomaly-only InstantiationShadowReport.v1 payload.

    Inputs are validated against their contracts before detection; the report
    carries no explanation, prediction, or authority of any kind.
    """
    for state in states:
        validate_instantiation_state(state)
    for transition in transitions:
        validate_instantiation_transition(transition)

    states_by_id = {state["state_id"]: state for state in states}
    if len(states_by_id) != len(states):
        raise ValueError("states must have unique state_id values")

    findings: list[dict[str, str]] = []
    for state_id in sorted(states_by_id):
        findings.extend(_state_findings(states_by_id[state_id]))
    for transition in sorted(transitions, key=lambda t: t["transition_id"]):
        findings.extend(_transition_findings(transition, states_by_id))

    findings.sort(key=lambda f: (f["subject_id"], f["code"], f["message"]))
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "report_id": report_id,
        "lane": "SHADOW",
        "state_refs": [
            {"object_id": s["state_id"], "canonical_hash": s["state_hash"]}
            for s in (states_by_id[i] for i in sorted(states_by_id))
        ],
        "transition_refs": [
            {"object_id": t["transition_id"], "canonical_hash": t["transition_hash"]}
            for t in sorted(transitions, key=lambda t: t["transition_id"])
        ],
        "findings": findings,
        "finding_count": len(findings),
        "anomaly_count": sum(1 for f in findings if f["severity"] == "anomaly"),
        "authority": dict(SHADOW_AUTHORITY),
        "report_hash": "",
    }
    body = {key: value for key, value in payload.items() if key != "report_hash"}
    payload["report_hash"] = canonical_hash(body)
    return payload


def validate_instantiation_shadow_report(payload: Mapping[str, Any]) -> None:
    """Fail-closed structural validation of a shadow report payload."""
    data = dict(payload)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if data.get("lane") != "SHADOW":
        raise ValueError("lane must be SHADOW")
    if data.get("authority") != SHADOW_AUTHORITY:
        raise ValueError("authority locks must all be false")
    findings = data.get("findings", [])
    if data.get("finding_count") != len(findings):
        raise ValueError("finding_count does not match findings")
    for finding in findings:
        if finding.get("severity") not in SEVERITIES:
            raise ValueError(f"unsupported severity: {finding.get('severity')!r}")
    expected = canonical_hash({k: v for k, v in data.items() if k != "report_hash"})
    if data.get("report_hash") != expected:
        raise ValueError("report_hash does not match canonical payload")
