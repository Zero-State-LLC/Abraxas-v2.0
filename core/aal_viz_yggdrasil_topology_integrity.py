"""Deterministic, projection-only integrity findings for YGGDRASIL topology."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

from core.aal_viz_temporal_diff import AUTHORITY as TEMPORAL_AUTHORITY
from core.aal_viz_yggdrasil_topology import AUTHORITY as TOPOLOGY_AUTHORITY

SCHEMA_VERSION = "AALViz.YggdrasilTopologyIntegrity.v1"
GENERATED_BY = "YGGDRASIL_TOPOLOGY_INTEGRITY_FINDINGS_001"
SEVERITY_BY_TYPE = {
    "GENERATION_MISMATCH": "HIGH",
    "INFERRED_LINK": "INFO",
    "MISSING_EVIDENCE": "LOW",
    "SECTION_NOT_COMPUTABLE": "NOT_COMPUTABLE",
    "SOURCE_INTEGRITY_GAP": "HIGH",
    "STALE_ENTITY": "MEDIUM",
    "TEMPORAL_REMOVAL": "MEDIUM",
    "TEMPORAL_WEAKENING": "MEDIUM",
    "UNRESOLVED_ENTITY": "MEDIUM",
}
TEMPORAL_TYPES = {"TEMPORAL_REMOVAL", "TEMPORAL_WEAKENING"}
AUTHORITY = {
    "projection_only": True,
    "runtime_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "execution_authority": False,
    "production_activation_allowed": False,
    "graph_driven_execution_allowed": False,
    "alert_delivery_allowed": False,
    "acknowledgement_state_allowed": False,
    "browser_persistence_allowed": False,
    "route_receipt_triggering_allowed": False,
    "scheduling_allowed": False,
}


class YggdrasilTopologyIntegrityError(ValueError):
    """Raised when integrity input or output violates the locked contract."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _hash(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise YggdrasilTopologyIntegrityError(
            f"{label} must be a lowercase SHA-256 hash"
        )
    return value


def _repository_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in value
        or (len(value) > 2 and value[1] == ":")
    ):
        raise YggdrasilTopologyIntegrityError(
            f"published path must be repository-relative POSIX: {value}"
        )
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
    generation.pop("integrity_generation_id", None)
    return sha256_json(semantic)


def finding_id(
    finding_type: str,
    entity_ref: Mapping[str, Any] | None,
    subject_key: str,
    topology_generation_id: str,
) -> str:
    reference = entity_ref or {}
    identity = [
        finding_type,
        reference.get("category"),
        reference.get("entity_id"),
        subject_key,
        topology_generation_id,
    ]
    return f"finding:{sha256_json(identity)}"


def _source_descriptor(
    source_key: str,
    path: str,
    artifact: Mapping[str, Any] | None,
    content_sha256: str | None,
) -> dict[str, Any]:
    _repository_path(path)
    content_hash = _hash(
        content_sha256, f"{source_key} content hash", nullable=True
    )
    declared = artifact.get("canonical_hash") if artifact is not None else None
    declared_hash = _hash(
        declared, f"{source_key} canonical hash", nullable=True
    )
    return {
        "id": f"source:{source_key}",
        "source_key": source_key,
        "path": path,
        "declared_canonical_hash": declared_hash,
        "content_sha256": content_hash,
        "integrity_state": "VERIFIED" if artifact is not None else "NOT_COMPUTABLE",
    }


def _validate_topology_input(topology: Mapping[str, Any]) -> None:
    if topology.get("schema_version") != "AALViz.YggdrasilTopology.v1":
        raise YggdrasilTopologyIntegrityError("unsupported topology schema")
    if topology.get("authority") != TOPOLOGY_AUTHORITY:
        raise YggdrasilTopologyIntegrityError("topology authority violation")
    if topology.get("canonical_hash") != sha256_json(
        {key: value for key, value in topology.items() if key != "canonical_hash"}
    ):
        raise YggdrasilTopologyIntegrityError("topology canonical hash mismatch")
    generation = topology.get("generation")
    if not isinstance(generation, Mapping):
        raise YggdrasilTopologyIntegrityError("topology generation is malformed")
    _hash(generation.get("topology_generation_id"), "topology generation id")
    _hash(
        generation.get("operator_platform_generation_id"),
        "operator platform generation id",
        nullable=True,
    )
    payload = topology.get("payload")
    if topology.get("status") == "NOT_COMPUTABLE":
        if payload is not None:
            raise YggdrasilTopologyIntegrityError(
                "not-computable topology payload must be null"
            )
        return
    if not isinstance(payload, Mapping):
        raise YggdrasilTopologyIntegrityError("topology payload is malformed")
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    evidence = payload.get("evidence")
    if not all(isinstance(items, Sequence) for items in (nodes, edges, evidence)):
        raise YggdrasilTopologyIntegrityError("topology collections are malformed")
    node_ids = [item.get("id") for item in nodes if isinstance(item, Mapping)]
    edge_ids = [item.get("id") for item in edges if isinstance(item, Mapping)]
    evidence_ids = [item.get("id") for item in evidence if isinstance(item, Mapping)]
    for label, identities, records in (
        ("node", node_ids, nodes),
        ("edge", edge_ids, edges),
        ("evidence", evidence_ids, evidence),
    ):
        if len(identities) != len(records) or any(
            not isinstance(identity, str) or not identity for identity in identities
        ):
            raise YggdrasilTopologyIntegrityError(
                f"topology contains a malformed {label}"
            )
        if identities != sorted(identities) or len(identities) != len(set(identities)):
            raise YggdrasilTopologyIntegrityError(
                f"topology {label} identities are invalid"
            )
    node_set = set(node_ids)
    evidence_set = set(evidence_ids)
    for edge in edges:
        if edge.get("source") not in node_set or edge.get("target") not in node_set:
            raise YggdrasilTopologyIntegrityError("topology contains a dangling edge")
    for entity in [*nodes, *edges]:
        references = entity.get("evidence_refs")
        if not isinstance(references, list) or not set(references).issubset(evidence_set):
            raise YggdrasilTopologyIntegrityError(
                "topology contains a dangling evidence reference"
            )


def _validate_temporal_input(temporal_diff: Mapping[str, Any]) -> None:
    if temporal_diff.get("schema_version") != "AALViz.TemporalDiff.v1":
        raise YggdrasilTopologyIntegrityError("unsupported Temporal Diff schema")
    if temporal_diff.get("authority") != TEMPORAL_AUTHORITY:
        raise YggdrasilTopologyIntegrityError("Temporal Diff authority violation")
    if temporal_diff.get("canonical_hash") != sha256_json(
        {
            key: value
            for key, value in temporal_diff.items()
            if key != "canonical_hash"
        }
    ):
        raise YggdrasilTopologyIntegrityError(
            "Temporal Diff canonical hash mismatch"
        )
    current = temporal_diff.get("current_generation")
    if not isinstance(current, Mapping):
        raise YggdrasilTopologyIntegrityError(
            "Temporal Diff current generation is malformed"
        )
    _hash(
        current.get("generation_id"),
        "Temporal Diff current generation id",
        nullable=True,
    )
    entries = temporal_diff.get("entries")
    if not isinstance(entries, list):
        raise YggdrasilTopologyIntegrityError("Temporal Diff entries are malformed")
    entry_ids = [entry.get("id") for entry in entries if isinstance(entry, Mapping)]
    if len(entry_ids) != len(entries) or len(entry_ids) != len(set(entry_ids)):
        raise YggdrasilTopologyIntegrityError(
            "Temporal Diff entries contain duplicate or malformed ids"
        )


def _finding(
    finding_type: str,
    subject_key: str,
    generation: Mapping[str, Any],
    *,
    entity_ref: Mapping[str, Any] | None,
    evidence_refs: Sequence[str],
    provenance: str,
    confidence: str,
    reason: str,
) -> dict[str, Any]:
    topology_id = str(generation["topology_generation_id"])
    return {
        "id": finding_id(finding_type, entity_ref, subject_key, topology_id),
        "finding_type": finding_type,
        "severity": SEVERITY_BY_TYPE[finding_type],
        "subject_key": subject_key,
        "entity_ref": dict(entity_ref) if entity_ref is not None else None,
        "evidence_refs": sorted(set(evidence_refs)),
        "provenance": provenance,
        "confidence": confidence,
        "reason": reason,
        "computability": (
            "NOT_COMPUTABLE"
            if finding_type == "SECTION_NOT_COMPUTABLE"
            else "COMPUTABLE"
        ),
        "generation_binding": {
            "topology_generation_id": generation["topology_generation_id"],
            "operator_platform_generation_id": generation[
                "operator_platform_generation_id"
            ],
            "temporal_diff_generation_id": generation[
                "temporal_diff_generation_id"
            ],
        },
    }


def _summary(findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    entities = {
        (finding["entity_ref"]["category"], finding["entity_ref"]["entity_id"])
        for finding in findings
        if isinstance(finding.get("entity_ref"), Mapping)
    }
    return {
        "finding_count": len(findings),
        "affected_entity_count": len(entities),
        "non_computable_count": sum(
            finding["computability"] == "NOT_COMPUTABLE" for finding in findings
        ),
        "severity_counts": dict(
            sorted(Counter(finding["severity"] for finding in findings).items())
        ),
        "type_counts": dict(
            sorted(Counter(finding["finding_type"] for finding in findings).items())
        ),
    }


def evaluate_yggdrasil_topology_integrity(
    topology: Mapping[str, Any] | None,
    temporal_diff: Mapping[str, Any] | None,
    *,
    topology_path: str,
    temporal_diff_path: str,
    topology_content_sha256: str | None,
    temporal_diff_content_sha256: str | None,
    generated_at: str,
) -> dict[str, Any]:
    """Evaluate explicit projections without discovery, retention, or mutation."""
    topology_source = _source_descriptor(
        "topology", topology_path, topology, topology_content_sha256
    )
    temporal_source = _source_descriptor(
        "temporal_diff",
        temporal_diff_path,
        temporal_diff,
        temporal_diff_content_sha256,
    )
    sources = sorted([temporal_source, topology_source], key=lambda item: item["id"])
    if topology is None:
        artifact: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "generation": {
                "generated_at": generated_at,
                "generated_by": GENERATED_BY,
                "integrity_generation_id": "0" * 64,
                "topology_generation_id": None,
                "operator_platform_generation_id": None,
                "temporal_diff_generation_id": None,
            },
            "status": "NOT_COMPUTABLE",
            "provenance": "INFERRED",
            "source_artifacts": sources,
            "authority": dict(AUTHORITY),
            "payload": None,
            "not_computable_reason": "No usable topology evidence was supplied.",
            "validation_findings": ["Topology evidence was unavailable."],
            "canonical_hash": "0" * 64,
        }
        artifact["generation"]["integrity_generation_id"] = _generation_id(
            artifact
        )
        artifact["canonical_hash"] = _canonical_hash(artifact)
        return artifact

    _validate_topology_input(topology)
    if temporal_diff is not None:
        _validate_temporal_input(temporal_diff)
    topology_generation = topology["generation"]
    topology_id = topology_generation["topology_generation_id"]
    operator_id = topology_generation["operator_platform_generation_id"]
    if topology.get("status") == "NOT_COMPUTABLE":
        artifact = {
            "schema_version": SCHEMA_VERSION,
            "generation": {
                "generated_at": generated_at,
                "generated_by": GENERATED_BY,
                "integrity_generation_id": "0" * 64,
                "topology_generation_id": topology_id,
                "operator_platform_generation_id": operator_id,
                "temporal_diff_generation_id": None,
            },
            "status": "NOT_COMPUTABLE",
            "provenance": "INFERRED",
            "source_artifacts": sources,
            "authority": dict(AUTHORITY),
            "payload": None,
            "not_computable_reason": "The supplied topology projection is not computable.",
            "validation_findings": ["Topology evidence was not computable."],
            "canonical_hash": "0" * 64,
        }
        artifact["generation"]["integrity_generation_id"] = _generation_id(
            artifact
        )
        artifact["canonical_hash"] = _canonical_hash(artifact)
        return artifact
    temporal_id: str | None = None
    if temporal_diff is not None:
        temporal_id = temporal_diff["current_generation"]["generation_id"]
    generation = {
        "generated_at": generated_at,
        "generated_by": GENERATED_BY,
        "integrity_generation_id": "0" * 64,
        "topology_generation_id": topology_id,
        "operator_platform_generation_id": operator_id,
        "temporal_diff_generation_id": temporal_id,
    }
    findings: list[dict[str, Any]] = []
    validation_findings: list[str] = []
    partial = topology.get("status") != "AVAILABLE"
    payload = topology.get("payload")
    if not isinstance(payload, Mapping):
        raise YggdrasilTopologyIntegrityError(
            "usable topology must contain an object payload"
        )
    evidence = {
        item["id"]: item for item in payload["evidence"] if isinstance(item, Mapping)
    }
    entities = [*payload["nodes"], *payload["edges"]]
    for record in sorted(evidence.values(), key=lambda item: item["id"]):
        if record.get("integrity_state") != "VERIFIED":
            partial = True
            findings.append(
                _finding(
                    "SOURCE_INTEGRITY_GAP",
                    record["id"],
                    generation,
                    entity_ref={
                        "category": "SOURCE_ARTIFACT",
                        "entity_id": record["id"],
                    },
                    evidence_refs=[record["id"], "source:topology"],
                    provenance="OBSERVED",
                    confidence="VERIFIED",
                    reason="The topology source record is not integrity-verified.",
                )
            )
    for entity in entities:
        category = (
            "TOPOLOGY_EDGE" if "edge_class" in entity else "TOPOLOGY_NODE"
        )
        reference = {"category": category, "entity_id": entity["id"]}
        evidence_refs = [*entity.get("evidence_refs", []), "source:topology"]
        if entity.get("resolution_state") == "UNRESOLVED":
            findings.append(
                _finding(
                    "UNRESOLVED_ENTITY",
                    entity["id"],
                    generation,
                    entity_ref=reference,
                    evidence_refs=evidence_refs,
                    provenance=str(entity.get("provenance", "INFERRED")),
                    confidence=str(entity.get("confidence", "INFERRED")),
                    reason="The topology entity is explicitly unresolved.",
                )
            )
        elif entity.get("resolution_state") == "NOT_COMPUTABLE":
            partial = True
            findings.append(
                _finding(
                    "SECTION_NOT_COMPUTABLE",
                    entity["id"],
                    generation,
                    entity_ref=reference,
                    evidence_refs=evidence_refs,
                    provenance="INFERRED",
                    confidence="NOT_COMPUTABLE",
                    reason="The topology entity cannot be resolved from current evidence.",
                )
            )
        if entity.get("freshness") == "STALE":
            findings.append(
                _finding(
                    "STALE_ENTITY",
                    entity["id"],
                    generation,
                    entity_ref=reference,
                    evidence_refs=evidence_refs,
                    provenance=str(entity.get("provenance", "INFERRED")),
                    confidence=str(entity.get("confidence", "INFERRED")),
                    reason="The topology entity is stale for the bound generation.",
                )
            )
        if category == "TOPOLOGY_EDGE" and entity.get("provenance") == "INFERRED":
            findings.append(
                _finding(
                    "INFERRED_LINK",
                    entity["id"],
                    generation,
                    entity_ref=reference,
                    evidence_refs=evidence_refs,
                    provenance="INFERRED",
                    confidence=str(entity.get("confidence", "INFERRED")),
                    reason="The edge is derived from an exact evidence join.",
                )
            )
        missing_refs = [
            reference_id
            for reference_id in entity.get("evidence_refs", [])
            if reference_id not in evidence
            or evidence[reference_id].get("integrity_state") != "VERIFIED"
        ]
        if not entity.get("evidence_refs") or missing_refs:
            partial = True
            findings.append(
                _finding(
                    "MISSING_EVIDENCE",
                    entity["id"],
                    generation,
                    entity_ref=reference,
                    evidence_refs=evidence_refs,
                    provenance="INFERRED",
                    confidence="INFERRED",
                    reason="The entity lacks complete integrity-verified evidence.",
                )
            )
    if topology.get("status") == "PARTIAL":
        partial = True
        findings.append(
            _finding(
                "SECTION_NOT_COMPUTABLE",
                "topology",
                generation,
                entity_ref={"category": "SECTION", "entity_id": "topology"},
                evidence_refs=["source:topology"],
                provenance="INFERRED",
                confidence="NOT_COMPUTABLE",
                reason="The topology projection is partial.",
            )
        )
    temporal_matched = temporal_diff is not None and temporal_id == operator_id
    if temporal_diff is None:
        partial = True
        validation_findings.append("Temporal Diff evidence was unavailable.")
        findings.append(
            _finding(
                "MISSING_EVIDENCE",
                "temporal_diff",
                generation,
                entity_ref={"category": "SECTION", "entity_id": "temporal_diff"},
                evidence_refs=["source:temporal_diff"],
                provenance="INFERRED",
                confidence="INFERRED",
                reason="Temporal Diff evidence was not supplied.",
            )
        )
    elif not temporal_matched:
        partial = True
        validation_findings.append(
            "Temporal Diff current generation does not match the topology binding."
        )
        findings.append(
            _finding(
                "GENERATION_MISMATCH",
                "temporal_diff",
                generation,
                entity_ref={"category": "SECTION", "entity_id": "temporal_diff"},
                evidence_refs=["source:temporal_diff", "source:topology"],
                provenance="OBSERVED",
                confidence="VERIFIED",
                reason="Temporal Diff is bound to a different current generation.",
            )
        )
    elif temporal_diff.get("comparison_status") != "AVAILABLE":
        partial = True
        findings.append(
            _finding(
                "SECTION_NOT_COMPUTABLE",
                "temporal_diff",
                generation,
                entity_ref={"category": "SECTION", "entity_id": "temporal_diff"},
                evidence_refs=["source:temporal_diff", "source:topology"],
                provenance="INFERRED",
                confidence="NOT_COMPUTABLE",
                reason="Temporal Diff evidence is partial or not computable.",
            )
        )
    else:
        for entry in temporal_diff["entries"]:
            category = entry.get("category")
            entity_category = (
                category
                if category in {"TOPOLOGY_NODE", "TOPOLOGY_EDGE"}
                else "SECTION"
            )
            reference = {
                "category": entity_category,
                "entity_id": str(entry.get("entity_id", entry["id"])),
            }
            common = {
                "generation": generation,
                "entity_ref": reference,
                "evidence_refs": ["source:temporal_diff", "source:topology"],
                "provenance": str(entry.get("provenance", "OBSERVED")),
                "confidence": "VERIFIED",
            }
            if entry.get("operation") == "REMOVED":
                findings.append(
                    _finding(
                        "TEMPORAL_REMOVAL",
                        f"{entry['id']}:removal",
                        reason="The matching Temporal Diff records this entity as removed.",
                        **common,
                    )
                )
            if entry.get("impact") == "WEAKENED":
                findings.append(
                    _finding(
                        "TEMPORAL_WEAKENING",
                        f"{entry['id']}:weakening",
                        reason="The matching Temporal Diff records weakened evidence.",
                        **common,
                    )
                )
    ordered = sorted(findings, key=lambda item: item["id"])
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "generation": generation,
        "status": "PARTIAL" if partial else "AVAILABLE",
        "provenance": (
            "INFERRED"
            if any(finding["provenance"] == "INFERRED" for finding in ordered)
            else "OBSERVED"
        ),
        "source_artifacts": sources,
        "authority": dict(AUTHORITY),
        "payload": {"summary": _summary(ordered), "findings": ordered},
        "not_computable_reason": None,
        "validation_findings": sorted(validation_findings),
        "canonical_hash": "0" * 64,
    }
    artifact["generation"]["integrity_generation_id"] = _generation_id(artifact)
    artifact["canonical_hash"] = _canonical_hash(artifact)
    return artifact


def validate_yggdrasil_topology_integrity(
    artifact: Mapping[str, Any],
    schema_path: Path,
    *,
    topology: Mapping[str, Any] | None = None,
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise YggdrasilTopologyIntegrityError(
            f"integrity schema violation: {errors[0].message}"
        )
    if artifact.get("authority") != AUTHORITY:
        raise YggdrasilTopologyIntegrityError("integrity authority locks are malformed")
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        raise YggdrasilTopologyIntegrityError("integrity canonical hash mismatch")
    generation = artifact["generation"]
    if generation["integrity_generation_id"] != _generation_id(artifact):
        raise YggdrasilTopologyIntegrityError("integrity generation id mismatch")
    sources = artifact["source_artifacts"]
    if sources != sorted(sources, key=lambda item: item["id"]):
        raise YggdrasilTopologyIntegrityError(
            "integrity sources are not canonically ordered"
        )
    if artifact["validation_findings"] != sorted(artifact["validation_findings"]):
        raise YggdrasilTopologyIntegrityError(
            "integrity validation findings are not canonically ordered"
        )
    payload = artifact.get("payload")
    if not isinstance(payload, Mapping):
        return
    findings = payload["findings"]
    identities = [finding["id"] for finding in findings]
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        raise YggdrasilTopologyIntegrityError("integrity finding ids are invalid")
    source_ids = {source["id"] for source in sources}
    topology_evidence_ids: set[str] = set()
    if topology is not None and isinstance(topology.get("payload"), Mapping):
        topology_evidence_ids = {
            record["id"] for record in topology["payload"]["evidence"]
        }
    evidence_domain = source_ids | topology_evidence_ids
    for finding in findings:
        expected_severity = SEVERITY_BY_TYPE[finding["finding_type"]]
        if finding["severity"] != expected_severity:
            raise YggdrasilTopologyIntegrityError("integrity severity mismatch")
        if finding["id"] != finding_id(
            finding["finding_type"],
            finding["entity_ref"],
            finding["subject_key"],
            generation["topology_generation_id"],
        ):
            raise YggdrasilTopologyIntegrityError("integrity finding id mismatch")
        if finding["evidence_refs"] != sorted(finding["evidence_refs"]):
            raise YggdrasilTopologyIntegrityError(
                "integrity evidence references are not canonically ordered"
            )
        if not set(finding["evidence_refs"]).issubset(evidence_domain):
            raise YggdrasilTopologyIntegrityError(
                "integrity finding has a dangling evidence reference"
            )
        binding = finding["generation_binding"]
        if any(
            binding[key] != generation[key]
            for key in (
                "topology_generation_id",
                "operator_platform_generation_id",
                "temporal_diff_generation_id",
            )
        ):
            raise YggdrasilTopologyIntegrityError(
                "integrity finding generation binding mismatch"
            )
        if finding["finding_type"] in TEMPORAL_TYPES and (
            generation["temporal_diff_generation_id"] is None
            or generation["temporal_diff_generation_id"]
            != generation["operator_platform_generation_id"]
        ):
            raise YggdrasilTopologyIntegrityError(
                "temporal conclusion without matched evidence"
            )
    if payload["summary"] != _summary(findings):
        raise YggdrasilTopologyIntegrityError("integrity summary mismatch")
