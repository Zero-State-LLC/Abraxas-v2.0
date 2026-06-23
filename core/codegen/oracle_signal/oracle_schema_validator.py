"""Oracle schema validation advisory layer.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live ingest.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.codegen.oracle_signal.oracle_signal_intake_builder import (
    ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
)


SCHEMA_BY_PACKET_KEY: dict[str, str] = {
    "oracle_signal_envelope": (
        "contracts/canon/oracle/oracle_signal_envelope.v1.schema.json"
    ),
    "oracle_holler_intake": (
        "contracts/canon/oracle/oracle_holler_intake.v1.schema.json"
    ),
    "oracle_calibration_report": (
        "contracts/canon/oracle/oracle_calibration_report.v1.schema.json"
    ),
    "oracle_adversarial_fixture": (
        "contracts/canon/oracle/oracle_adversarial_fixture.v1.schema.json"
    ),
    "oracle_schema_registry": (
        "contracts/canon/oracle/oracle_schema_registry.v1.schema.json"
    ),
    "oracle_ingest_wiring": (
        "contracts/canon/oracle/oracle_ingest_wiring.v1.schema.json"
    ),
    "oracle_shadow_dryrun": (
        "contracts/canon/oracle/oracle_shadow_dryrun.v1.schema.json"
    ),
    "oracle_measurement_readiness": (
        "contracts/canon/oracle/oracle_measurement_readiness.v1.schema.json"
    ),
    "oracle_shadow_measurement": (
        "contracts/canon/oracle/oracle_shadow_measurement.v1.schema.json"
    ),
    "oracle_measurement_proposal": (
        "contracts/canon/oracle/oracle_measurement_proposal.v1.schema.json"
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_signal_ingest": False,
        "schema_writeback": False,
        "github_writeback": False,
        "notion_writeback": False,
        "mcp_tool_exposure_live": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }


def load_oracle_schema(schema_path: str, *, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or _repo_root()
    return json.loads((root / schema_path).read_text(encoding="utf-8"))


def validate_oracle_packet(
    *,
    packet_key: str,
    packet: Mapping[str, Any],
    schema_path: str,
    timestamp: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    schema = load_oracle_schema(schema_path, repo_root=repo_root)
    errors = _validate_with_available_engine(dict(packet), schema)
    canonical_packet_hash = str(packet.get("canonical_hash", ""))
    recalculated_hash = _recalculate_packet_hash(packet)
    base: dict[str, Any] = {
        "schema_version": "OracleSchemaValidationResult.v1",
        "validation_id": canonical_hash(
            {
                "record": "oracle_schema_validation_result",
                "packet_key": packet_key,
                "schema_path": schema_path,
                "packet_hash": canonical_packet_hash,
            }
        ),
        "validation_status": (
            "VALID_ADVISORY_ONLY"
            if not errors and canonical_packet_hash == recalculated_hash
            else "INVALID_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "packet_key": packet_key,
        "schema_path": schema_path,
        "packet_hash": canonical_packet_hash,
        "recalculated_packet_hash": recalculated_hash,
        "schema_errors": errors,
        "provenance_seal": {
            "source": "oracle_schema_validator",
            "schema_path": schema_path,
            "packet_key": packet_key,
            "sealed_for_live_validation": False,
            "brier_score": 0.1,
        },
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_ingest": False,
        "valid_for_schema_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def validate_oracle_schema_packets(
    *,
    packets: Mapping[str, Mapping[str, Any]],
    timestamp: str,
    repo_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        packet_key: validate_oracle_packet(
            packet_key=packet_key,
            packet=packet,
            schema_path=SCHEMA_BY_PACKET_KEY[packet_key],
            timestamp=timestamp,
            repo_root=repo_root,
        )
        for packet_key, packet in packets.items()
    }


def build_oracle_schema_validation_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    validation_results: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    all_valid = all(
        result["validation_status"] == "VALID_ADVISORY_ONLY"
        for result in validation_results.values()
    )
    base: dict[str, Any] = {
        "schema_version": "OracleSchemaValidationReceipt.v1",
        "receipt_id": "ORACLE_SCHEMA_VALIDATION_RECEIPT_001",
        "receipt_status": (
            "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
            if all_valid
            else "ORACLE_SCHEMA_VALIDATION_BLOCKED_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "schema_registry_path": (
            "contracts/canon/oracle/oracle_schema_registry.v1.schema.json"
        ),
        "schema_paths": list(ORACLE_CANON_EXTENSION_SCHEMA_PATHS),
        "validation_result_hashes": {
            key: result["canonical_hash"] for key, result in validation_results.items()
        },
        "validation_summary": {
            "valid_result_count": sum(
                result["validation_status"] == "VALID_ADVISORY_ONLY"
                for result in validation_results.values()
            ),
            "invalid_result_count": sum(
                result["validation_status"] != "VALID_ADVISORY_ONLY"
                for result in validation_results.values()
            ),
            "all_valid": all_valid,
            "brier_score": 0.1,
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_SCHEMA_VALIDATION_OPERATOR_DECISION_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "approval_records_live_validation": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Prepare full oracle ingest wiring slice for operator review."
        ),
        "provenance": _provenance("oracle_schema_validation_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_validation": False,
        "valid_for_live_ingest": False,
        "valid_for_schema_writeback": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_schema_validation_fixture_set(
    *,
    valid_packets: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    invalid_holler = copy.deepcopy(dict(valid_packets["oracle_holler_intake"]))
    invalid_holler["holler_batch"]["market_count"] = -1
    invalid_envelope = copy.deepcopy(dict(valid_packets["oracle_signal_envelope"]))
    invalid_envelope["payload_ref"]["payload_hash"] = "not-a-sha"
    base = {
        "schema_version": "OracleSchemaValidationFixtureSet.v1",
        "fixture_status": "SHADOW_REPLAY_FIXTURES_READY_ADVISORY_ONLY",
        "valid_fixture_keys": sorted(valid_packets),
        "invalid_fixtures": {
            "oracle_holler_intake_negative_market_count": invalid_holler,
            "oracle_signal_envelope_bad_payload_hash": invalid_envelope,
        },
        "authority_locks": _authority_locks(),
        "valid_for_live_validation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _recalculate_packet_hash(packet: Mapping[str, Any]) -> str:
    candidate = dict(packet)
    candidate.pop("canonical_hash", None)
    return canonical_hash(candidate)


def _validate_with_available_engine(
    packet: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> list[dict[str, Any]]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return _validate_schema_subset(packet, schema)
    validator = Draft202012Validator(schema)
    return [
        {
            "path": ".".join(str(part) for part in error.path),
            "message": error.message,
            "validator": error.validator,
            "brier_score": 0.1,
        }
        for error in sorted(validator.iter_errors(dict(packet)), key=str)
    ]


def _validate_schema_subset(
    value: Any,
    schema: Mapping[str, Any],
    *,
    path: str = "",
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if "const" in schema and value != schema["const"]:
        errors.append(_error(path, f"expected const {schema['const']!r}", "const"))
        return errors
    schema_type = schema.get("type")
    if schema_type and not _type_matches(value, str(schema_type)):
        errors.append(_error(path, f"expected type {schema_type}", "type"))
        return errors
    if isinstance(value, str):
        if int(schema.get("minLength", 0)) and not value:
            errors.append(_error(path, "string is shorter than minLength", "minLength"))
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.match(pattern, value) is None:
            errors.append(_error(path, f"string does not match {pattern}", "pattern"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(_error(path, f"value is less than {minimum}", "minimum"))
        if isinstance(maximum, (int, float)) and value > maximum:
            errors.append(_error(path, f"value is greater than {maximum}", "maximum"))
    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(_error(path, f"array has fewer than {min_items} items", "minItems"))
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(value):
                errors.extend(
                    _validate_schema_subset(
                        item,
                        item_schema,
                        path=_join_path(path, str(index)),
                    )
                )
    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(
                        _error(
                            _join_path(path, str(key)),
                            "required key missing",
                            "required",
                        )
                    )
        properties = schema.get("properties", {})
        if isinstance(properties, Mapping):
            for key, prop_schema in properties.items():
                if key in value and isinstance(prop_schema, Mapping):
                    errors.extend(
                        _validate_schema_subset(
                            value[key],
                            prop_schema,
                            path=_join_path(path, str(key)),
                        )
                    )
        additional = schema.get("additionalProperties", True)
        if additional is False and isinstance(properties, Mapping):
            for key in sorted(set(value) - set(properties)):
                errors.append(
                    _error(
                        _join_path(path, key),
                        "additional property is not allowed",
                        "additionalProperties",
                    )
                )
        elif isinstance(additional, Mapping):
            for key, item in value.items():
                if not isinstance(properties, Mapping) or key not in properties:
                    errors.extend(
                        _validate_schema_subset(
                            item,
                            additional,
                            path=_join_path(path, str(key)),
                        )
                    )
    return errors


def _type_matches(value: Any, schema_type: str) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    return True


def _join_path(prefix: str, part: str) -> str:
    return part if not prefix else f"{prefix}.{part}"


def _error(path: str, message: str, validator: str) -> dict[str, Any]:
    return {
        "path": path,
        "message": message,
        "validator": validator,
        "brier_score": 0.1,
    }
