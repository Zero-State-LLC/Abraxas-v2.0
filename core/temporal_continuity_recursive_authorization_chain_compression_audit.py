from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityRecursiveAuthorizationChainCompressionAudit.v1"
SOURCE_CHAIN_SCOPE = "P86_TO_P101_RECURSIVE_AUTHORIZATION_CHAIN"
LATEST_REQUIRED_SOURCE_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_authorization_gate/latest.json"
)
EXPECTED_LATEST_REQUIRED_STATUS = (
    "P83_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_ELIGIBLE"
)
EXPECTED_LATEST_REQUIRED_NEXT_LANE = (
    "P102_TEMPORAL_CONTINUITY_RECURSIVE_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT"
)
_REGENERATION_NEXT_LANE = (
    "P101_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"
)
_EVIDENCE_RESTORATION_NEXT_LANE = "P86_TO_P101_CHAIN_EVIDENCE_RESTORATION_PLAN"
_COMPRESS_NEXT_LANE = "P103_TEMPORAL_CONTINUITY_GENERIC_AUTHORIZATION_LANE_TEMPLATE_PLAN"
_SEAL_NEXT_LANE = "P103_TEMPORAL_CONTINUITY_RECURSIVE_AUTHORIZATION_CHAIN_SEAL_RECEIPT"
_CONTINUE_NEXT_LANE = "P103_TEMPORAL_CONTINUITY_RECURSION_CONTINUATION_PLAN"

_CHAIN_ARTIFACT_SPECS: tuple[dict[str, str], ...] = (
    {
        "artifact_id": "P86_P84_REGENERATION_PLAN_REGENERATION_PLAN",
        "path": "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json",
        "status_field": "p84_regeneration_plan_regeneration_status",
        "lane_archetype": "REGENERATION_PLAN",
    },
    {
        "artifact_id": "P87_P83_STATUS_PLAN_REGENERATION_PLAN",
        "path": "out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json",
        "status_field": "p83_regeneration_plan_status",
        "lane_archetype": "REGENERATION_PLAN",
    },
    {
        "artifact_id": "P88_P83_STATUS_PLAN_REGENERATION_EXECUTION_PLAN",
        "path": "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json",
        "status_field": "p83_regeneration_execution_plan_status",
        "lane_archetype": "EXECUTION_PLAN",
    },
    {
        "artifact_id": "P89_P83_REGENERATION_AUTHORIZATION_GATE",
        "path": "out/temporal_continuity_p83_regeneration_authorization_gate/latest.json",
        "status_field": "p83_regeneration_authorization_gate_status",
        "lane_archetype": "AUTHORIZATION_GATE",
    },
    {
        "artifact_id": "P90_P83_REGENERATION_AUTHORIZATION_RECORD_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json",
        "status_field": "p83_regeneration_record_plan_status",
        "lane_archetype": "AUTHORIZATION_RECORD_PLAN",
    },
    {
        "artifact_id": "P91_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_plan/latest.json",
        "status_field": "p83_regeneration_record_creation_plan_status",
        "lane_archetype": "AUTHORIZATION_RECORD_CREATION_PLAN",
    },
    {
        "artifact_id": "P92_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_AUTHORIZATION_GATE",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_authorization_gate/latest.json",
        "status_field": "p83_record_creation_authorization_gate_status",
        "lane_archetype": "AUTHORIZATION_RECORD_CREATION_GATE",
    },
    {
        "artifact_id": "P93_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_plan/latest.json",
        "status_field": "p83_record_creation_record_plan_status",
        "lane_archetype": "RECORD_PLAN",
    },
    {
        "artifact_id": "P94_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_record_creation_plan/latest.json",
        "status_field": "p83_record_creation_sequence_plan_status",
        "lane_archetype": "RECORD_CREATION_PLAN",
    },
    {
        "artifact_id": "P95_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_AUTHORIZATION_GATE",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_authorization_gate/latest.json",
        "status_field": "p83_record_creation_sequence_authorization_gate_status",
        "lane_archetype": "SEQUENCE_GATE",
    },
    {
        "artifact_id": "P96_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_plan/latest.json",
        "status_field": "p83_sequence_record_plan_status",
        "lane_archetype": "SEQUENCE_RECORD_PLAN",
    },
    {
        "artifact_id": "P97_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_plan/latest.json",
        "status_field": "p83_sequence_record_creation_plan_status",
        "lane_archetype": "SEQUENCE_RECORD_CREATION_PLAN",
    },
    {
        "artifact_id": "P98_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_AUTHORIZATION_GATE",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_authorization_gate/latest.json",
        "status_field": "p83_sequence_record_creation_authorization_gate_status",
        "lane_archetype": "SEQUENCE_RECORD_CREATION_GATE",
    },
    {
        "artifact_id": "P99_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_plan/latest.json",
        "status_field": "p83_sequence_record_creation_record_plan_status",
        "lane_archetype": "RECORD_PLAN",
    },
    {
        "artifact_id": "P100_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_PLAN",
        "path": "out/temporal_continuity_p83_regeneration_authorization_record_creation_sequence_record_creation_record_creation_plan/latest.json",
        "status_field": "p83_sequence_record_creation_record_creation_plan_status",
        "lane_archetype": "RECORD_CREATION_PLAN",
    },
    {
        "artifact_id": "P101_P83_REGENERATION_AUTHORIZATION_RECORD_CREATION_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE",
        "path": LATEST_REQUIRED_SOURCE_PATH,
        "status_field": "p83_sequence_record_creation_record_creation_authorization_gate_status",
        "lane_archetype": "RECORD_CREATION_GATE",
    },
)

_GOVERNANCE_LOCK_FIELDS: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "repair_execution_authority",
    "regeneration_authority",
    "regeneration_execution_authority",
    "evidence_generation_authority",
    "restoration_execution_authority",
    "generator_execution_authority",
    "upstream_input_generation_authority",
    "artifact_regeneration_authority",
    "execution_authority",
    "authorization_authority",
    "authorization_granted",
    "authorization_token_created",
    "authorization_record_creation_authority",
    "authorization_record_created",
    "spine_implementation_authority",
)

_DENIED_AUTHORITY: tuple[str, ...] = tuple(sorted(_GOVERNANCE_LOCK_FIELDS))
_RECOMMENDATION_ORDER = {
    "NOT_COMPUTABLE": 0,
    "CONTINUE_RECURSION": 1,
    "COMPRESS_TO_GENERIC_TEMPLATE": 2,
    "SEAL_RECURSIVE_AUTHORIZATION_CHAIN": 3,
}



def _round(value: float) -> float:
    return round(value, 6)



def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)



def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()



def _observe_artifact(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    rel_path = spec["path"]
    path = root / rel_path
    observed = path.exists()
    readable = False
    malformed = False
    file_hash = "NOT_COMPUTABLE"
    payload: dict[str, Any] | None = None
    status_value = "NOT_COMPUTABLE"
    recommended_next_lane = "NOT_COMPUTABLE"
    authority_lock_fields_present: list[str] = []
    authority_lock_fields_false: list[str] = []
    output_shape_signature = "NOT_COMPUTABLE"

    if observed:
        try:
            raw_bytes = path.read_bytes()
        except OSError:
            raw_bytes = b""
        else:
            readable = True
            file_hash = _sha256_bytes(raw_bytes)
            try:
                parsed = json.loads(raw_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                malformed = True
            else:
                if isinstance(parsed, dict):
                    payload = parsed
                    status_value = str(parsed.get(spec["status_field"], "NOT_COMPUTABLE"))
                    recommended_next_lane = str(
                        parsed.get("recommended_next_lane", "NOT_COMPUTABLE")
                    )
                    authority_lock_fields_present = [
                        field for field in _GOVERNANCE_LOCK_FIELDS if field in parsed
                    ]
                    authority_lock_fields_false = [
                        field
                        for field in authority_lock_fields_present
                        if parsed.get(field) is False
                    ]
                    output_shape_signature = _shape_signature(parsed)
                else:
                    malformed = True

    return {
        "artifact_id": spec["artifact_id"],
        "path": rel_path,
        "observed": observed,
        "readable": readable,
        "malformed": malformed,
        "artifact_type": (
            str(payload.get("artifact_type", "NOT_COMPUTABLE")) if payload else "NOT_COMPUTABLE"
        ),
        "status_field": spec["status_field"],
        "status_value": status_value,
        "recommended_next_lane": recommended_next_lane,
        "file_hash": file_hash,
        "authority_lock_fields_present": authority_lock_fields_present,
        "authority_lock_fields_false": authority_lock_fields_false,
        "output_shape_signature": output_shape_signature,
        "lane_archetype": spec["lane_archetype"],
        "contributes_to_repetition_metrics": readable and not malformed and payload is not None,
        "payload": payload,
    }



def _shape_descriptor(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            "type": "object",
            "keys": {
                _normalize_shape_key(key): _shape_descriptor(value[key])
                for key in sorted(value)
            },
        }
    if isinstance(value, list):
        unique_items = sorted(
            {canonical_dumps(_shape_descriptor(item)) for item in value}
        )
        return {"type": "array", "items": unique_items}
    if isinstance(value, bool):
        return "bool"
    if value is None:
        return "null"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return type(value).__name__


def _normalize_shape_key(key: str) -> str:
    if key.endswith("_status"):
        return "<status_field>"
    if key.endswith("_eligible"):
        return "<eligible_field>"
    if key.endswith("_required"):
        return "<required_field>"
    if key.endswith("_allowed"):
        return "<allowed_field>"
    return key


def _shape_signature(value: dict[str, Any]) -> str:
    descriptor = _shape_descriptor(value)
    return f"shape_{canonical_hash(descriptor)[:16]}"



def _status_pattern(status_value: str) -> str:
    if status_value == "NOT_COMPUTABLE":
        return "NOT_COMPUTABLE"
    for token in (
        "BLOCKED",
        "READY",
        "ELIGIBLE",
        "DENIED",
        "NOT_REQUIRED",
        "DEGRADED",
    ):
        if token in status_value:
            return token
    return "OTHER"



def _recommended_lane_pattern(recommended_next_lane: str) -> str:
    if recommended_next_lane == "NOT_COMPUTABLE":
        return "NOT_COMPUTABLE"
    if "SEAL" in recommended_next_lane:
        return "SEAL"
    if "GENERIC_AUTHORIZATION_LANE_TEMPLATE" in recommended_next_lane:
        return "GENERIC_TEMPLATE"
    if "EVIDENCE_RESTORATION" in recommended_next_lane:
        return "EVIDENCE_RESTORATION"
    if "CONTINUATION" in recommended_next_lane:
        return "CONTINUATION"
    if "AUTHORIZATION_GATE_REGENERATION" in recommended_next_lane:
        return "AUTHORIZATION_GATE_REGENERATION"
    if "REGENERATION" in recommended_next_lane:
        return "REGENERATION"
    if "AUTHORIZATION_GATE" in recommended_next_lane:
        return "AUTHORIZATION_GATE"
    if "AUTHORIZATION_RECORD_CREATION" in recommended_next_lane:
        return "AUTHORIZATION_RECORD_CREATION"
    if "AUTHORIZATION_RECORD_PLAN" in recommended_next_lane:
        return "AUTHORIZATION_RECORD_PLAN"
    if "RECORD_CREATION_PLAN" in recommended_next_lane:
        return "RECORD_CREATION_PLAN"
    if "RECORD_PLAN" in recommended_next_lane:
        return "RECORD_PLAN"
    if "EXECUTION_PLAN" in recommended_next_lane:
        return "EXECUTION_PLAN"
    if "PLAN" in recommended_next_lane:
        return "PLAN"
    return re.sub(r"^P\d+_", "", recommended_next_lane)



def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return _round(numerator / denominator)



def _build_repeated_lane_archetypes(inspected: list[dict[str, Any]], readable_count: int) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for item in inspected:
        if item["contributes_to_repetition_metrics"]:
            groups[str(item["lane_archetype"])].append(str(item["path"]))
    results = []
    for archetype in sorted(groups):
        paths = sorted(groups[archetype])
        if len(paths) < 2:
            continue
        repetition_ratio = _ratio(len(paths), readable_count)
        results.append(
            {
                "archetype": archetype,
                "count": len(paths),
                "paths": paths,
                "repetition_ratio": repetition_ratio,
                "compression_candidate": repetition_ratio >= 0.2,
            }
        )
    return results



def _build_repeated_governance_locks(inspected: list[dict[str, Any]], readable_count: int) -> list[dict[str, Any]]:
    results = []
    for field in sorted(_GOVERNANCE_LOCK_FIELDS):
        present_count = 0
        false_count = 0
        for item in inspected:
            if not item["contributes_to_repetition_metrics"]:
                continue
            present_fields = item["authority_lock_fields_present"]
            false_fields = item["authority_lock_fields_false"]
            if field in present_fields:
                present_count += 1
            if field in false_fields:
                false_count += 1
        false_ratio = _ratio(false_count, readable_count)
        results.append(
            {
                "field": field,
                "present_count": present_count,
                "false_count": false_count,
                "total_readable_count": readable_count,
                "false_ratio": false_ratio,
                "compression_candidate": readable_count > 0 and false_ratio >= 0.8,
            }
        )
    return results



def _build_repeated_routing_patterns(inspected: list[dict[str, Any]], readable_count: int) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for item in inspected:
        if not item["contributes_to_repetition_metrics"]:
            continue
        key = (
            _status_pattern(str(item["status_value"])),
            _recommended_lane_pattern(str(item["recommended_next_lane"])),
        )
        groups[key].append(str(item["path"]))

    results = []
    for status_pattern, lane_pattern in sorted(groups):
        paths = sorted(groups[(status_pattern, lane_pattern)])
        if len(paths) < 2:
            continue
        pattern_id = f"route_{hashlib.sha256(f'{status_pattern}|{lane_pattern}'.encode('utf-8')).hexdigest()[:12]}"
        results.append(
            {
                "pattern_id": pattern_id,
                "source_status_pattern": status_pattern,
                "recommended_lane_pattern": lane_pattern,
                "count": len(paths),
                "paths": paths,
                "compression_candidate": _ratio(len(paths), readable_count) >= 0.2,
            }
        )
    return sorted(results, key=lambda item: str(item["pattern_id"]))



def _build_repeated_artifact_shapes(inspected: list[dict[str, Any]], readable_count: int) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for item in inspected:
        if item["contributes_to_repetition_metrics"]:
            groups[str(item["output_shape_signature"])].append(str(item["path"]))
    results = []
    for signature in sorted(groups):
        paths = sorted(groups[signature])
        if len(paths) < 2:
            continue
        shape_id = f"shape_{hashlib.sha256(signature.encode('utf-8')).hexdigest()[:12]}"
        results.append(
            {
                "shape_id": shape_id,
                "signature": signature,
                "count": len(paths),
                "paths": paths,
                "compression_candidate": _ratio(len(paths), readable_count) >= 0.2,
            }
        )
    return sorted(results, key=lambda item: str(item["shape_id"]))



def _build_metrics(inspected: list[dict[str, Any]]) -> dict[str, float | int]:
    readable_items = [item for item in inspected if item["contributes_to_repetition_metrics"]]
    readable_count = len(readable_items)
    missing_count = sum(1 for item in inspected if not item["observed"])
    unreadable_count = sum(
        1 for item in inspected if item["observed"] and not item["readable"]
    )
    malformed_count = sum(1 for item in inspected if item["malformed"])
    recursive_depth_observed = readable_count

    governance_locks = _build_repeated_governance_locks(inspected, readable_count)
    repeated_lane_archetypes = _build_repeated_lane_archetypes(inspected, readable_count)
    repeated_routing_patterns = _build_repeated_routing_patterns(inspected, readable_count)
    repeated_artifact_shapes = _build_repeated_artifact_shapes(inspected, readable_count)

    repeated_authority_lock_ratio = _round(
        sum(float(item["false_ratio"]) for item in governance_locks) / len(governance_locks)
    ) if governance_locks else 0.0

    status_counter = Counter(
        _status_pattern(str(item["status_value"])) for item in readable_items
    )
    route_counter = Counter(
        _recommended_lane_pattern(str(item["recommended_next_lane"]))
        for item in readable_items
    )
    shape_counter = Counter(str(item["output_shape_signature"]) for item in readable_items)
    signal_counter = Counter(
        (
            _status_pattern(str(item["status_value"])),
            _recommended_lane_pattern(str(item["recommended_next_lane"])),
            str(item["output_shape_signature"]),
        )
        for item in readable_items
    )

    repeated_status_rule_ratio = _ratio(
        sum(count for count in status_counter.values() if count > 1), readable_count
    )
    repeated_output_shape_ratio = _ratio(
        sum(count for count in shape_counter.values() if count > 1), readable_count
    )
    repeated_recommended_lane_pattern_ratio = _ratio(
        sum(count for count in route_counter.values() if count > 1), readable_count
    )
    unique_new_signal_ratio = _ratio(
        sum(count for count in signal_counter.values() if count == 1), readable_count
    )
    ambiguity_reduction_score = unique_new_signal_ratio
    avg_repetition = _round(
        (
            repeated_authority_lock_ratio
            + repeated_status_rule_ratio
            + repeated_output_shape_ratio
            + repeated_recommended_lane_pattern_ratio
        )
        / 4
    ) if readable_count else 0.0
    complexity_rent_score = _round(
        (unique_new_signal_ratio + ambiguity_reduction_score + (1 - avg_repetition)) / 3
    ) if readable_count else 0.0

    return {
        "metrics": {
            "readable_artifact_count": readable_count,
            "missing_artifact_count": missing_count,
            "unreadable_artifact_count": unreadable_count,
            "malformed_artifact_count": malformed_count,
            "recursive_depth_observed": recursive_depth_observed,
            "repeated_authority_lock_ratio": repeated_authority_lock_ratio,
            "repeated_status_rule_ratio": repeated_status_rule_ratio,
            "repeated_output_shape_ratio": repeated_output_shape_ratio,
            "repeated_recommended_lane_pattern_ratio": repeated_recommended_lane_pattern_ratio,
            "unique_new_signal_ratio": unique_new_signal_ratio,
            "ambiguity_reduction_score": ambiguity_reduction_score,
            "complexity_rent_score": complexity_rent_score,
        },
        "repeated_lane_archetypes": repeated_lane_archetypes,
        "repeated_governance_locks": governance_locks,
        "repeated_routing_patterns": repeated_routing_patterns,
        "repeated_artifact_shapes": repeated_artifact_shapes,
    }



def _metrics_consistent(metrics: dict[str, float | int]) -> bool:
    ratio_keys = (
        "repeated_authority_lock_ratio",
        "repeated_status_rule_ratio",
        "repeated_output_shape_ratio",
        "repeated_recommended_lane_pattern_ratio",
        "unique_new_signal_ratio",
        "ambiguity_reduction_score",
        "complexity_rent_score",
    )
    for key in ratio_keys:
        value = float(metrics[key])
        if value < 0 or value > 1:
            return False
    return int(metrics["readable_artifact_count"]) >= 0



def _assessment(metrics: dict[str, float | int]) -> tuple[dict[str, Any], dict[str, Any]]:
    unique_ratio = float(metrics["unique_new_signal_ratio"])
    readable_count = int(metrics["readable_artifact_count"])
    repeated_semantics_detected = (
        float(metrics["repeated_status_rule_ratio"]) >= 0.5
        or float(metrics["repeated_output_shape_ratio"]) >= 0.5
    )
    if unique_ratio >= 0.5:
        marginal_utility = "HIGH"
    elif unique_ratio >= 0.25:
        marginal_utility = "MEDIUM"
    elif unique_ratio > 0:
        marginal_utility = "LOW"
    else:
        marginal_utility = "NONE"

    ambiguity = {
        "ambiguity_reduced_by_latest_batch": unique_ratio > 0.25,
        "new_signal_detected": unique_ratio > 0,
        "repeated_semantics_detected": repeated_semantics_detected,
        "marginal_utility": marginal_utility,
        "assessment_reason": (
            f"Readable chain artifacts={readable_count}; unique_new_signal_ratio={unique_ratio}; repeated semantics={'detected' if repeated_semantics_detected else 'not detected'}."
        ),
    }
    complexity = {
        "complexity_added": readable_count,
        "ambiguity_reduction": float(metrics["ambiguity_reduction_score"]),
        "rent_paid": _round(readable_count * (1 - unique_ratio)),
        "rent_score": float(metrics["complexity_rent_score"]),
        "assessment_reason": (
            "Low rent score means added recursive lanes are contributing limited new signal relative to repeated governance and routing topology."
        ),
    }
    return ambiguity, complexity



def _build_templates(recommendation: str) -> list[dict[str, Any]]:
    templates = [
        {
            "template_id": "template_001_generic_advisory_recursive_lane",
            "template_name": "Generic Advisory Recursive Authorization Lane",
            "applicable_archetypes": [
                "AUTHORIZATION_GATE",
                "AUTHORIZATION_RECORD_PLAN",
                "AUTHORIZATION_RECORD_CREATION_PLAN",
                "AUTHORIZATION_RECORD_CREATION_GATE",
                "RECORD_PLAN",
                "RECORD_CREATION_PLAN",
                "RECORD_CREATION_GATE",
                "SEQUENCE_GATE",
                "SEQUENCE_RECORD_PLAN",
                "SEQUENCE_RECORD_CREATION_PLAN",
                "SEQUENCE_RECORD_CREATION_GATE",
            ],
            "required_inputs": [
                "latest upstream artifact path",
                "upstream status field",
                "recommended next lane",
                "governance lock inventory",
            ],
            "required_outputs": [
                "artifact_type",
                "status field",
                "recommended_next_lane",
                "denied_authority",
                "packet_hash",
            ],
            "invariant_fields": [
                "canonical_status=ADVISORY_ONLY",
                "audit_only=true",
                "projection_only=true",
                "all authority fields=false",
            ],
            "variable_fields": [
                "status field name",
                "lane-specific summary object",
                "recommended_next_lane_reason",
                "artifact-specific prerequisite lists",
            ],
            "status_rule_template": "missing/unreadable/malformed => NOT_COMPUTABLE; ready+locks false => next advisory lane; weak signal => regeneration",
            "governance_locks": list(_GOVERNANCE_LOCK_FIELDS),
            "recommended_use": (
                "Use when P102 recommends COMPRESS_TO_GENERIC_TEMPLATE and repetition remains high across advisory-only recursive lanes."
            ),
            "implementation_authority": False,
        },
        {
            "template_id": "template_002_recursive_chain_seal_receipt",
            "template_name": "Recursive Authorization Chain Seal Receipt",
            "applicable_archetypes": ["AUTHORIZATION_GATE", "REGENERATION_PLAN"],
            "required_inputs": [
                "sealed chain summary",
                "compression findings",
                "structural repetition metrics",
            ],
            "required_outputs": [
                "seal status",
                "recommended_next_lane",
                "denied_authority",
                "packet_hash",
            ],
            "invariant_fields": [
                "canonical_status=ADVISORY_ONLY",
                "all authority fields=false",
                "no regeneration execution",
            ],
            "variable_fields": [
                "seal rationale",
                "sealed chain scope",
                "handoff notes",
            ],
            "status_rule_template": "extreme redundancy => seal receipt; weak signal => not computable until upstream eligibility is restored",
            "governance_locks": list(_GOVERNANCE_LOCK_FIELDS),
            "recommended_use": (
                "Use when P102 recommends SEAL_RECURSIVE_AUTHORIZATION_CHAIN and hand-written recursive lane expansion should stop."
            ),
            "implementation_authority": False,
        },
    ]
    if recommendation == "NOT_COMPUTABLE":
        return []
    return sorted(templates, key=lambda item: str(item["template_id"]))



def _build_findings(
    *,
    inspected: list[dict[str, Any]],
    metrics: dict[str, float | int],
    status: str,
    recommendation: str,
    reason: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    evidence_gap_paths = sorted(
        str(item["path"])
        for item in inspected
        if (not item["observed"]) or (not item["readable"]) or item["malformed"]
    )
    if evidence_gap_paths:
        findings.append(
            {
                "finding_id": "finding_001_evidence_gap",
                "finding_type": "EVIDENCE_GAP",
                "severity": "MEDIUM",
                "evidence_paths": evidence_gap_paths,
                "observation": "One or more recursive chain artifacts are missing, unreadable, or malformed.",
                "recommendation": reason,
            }
        )

    if float(metrics["repeated_status_rule_ratio"]) >= 0.7:
        findings.append(
            {
                "finding_id": "finding_010_recursive_self_similarity",
                "finding_type": "RECURSIVE_SELF_SIMILARITY",
                "severity": "MEDIUM",
                "evidence_paths": [str(item["path"]) for item in inspected if item["contributes_to_repetition_metrics"]],
                "observation": "Status transitions repeat across the recursive chain with limited variation.",
                "recommendation": "Prefer compressing repeated rule topology instead of extending another bespoke recursive lane.",
            }
        )
        findings.append(
            {
                "finding_id": "finding_020_status_rule_repetition",
                "finding_type": "STATUS_RULE_REPETITION",
                "severity": "MEDIUM",
                "evidence_paths": [str(item["path"]) for item in inspected if item["contributes_to_repetition_metrics"]],
                "observation": "Normalized status-rule motifs repeat at a high rate.",
                "recommendation": "Capture status propagation in a reusable template shape.",
            }
        )

    if float(metrics["repeated_authority_lock_ratio"]) >= 0.8:
        findings.append(
            {
                "finding_id": "finding_030_governance_lock_repetition",
                "finding_type": "GOVERNANCE_LOCK_REPETITION",
                "severity": "LOW",
                "evidence_paths": [str(item["path"]) for item in inspected if item["contributes_to_repetition_metrics"]],
                "observation": "Authority and governance lock fields remain uniformly false across readable chain artifacts.",
                "recommendation": "Template the invariant lock block instead of hand-authoring repeated false-lock payloads.",
            }
        )

    if float(metrics["repeated_output_shape_ratio"]) >= 0.7:
        findings.append(
            {
                "finding_id": "finding_040_output_shape_repetition",
                "finding_type": "OUTPUT_SHAPE_REPETITION",
                "severity": "MEDIUM",
                "evidence_paths": [str(item["path"]) for item in inspected if item["contributes_to_repetition_metrics"]],
                "observation": "Artifact payload shapes repeat across the recursive chain.",
                "recommendation": "Capture the repeated packet envelope in a generic advisory lane template.",
            }
        )

    if float(metrics["unique_new_signal_ratio"]) <= 0.25 and int(metrics["readable_artifact_count"]) > 0:
        findings.append(
            {
                "finding_id": "finding_050_low_unique_signal",
                "finding_type": "LOW_UNIQUE_SIGNAL",
                "severity": "HIGH",
                "evidence_paths": [str(item["path"]) for item in inspected if item["contributes_to_repetition_metrics"]],
                "observation": "The recursive chain is adding limited unique signal relative to its repeated topology.",
                "recommendation": "Stop adding hand-written recursive lanes when ambiguity reduction is marginal.",
            }
        )

    if recommendation == "COMPRESS_TO_GENERIC_TEMPLATE":
        findings.append(
            {
                "finding_id": "finding_060_compression_candidate",
                "finding_type": "COMPRESSION_CANDIDATE",
                "severity": "HIGH",
                "evidence_paths": [LATEST_REQUIRED_SOURCE_PATH],
                "observation": "Compression thresholds are satisfied while the chain remains advisory-only.",
                "recommendation": reason,
            }
        )
    elif recommendation == "SEAL_RECURSIVE_AUTHORIZATION_CHAIN":
        findings.append(
            {
                "finding_id": "finding_060_compression_candidate",
                "finding_type": "COMPRESSION_CANDIDATE",
                "severity": "HIGH",
                "evidence_paths": [LATEST_REQUIRED_SOURCE_PATH],
                "observation": "Compression thresholds are satisfied and redundancy is extreme.",
                "recommendation": reason,
            }
        )
        findings.append(
            {
                "finding_id": "finding_070_seal_candidate",
                "finding_type": "SEAL_CANDIDATE",
                "severity": "HIGH",
                "evidence_paths": [LATEST_REQUIRED_SOURCE_PATH],
                "observation": "Seal thresholds are satisfied; further recursive expansion is unlikely to reduce ambiguity.",
                "recommendation": reason,
            }
        )
    elif recommendation == "CONTINUE_RECURSION" and status == "COMPRESSION_AUDIT_READY":
        findings.append(
            {
                "finding_id": "finding_080_continuation_justified",
                "finding_type": "CONTINUATION_JUSTIFIED",
                "severity": "LOW",
                "evidence_paths": [LATEST_REQUIRED_SOURCE_PATH],
                "observation": "Repetition thresholds are not yet high enough to justify sealing or compression.",
                "recommendation": reason,
            }
        )

    return sorted(findings, key=lambda item: str(item["finding_id"]))



def _classify_ready_chain(metrics: dict[str, float | int]) -> tuple[str, str, str]:
    authority_ratio = float(metrics["repeated_authority_lock_ratio"])
    status_ratio = float(metrics["repeated_status_rule_ratio"])
    shape_ratio = float(metrics["repeated_output_shape_ratio"])
    unique_ratio = float(metrics["unique_new_signal_ratio"])
    rent_score = float(metrics["complexity_rent_score"])

    seal = (
        authority_ratio >= 0.9
        and status_ratio >= 0.85
        and shape_ratio >= 0.85
        and unique_ratio <= 0.15
        and rent_score < 0.25
    )
    compress = (
        authority_ratio >= 0.8
        and status_ratio >= 0.7
        and shape_ratio >= 0.7
        and unique_ratio <= 0.25
        and rent_score < 0.4
    )

    if seal:
        return (
            "SEAL_RECURSIVE_AUTHORIZATION_CHAIN",
            _SEAL_NEXT_LANE,
            "Redundancy is extreme across authority locks, status rules, output shapes, and routing; seal the recursive authorization chain instead of extending it.",
        )
    if compress:
        return (
            "COMPRESS_TO_GENERIC_TEMPLATE",
            _COMPRESS_NEXT_LANE,
            "Repeated topology is no longer reducing ambiguity; compress the recursive lane family into a generic advisory template shape.",
        )
    return (
        "CONTINUE_RECURSION",
        _CONTINUE_NEXT_LANE,
        "The chain still carries enough unique signal that another advisory recursion step remains justifiable.",
    )



def build_temporal_continuity_recursive_authorization_chain_compression_audit(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    inspected = [_observe_artifact(root, spec) for spec in _CHAIN_ARTIFACT_SPECS]
    inspected = sorted(inspected, key=lambda item: str(item["path"]))

    latest = next(item for item in inspected if str(item["path"]) == LATEST_REQUIRED_SOURCE_PATH)
    latest_payload = latest["payload"] if isinstance(latest["payload"], dict) else {}
    degraded_evidence_inputs = _as_list(latest_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_list(latest_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_list(latest_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_list(latest_payload.get("semantic_overlap_flags"))

    missing_artifacts = sorted(
        str(item["path"]) for item in inspected if not bool(item["observed"])
    )
    unreadable_artifacts = sorted(
        str(item["path"]) for item in inspected if bool(item["observed"]) and not bool(item["readable"])
    )
    malformed_artifacts = sorted(
        str(item["path"]) for item in inspected if bool(item["malformed"])
    )

    metrics_bundle = _build_metrics(inspected)
    metrics = metrics_bundle["metrics"]
    ambiguity_assessment, complexity_assessment = _assessment(metrics)

    latest_ready = (
        bool(latest["readable"])
        and not bool(latest["malformed"])
        and str(latest["status_value"]) == EXPECTED_LATEST_REQUIRED_STATUS
        and str(latest["recommended_next_lane"]) == EXPECTED_LATEST_REQUIRED_NEXT_LANE
        and bool(latest_payload.get("p83_sequence_record_creation_record_creation_authorization_eligible"))
    )

    if not bool(latest["observed"]) or not bool(latest["readable"]) or bool(latest["malformed"]):
        chain_status = "NOT_COMPUTABLE"
        recommendation = "NOT_COMPUTABLE"
        recommended_next_lane = _REGENERATION_NEXT_LANE
        recommendation_reason = (
            "Latest required P101 authorization-gate artifact is missing, unreadable, or malformed; regenerate P101 before attempting a compression audit."
        )
    elif not latest_ready:
        chain_status = "COMPRESSION_AUDIT_DEGRADED"
        recommendation = "NOT_COMPUTABLE"
        recommended_next_lane = _REGENERATION_NEXT_LANE
        recommendation_reason = (
            "Latest required P101 authorization-gate artifact is readable but not eligible for P102 compression auditing; restore the P101 advisory gate chain first."
        )
    elif int(metrics["readable_artifact_count"]) < 8:
        chain_status = "COMPRESSION_AUDIT_DEGRADED"
        recommendation = "NOT_COMPUTABLE"
        recommended_next_lane = _EVIDENCE_RESTORATION_NEXT_LANE
        recommendation_reason = (
            "Fewer than 8 recursive chain artifacts are readable; restore chain evidence before classifying recursive compression utility."
        )
    elif not _metrics_consistent(metrics):
        chain_status = "NOT_COMPUTABLE"
        recommendation = "NOT_COMPUTABLE"
        recommended_next_lane = _REGENERATION_NEXT_LANE
        recommendation_reason = (
            "Recursive compression metrics are inconsistent; restore the upstream P101 lane before continuing."
        )
    else:
        chain_status = "COMPRESSION_AUDIT_READY"
        recommendation, recommended_next_lane, recommendation_reason = _classify_ready_chain(metrics)

    compression_findings = _build_findings(
        inspected=inspected,
        metrics=metrics,
        status=chain_status,
        recommendation=recommendation,
        reason=recommendation_reason,
    )
    reusable_lane_templates = _build_templates(recommendation)

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "compression_audit_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "repair_execution_authority": False,
        "regeneration_authority": False,
        "regeneration_execution_authority": False,
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "upstream_input_generation_authority": False,
        "artifact_regeneration_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_token_created": False,
        "authorization_record_creation_authority": False,
        "authorization_record_created": False,
        "spine_implementation_authority": False,
        "source_chain_scope": SOURCE_CHAIN_SCOPE,
        "latest_required_source_path": LATEST_REQUIRED_SOURCE_PATH,
        "latest_required_source_observed": bool(latest["observed"]),
        "latest_required_source_readable": bool(latest["readable"]),
        "latest_required_source_hash": str(latest["file_hash"]),
        "latest_required_source_status": str(latest["status_value"]),
        "latest_required_recommended_next_lane": str(latest["recommended_next_lane"]),
        "inspected_artifacts": [
            {
                key: value
                for key, value in item.items()
                if key != "payload"
            }
            for item in inspected
        ],
        "missing_artifacts": missing_artifacts,
        "unreadable_artifacts": unreadable_artifacts,
        "malformed_artifacts": malformed_artifacts,
        "recursive_depth_observed": int(metrics["recursive_depth_observed"]),
        "repeated_lane_archetypes": metrics_bundle["repeated_lane_archetypes"],
        "repeated_governance_locks": metrics_bundle["repeated_governance_locks"],
        "repeated_routing_patterns": metrics_bundle["repeated_routing_patterns"],
        "repeated_artifact_shapes": metrics_bundle["repeated_artifact_shapes"],
        "structural_repetition_metrics": metrics,
        "ambiguity_reduction_assessment": ambiguity_assessment,
        "complexity_rent_assessment": complexity_assessment,
        "compression_findings": compression_findings,
        "reusable_lane_templates": reusable_lane_templates,
        "chain_compression_audit_status": chain_status,
        "chain_recommendation": recommendation,
        "chain_recommendation_reason": recommendation_reason,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommendation_reason,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "denied_authority": list(_DENIED_AUTHORITY),
    }
    packet = {
        **packet_base,
        "packet_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))



def write_temporal_continuity_recursive_authorization_chain_compression_audit(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
