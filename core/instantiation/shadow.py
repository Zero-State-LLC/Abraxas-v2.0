"""SHADOW anomaly detection over instantiation states and transitions (RDI-4).

SHADOW detects only: anomaly, divergence, unexpected transition, missing
evidence, contamination, and unexplained decay. This module never explains why
a transition occurred, never issues a forecast, and never authorizes an
intervention (`docs/architecture/REPRESENTATION_DRIVEN_INSTANTIATION_001.md`
section 8). Findings are structural observations over already-validated
payloads; every judgment beyond detection is out of scope by contract.

Detection is pure and deterministic: same states/transitions in, same report
(and hash) out. The operator-scoped live-wire entry point publishes only a
classified SANDBOX dry-run artifact under ``out/``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.belief_graph.evidence_object import EvidenceObject
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import canonical_hash
from core.cfar import (
    CFARRoute,
    ConstructPacket,
    ConstructStatus,
    VariableClass,
    cfar_route,
)
from core.ports.storage import ArtifactStore, FilesystemArtifactStore
from core.signal.evidence_pack import assert_valid_evidence_pack

from .contracts import (
    DIMENSIONS,
    build_instantiation_state,
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
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: simulation is evidence only for "
        "the constitutive properties actually demonstrated; it is neither proof nor "
        "disproof of instantiation."
    ),
    (
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: dimensions are independently "
        "evidenced, may coexist, regress, bifurcate, develop in different orders, "
        "or remain NOT_COMPUTABLE; they are not maturity stages."
    ),
    (
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: an absent or unsupported dimension "
        "is NOT_COMPUTABLE, not zero or false; aggregate Instantiation Depth remains "
        "NOT_COMPUTABLE."
    ),
    (
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: missing or ambiguous causal exposure "
        "remains UNKNOWN and temporal order or correlation is not causal attribution."
    ),
    (
        "REPRESENTATION_DRIVEN_INSTANTIATION_001: SHADOW detects only and grants no "
        "explanation, forecast, intervention, execution, or canon authority."
    ),
)

_EVIDENCE_OBJECT_KEYS = {
    "schema_version",
    "source",
    "provenance",
    "timestamp",
    "evidence_type",
    "hash",
}


def _iso_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
        aware = parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed
        return aware.astimezone(UTC)
    except ValueError:
        return None


def _horizon_bounds(value: Any) -> tuple[datetime, datetime]:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("EvidencePack.time_horizon is required for RDI live wiring")
    parts = value.split("/")
    if len(parts) != 2:
        raise ValueError(
            "EvidencePack.time_horizon must be an ISO-8601 start/end interval"
        )
    start, end = (_iso_timestamp(part) for part in parts)
    if start is None or end is None:
        raise ValueError(
            "EvidencePack.time_horizon must contain parseable ISO-8601 bounds"
        )
    if start > end:
        raise ValueError("EvidencePack.time_horizon start must not follow end")
    return start, end


def _claim_dimension(claim: Mapping[str, Any]) -> str | None:
    value = claim.get("dimension")
    return value if isinstance(value, str) and value in DIMENSIONS else None


def _normalized_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _normalized_iso_timestamp(value: str) -> str:
    parsed = _iso_timestamp(value)
    if parsed is None:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}")
    return _normalized_timestamp(parsed)


def _validated_evidence_objects(
    evidence_objects: Sequence[Mapping[str, Any] | EvidenceObject],
) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    hashes: set[str] = set()
    for index, item in enumerate(evidence_objects):
        if isinstance(item, EvidenceObject):
            evidence = item
        else:
            if set(item) != _EVIDENCE_OBJECT_KEYS:
                raise ValueError(
                    f"EvidenceObject at index {index} must match "
                    "EvidenceObject.v1 exactly"
                )
            try:
                evidence = EvidenceObject.model_validate(item, strict=True)
            except Exception as exc:
                raise ValueError(
                    f"invalid EvidenceObject at index {index}: {exc}"
                ) from exc
        if _iso_timestamp(evidence.timestamp) is None:
            raise ValueError(
                f"EvidenceObject at index {index} has an invalid ISO-8601 timestamp"
            )
        if evidence.hash in hashes:
            raise ValueError(f"duplicate EvidenceObject hash: {evidence.hash}")
        hashes.add(evidence.hash)
        validated.append(evidence.model_dump(mode="json"))
    return validated


def _source_aliases(pack: Mapping[str, Any]) -> dict[str, frozenset[str]]:
    aliases: dict[str, frozenset[str]] = {}
    used_aliases: dict[str, str] = {}
    for source in pack.get("sources", []):
        source_id = str(source["source_id"])
        if source_id in aliases:
            raise ValueError(f"duplicate EvidencePack source_id: {source_id}")
        values = frozenset(
            value for value in (source_id, str(source.get("url_or_path", ""))) if value
        )
        for value in values:
            other = used_aliases.get(value)
            if other is not None and other != source_id:
                raise ValueError(
                    f"ambiguous EvidencePack source identity {value!r}: {other}, {source_id}"
                )
            used_aliases[value] = source_id
        aliases[source_id] = values
    return aliases


def derive_rdi_live_wire_window(
    pack: Mapping[str, Any],
    evidence_objects: Sequence[Mapping[str, Any] | EvidenceObject],
) -> dict[str, Any]:
    """Derive the bounded window from the pack horizon and object timestamps."""
    start, end = _horizon_bounds(pack.get("time_horizon"))
    timestamps: list[str] = []
    for item in _validated_evidence_objects(evidence_objects):
        parsed = _iso_timestamp(item["timestamp"])
        if parsed is not None and start <= parsed <= end:
            timestamps.append(_normalized_timestamp(parsed))
    return {
        "time_horizon": pack.get("time_horizon"),
        "start": _normalized_timestamp(start),
        "end": _normalized_timestamp(end),
        "evidence_object_timestamps": sorted(timestamps),
    }


def _build_rdi_construct_packet() -> ConstructPacket:
    query = "RDI instantiation vector H"
    # Start from CFAR's existing deterministic constructor so input_hash,
    # object_id, lane, status, and authority semantics remain canonical.
    base = cfar_route(query)
    return replace(
        base,
        construct=query,
        construct_status=ConstructStatus.EMERGENT,
        variable_class=VariableClass.HYBRID,
        dimensions=tuple(DIMENSIONS),
        assumptions=RDI_SCOPE_ASSUMPTIONS,
        route=CFARRoute.EVIDENCE_RETRIEVAL,
        rationale=(
            (
                "The operator-scoped RDI instantiation vector H is sufficiently "
                "bounded for evidence retrieval."
            ),
        ),
        authority={
            "truth_assignment": False,
            "forecast_routing": False,
            "canon_mutation": False,
            "execution_authority": False,
            "retrieval_authority": True,
        },
    )


def _live_wire_dimensions(
    selected_claims: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_dimension: dict[str, list[Mapping[str, Any]]] = {}
    for claim in selected_claims:
        by_dimension.setdefault(str(claim["dimension"]), []).append(claim)

    dimensions: list[dict[str, Any]] = []
    for name in DIMENSIONS:
        claims = by_dimension.get(name, [])
        if not claims:
            dimensions.append(
                {
                    "name": name,
                    "epistemic_status": "NOT_COMPUTABLE",
                    "claim_refs": [],
                    "evidence_refs": [],
                    "not_computable_reason": (
                        "no eligible OBSERVED or INFERRED EvidencePack.v0 claim "
                        "with in-window EvidenceObject evidence"
                    ),
                }
            )
            continue
        registers = {str(claim["register"]) for claim in claims}
        if len(registers) != 1:
            raise ValueError(
                f"ambiguous epistemic registers for dimension {name}: "
                f"{sorted(registers)}"
            )
        dimensions.append(
            {
                "name": name,
                "epistemic_status": registers.pop(),
                "claim_refs": sorted(str(claim["claim_id"]) for claim in claims),
                "evidence_refs": sorted(
                    {str(ref) for claim in claims for ref in claim["evidence_refs"]}
                ),
                "not_computable_reason": None,
            }
        )
    return dimensions


def build_rdi_live_wire_artifact(
    pack: Mapping[str, Any],
    evidence_objects: Sequence[Mapping[str, Any] | EvidenceObject],
    *,
    artifact_id: str,
    out_root: str | Path = "out",
    artifact_store: ArtifactStore | None = None,
) -> dict[str, Any]:
    """Build and write a SANDBOX-only, detection-only live-wire artifact."""
    if not artifact_id or Path(artifact_id).name != artifact_id:
        raise ValueError("artifact_id must be a non-empty filename-safe identifier")
    validated_pack = assert_valid_evidence_pack(pack)
    validated_objects = _validated_evidence_objects(evidence_objects)
    if not validated_objects:
        raise ValueError("RDI live wiring requires at least one EvidenceObject.v1")

    start, end = _horizon_bounds(pack.get("time_horizon"))
    window = derive_rdi_live_wire_window(validated_pack, validated_objects)
    aliases = _source_aliases(validated_pack)

    by_alias: dict[str, list[dict[str, Any]]] = {}
    for item in validated_objects:
        by_alias.setdefault(str(item["source"]), []).append(item)

    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    seen_claim_ids: set[str] = set()
    for claim in validated_pack.get("claims", []):
        claim_id = str(claim.get("claim_id", "")).strip()
        if not claim_id or claim_id in seen_claim_ids:
            raise ValueError(
                "RDI live-wire claims require unique non-blank claim_id values"
            )
        seen_claim_ids.add(claim_id)
        register = str(claim.get("register", "")).upper()
        dimension = _claim_dimension(claim)
        if register not in {"OBSERVED", "INFERRED"}:
            excluded.append({"claim_id": claim_id, "reason": "REGISTER_NOT_ALLOWED"})
            continue
        if dimension is None:
            excluded.append({"claim_id": claim_id, "reason": "DIMENSION_NOT_TARGETED"})
            continue
        refs = sorted({str(ref) for ref in claim.get("source_ids", [])})
        objects_by_ref: dict[str, list[dict[str, Any]]] = {}
        for ref in refs:
            matched = {
                str(item["hash"]): item
                for alias in aliases.get(ref, frozenset())
                for item in by_alias.get(alias, [])
                if (timestamp := _iso_timestamp(item["timestamp"])) is not None
                and start <= timestamp <= end
            }
            objects_by_ref[ref] = [matched[key] for key in sorted(matched)]
        if not refs or any(not objects_by_ref[ref] for ref in refs):
            excluded.append(
                {"claim_id": claim_id, "reason": "MISSING_IN_WINDOW_EVIDENCE"}
            )
            continue
        objects = [item for ref in refs for item in objects_by_ref[ref]]
        selected.append(
            {
                "claim_id": claim_id,
                "dimension": dimension,
                "register": register,
                "source_ids": refs,
                "evidence_refs": sorted({str(item["hash"]) for item in objects}),
                "evidence_object_timestamps": sorted(
                    {
                        _normalized_iso_timestamp(str(item["timestamp"]))
                        for item in objects
                    }
                ),
            }
        )
    selected.sort(
        key=lambda item: (DIMENSIONS.index(item["dimension"]), item["claim_id"])
    )
    excluded.sort(key=lambda item: (item["claim_id"], item["reason"]))
    if not selected:
        raise ValueError(
            "RDI live wiring found no eligible OBSERVED or INFERRED dimension claims "
            "with complete in-window EvidenceObject evidence"
        )

    packet = _build_rdi_construct_packet().to_dict()
    packet_hash = canonical_hash(packet)
    state = build_instantiation_state(
        state_id=f"is-rdi-{canonical_hash({'pack_id': pack['pack_id'], 'window': window})[:16]}",
        construct_id=packet["object_id"],
        construct_hash=packet_hash,
        observation_start=window["start"],
        observation_end=window["end"],
        dimensions=_live_wire_dimensions(selected),
        causal_exposure="UNKNOWN",
    )
    shadow_report = detect_instantiation_anomalies(
        [state], report_id=f"rdi-shadow-{artifact_id}"
    )
    artifact: dict[str, Any] = {
        "schema_version": RDI_LIVE_WIRE_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "lane": "SHADOW",
        "activation_lane": "SANDBOX",
        "dry_run": True,
        "detection_only": True,
        "console_feed_changed": False,
        "source_pack_id": pack.get("pack_id"),
        "source_pack_hash": canonical_hash(validated_pack),
        "window": window,
        "construct_packet": packet,
        "construct_packet_hash": packet_hash,
        "selected_claims": selected,
        "excluded_claims": excluded,
        "instantiation_state": state,
        "shadow_report": shadow_report,
        "authority": dict(SHADOW_AUTHORITY),
    }
    store = artifact_store or FilesystemArtifactStore(
        Path(out_root).resolve().parent,
        Path(out_root).resolve(),
    )
    return store.write_artifact(
        f"out/{RDI_LIVE_WIRE_KIND}/{artifact_id}.json",
        artifact,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )


def _finding(code: str, severity: str, subject_id: str, message: str) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "subject_id": subject_id,
        "message": message,
    }


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
