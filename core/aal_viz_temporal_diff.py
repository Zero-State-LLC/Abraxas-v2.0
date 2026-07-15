"""Deterministic, projection-only comparison for Operator Platform v0.2."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "AALViz.TemporalDiff.v1"
PROJECTION_VERSION = "AALViz.OperatorPlatformProjection.v0.2"
CATEGORIES = (
    "TOPOLOGY_NODE",
    "TOPOLOGY_EDGE",
    "CONTRACT_FIELD",
    "OWNERSHIP",
    "VALIDATOR_STATE",
    "RECEIPT",
    "PACKET",
    "SOURCE_INTEGRITY",
    "SECTION_STATUS",
)
COMPARISON_SCOPE = (
    "CONTRACTS",
    "OWNERSHIP",
    "PACKETS",
    "RECEIPTS",
    "SOURCE_INTEGRITY",
    "TOPOLOGY",
    "VALIDATORS",
)
OUT_OF_SCOPE = (
    "ALERTS",
    "HYPERSTITION_FORECASTING",
    "LINEAGE",
    "ORCHESTRATION",
    "PRODUCTION_ACTIVATION",
    "QUEUE",
    "ROUTE_RECEIPT_SCHEDULING",
    "TOPOLOGY_MUTATION",
    "TRANSPORT",
)
AUTHORITY = {
    "projection_only": True,
    "runtime_mutation_allowed": False,
    "promotion_allowed": False,
    "production_activation_allowed": False,
    "history_retention_allowed": False,
    "alerting_allowed": False,
    "scheduling_allowed": False,
}
SECTION_CATEGORIES: dict[str, tuple[str, ...]] = {
    "topology": ("TOPOLOGY_NODE", "TOPOLOGY_EDGE"),
    "contract_graph": ("CONTRACT_FIELD", "OWNERSHIP", "VALIDATOR_STATE"),
    "evidence_index": ("RECEIPT", "PACKET"),
}
SET_LIKE_FIELDS = {
    "artifacts",
    "consumers",
    "excluded_surfaces",
    "failures",
    "inherited_debt",
    "inputs",
    "links",
    "operator_summary",
    "outputs",
    "producers",
    "receipts",
    "schemas",
    "source_artifacts",
    "unresolved_links",
    "validators",
    "validation_findings",
}


class TemporalDiffError(ValueError):
    """Raised when an input or output violates the locked contract."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _repository_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise TemporalDiffError(f"published path must be repository-relative: {value}")
    return value


def _validate_hash(value: str, label: str) -> str:
    if len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise TemporalDiffError(f"{label} must be a lowercase SHA-256 hash")
    return value


def _validator(schema_path: Path) -> Draft202012Validator:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TemporalDiffError(f"schema unavailable: {schema_path}: {exc}") from exc
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_projection(projection: Mapping[str, Any], schema_path: Path) -> None:
    errors = sorted(
        _validator(schema_path).iter_errors(projection),
        key=lambda error: list(error.path),
    )
    if errors:
        raise TemporalDiffError(
            f"operator projection schema violation: {errors[0].message}"
        )
    if projection.get("schema_version") != PROJECTION_VERSION:
        raise TemporalDiffError("unsupported operator projection version")
    authority = projection.get("authority")
    if not isinstance(authority, Mapping):
        raise TemporalDiffError("operator projection authority is malformed")
    for key in (
        "projection_only",
        "runtime_mutation_allowed",
        "promotion_allowed",
        "production_activation_allowed",
    ):
        if authority.get(key) != AUTHORITY[key]:
            raise TemporalDiffError(f"operator projection authority violation: {key}")


def _id_map(items: Any, path: str) -> dict[str, Any]:
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        raise TemporalDiffError(f"{path} must be an array")
    result: dict[str, Any] = {}
    for item in items:
        if not isinstance(item, Mapping):
            raise TemporalDiffError(f"{path} contains a malformed record")
        stable_id = item.get("id")
        if not isinstance(stable_id, str) or not stable_id:
            raise TemporalDiffError(f"{path} contains a record without a stable id")
        if stable_id in result:
            raise TemporalDiffError(f"{path} contains duplicate stable id: {stable_id}")
        result[stable_id] = _normalize_value(dict(item), path)
    return dict(sorted(result.items()))


def _normalize_value(value: Any, path: str = "") -> Any:
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, child in sorted(value.items()):
            child_path = f"{path}/{key}"
            if key == "source_artifacts":
                if not isinstance(child, list):
                    raise TemporalDiffError(f"{child_path} must be an array")
                normalized[key] = _id_map(
                    [
                        {**item, "id": item.get("source_key")}
                        for item in child
                        if isinstance(item, Mapping)
                    ],
                    child_path,
                )
            elif key == "nodes" and path.endswith("/topology/payload"):
                normalized[key] = _id_map(child, child_path)
            elif key == "edges" and path.endswith("/topology/payload"):
                normalized[key] = _id_map(child, child_path)
            elif key == "contracts" and path.endswith("/contract_graph/payload"):
                normalized[key] = _id_map(child, child_path)
            elif key == "records" and path.endswith("/evidence_index/payload"):
                normalized[key] = _id_map(child, child_path)
            elif key == "work_items" and path.endswith("/system_status/payload"):
                normalized[key] = _id_map(child, child_path)
            else:
                normalized[key] = _normalize_value(child, child_path)
        return normalized
    if isinstance(value, list):
        normalized_items = [_normalize_value(item, path) for item in value]
        field_name = path.rsplit("/", 1)[-1]
        if field_name in SET_LIKE_FIELDS:
            return sorted(normalized_items, key=canonical_json)
        return normalized_items
    return value


def normalize_projection(projection: Mapping[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(dict(projection))
    normalized.pop("temporal_diff", None)
    generation = normalized.get("generation")
    if isinstance(generation, dict):
        generation.pop("generated_at", None)
    return _normalize_value(normalized, "")


def generation_id(projection: Mapping[str, Any]) -> str:
    return sha256_json(normalize_projection(projection))


def _pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _entry_id(operation: str, category: str, entity_id: str, field_path: str) -> str:
    return sha256_json([operation, category, entity_id, field_path])


def _entry(
    *,
    operation: str,
    category: str,
    surface: str,
    entity_id: str,
    field_path: str,
    prior_value: Any,
    current_value: Any,
    prior_generation_id: str | None,
    current_generation_id: str | None,
    prior_status: str = "AVAILABLE",
    current_status: str = "AVAILABLE",
    reason_code: str | None = None,
    source_keys: Sequence[str] = (),
    impact: str = "NEUTRAL",
) -> dict[str, Any]:
    if operation == "NOT_COMPUTABLE":
        impact = "NOT_COMPUTABLE"
    return {
        "id": _entry_id(operation, category, entity_id, field_path),
        "operation": operation,
        "category": category,
        "impact": impact,
        "surface": surface,
        "entity_id": entity_id,
        "field_path": field_path,
        "prior_value": prior_value,
        "current_value": current_value,
        "provenance": "OBSERVED" if operation != "NOT_COMPUTABLE" else "INFERRED",
        "prior_generation_id": prior_generation_id,
        "current_generation_id": current_generation_id,
        "prior_evidence_status": prior_status,
        "current_evidence_status": current_status,
        "reason_code": reason_code,
        "source_keys": sorted(set(source_keys)),
    }


def _section(projection: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    section = projection.get(name)
    if not isinstance(section, Mapping):
        raise TemporalDiffError(f"projection section is malformed: {name}")
    return section


def _payload_map(section: Mapping[str, Any], key: str) -> dict[str, Any]:
    payload = section.get("payload")
    if not isinstance(payload, Mapping):
        return {}
    return _id_map(payload.get(key, []), f"{key}")


def _source_keys(section: Mapping[str, Any]) -> list[str]:
    sources = section.get("source_artifacts")
    if not isinstance(sources, list):
        return []
    return sorted(
        source["source_key"]
        for source in sources
        if isinstance(source, Mapping) and isinstance(source.get("source_key"), str)
    )


def _missing_entries(
    section_name: str,
    prior: Mapping[str, Any],
    current: Mapping[str, Any],
    prior_id: str,
    current_id: str,
) -> list[dict[str, Any]]:
    prior_status = str(prior.get("status", "NOT_COMPUTABLE"))
    current_status = str(current.get("status", "NOT_COMPUTABLE"))
    reason = (
        "PARTIAL_EVIDENCE"
        if "PARTIAL" in {prior_status, current_status}
        else "SECTION_NOT_COMPUTABLE"
    )
    source_keys = [*_source_keys(prior), *_source_keys(current)]
    return [
        _entry(
            operation="NOT_COMPUTABLE",
            category=category,
            surface=section_name,
            entity_id=section_name,
            field_path=f"/{section_name}",
            prior_value=None,
            current_value=None,
            prior_generation_id=prior_id,
            current_generation_id=current_id,
            prior_status=prior_status,
            current_status=current_status,
            reason_code=reason,
            source_keys=source_keys,
        )
        for category in SECTION_CATEGORIES[section_name]
    ]


def _compare_entity_presence(
    prior_items: Mapping[str, Any],
    current_items: Mapping[str, Any],
    *,
    category: str,
    surface: str,
    base_path: str,
    prior_id: str,
    current_id: str,
    source_keys: Sequence[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for entity_id in sorted(current_items.keys() - prior_items.keys()):
        path = f"{base_path}/{_pointer_token(entity_id)}"
        entries.append(
            _entry(
                operation="ADDED",
                category=category,
                surface=surface,
                entity_id=entity_id,
                field_path=path,
                prior_value=None,
                current_value=current_items[entity_id],
                prior_generation_id=prior_id,
                current_generation_id=current_id,
                source_keys=source_keys,
            )
        )
    for entity_id in sorted(prior_items.keys() - current_items.keys()):
        path = f"{base_path}/{_pointer_token(entity_id)}"
        entries.append(
            _entry(
                operation="REMOVED",
                category=category,
                surface=surface,
                entity_id=entity_id,
                field_path=path,
                prior_value=prior_items[entity_id],
                current_value=None,
                prior_generation_id=prior_id,
                current_generation_id=current_id,
                source_keys=source_keys,
            )
        )
    return entries


def _compare_topology(
    prior: Mapping[str, Any], current: Mapping[str, Any], prior_id: str, current_id: str
) -> list[dict[str, Any]]:
    if prior.get("status") != "AVAILABLE" or current.get("status") != "AVAILABLE":
        return _missing_entries("topology", prior, current, prior_id, current_id)
    keys = [*_source_keys(prior), *_source_keys(current)]
    return [
        *_compare_entity_presence(
            _payload_map(prior, "nodes"),
            _payload_map(current, "nodes"),
            category="TOPOLOGY_NODE",
            surface="topology",
            base_path="/topology/payload/nodes",
            prior_id=prior_id,
            current_id=current_id,
            source_keys=keys,
        ),
        *_compare_entity_presence(
            _payload_map(prior, "edges"),
            _payload_map(current, "edges"),
            category="TOPOLOGY_EDGE",
            surface="topology",
            base_path="/topology/payload/edges",
            prior_id=prior_id,
            current_id=current_id,
            source_keys=keys,
        ),
    ]


def _ownership_impact(field: str, prior_value: Any, current_value: Any) -> str:
    if field == "owner_resolved" and prior_value is False and current_value is True:
        return "STRENGTHENED"
    if field == "owner_resolved" and prior_value is True and current_value is False:
        return "WEAKENED"
    if field == "owner":
        prior_resolved = prior_value not in {None, "", "UNRESOLVED"}
        current_resolved = current_value not in {None, "", "UNRESOLVED"}
        if not prior_resolved and current_resolved:
            return "STRENGTHENED"
        if prior_resolved and not current_resolved:
            return "WEAKENED"
    return "NEUTRAL"


def _validator_impact(field: str, prior_value: Any, current_value: Any) -> str:
    if field != "validators":
        return "NEUTRAL"
    prior_present = bool(prior_value)
    current_present = bool(current_value)
    if not prior_present and current_present:
        return "STRENGTHENED"
    if prior_present and not current_present:
        return "WEAKENED"
    return "NEUTRAL"


def _compare_contracts(
    prior: Mapping[str, Any], current: Mapping[str, Any], prior_id: str, current_id: str
) -> list[dict[str, Any]]:
    if prior.get("status") != "AVAILABLE" or current.get("status") != "AVAILABLE":
        return _missing_entries("contract_graph", prior, current, prior_id, current_id)
    prior_items = _payload_map(prior, "contracts")
    current_items = _payload_map(current, "contracts")
    keys = [*_source_keys(prior), *_source_keys(current)]
    entries = _compare_entity_presence(
        prior_items,
        current_items,
        category="CONTRACT_FIELD",
        surface="contract_graph",
        base_path="/contract_graph/payload/contracts",
        prior_id=prior_id,
        current_id=current_id,
        source_keys=keys,
    )
    for entity_id in sorted(prior_items.keys() & current_items.keys()):
        prior_contract = prior_items[entity_id]
        current_contract = current_items[entity_id]
        for field in sorted(set(prior_contract) | set(current_contract)):
            if field == "id" or prior_contract.get(field) == current_contract.get(
                field
            ):
                continue
            category = (
                "OWNERSHIP"
                if field in {"owner", "owner_resolved"}
                else "VALIDATOR_STATE"
                if field in {"validators", "validation_mode"}
                else "CONTRACT_FIELD"
            )
            impact = (
                _ownership_impact(
                    field, prior_contract.get(field), current_contract.get(field)
                )
                if category == "OWNERSHIP"
                else _validator_impact(
                    field, prior_contract.get(field), current_contract.get(field)
                )
            )
            path = f"/contract_graph/payload/contracts/{_pointer_token(entity_id)}/{_pointer_token(field)}"
            entries.append(
                _entry(
                    operation="CHANGED",
                    category=category,
                    surface="contract_graph",
                    entity_id=entity_id,
                    field_path=path,
                    prior_value=prior_contract.get(field),
                    current_value=current_contract.get(field),
                    prior_generation_id=prior_id,
                    current_generation_id=current_id,
                    source_keys=keys,
                    impact=impact,
                )
            )
    return entries


def _record_category(record: Mapping[str, Any]) -> str | None:
    source_path = str(record.get("source_path", "")).lower()
    stable_id = str(record.get("id", "")).lower()
    if "receipt" in source_path or "receipt" in stable_id:
        return "RECEIPT"
    if any(
        token in source_path or token in stable_id
        for token in ("packet", "operator_runtime_console", "yggdrasil")
    ):
        return "PACKET"
    return None


def _compare_evidence(
    prior: Mapping[str, Any], current: Mapping[str, Any], prior_id: str, current_id: str
) -> list[dict[str, Any]]:
    if prior.get("status") != "AVAILABLE" or current.get("status") != "AVAILABLE":
        return _missing_entries("evidence_index", prior, current, prior_id, current_id)
    prior_items = _payload_map(prior, "records")
    current_items = _payload_map(current, "records")
    keys = [*_source_keys(prior), *_source_keys(current)]
    entries: list[dict[str, Any]] = []
    for entity_id in sorted(set(prior_items) | set(current_items)):
        prior_record = prior_items.get(entity_id)
        current_record = current_items.get(entity_id)
        category = _record_category(current_record or prior_record or {})
        if category is None:
            continue
        path = f"/evidence_index/payload/records/{_pointer_token(entity_id)}"
        if prior_record is None:
            entries.append(
                _entry(
                    operation="ADDED",
                    category=category,
                    surface="evidence_index",
                    entity_id=entity_id,
                    field_path=path,
                    prior_value=None,
                    current_value=current_record,
                    prior_generation_id=prior_id,
                    current_generation_id=current_id,
                    source_keys=keys,
                )
            )
        elif current_record is None:
            entries.append(
                _entry(
                    operation="REMOVED",
                    category=category,
                    surface="evidence_index",
                    entity_id=entity_id,
                    field_path=path,
                    prior_value=prior_record,
                    current_value=None,
                    prior_generation_id=prior_id,
                    current_generation_id=current_id,
                    source_keys=keys,
                )
            )
        elif prior_record != current_record:
            entries.append(
                _entry(
                    operation="CHANGED",
                    category=category,
                    surface="evidence_index",
                    entity_id=entity_id,
                    field_path=path,
                    prior_value=prior_record,
                    current_value=current_record,
                    prior_generation_id=prior_id,
                    current_generation_id=current_id,
                    source_keys=keys,
                )
            )
    return entries


def _compare_sources(
    prior: Mapping[str, Any], current: Mapping[str, Any], prior_id: str, current_id: str
) -> list[dict[str, Any]]:
    prior_items = _id_map(
        [
            {**source, "id": source.get("source_key")}
            for source in prior.get("source_artifacts", [])
            if isinstance(source, Mapping)
        ],
        "source_artifacts",
    )
    current_items = _id_map(
        [
            {**source, "id": source.get("source_key")}
            for source in current.get("source_artifacts", [])
            if isinstance(source, Mapping)
        ],
        "source_artifacts",
    )
    entries: list[dict[str, Any]] = []
    for source_key in sorted(set(prior_items) | set(current_items)):
        before = prior_items.get(source_key)
        after = current_items.get(source_key)
        if before == after:
            continue
        operation = (
            "ADDED" if before is None else "REMOVED" if after is None else "CHANGED"
        )
        path = f"/source_artifacts/{_pointer_token(source_key)}"
        entries.append(
            _entry(
                operation=operation,
                category="SOURCE_INTEGRITY",
                surface="source_artifacts",
                entity_id=source_key,
                field_path=path,
                prior_value=before,
                current_value=after,
                prior_generation_id=prior_id,
                current_generation_id=current_id,
                source_keys=[source_key],
            )
        )
    return entries


def _compare_section_statuses(
    prior: Mapping[str, Any], current: Mapping[str, Any], prior_id: str, current_id: str
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for section_name in sorted(SECTION_CATEGORIES):
        before = str(_section(prior, section_name).get("status"))
        after = str(_section(current, section_name).get("status"))
        if before == after:
            continue
        entries.append(
            _entry(
                operation="CHANGED",
                category="SECTION_STATUS",
                surface=section_name,
                entity_id=section_name,
                field_path=f"/{section_name}/status",
                prior_value=before,
                current_value=after,
                prior_generation_id=prior_id,
                current_generation_id=current_id,
                prior_status=before,
                current_status=after,
                source_keys=[],
            )
        )
    return entries


def _sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        entries,
        key=lambda entry: (
            entry["category"],
            entry["surface"],
            entry["entity_id"],
            entry["field_path"],
            entry["operation"],
            entry["id"],
        ),
    )


def compare_operator_platform_projections(
    prior: Mapping[str, Any],
    current: Mapping[str, Any],
    *,
    prior_source_path: str,
    current_source_path: str,
    prior_source_sha256: str,
    current_source_sha256: str,
    projection_schema_path: Path,
    temporal_schema_path: Path,
) -> dict[str, Any]:
    """Compare two explicitly supplied projections without retaining either input."""
    validate_projection(prior, projection_schema_path)
    validate_projection(current, projection_schema_path)
    prior_path = _repository_path(prior_source_path)
    current_path = _repository_path(current_source_path)
    prior_sha = _validate_hash(prior_source_sha256, "prior source hash")
    current_sha = _validate_hash(current_source_sha256, "current source hash")
    prior_id = generation_id(prior)
    current_id = generation_id(current)

    entries = _sort_entries(
        [
            *_compare_section_statuses(prior, current, prior_id, current_id),
            *_compare_topology(
                _section(prior, "topology"),
                _section(current, "topology"),
                prior_id,
                current_id,
            ),
            *_compare_contracts(
                _section(prior, "contract_graph"),
                _section(current, "contract_graph"),
                prior_id,
                current_id,
            ),
            *_compare_evidence(
                _section(prior, "evidence_index"),
                _section(current, "evidence_index"),
                prior_id,
                current_id,
            ),
            *_compare_sources(prior, current, prior_id, current_id),
        ]
    )
    category_counts = {category: 0 for category in CATEGORIES}
    for entry in entries:
        category_counts[entry["category"]] += 1
    changed_count = sum(entry["operation"] != "NOT_COMPUTABLE" for entry in entries)
    missing_count = len(entries) - changed_count
    missing_reasons = sorted(
        [
            {
                "reason_code": entry["reason_code"],
                "surface": entry["surface"],
                "detail": f"{entry['surface']} comparison is not computable from {entry['prior_evidence_status']} and {entry['current_evidence_status']} evidence.",
            }
            for entry in entries
            if entry["operation"] == "NOT_COMPUTABLE"
        ],
        key=lambda reason: (reason["surface"], reason["reason_code"], reason["detail"]),
    )
    comparison_status = (
        "NOT_COMPUTABLE"
        if entries and changed_count == 0 and missing_count
        else "PARTIAL"
        if missing_count
        else "AVAILABLE"
    )
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "comparison_status": comparison_status,
        "status": "CHANGED"
        if changed_count
        else "NOT_COMPUTABLE"
        if missing_count
        else "NO_CHANGE",
        "prior_generation": {
            "generation_id": prior_id,
            "source_path": prior_path,
            "source_sha256": prior_sha,
            "projection_schema_version": PROJECTION_VERSION,
        },
        "current_generation": {
            "generation_id": current_id,
            "source_path": current_path,
            "source_sha256": current_sha,
            "projection_schema_version": PROJECTION_VERSION,
        },
        "comparison_scope": list(COMPARISON_SCOPE),
        "out_of_scope": list(OUT_OF_SCOPE),
        "authority": dict(AUTHORITY),
        "summary": {
            "total_change_count": changed_count,
            "not_computable_count": missing_count,
            "category_counts": category_counts,
        },
        "entries": entries,
        "not_computable_reasons": missing_reasons,
    }
    artifact["canonical_hash"] = sha256_json(artifact)
    errors = sorted(
        _validator(temporal_schema_path).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise TemporalDiffError(f"temporal diff schema violation: {errors[0].message}")
    return artifact


def not_computable_artifact(
    *,
    prior_path: str,
    current_path: str,
    missing_reason: str,
    temporal_schema_path: Path,
    prior_generation: Mapping[str, Any] | None = None,
    current_generation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the only publishable result for a missing explicit input."""
    reason_code = (
        "MISSING_PRIOR_INPUT" if missing_reason == "prior" else "MISSING_CURRENT_INPUT"
    )
    prior_source = _repository_path(prior_path)
    current_source = _repository_path(current_path)
    prior_descriptor = (
        dict(prior_generation)
        if prior_generation is not None
        else {
            "generation_id": None,
            "source_path": prior_source,
            "source_sha256": None,
            "projection_schema_version": None,
        }
    )
    current_descriptor = (
        dict(current_generation)
        if current_generation is not None
        else {
            "generation_id": None,
            "source_path": current_source,
            "source_sha256": None,
            "projection_schema_version": None,
        }
    )
    missing_entry = _entry(
        operation="NOT_COMPUTABLE",
        category="SECTION_STATUS",
        surface="comparison",
        entity_id="comparison",
        field_path="/comparison",
        prior_value=None,
        current_value=None,
        prior_generation_id=prior_descriptor["generation_id"],
        current_generation_id=current_descriptor["generation_id"],
        prior_status=(
            "AVAILABLE" if prior_generation is not None else "NOT_COMPUTABLE"
        ),
        current_status=(
            "AVAILABLE" if current_generation is not None else "NOT_COMPUTABLE"
        ),
        reason_code=reason_code,
    )
    category_counts = {category: 0 for category in CATEGORIES}
    category_counts["SECTION_STATUS"] = 1
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "comparison_status": "NOT_COMPUTABLE",
        "status": "NOT_COMPUTABLE",
        "prior_generation": prior_descriptor,
        "current_generation": current_descriptor,
        "comparison_scope": list(COMPARISON_SCOPE),
        "out_of_scope": list(OUT_OF_SCOPE),
        "authority": dict(AUTHORITY),
        "summary": {
            "total_change_count": 0,
            "not_computable_count": 1,
            "category_counts": category_counts,
        },
        "entries": [missing_entry],
        "not_computable_reasons": [
            {
                "reason_code": reason_code,
                "surface": "comparison",
                "detail": f"Explicit {missing_reason} projection input is missing.",
            }
        ],
    }
    artifact["canonical_hash"] = sha256_json(artifact)
    errors = list(_validator(temporal_schema_path).iter_errors(artifact))
    if errors:
        raise TemporalDiffError(f"temporal diff schema violation: {errors[0].message}")
    return artifact
