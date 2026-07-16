"""Deterministic, projection-only ROUTE_RECEIPT advisory alert evaluation."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


SCHEMA_VERSION = "AALViz.RouteReceiptAdvisoryAlerts.v1"
ACKNOWLEDGEMENT_SCHEMA_VERSION = "AALViz.RouteReceiptAdvisoryAcknowledgements.v1"
GENERATED_BY = "ROUTE_RECEIPT_ADVISORY_ALERTS_001"
POLICY_VERSION = "ROUTE_RECEIPT_ADVISORY_ALERTS_POLICY.v1"
COOLDOWN_SECONDS = 86_400
SUPPORTED_CONFIDENCE = {"SUPPORTED", "VERIFIED"}
SEVERITY_ORDER = {"NOT_COMPUTABLE": 0, "INFO": 1, "LOW": 2, "MEDIUM": 3, "HIGH": 4}
AUTHORITY = {
    "projection_only": True,
    "receipt_advisory_only": True,
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "topology_mutation_allowed": False,
    "graph_driven_execution_allowed": False,
    "production_activation_allowed": False,
    "scheduling_allowed": False,
    "notification_delivery_allowed": False,
    "acknowledgement_writeback_allowed": False,
    "browser_persistence_allowed": False,
    "automatic_remediation_allowed": False,
    "autonomous_escalation_allowed": False,
}
ACKNOWLEDGEMENT_AUTHORITY = {
    "projection_metadata_only": True,
    "execution_authority": False,
    "suppression_allowed": False,
    "closure_allowed": False,
    "reprioritization_allowed": False,
    "writeback_allowed": False,
}


class RouteReceiptAdvisoryAlertsError(ValueError):
    """Raised when advisory alerts cannot be published safely."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def typed_id(prefix: str, *identity: Any) -> str:
    return f"{prefix}:{sha256_json(list(identity))}"


def _repository_path(value: str) -> str:
    candidate = PurePosixPath(value)
    if (
        not value
        or candidate.is_absolute()
        or ".." in candidate.parts
        or "\\" in value
        or (len(value) > 2 and value[1] == ":")
    ):
        raise RouteReceiptAdvisoryAlertsError(
            f"published source path must be repository-relative POSIX: {value}"
        )
    return value


def _hash(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise RouteReceiptAdvisoryAlertsError(f"{label} is malformed")
    try:
        int(value, 16)
    except ValueError as exc:
        raise RouteReceiptAdvisoryAlertsError(f"{label} is malformed") from exc
    return value


def _canonical_hash(artifact: Mapping[str, Any]) -> str:
    return sha256_json(
        {key: value for key, value in artifact.items() if key != "canonical_hash"}
    )


def _generation_id(artifact: Mapping[str, Any]) -> str:
    semantic = copy.deepcopy(dict(artifact))
    semantic.pop("canonical_hash", None)
    generation = semantic["generation"]
    generation.pop("generated_at", None)
    generation.pop("alert_generation_id", None)
    return sha256_json(semantic)


def _acknowledgement_generation_id(artifact: Mapping[str, Any]) -> str:
    semantic = copy.deepcopy(dict(artifact))
    semantic.pop("canonical_hash", None)
    generation = semantic["generation"]
    generation.pop("generated_at", None)
    generation.pop("acknowledgement_generation_id", None)
    return sha256_json(semantic)


def _source(
    key: str,
    path: str,
    artifact: Mapping[str, Any] | None,
    content_hash: str | None,
) -> dict[str, Any]:
    _repository_path(path)
    declared = artifact.get("canonical_hash") if artifact is not None else None
    return {
        "id": f"source:{key}",
        "source_key": key,
        "path": path,
        "declared_canonical_hash": _hash(
            declared, f"{key} canonical hash", nullable=True
        ),
        "content_sha256": _hash(content_hash, f"{key} content hash", nullable=True),
        "integrity_state": "VERIFIED" if artifact is not None else "NOT_COMPUTABLE",
    }


def _index(records: Any, label: str, *, key: str = "id") -> dict[str, Mapping[str, Any]]:
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        raise RouteReceiptAdvisoryAlertsError(f"{label} is malformed")
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping) or not isinstance(record.get(key), str):
            raise RouteReceiptAdvisoryAlertsError(
                f"{label} contains a malformed record"
            )
        identifier = str(record[key])
        if identifier in result:
            raise RouteReceiptAdvisoryAlertsError(
                f"{label} contains duplicate {key}: {identifier}"
            )
        result[identifier] = record
    return result


def _entries(artifact: Mapping[str, Any], section: str) -> list[Mapping[str, Any]]:
    sections = artifact.get("sections")
    if not isinstance(sections, Mapping):
        raise RouteReceiptAdvisoryAlertsError("delta sections are malformed")
    envelope = sections.get(section)
    if not isinstance(envelope, Mapping):
        raise RouteReceiptAdvisoryAlertsError(f"delta {section} section is malformed")
    entries = envelope.get("entries")
    if entries is None:
        return []
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise RouteReceiptAdvisoryAlertsError(f"delta {section} entries are malformed")
    return [entry for entry in entries if isinstance(entry, Mapping)]


def _score_tier(score: int) -> str:
    if score <= 49:
        return "BASELINE"
    if score <= 69:
        return "ELEVATED"
    if score <= 84:
        return "HIGH"
    return "CRITICAL"


def _elapsed_seconds(prior: Mapping[str, Any], generated_at: str) -> int | None:
    try:
        before = datetime.fromisoformat(
            str(prior["generation"]["generated_at"]).replace("Z", "+00:00")
        )
        current = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        return None
    return max(0, int((current - before).total_seconds()))


def _candidate_context(
    priority: Mapping[str, Any],
    correlations: Mapping[str, Mapping[str, Any]],
    structural: Mapping[str, Mapping[str, Any]],
    section_statuses: Mapping[str, str],
) -> dict[str, Any]:
    source_ref = priority.get("source_ref")
    if not isinstance(source_ref, Mapping):
        raise RouteReceiptAdvisoryAlertsError("priority source reference is malformed")
    category = str(source_ref.get("category"))
    entity_id = str(source_ref.get("entity_id"))
    classes = sorted(str(value) for value in priority.get("structural_classes", []))
    context: dict[str, Any] = {
        "state": "NEW",
        "severity_change": "NOT_COMPUTABLE",
        "prior_severity": None,
        "persistence_seconds_lower_bound": None,
        "evidence_complete": section_statuses.get("review_priorities") == "AVAILABLE",
    }
    if category == "INTEGRITY_FINDING":
        correlation = correlations.get(entity_id)
        if correlation is None:
            context["evidence_complete"] = False
        else:
            context.update(
                state=str(correlation.get("state")),
                severity_change=str(correlation.get("severity_change")),
                prior_severity=correlation.get("prior_severity"),
                persistence_seconds_lower_bound=correlation.get(
                    "persistence_seconds_lower_bound"
                ),
            )
        context["evidence_complete"] = bool(context["evidence_complete"]) and (
            section_statuses.get("finding_correlation") == "AVAILABLE"
        )
    elif category == "STRUCTURAL_DELTA":
        record = structural.get(entity_id)
        if record is None:
            context["evidence_complete"] = False
        else:
            classes = sorted(
                set(classes) | {str(record.get("structural_class"))}
            )
        context["evidence_complete"] = bool(context["evidence_complete"]) and (
            section_statuses.get("structural_deltas") == "AVAILABLE"
        )
    else:
        raise RouteReceiptAdvisoryAlertsError(
            f"unsupported priority source category: {category}"
        )
    context["structural_classes"] = classes
    return context


def _triggers(
    priority: Mapping[str, Any],
    context: Mapping[str, Any],
    prior_record: Mapping[str, Any] | None,
) -> list[str]:
    state = context["state"]
    severity = str(priority["severity"])
    score = int(priority["score"])
    confidence = str(priority["confidence"])
    classes = set(context["structural_classes"])
    complete = bool(context["evidence_complete"])
    surfaces = priority.get("affected_surface_ids", [])
    result: list[str] = []
    if (
        state == "NEW"
        and severity == "HIGH"
        and score >= 70
        and confidence in SUPPORTED_CONFIDENCE
        and bool(surfaces)
        and bool(classes)
        and complete
    ):
        result.append("NEW_CRITICAL_STRUCTURAL_FINDING")
    prior_score = int(prior_record["score"]) if prior_record is not None else None
    tier_reached_high = prior_score is not None and prior_score < 70 <= score
    severity_reached_high = (
        state == "PERSISTENT"
        and context["severity_change"] == "INCREASED"
        and severity == "HIGH"
    )
    if (
        state == "PERSISTENT"
        and (severity_reached_high or tier_reached_high)
        and score >= 70
        and confidence in SUPPORTED_CONFIDENCE
        and complete
    ):
        result.append("SEVERITY_ESCALATION")
    for structural_class in (
        "VALIDATOR_COVERAGE_LOSS",
        "BROKEN_PRODUCER_CONSUMER_PATH",
        "OWNERSHIP_DRIFT",
    ):
        if (
            structural_class in classes
            and score >= 60
            and confidence in SUPPORTED_CONFIDENCE
            and complete
        ):
            result.append(structural_class)
    if (
        "TOPOLOGY_FRAGMENTATION" in classes
        and score >= 70
        and confidence in SUPPORTED_CONFIDENCE
        and complete
    ):
        result.append("TOPOLOGY_FRAGMENTATION")
    if (
        "UNEXPECTED_CLUSTER_FUSION" in classes
        and score >= 60
        and confidence in SUPPORTED_CONFIDENCE | {"INFERRED"}
        and complete
    ):
        result.append("UNEXPECTED_CLUSTER_FUSION")
    if (
        state == "PERSISTENT"
        and severity in {"MEDIUM", "HIGH"}
        and score >= 70
        and confidence in SUPPORTED_CONFIDENCE
        and int(context["persistence_seconds_lower_bound"] or 0) >= COOLDOWN_SECONDS
        and complete
    ):
        result.append("PERSISTENT_UNRESOLVED_DAMAGE")
    return sorted(result)


def _suppression_reasons(
    priority: Mapping[str, Any], context: Mapping[str, Any], triggers: Sequence[str]
) -> list[str]:
    if triggers:
        return []
    reasons = {"NO_ELIGIBLE_TRIGGER"}
    score = int(priority["score"])
    confidence = str(priority["confidence"])
    classes = set(context["structural_classes"])
    if score < 60 or ("TOPOLOGY_FRAGMENTATION" in classes and score < 70):
        reasons.add("BELOW_SCORE_THRESHOLD")
    if confidence not in SUPPORTED_CONFIDENCE and not (
        "UNEXPECTED_CLUSTER_FUSION" in classes and confidence == "INFERRED"
    ):
        reasons.add("BELOW_CONFIDENCE_THRESHOLD")
    if (
        context["state"] == "PERSISTENT"
        and int(context["persistence_seconds_lower_bound"] or 0) < COOLDOWN_SECONDS
        and score >= 70
    ):
        reasons.add("PERSISTENCE_THRESHOLD_NOT_MET")
    if (
        context["state"] == "NEW"
        and str(priority["severity"]) == "HIGH"
        and score >= 70
        and not priority.get("affected_surface_ids")
    ):
        reasons.add("NO_AFFECTED_OPERATIONAL_SURFACE")
    return sorted(reasons)


def _record(
    *,
    delta_generation_id: str,
    priority: Mapping[str, Any],
    trigger_types: Sequence[str],
    event_type: str,
    disposition: str,
    lifecycle: str = "ACTIVE",
    suppression_reasons: Iterable[str] = (),
    resolution_evidence_refs: Iterable[str] = (),
    acknowledged: bool | None = None,
    acknowledgement_ref: str | None = None,
    persistence_seconds: int | None = None,
) -> dict[str, Any]:
    source_ref = copy.deepcopy(priority["source_ref"])
    alert_id = typed_id(
        "alert", POLICY_VERSION, source_ref["category"], source_ref["entity_id"]
    )
    record = {
        "receipt_id": "",
        "receipt_kind": "ROUTE_RECEIPT_ADVISORY_ALERT",
        "alert_id": alert_id,
        "priority_id": priority.get("id"),
        "source_ref": source_ref,
        "trigger_types": sorted(set(trigger_types)),
        "event_type": event_type,
        "receipt_disposition": disposition,
        "lifecycle": lifecycle,
        "score": int(priority["score"]),
        "score_tier": _score_tier(int(priority["score"])),
        "severity": str(priority["severity"]),
        "confidence": str(priority["confidence"]),
        "persistence_seconds_lower_bound": persistence_seconds,
        "affected_surface_ids": sorted(
            set(str(value) for value in priority.get("affected_surface_ids", []))
        ),
        "evidence_refs": ["source:delta_intelligence"],
        "resolution_evidence_refs": sorted(set(resolution_evidence_refs)),
        "suppression_reasons": sorted(set(suppression_reasons)),
        "why_this_fired": str(priority["why_this_matters"]),
        "acknowledged": acknowledged,
        "acknowledgement_ref": acknowledgement_ref,
        "delivery_state": "NOT_DELIVERED",
    }
    record["receipt_id"] = typed_id(
        "receipt", alert_id, event_type, disposition, delta_generation_id
    )
    return record


def _section(
    entries: list[dict[str, Any]] | None,
    *,
    findings: Iterable[str] = (),
    unavailable_reason: str | None = None,
) -> dict[str, Any]:
    warnings = sorted(set(findings))
    if entries is None:
        return {
            "status": "NOT_COMPUTABLE",
            "provenance": "INFERRED",
            "not_computable_reason": unavailable_reason
            or warnings[0]
            if warnings
            else "Required evidence is unavailable.",
            "validation_findings": warnings,
            "entries": None,
        }
    return {
        "status": "PARTIAL" if warnings else "AVAILABLE",
        "provenance": "INFERRED",
        "not_computable_reason": None,
        "validation_findings": warnings,
        "entries": sorted(entries, key=lambda item: item["receipt_id"]),
    }


def _all_prior_records(prior: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    sections = prior.get("sections")
    if not isinstance(sections, Mapping):
        return records
    for name in ("active_alerts", "suppressed_candidates"):
        section = sections.get(name)
        entries = section.get("entries") if isinstance(section, Mapping) else None
        if not isinstance(entries, Sequence):
            continue
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            alert_id = str(entry.get("alert_id"))
            if alert_id in records:
                raise RouteReceiptAdvisoryAlertsError(
                    f"prior alerts contain duplicate alert id: {alert_id}"
                )
            records[alert_id] = entry
    return records


def _summary(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    active = sections["active_alerts"].get("entries") or []
    resolved = sections["resolved_alerts"].get("entries") or []
    suppressed = sections["suppressed_candidates"].get("entries") or []
    return {
        "candidate_count": len(active) + len(suppressed),
        "active_count": len(active),
        "resolved_count": len(resolved),
        "suppressed_count": len(suppressed),
        "not_computable_count": sum(
            section["status"] == "NOT_COMPUTABLE" for section in sections.values()
        ),
        "published_receipt_count": sum(
            entry["receipt_disposition"] == "PUBLISH"
            for section in sections.values()
            for entry in section.get("entries") or []
        ),
        "highest_active_score": max(
            (int(entry["score"]) for entry in active), default=None
        ),
    }


def evaluate_route_receipt_advisory_alerts(
    delta_intelligence: Mapping[str, Any],
    *,
    prior_alerts: Mapping[str, Any] | None = None,
    acknowledgements: Mapping[str, Any] | None = None,
    source_paths: Mapping[str, str],
    content_hashes: Mapping[str, str | None],
    generated_at: str,
) -> dict[str, Any]:
    """Evaluate one explicit delta projection without discovery or retention."""
    delta_generation = delta_intelligence["generation"]
    delta_id = str(delta_generation["delta_generation_id"])
    generation = {
        "generated_at": generated_at,
        "generated_by": GENERATED_BY,
        "alert_generation_id": "0" * 64,
        "delta_generation_id": delta_id,
        "prior_topology_generation_id": str(
            delta_generation["prior_topology_generation_id"]
        ),
        "current_topology_generation_id": str(
            delta_generation["current_topology_generation_id"]
        ),
        "prior_operator_platform_generation_id": str(
            delta_generation["prior_operator_platform_generation_id"]
        ),
        "current_operator_platform_generation_id": str(
            delta_generation["current_operator_platform_generation_id"]
        ),
        "prior_alert_generation_id": None,
        "acknowledgement_generation_id": None,
    }
    sources = sorted(
        [
            _source(key, source_paths[key], artifact, content_hashes.get(key))
            for key, artifact in (
                ("delta_intelligence", delta_intelligence),
                ("prior_alerts", prior_alerts),
                ("acknowledgements", acknowledgements),
            )
        ],
        key=lambda item: item["id"],
    )
    validation_findings: list[str] = []
    usable_prior = prior_alerts
    if prior_alerts is not None and (
        prior_alerts["generation"]["current_topology_generation_id"]
        != generation["prior_topology_generation_id"]
        or prior_alerts["generation"]["current_operator_platform_generation_id"]
        != generation["prior_operator_platform_generation_id"]
    ):
        usable_prior = None
        validation_findings.append(
            "Prior alert generation binding mismatch; history was suppressed."
        )
    if usable_prior is not None:
        generation["prior_alert_generation_id"] = usable_prior["generation"][
            "alert_generation_id"
        ]
    if acknowledgements is not None:
        generation["acknowledgement_generation_id"] = acknowledgements["generation"][
            "acknowledgement_generation_id"
        ]
    correlations = _index(
        _entries(delta_intelligence, "finding_correlation"), "finding correlations"
    )
    structural = _index(
        _entries(delta_intelligence, "structural_deltas"), "structural deltas"
    )
    priorities = _entries(delta_intelligence, "review_priorities")
    section_statuses = {
        name: str(section["status"])
        for name, section in delta_intelligence["sections"].items()
    }
    prior_records = _all_prior_records(usable_prior) if usable_prior is not None else {}
    acknowledgement_records = (
        _index(acknowledgements["records"], "acknowledgements", key="alert_id")
        if acknowledgements is not None
        else {}
    )
    elapsed = _elapsed_seconds(usable_prior, generated_at) if usable_prior else None
    active: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    non_computable_records: list[dict[str, Any]] = []
    seen_alerts: set[str] = set()
    for priority in priorities:
        context = _candidate_context(
            priority, correlations, structural, section_statuses
        )
        source_ref = priority["source_ref"]
        alert_id = typed_id(
            "alert",
            POLICY_VERSION,
            source_ref["category"],
            source_ref["entity_id"],
        )
        prior_record = prior_records.get(alert_id)
        triggers = _triggers(priority, context, prior_record)
        acknowledgement = acknowledgement_records.get(alert_id)
        acknowledged = True if acknowledgement is not None else False if acknowledgements else None
        acknowledgement_ref = (
            str(acknowledgement["id"]) if acknowledgement is not None else None
        )
        if not context["evidence_complete"]:
            non_computable_records.append(
                _record(
                    delta_generation_id=delta_id,
                    priority=priority,
                    trigger_types=[],
                    event_type="FIRST_OBSERVED"
                    if prior_record is None
                    else "CARRIED_FORWARD",
                    disposition="NOT_COMPUTABLE",
                    acknowledged=acknowledged,
                    acknowledgement_ref=acknowledgement_ref,
                    persistence_seconds=context["persistence_seconds_lower_bound"],
                )
            )
            seen_alerts.add(alert_id)
            continue
        if not triggers:
            suppressed.append(
                _record(
                    delta_generation_id=delta_id,
                    priority=priority,
                    trigger_types=[],
                    event_type="FIRST_OBSERVED"
                    if prior_record is None
                    else "CARRIED_FORWARD",
                    disposition="SUPPRESS",
                    suppression_reasons=_suppression_reasons(
                        priority, context, triggers
                    ),
                    acknowledged=acknowledged,
                    acknowledgement_ref=acknowledgement_ref,
                    persistence_seconds=context["persistence_seconds_lower_bound"],
                )
            )
            seen_alerts.add(alert_id)
            continue
        changed = prior_record is not None and (
            prior_record["severity"] != priority["severity"]
            or prior_record["score_tier"] != _score_tier(int(priority["score"]))
            or list(prior_record["trigger_types"]) != triggers
        )
        if prior_record is None:
            event_type, disposition, reasons = "FIRST_OBSERVED", "PUBLISH", []
        elif changed:
            event_type, disposition, reasons = "UPDATED", "PUBLISH", []
        elif elapsed is not None and elapsed >= COOLDOWN_SECONDS:
            event_type, disposition, reasons = "REFRESHED", "PUBLISH", []
        else:
            event_type, disposition, reasons = (
                "CARRIED_FORWARD",
                "SUPPRESS",
                ["UNCHANGED_WITHIN_COOLDOWN"],
            )
        active.append(
            _record(
                delta_generation_id=delta_id,
                priority=priority,
                trigger_types=triggers,
                event_type=event_type,
                disposition=disposition,
                suppression_reasons=reasons,
                acknowledged=acknowledged,
                acknowledgement_ref=acknowledgement_ref,
                persistence_seconds=context["persistence_seconds_lower_bound"],
            )
        )
        seen_alerts.add(alert_id)

    resolved: list[dict[str, Any]] = []
    for alert_id, prior_record in sorted(prior_records.items()):
        if alert_id in seen_alerts or prior_record.get("lifecycle") != "ACTIVE":
            continue
        source_ref = prior_record["source_ref"]
        correlation = (
            correlations.get(str(source_ref["entity_id"]))
            if source_ref["category"] == "INTEGRITY_FINDING"
            else None
        )
        can_resolve = (
            correlation is not None
            and correlation.get("state") == "RESOLVED"
            and section_statuses.get("finding_correlation") == "AVAILABLE"
        )
        acknowledgement = acknowledgement_records.get(alert_id)
        priority = {
            "id": prior_record.get("priority_id"),
            "source_ref": copy.deepcopy(source_ref),
            "score": prior_record["score"],
            "severity": prior_record["severity"],
            "confidence": prior_record["confidence"],
            "affected_surface_ids": prior_record["affected_surface_ids"],
            "why_this_matters": prior_record["why_this_fired"],
        }
        if can_resolve:
            resolved.append(
                _record(
                    delta_generation_id=delta_id,
                    priority=priority,
                    trigger_types=prior_record["trigger_types"],
                    event_type="RESOLVED",
                    disposition="PUBLISH",
                    lifecycle="RESOLVED",
                    resolution_evidence_refs=["source:delta_intelligence"],
                    acknowledged=True if acknowledgement is not None else None,
                    acknowledgement_ref=str(acknowledgement["id"])
                    if acknowledgement is not None
                    else None,
                    persistence_seconds=prior_record[
                        "persistence_seconds_lower_bound"
                    ],
                )
            )
        else:
            active.append(
                _record(
                    delta_generation_id=delta_id,
                    priority=priority,
                    trigger_types=prior_record["trigger_types"],
                    event_type="CARRIED_FORWARD",
                    disposition="NOT_COMPUTABLE",
                    acknowledged=True if acknowledgement is not None else None,
                    acknowledgement_ref=str(acknowledgement["id"])
                    if acknowledgement is not None
                    else None,
                    persistence_seconds=prior_record[
                        "persistence_seconds_lower_bound"
                    ],
                )
            )

    known_alerts = {
        record["alert_id"]
        for group in (active, suppressed, non_computable_records, resolved)
        for record in group
    }
    unknown_acknowledgements = sorted(set(acknowledgement_records) - known_alerts)
    if unknown_acknowledgements:
        validation_findings.append(
            "Acknowledgements with unknown alert references were excluded: "
            + ", ".join(unknown_acknowledgements)
        )
    optional_findings: list[str] = []
    if prior_alerts is None:
        optional_findings.append(
            "Prior alert projection was unavailable; cooldown, deduplication, and historical closure are partial."
        )
    elif usable_prior is None:
        optional_findings.append(
            "Prior alert generation mismatch suppressed history-dependent conclusions."
        )
    if acknowledgements is None:
        optional_findings.append("Acknowledgement metadata is unavailable.")
    if non_computable_records:
        not_computable = _section(
            non_computable_records,
            findings=[
                "One or more alert candidates lacked complete eligibility evidence."
            ]
            + optional_findings,
        )
    elif optional_findings:
        not_computable = _section(
            None,
            findings=optional_findings,
            unavailable_reason="Optional history or acknowledgement evidence was unavailable.",
        )
    else:
        not_computable = _section([])
    sections = {
        "eligibility_decisions": _section([]),
        "active_alerts": _section(active),
        "resolved_alerts": _section(
            resolved if usable_prior is not None else [],
            findings=[] if usable_prior is not None else [
                "Historical closure requires a matching prior alert projection."
            ],
        ),
        "suppressed_candidates": _section(suppressed),
        "not_computable": not_computable,
    }
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generation": generation,
        "status": "PARTIAL"
        if validation_findings
        or optional_findings
        or any(section["status"] != "AVAILABLE" for section in sections.values())
        else "AVAILABLE",
        "provenance": "INFERRED",
        "source_artifacts": sources,
        "policy": {
            "policy_version": POLICY_VERSION,
            "cooldown_seconds": COOLDOWN_SECONDS,
            "persistence_seconds": COOLDOWN_SECONDS,
            "score_tiers": [49, 69, 84, 100],
        },
        "sections": sections,
        "summary": _summary(sections),
        "authority": dict(AUTHORITY),
        "validation_findings": sorted(set(validation_findings + optional_findings)),
        "canonical_hash": "0" * 64,
    }
    artifact["generation"]["alert_generation_id"] = _generation_id(artifact)
    artifact["canonical_hash"] = _canonical_hash(artifact)
    return artifact


def validate_route_receipt_advisory_acknowledgements(
    artifact: Mapping[str, Any], schema_path: Path
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise RouteReceiptAdvisoryAlertsError(
            f"acknowledgement schema violation: {errors[0].message}"
        )
    if artifact.get("authority") != ACKNOWLEDGEMENT_AUTHORITY:
        raise RouteReceiptAdvisoryAlertsError(
            "acknowledgement authority locks are malformed"
        )
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        raise RouteReceiptAdvisoryAlertsError("acknowledgement canonical hash mismatch")
    if (
        artifact["generation"]["acknowledgement_generation_id"]
        != _acknowledgement_generation_id(artifact)
    ):
        raise RouteReceiptAdvisoryAlertsError(
            "acknowledgement generation id mismatch"
        )
    records = artifact["records"]
    if records != sorted(records, key=lambda item: item["id"]):
        raise RouteReceiptAdvisoryAlertsError(
            "acknowledgements are not canonically ordered"
        )
    for record in records:
        expected = typed_id(
            "ack", record["alert_id"], record["acknowledged_at"], record["operator_ref"]
        )
        if record["id"] != expected:
            raise RouteReceiptAdvisoryAlertsError("acknowledgement id mismatch")


def validate_route_receipt_advisory_alerts(
    artifact: Mapping[str, Any], schema_path: Path
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise RouteReceiptAdvisoryAlertsError(
            f"advisory alerts schema violation: {errors[0].message}"
        )
    if artifact.get("authority") != AUTHORITY:
        raise RouteReceiptAdvisoryAlertsError(
            "advisory alert authority locks are malformed"
        )
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        raise RouteReceiptAdvisoryAlertsError("advisory alert canonical hash mismatch")
    if artifact["generation"]["alert_generation_id"] != _generation_id(artifact):
        raise RouteReceiptAdvisoryAlertsError("advisory alert generation id mismatch")
    sources = artifact["source_artifacts"]
    if sources != sorted(sources, key=lambda item: item["id"]):
        raise RouteReceiptAdvisoryAlertsError(
            "advisory alert sources are not canonically ordered"
        )
    source_ids = {source["id"] for source in sources}
    if len(source_ids) != len(sources):
        raise RouteReceiptAdvisoryAlertsError("duplicate advisory alert source id")
    if artifact["validation_findings"] != sorted(artifact["validation_findings"]):
        raise RouteReceiptAdvisoryAlertsError(
            "advisory alert findings are not canonically ordered"
        )
    receipt_ids: set[str] = set()
    acknowledgement_ids: set[str] = set()
    for name, section in artifact["sections"].items():
        entries = section["entries"]
        if section["status"] == "NOT_COMPUTABLE":
            if entries is not None or not section["not_computable_reason"]:
                raise RouteReceiptAdvisoryAlertsError(
                    f"{name} NOT_COMPUTABLE envelope mismatch"
                )
            continue
        if entries is None or section["not_computable_reason"] is not None:
            raise RouteReceiptAdvisoryAlertsError(f"{name} available envelope mismatch")
        if entries != sorted(entries, key=lambda item: item["receipt_id"]):
            raise RouteReceiptAdvisoryAlertsError(
                f"{name} is not canonically ordered"
            )
        for entry in entries:
            if entry["receipt_id"] in receipt_ids:
                raise RouteReceiptAdvisoryAlertsError("duplicate receipt id")
            receipt_ids.add(entry["receipt_id"])
            expected_alert = typed_id(
                "alert",
                POLICY_VERSION,
                entry["source_ref"]["category"],
                entry["source_ref"]["entity_id"],
            )
            expected_receipt = typed_id(
                "receipt",
                expected_alert,
                entry["event_type"],
                entry["receipt_disposition"],
                artifact["generation"]["delta_generation_id"],
            )
            if entry["alert_id"] != expected_alert or entry["receipt_id"] != expected_receipt:
                raise RouteReceiptAdvisoryAlertsError("advisory receipt identity mismatch")
            if entry["score_tier"] != _score_tier(entry["score"]):
                raise RouteReceiptAdvisoryAlertsError("advisory alert score tier mismatch")
            for field in (
                "trigger_types",
                "affected_surface_ids",
                "evidence_refs",
                "resolution_evidence_refs",
                "suppression_reasons",
            ):
                if entry[field] != sorted(entry[field]):
                    raise RouteReceiptAdvisoryAlertsError(
                        f"advisory alert {field} is not canonical"
                    )
            if not set(entry["evidence_refs"] + entry["resolution_evidence_refs"]).issubset(source_ids):
                raise RouteReceiptAdvisoryAlertsError("dangling alert evidence reference")
            if entry["acknowledgement_ref"] is not None:
                acknowledgement_ids.add(entry["acknowledgement_ref"])
            if name == "resolved_alerts" and not (
                entry["lifecycle"] == "RESOLVED"
                and entry["event_type"] == "RESOLVED"
                and entry["receipt_disposition"] == "PUBLISH"
                and entry["resolution_evidence_refs"]
            ):
                raise RouteReceiptAdvisoryAlertsError("false alert resolution")
            if name == "suppressed_candidates" and not (
                entry["lifecycle"] == "ACTIVE"
                and entry["receipt_disposition"] == "SUPPRESS"
                and entry["suppression_reasons"]
            ):
                raise RouteReceiptAdvisoryAlertsError("invalid suppressed candidate")
    if acknowledgement_ids and artifact["generation"]["acknowledgement_generation_id"] is None:
        raise RouteReceiptAdvisoryAlertsError("dangling acknowledgement reference")
    if artifact["summary"] != _summary(artifact["sections"]):
        raise RouteReceiptAdvisoryAlertsError("advisory alert summary mismatch")
