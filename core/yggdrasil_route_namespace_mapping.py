from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.pipelines.registry import load_contracts
from core.repo_notion_diff import OUT_JSON as REPO_NOTION_DIFF_JSON
from core.yggdrasil.validator import load_route_graphs

ARTIFACT_TYPE = "YggdrasilRouteNamespaceMapping.v1"
MAPPING_ID = "YGGDRASIL_ROUTE_NAMESPACE_MAPPING_001"
OUT_JSON = "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json"
OUT_MD = "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.md"

_NOTION_NAMESPACES: dict[str, str] = {
    "aal_viz_projection": "AAL-Viz Projection Spine",
    "canon_sync": "Canon Sync",
    "outcome_brier": "Outcome Brier",
    "pse_forecast": "PSE Forecast",
    "research_drop_validation": "Research Drop Validation",
    "research_intake": "Research Intake",
    "universal_ingest": "Global Ingest Adapter Spine",
}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _locked(authority: Any) -> bool:
    values = authority.model_dump() if hasattr(authority, "model_dump") else dict(authority)
    return all(value is False for value in values.values())


def _route_file_for(pipeline_id: str) -> str:
    return f"contracts/yggdrasil/routes/{pipeline_id}.route.v1.json"


def _pipeline_file_for(pipeline_id: str) -> str:
    return f"contracts/pipelines/{pipeline_id}.v1_1.json"


def _route_node_namespace(node_ids: list[str]) -> str:
    if not node_ids:
        return "NOT_COMPUTABLE"
    split_ids = [node_id.split(".") for node_id in node_ids]
    prefix: list[str] = []
    for parts in zip(*split_ids):
        if len(set(parts)) != 1:
            break
        prefix.append(parts[0])
    if prefix:
        return ".".join(prefix)
    first = split_ids[0]
    return ".".join(first[:-1]) if len(first) > 1 else first[0]


def _mapping_strength(route_observed: bool, pipeline_observed: bool) -> str:
    if route_observed and pipeline_observed:
        return "EXACT"
    if route_observed or pipeline_observed:
        return "PARTIAL"
    return "MISSING"


def _duplicate_risk(mapping_strength: str, authority_boundary_count: int) -> str:
    if mapping_strength == "EXACT" and authority_boundary_count == 0:
        return "LOW"
    if mapping_strength == "EXACT":
        return "MEDIUM"
    if mapping_strength == "PARTIAL":
        return "HIGH"
    return "MEDIUM"


def build_yggdrasil_route_namespace_mapping(
    *,
    repo_root: str | Path,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    routes = load_route_graphs(root / "contracts/yggdrasil/routes")
    pipelines = {
        contract.pipeline_id: contract
        for contract in sorted(
            load_contracts(root / "contracts/pipelines"),
            key=lambda item: item.pipeline_id,
        )
    }
    all_pipeline_ids = sorted(set(routes) | set(pipelines))

    records: list[dict[str, Any]] = []
    for pipeline_id in all_pipeline_ids:
        route = routes.get(pipeline_id)
        pipeline = pipelines.get(pipeline_id)
        route_observed = route is not None
        pipeline_observed = pipeline is not None
        node_ids = [node.node_id for node in route.nodes] if route is not None else []
        lane_set = sorted({node.lane for node in route.nodes}) if route is not None else []
        authority_boundary_count = (
            sum(1 for edge in route.edges if edge.authority_boundary.value != "none")
            if route is not None
            else 0
        )
        mapping_strength = _mapping_strength(route_observed, pipeline_observed)
        records.append(
            {
                "pipeline_id": pipeline_id,
                "notion_namespace": _NOTION_NAMESPACES.get(
                    pipeline_id,
                    pipeline_id.replace("_", " ").title(),
                ),
                "route_file": _route_file_for(pipeline_id) if route_observed else "NOT_COMPUTABLE",
                "pipeline_contract": (
                    _pipeline_file_for(pipeline_id) if pipeline_observed else "NOT_COMPUTABLE"
                ),
                "route_node_namespace": _route_node_namespace(node_ids),
                "route_observed": route_observed,
                "pipeline_observed": pipeline_observed,
                "node_count": len(route.nodes) if route is not None else 0,
                "edge_count": len(route.edges) if route is not None else 0,
                "lane_set": lane_set,
                "authority_boundary_count": authority_boundary_count,
                "required_rune_count": len(pipeline.required_runes) if pipeline is not None else 0,
                "mapping_strength": mapping_strength,
                "duplicate_risk": _duplicate_risk(mapping_strength, authority_boundary_count),
                "route_authority_locked": _locked(route.authority) if route is not None else False,
                "pipeline_authority_locked": _locked(pipeline.authority) if pipeline is not None else False,
                "recommended_action": (
                    "preserve existing route and map namespace only"
                    if mapping_strength == "EXACT"
                    else "record gap before any route design"
                ),
            }
        )
    records.sort(key=lambda item: item["pipeline_id"])

    route_ids = set(routes)
    pipeline_ids = set(pipelines)
    diff_target = root / repo_notion_diff_path
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "mapping_id": MAPPING_ID,
        "mapping_status": "EMITTED_ADVISORY_ONLY" if records else "NOT_COMPUTABLE",
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "patch_id": "PATCH-ABX-YGGDRASIL-ROUTE-NAMESPACE-MAPPING-001",
        "depends_on_patch": "PATCH-ABX-REPO-NOTION-DIFF-001",
        "repo_notion_diff_path": Path(repo_notion_diff_path).as_posix(),
        "repo_notion_diff_hash": _sha256(diff_target),
        "route_count": len(routes),
        "pipeline_count": len(pipelines),
        "mapped_count": sum(1 for record in records if record["mapping_strength"] == "EXACT"),
        "unmapped_routes": sorted(route_ids - pipeline_ids),
        "missing_routes_for_pipelines": sorted(pipeline_ids - route_ids),
        "namespace_records": records,
        "existing_routes_preserved": True,
        "new_route_authority_created": False,
        "runtime_dispatch_mutation": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": "PATCH-ABX-RUNE-EQUIVALENT-SURFACE-AUDIT-001",
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


def write_yggdrasil_route_namespace_mapping(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_yggdrasil_route_namespace_mapping_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# YGGDRASIL Route Namespace Mapping",
        "",
        f"- mapping_id: {packet['mapping_id']}",
        f"- mapping_status: {packet['mapping_status']}",
        f"- route_count: {packet['route_count']}",
        f"- pipeline_count: {packet['pipeline_count']}",
        f"- mapped_count: {packet['mapped_count']}",
        f"- existing_routes_preserved: {packet['existing_routes_preserved']}",
        f"- new_route_authority_created: {packet['new_route_authority_created']}",
        f"- runtime_dispatch_mutation: {packet['runtime_dispatch_mutation']}",
        f"- forecast_routing: {packet['forecast_routing']}",
        f"- canon_mutation: {packet['canon_mutation']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        "",
        "## Namespace Records",
    ]
    for record in packet.get("namespace_records", []):
        lines.append(
            "- "
            f"{record['pipeline_id']}: {record['notion_namespace']} "
            f"({record['mapping_strength']}, duplicate_risk={record['duplicate_risk']})"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
