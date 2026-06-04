from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.pipelines.registry import load_contracts
from core.runes.registry import load_rune_catalog
from core.yggdrasil.validator import load_route_graphs
from core.yggdrasil_route_namespace_mapping import OUT_JSON as ROUTE_NAMESPACE_MAPPING_JSON

ARTIFACT_TYPE = "RuneEquivalentSurfaceAudit.v1"
AUDIT_ID = "RUNE_EQUIVALENT_SURFACE_AUDIT_001"
OUT_JSON = "out/audit/rune_equivalent_surface_audit_001.latest.json"
OUT_MD = "out/audit/rune_equivalent_surface_audit_001.latest.md"


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _locked(authority: Any) -> bool:
    values = authority.model_dump() if hasattr(authority, "model_dump") else dict(authority)
    return all(value is False for value in values.values())


def _surface_family(rune_id: str) -> str:
    parts = rune_id.split(".")
    return parts[1] if len(parts) > 1 else "UNKNOWN"


def _rune_to_pipelines(contracts: list[Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for contract in contracts:
        for rune_id in contract.required_runes:
            mapping.setdefault(rune_id, []).append(contract.pipeline_id)
    return {rune_id: sorted(pipelines) for rune_id, pipelines in sorted(mapping.items())}


def _route_evidence_for_family(routes: dict[str, Any], family: str) -> list[str]:
    evidence: set[str] = set()
    for pipeline_id, route in routes.items():
        for node in route.nodes:
            if family == "YGGDRASIL":
                evidence.add(pipeline_id)
            elif family == "PIPELINE" and node.node_type.value == "pipeline":
                evidence.add(pipeline_id)
            elif family == "GOVERNANCE" and node.lane == "GOVERNANCE":
                evidence.add(pipeline_id)
    return sorted(evidence)


def build_rune_equivalent_surface_audit(
    *,
    repo_root: str | Path,
    route_namespace_mapping_path: str | Path = ROUTE_NAMESPACE_MAPPING_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    catalog = load_rune_catalog(root / "contracts/runes/catalog.v1.json")
    contracts = sorted(load_contracts(root / "contracts/pipelines"), key=lambda item: item.pipeline_id)
    routes = load_route_graphs(root / "contracts/yggdrasil/routes")
    rune_to_pipelines = _rune_to_pipelines(contracts)

    records: list[dict[str, Any]] = []
    for rune_id, rune in sorted(catalog.items()):
        pipelines = rune_to_pipelines.get(rune_id, [])
        family = _surface_family(rune_id)
        route_evidence = _route_evidence_for_family(routes, family)
        required = bool(pipelines)
        records.append(
            {
                "rune_id": rune_id,
                "surface_family": family,
                "lane": rune.lane,
                "catalog_contract_observed": True,
                "catalog_authority_locked": _locked(rune.authority),
                "required_by_pipelines": pipelines,
                "pipeline_requirement_count": len(pipelines),
                "route_namespace_evidence": route_evidence,
                "route_namespace_count": len(route_evidence),
                "equivalence_status": "OBSERVED_REQUIRED" if required else "OBSERVED_CANDIDATE_ONLY",
                "candidate_only": not required,
                "duplicate_risk": "LOW" if required else "HIGH",
                "recommended_action": (
                    "preserve existing rune contract and pipeline requirements"
                    if required
                    else "keep candidate advisory-only until future registry formalization plan"
                ),
            }
        )

    unrequired_runes = sorted(record["rune_id"] for record in records if record["candidate_only"] is True)
    mapping_target = root / route_namespace_mapping_path
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "audit_status": "EMITTED_ADVISORY_ONLY" if records else "NOT_COMPUTABLE",
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "patch_id": "PATCH-ABX-RUNE-EQUIVALENT-SURFACE-AUDIT-001",
        "depends_on_patch": "PATCH-ABX-YGGDRASIL-ROUTE-NAMESPACE-MAPPING-001",
        "route_namespace_mapping_path": Path(route_namespace_mapping_path).as_posix(),
        "route_namespace_mapping_hash": _sha256(mapping_target),
        "catalog_rune_count": len(catalog),
        "pipeline_count": len(contracts),
        "route_count": len(routes),
        "required_rune_count": len(records) - len(unrequired_runes),
        "unrequired_rune_count": len(unrequired_runes),
        "surface_records": records,
        "unrequired_runes": unrequired_runes,
        "rune_registration_performed": False,
        "execution_dispatch_changed": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": "PATCH-ABX-BELIEF-GRAPH-GAP-VERIFICATION-001",
        "authority_locks": {
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_rune_equivalent_surface_audit(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_rune_equivalent_surface_audit_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Rune Equivalent Surface Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- audit_status: {packet['audit_status']}",
        f"- catalog_rune_count: {packet['catalog_rune_count']}",
        f"- required_rune_count: {packet['required_rune_count']}",
        f"- unrequired_rune_count: {packet['unrequired_rune_count']}",
        f"- rune_registration_performed: {packet['rune_registration_performed']}",
        f"- execution_dispatch_changed: {packet['execution_dispatch_changed']}",
        f"- forecast_routing: {packet['forecast_routing']}",
        f"- canon_mutation: {packet['canon_mutation']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        "",
        "## Unrequired Candidate Runes",
    ]
    for rune_id in packet.get("unrequired_runes", []):
        lines.append(f"- {rune_id}")
    lines.extend(["", "## Surface Records"])
    for record in packet.get("surface_records", []):
        lines.append(
            "- "
            f"{record['rune_id']}: {record['equivalence_status']} "
            f"(pipelines={record['pipeline_requirement_count']}, duplicate_risk={record['duplicate_risk']})"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
