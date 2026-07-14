from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryPolicyReview.v1"
REVIEW_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_001"
AUDIT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
)
JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
)
MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.md"
)
DEFAULT_CLASSIFICATION = "EXCLUDE_FROM_CANONICAL_REPAIR"

POLICY_OPTIONS = [
    "EXCLUDE_FROM_CANONICAL_REPAIR",
    "REGISTER_AS_DERIVED_OPTIONAL",
    "ARCHIVE_CANDIDATE",
    "HOLD",
]

BLOCKED_ACTIONS = [
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REGISTRY_REPAIR_EXECUTION",
    "DIRECT_REGISTRY_REPAIR",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _orphan_records(audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in audit.get("orphan_research_outputs", []):
        if not isinstance(item, dict):
            continue
        records.append(
            {
                "output_json_path": str(item.get("output_json_path", NOT_COMPUTABLE)),
                "lane_id_observed": str(item.get("lane_id_observed", NOT_COMPUTABLE)),
                "artifact_type_observed": str(item.get("artifact_type_observed", NOT_COMPUTABLE)),
                "classification": str(item.get("classification", "ORPHAN_RESEARCH_OUTPUT")),
                "default_classification": DEFAULT_CLASSIFICATION,
            }
        )
    return sorted(records, key=lambda record: record["output_json_path"])


def build_abx_research_canary_orphan_output_registry_policy_review(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    audit = _read_json(root / AUDIT_JSON_PATH)
    coverage = audit.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        coverage = {}
    orphan_records = _orphan_records(audit)
    orphan_count = coverage.get("orphan_research_output_count")
    if orphan_count is None:
        orphan_count = len(orphan_records)
    try:
        orphan_count_int = int(orphan_count)
    except (TypeError, ValueError):
        orphan_count_int = -1
    source_audit_ready = (
        audit.get("audit_id") == "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001"
        and coverage.get("direct_registry_lane_id_coverage") is True
        and coverage.get("lane_id_gap_count") == 0
        and coverage.get("output_path_gap_count") == 0
        and orphan_count_int == len(orphan_records) == 0
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": REVIEW_ID,
        "review_id": "abx_research_canary_orphan_output_registry_policy_review_001",
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_HELD_FOR_OPERATOR"
            if source_audit_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_BLOCKED"
        ),
        "review_hash": "",
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "policy_review_only": True,
        "registry_mutation_performed": False,
        "source_coverage_audit": {
            "path": str(AUDIT_JSON_PATH),
            "audit_id": str(audit.get("audit_id", NOT_COMPUTABLE)),
            "audit_hash": str(audit.get("audit_hash", NOT_COMPUTABLE)),
            "audit_status": str(audit.get("audit_status", NOT_COMPUTABLE)),
            "source_audit_ready": source_audit_ready,
            "orphan_research_output_count": coverage.get("orphan_research_output_count"),
        },
        "review_scope": "ORPHAN_RESEARCH_OUTPUT_REGISTRY_POLICY_DECISION_ONLY",
        "orphan_count": len(orphan_records),
        "orphan_records": orphan_records,
        "policy_options": list(POLICY_OPTIONS),
        "recommended_policy": DEFAULT_CLASSIFICATION,
        "decision_question": (
            "Post-A4b orphan inclusion is sealed with zero remaining orphan research outputs. "
            "Should any future orphan registry policy remain held for operator review, or should "
            "a separate governed operator lane authorize per-path registry inclusion, archive "
            "candidacy, or continued hold?"
        ),
        "execution_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "governance_preservation": {
            "p130_hold_preserved": True,
            "orphan_exclusion_preserved": False,
            "orphan_inclusion_sealed_post_a4b": source_audit_ready,
            "research_canary_spine_refresh_performed": False,
            "separate_orphan_registry_governance_required": True,
        },
        "downstream_status": "ORPHAN_POLICY_REVIEW_HELD_FOR_OPERATOR",
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "review orphan output registry policy options and collect explicit operator decision "
            "evidence before any orphan registry inclusion or archive lane"
            if source_audit_ready
            else "complete post-repair coverage audit prerequisites before orphan policy review"
        ),
    }
    packet["review_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "review_hash"})
    return packet


def render_abx_research_canary_orphan_output_registry_policy_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Policy Review 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `orphan_count`: `{packet['orphan_count']}`",
        f"- `recommended_policy`: `{packet['recommended_policy']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Orphan Records",
    ]
    for record in packet.get("orphan_records", []):
        if isinstance(record, dict):
            lines.append(
                f"- `{record.get('output_json_path')}`: `{record.get('lane_id_observed')}` "
                f"(default `{record.get('default_classification')}`)"
            )
    lines.extend(
        [
            "",
            "## Policy Options",
            "",
            *[f"- `{option}`" for option in packet.get("policy_options", [])],
            "",
            "## Preserved Holds",
            "",
            "- `ORPHAN_OUTPUT_REGISTRY_INCLUSION` remains blocked",
            "- `P130_ACTIVATION` remains blocked",
            "- `RESEARCH_CANARY_SPINE_REFRESH` remains blocked",
        ]
    )
    return lines


def write_abx_research_canary_orphan_output_registry_policy_review(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_policy_review(root)
    write_canonical_json(target_root / JSON_PATH, packet)
    _write_markdown(
        target_root / MD_PATH,
        render_abx_research_canary_orphan_output_registry_policy_review_markdown(packet),
    )
    return packet
