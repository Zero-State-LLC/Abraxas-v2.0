from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

BACKLOG_SCHEMA_VERSION = "GlobalPipelineGapBacklog.v1"
BACKLOG_JSON_PATH = Path("out/operator_review/global_pipeline_gap_backlog_001.latest.json")
BACKLOG_MD_PATH = Path("out/operator_review/global_pipeline_gap_backlog_001.latest.md")

DOCTRINE_PROOF_PATH = Path("out/global_pipeline_doctrine_validation/latest.json")
REGISTRY_PATH = Path("out/global_pipeline_registry/latest.json")
INGEST_ALIGNMENT_PLAN_PATH = Path("out/sync/global_ingest_adapter_spine_alignment_plan/latest.json")
NOTION_DECISION_BACKLOG_PATH = Path("out/sync/notion_operator_decision_backlog/latest.json")

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_hash(data: Mapping[str, Any], field_name: str) -> str:
    payload = dict(data)
    payload.pop(field_name, None)
    return _sha256_text(_canonical_json(payload))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_and_markdown(json_path: Path, md_path: Path, packet: Mapping[str, Any], markdown_lines: list[str]) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(_canonical_json(packet) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")


def _priority_for_entry(entry: Mapping[str, Any]) -> str:
    if entry.get("pipeline_id") == "oracle_signal":
        return "P0"
    tier = int(entry.get("tier", 99))
    if tier <= 2:
        return "P2"
    return "P3"


def _build_oracle_signal_item(
    entry: Mapping[str, Any],
    ingest_alignment_plan: Mapping[str, Any],
    notion_backlog: Mapping[str, Any],
) -> dict[str, Any]:
    decision_backlog = notion_backlog.get("decision_backlog", [])
    top_decision = decision_backlog[0] if decision_backlog else {}
    required_inputs = list(top_decision.get("required_inputs", ()))
    if not required_inputs:
        required_inputs = [str(ingest_alignment_plan.get("required_operator_input", "explicit governed operator decision required"))]

    return {
        "pipeline_id": entry["pipeline_id"],
        "display_name": entry["display_name"],
        "tier": entry["tier"],
        "lane": entry["lane"],
        "priority": "P0",
        "queue_action": "HOLD_FOR_GOVERNED_OPERATOR_DECISION",
        "completion_status": "BLOCKED",
        "source_observed": True,
        "implementation_allowed": False,
        "safe_to_auto_continue": False,
        "missing_contract": True,
        "missing_validation": True,
        "next_action": entry.get("next_action"),
        "observed_paths": [
            "scripts/run_ingest_once.py",
            "scripts/run_oracle_intake.py",
        ],
        "missing_paths": ["core/oracle_signal.py"],
        "required_inputs": required_inputs,
        "recommended_action": "hold for explicit governed operator decision before any Oracle Signal Layer pipeline contract or implementation work",
        "blocked_reasons": [
            "EXPLICIT_OPERATOR_DECISION_REQUIRED",
            "GLOBAL_INGEST_ADAPTER_SPINE_HOLD_ACTIVE",
        ],
    }


def _build_deferred_item(entry: Mapping[str, Any]) -> dict[str, Any]:
    priority = _priority_for_entry(entry)
    return {
        "pipeline_id": entry["pipeline_id"],
        "display_name": entry["display_name"],
        "tier": entry["tier"],
        "lane": entry["lane"],
        "priority": priority,
        "queue_action": "DEFER_UNOBSERVED_SUBSYSTEM",
        "completion_status": "DEFERRED",
        "source_observed": False,
        "implementation_allowed": False,
        "safe_to_auto_continue": False,
        "missing_contract": True,
        "missing_validation": True,
        "next_action": entry.get("next_action"),
        "observed_paths": [],
        "missing_paths": [],
        "required_inputs": [
            "fresh governed specification or observed repo surface required before contract creation",
        ],
        "recommended_action": "defer until a fresh governed spec or observable subsystem surface exists; do not fabricate a pipeline contract from inventory metadata alone",
        "blocked_reasons": [
            "INSUFFICIENT_OBSERVED_REPO_SURFACE",
            "NO_GOVERNED_SPEC_BINDING_PRESENT",
        ],
    }


def build_global_pipeline_gap_backlog(source_root: str | Path = ".") -> dict[str, Any]:
    root = Path(source_root)
    doctrine_proof = _read_json(root / DOCTRINE_PROOF_PATH)
    registry = _read_json(root / REGISTRY_PATH)
    ingest_alignment_plan = _read_json(root / INGEST_ALIGNMENT_PLAN_PATH)
    notion_backlog = _read_json(root / NOTION_DECISION_BACKLOG_PATH)

    registry_entries = {
        item["pipeline_id"]: item
        for item in registry.get("pipelines", [])
    }

    missing_ids = list(doctrine_proof.get("missing_contract_ids", ()))
    backlog_items: list[dict[str, Any]] = []

    for pipeline_id in missing_ids:
        entry = registry_entries.get(pipeline_id)
        if entry is None:
            raise KeyError(f"Missing registry entry for doctrine gap pipeline_id={pipeline_id!r}")
        if pipeline_id == "oracle_signal":
            item = _build_oracle_signal_item(entry, ingest_alignment_plan, notion_backlog)
        else:
            item = _build_deferred_item(entry)
        backlog_items.append(item)

    backlog_items.sort(
        key=lambda item: (
            PRIORITY_ORDER[item["priority"]],
            int(item["tier"]),
            item["pipeline_id"],
        )
    )

    blocked_count = sum(1 for item in backlog_items if item["completion_status"] == "BLOCKED")
    deferred_count = sum(1 for item in backlog_items if item["completion_status"] == "DEFERRED")
    priority_counts = {
        level: sum(1 for item in backlog_items if item["priority"] == level)
        for level in ("P0", "P1", "P2", "P3")
    }

    packet = {
        "schema_version": BACKLOG_SCHEMA_VERSION,
        "status": "GLOBAL_PIPELINE_GAP_BACKLOG_EMITTED",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "backlog_id": "",
        "gap_count": len(backlog_items),
        "blocked_count": blocked_count,
        "deferred_count": deferred_count,
        "priority_counts": priority_counts,
        "recommended_next_state": "hold",
        "recommended_next_action": "preserve the oracle_signal governed hold and defer unobserved subsystems until a fresh governed spec or observable repo surface exists",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "source_hashes": {
            "doctrine_proof": doctrine_proof.get("proof_id"),
            "registry": registry.get("registry_id"),
            "ingest_alignment_plan": ingest_alignment_plan.get("packet_hash"),
            "notion_operator_decision_backlog": notion_backlog.get("packet_hash"),
        },
        "backlog_items": backlog_items,
    }
    packet["backlog_id"] = _canonical_hash(packet, "backlog_id")
    return packet


def render_global_pipeline_gap_backlog_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Global Pipeline Gap Backlog",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `gap_count`: `{packet['gap_count']}`",
        f"- `blocked_count`: `{packet['blocked_count']}`",
        f"- `deferred_count`: `{packet['deferred_count']}`",
        f"- `recommended_next_action`: `{packet['recommended_next_action']}`",
        "",
        "## Backlog",
        "",
    ]
    for item in packet["backlog_items"]:
        lines.append(
            f"- `{item['priority']}` `{item['pipeline_id']}` :: `{item['queue_action']}` :: {item['recommended_action']}"
        )
    return lines


def write_global_pipeline_gap_backlog(source_root: str | Path = ".") -> dict[str, Any]:
    packet = build_global_pipeline_gap_backlog(source_root=source_root)
    markdown = render_global_pipeline_gap_backlog_markdown(packet)
    _write_json_and_markdown(BACKLOG_JSON_PATH, BACKLOG_MD_PATH, packet, markdown)
    return packet
