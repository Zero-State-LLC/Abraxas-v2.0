from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.belief_graph_gap_verification import OUT_JSON as BELIEF_GRAPH_GAP_VERIFICATION_JSON
from core.canonical.json import canonical_hash, write_canonical_json
from core.rune_equivalent_surface_audit import OUT_JSON as RUNE_EQUIVALENT_AUDIT_JSON

ARTIFACT_TYPE = "RuneRegistryFormalizationPlan.v1"
PLAN_ID = "RUNE_REGISTRY_FORMALIZATION_PLAN_001"
OUT_JSON = "out/audit/rune_registry_formalization_plan_001.latest.json"
OUT_MD = "out/audit/rune_registry_formalization_plan_001.latest.md"


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _plan_record(surface_record: dict[str, Any]) -> dict[str, Any]:
    candidate_only = surface_record.get("candidate_only") is True
    action = "HOLD_CANDIDATE_ONLY" if candidate_only else "PRESERVE_REQUIRED_RUNE"
    return {
        "rune_id": str(surface_record.get("rune_id", "NOT_COMPUTABLE")),
        "surface_family": str(surface_record.get("surface_family", "NOT_COMPUTABLE")),
        "lane": str(surface_record.get("lane", "NOT_COMPUTABLE")),
        "source_equivalence_status": str(surface_record.get("equivalence_status", "NOT_COMPUTABLE")),
        "candidate_only": candidate_only,
        "pipeline_requirement_count": int(surface_record.get("pipeline_requirement_count", 0)),
        "duplicate_risk": str(surface_record.get("duplicate_risk", "NOT_COMPUTABLE")),
        "formalization_action": action,
        "catalog_change_required": False,
        "pipeline_change_required": False,
        "route_change_required": False,
        "dispatch_change_required": False,
        "operator_authorization_required": candidate_only,
        "recommended_action": (
            "keep advisory candidate in catalog; require future explicit operator/governance decision before pipeline use"
            if candidate_only
            else "preserve existing catalog rune and observed pipeline requirements"
        ),
    }


def build_rune_registry_formalization_plan(
    *,
    repo_root: str | Path,
    rune_equivalent_surface_audit_path: str | Path = RUNE_EQUIVALENT_AUDIT_JSON,
    belief_graph_gap_verification_path: str | Path = BELIEF_GRAPH_GAP_VERIFICATION_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    audit_target = root / rune_equivalent_surface_audit_path
    belief_target = root / belief_graph_gap_verification_path
    audit = _load_json(audit_target)
    belief_verification = _load_json(belief_target)
    surface_records = audit.get("surface_records", [])
    plan_records = [_plan_record(record) for record in surface_records]
    candidate_holds = [record["rune_id"] for record in plan_records if record["candidate_only"]]
    required_preserved = [record["rune_id"] for record in plan_records if not record["candidate_only"]]
    graph_observed = belief_verification.get("belief_graph_equivalent_observed") is True
    plan_status = (
        "PLAN_EMITTED_ADVISORY_ONLY"
        if plan_records and graph_observed
        else "NOT_COMPUTABLE"
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "patch_id": "PATCH-ABX-RUNE-REGISTRY-FORMALIZATION-PLAN-001",
        "depends_on_patch": "PATCH-ABX-BELIEF-GRAPH-GAP-VERIFICATION-001",
        "rune_equivalent_surface_audit_path": Path(rune_equivalent_surface_audit_path).as_posix(),
        "rune_equivalent_surface_audit_hash": _sha256(audit_target),
        "belief_graph_gap_verification_path": Path(belief_graph_gap_verification_path).as_posix(),
        "belief_graph_gap_verification_hash": _sha256(belief_target),
        "belief_graph_equivalent_observed": graph_observed,
        "catalog_rune_count": int(audit.get("catalog_rune_count", 0)),
        "required_rune_count": len(required_preserved),
        "candidate_hold_count": len(candidate_holds),
        "plan_records": plan_records,
        "candidate_holds": sorted(candidate_holds),
        "required_runes_preserved": sorted(required_preserved),
        "formalization_summary": {
            "total_plan_records": len(plan_records),
            "preserve_required_runes": len(required_preserved),
            "hold_candidate_only_runes": len(candidate_holds),
            "catalog_changes_planned": 0,
            "pipeline_changes_planned": 0,
            "route_changes_planned": 0,
            "dispatch_changes_planned": 0,
        },
        "rune_registration_performed": False,
        "catalog_mutation_performed": False,
        "pipeline_mutation_performed": False,
        "route_mutation_performed": False,
        "execution_dispatch_changed": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": "NOT_COMPUTABLE",
        "authority_locks": {
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
            "rune_registration": False,
            "dispatch_mutation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_rune_registry_formalization_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_rune_registry_formalization_plan_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Rune Registry Formalization Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- belief_graph_equivalent_observed: {packet['belief_graph_equivalent_observed']}",
        f"- catalog_rune_count: {packet['catalog_rune_count']}",
        f"- required_rune_count: {packet['required_rune_count']}",
        f"- candidate_hold_count: {packet['candidate_hold_count']}",
        f"- rune_registration_performed: {packet['rune_registration_performed']}",
        f"- execution_dispatch_changed: {packet['execution_dispatch_changed']}",
        f"- forecast_routing: {packet['forecast_routing']}",
        f"- canon_mutation: {packet['canon_mutation']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        "",
        "## Candidate Holds",
    ]
    for rune_id in packet.get("candidate_holds", []):
        lines.append(f"- {rune_id}")
    lines.extend(["", "## Formalization Records"])
    for record in packet.get("plan_records", []):
        lines.append(
            "- "
            f"{record['rune_id']}: {record['formalization_action']} "
            f"(duplicate_risk={record['duplicate_risk']})"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
