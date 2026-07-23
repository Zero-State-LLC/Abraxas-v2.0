"""Deterministic rune↔route binding matrix and coupling map surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.governance.authority import locked_authority
from core.pipelines.registry import load_contracts
from core.runes.registry import load_rune_catalog
from core.yggdrasil.validator import load_route_graph

_BINDING_REASON_UNSUPPORTED = (
    "Route rune nodes carry node_id/node_type/lane but no rune_id field."
)
_BINDING_REASON_MISSING_ROUTE = (
    "No route graph contract found for pipeline_id in contracts/yggdrasil/routes."
)
_BINDING_REASON_EXPLICIT = (
    "Route exposes rune_id on at least one node; explicit binding surface present."
)
_BINDING_REASON_PARTIAL_EXPOSURE = (
    "Some route rune/review_gate nodes expose rune_id; others remain unmapped."
)
_IMPLICIT_CLASSIFICATION = "PARTIAL"
_EXPLICIT_CLASSIFICATION = "EXPLICIT"
_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_PATCH_ID = "PATCH-ABX-YGGDRASIL-RUNES-SUBSYSTEM-BINDING-001"
_AUDIT_SOURCE = "ABRAXAS_BINDING_MATRIX_AND_COUPLING_MAP_AUDIT_001"
_FINAL_STATUS = "BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY"

OUT_MATRIX_JSON = "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json"
OUT_MATRIX_MD = "out/audit/yggdrasil_rune_route_binding_matrix_001.latest.md"
OUT_COUPLING_JSON = "out/audit/yggdrasil_coupling_map_001.latest.json"
OUT_COUPLING_MD = "out/audit/yggdrasil_coupling_map_001.latest.md"


def _routes_with_filenames(
    routes_dir: Path,
) -> tuple[
    dict[str, str],
    dict[str, dict[str, bool]],
    dict[str, int],
    dict[str, set[str]],
    dict[str, int],
]:
    filenames: dict[str, str] = {}
    authorities: dict[str, dict[str, bool]] = {}
    rune_node_counts: dict[str, int] = {}
    exposed_rune_ids: dict[str, set[str]] = {}
    nodes_missing_rune_id: dict[str, int] = {}
    for route_path in sorted(routes_dir.glob("*.json")):
        graph = load_route_graph(route_path)
        graph.authority.assert_locked()
        filenames[graph.pipeline_id] = route_path.name
        authorities[graph.pipeline_id] = graph.authority.model_dump()
        runeish = [
            node
            for node in graph.nodes
            if node.node_type.value in ("rune", "review_gate")
        ]
        rune_node_counts[graph.pipeline_id] = len(runeish)
        exposed = {
            node.rune_id
            for node in runeish
            if getattr(node, "rune_id", None)
        }
        exposed_rune_ids[graph.pipeline_id] = exposed
        nodes_missing_rune_id[graph.pipeline_id] = sum(
            1 for node in runeish if not getattr(node, "rune_id", None)
        )
    return filenames, authorities, rune_node_counts, exposed_rune_ids, nodes_missing_rune_id


def _seal() -> dict[str, bool]:
    return {
        "FORECAST_ROUTING": False,
        "CANON_MUTATION": False,
        "RUNTIME_MUTATION": False,
        "EXECUTION_AUTHORITY": False,
        "PRIVATE_RUNTIME_ROUTES_ALLOWED": False,
    }


def _sorted_rune_to_pipelines(
    required_runes_by_pipeline: dict[str, tuple[str, ...]],
    rune_ids: tuple[str, ...],
) -> dict[str, list[str]]:
    return {
        rune_id: sorted(
            pipeline_id
            for pipeline_id, required_runes in required_runes_by_pipeline.items()
            if rune_id in required_runes
        )
        for rune_id in rune_ids
    }


def build_rune_route_binding_matrix(*, repo_root: str | Path = ".") -> dict[str, Any]:
    """Build deterministic rune↔pipeline↔route binding matrix (advisory-only)."""
    root = Path(repo_root)
    catalog = load_rune_catalog(root / "contracts/runes/catalog.v1.json")
    contracts = sorted(
        load_contracts(root / "contracts/pipelines"),
        key=lambda contract: contract.pipeline_id,
    )
    (
        route_filenames,
        route_authorities,
        route_rune_node_counts,
        exposed_rune_ids,
        nodes_missing_rune_id,
    ) = _routes_with_filenames(root / "contracts/yggdrasil/routes")

    rows: list[dict[str, Any]] = []
    for contract in contracts:
        contract.authority.assert_locked()
        pipeline_id = contract.pipeline_id
        route_filename = route_filenames.get(pipeline_id)
        pipeline_rune_ids = sorted(contract.required_runes)
        for rune_id in pipeline_rune_ids:
            rune = catalog.get(rune_id)
            if rune is not None:
                rune.authority.assert_locked()
                rune_authority = rune.authority.model_dump()
                rune_present = True
            else:
                rune_authority = locked_authority()
                rune_present = False

            if route_filename is None:
                status = _NOT_COMPUTABLE
                reason = _BINDING_REASON_MISSING_ROUTE
                classification = _NOT_COMPUTABLE
                route_authority = locked_authority()
                route_rune_node_count = 0
                route_observed = False
                explicit_on_route = False
            else:
                route_authority = route_authorities[pipeline_id]
                route_rune_node_count = route_rune_node_counts[pipeline_id]
                route_observed = True
                exposed = exposed_rune_ids.get(pipeline_id, set())
                missing = nodes_missing_rune_id.get(pipeline_id, 0)
                explicit_on_route = rune_id in exposed

                if explicit_on_route and missing == 0:
                    status = "BOUND"
                    reason = _BINDING_REASON_EXPLICIT
                    classification = _EXPLICIT_CLASSIFICATION
                elif explicit_on_route:
                    status = "BOUND_PARTIAL_SURFACE"
                    reason = _BINDING_REASON_PARTIAL_EXPOSURE
                    classification = _EXPLICIT_CLASSIFICATION
                elif exposed:
                    # Route has some rune_ids, but not this required rune
                    status = _NOT_COMPUTABLE
                    reason = (
                        f"Route exposes rune_id on other nodes, but not for {rune_id}."
                    )
                    classification = _IMPLICIT_CLASSIFICATION
                else:
                    status = _NOT_COMPUTABLE
                    reason = _BINDING_REASON_UNSUPPORTED
                    classification = _IMPLICIT_CLASSIFICATION

            rows.append(
                {
                    "pipeline_id": pipeline_id,
                    "route": route_filename if route_filename is not None else _NOT_COMPUTABLE,
                    "rune_id": rune_id,
                    "status": status,
                    "reason": reason,
                    "classification": classification,
                    "pipeline_requires_rune": True,
                    "route_observed": route_observed,
                    "route_rune_node_count": route_rune_node_count,
                    "explicit_on_route": explicit_on_route if route_observed else False,
                    "rune_present_in_catalog": rune_present,
                    "authority": {
                        "rune": rune_authority,
                        "pipeline": contract.authority.model_dump(),
                        "route": route_authority,
                    },
                }
            )

    rows.sort(key=lambda row: (str(row["pipeline_id"]), str(row["rune_id"])))
    explicit_count = sum(
        1 for row in rows if row["classification"] == _EXPLICIT_CLASSIFICATION
    )
    partial_count = sum(
        1 for row in rows if row["classification"] == _IMPLICIT_CLASSIFICATION
    )
    return {
        "schema_version": "YggdrasilRuneRouteBindingMatrix.v1",
        "artifact_id": "yggdrasil_rune_route_binding_matrix_001",
        "patch_id": _PATCH_ID,
        "audit_source": _AUDIT_SOURCE,
        "pipeline_count": len(contracts),
        "catalog_rune_count": len(catalog),
        "binding_count": len(rows),
        "explicit_binding_count": explicit_count,
        "partial_binding_count": partial_count,
        "bindings": rows,
        "seal": _seal(),
        "FORECAST_ROUTING": False,
        "CANON_MUTATION": False,
        "RUNTIME_MUTATION": False,
        "EXECUTION_AUTHORITY": False,
        "PRIVATE_RUNTIME_ROUTES_ALLOWED": False,
        "final_status": _FINAL_STATUS,
    }


def build_coupling_map(*, repo_root: str | Path = ".") -> dict[str, Any]:
    """Build deterministic rune/pipeline/route coupling map (advisory-only)."""
    root = Path(repo_root)
    catalog = load_rune_catalog(root / "contracts/runes/catalog.v1.json")
    contracts = sorted(
        load_contracts(root / "contracts/pipelines"),
        key=lambda contract: contract.pipeline_id,
    )
    (
        route_filenames,
        _,
        _,
        exposed_rune_ids,
        nodes_missing_rune_id,
    ) = _routes_with_filenames(root / "contracts/yggdrasil/routes")

    required_runes_by_pipeline: dict[str, tuple[str, ...]] = {
        contract.pipeline_id: tuple(sorted(contract.required_runes))
        for contract in contracts
    }
    rune_ids = tuple(sorted(catalog.keys()))
    rune_to_pipelines = _sorted_rune_to_pipelines(required_runes_by_pipeline, rune_ids)

    pipeline_to_route: dict[str, str] = {}
    implicit_bindings: list[dict[str, str]] = []
    unsupported_bindings: list[dict[str, str]] = []
    for pipeline_id in sorted(required_runes_by_pipeline):
        route_filename = route_filenames.get(pipeline_id)
        if route_filename is None:
            pipeline_to_route[pipeline_id] = _NOT_COMPUTABLE
            for rune_id in required_runes_by_pipeline[pipeline_id]:
                unsupported_bindings.append(
                    {
                        "pipeline_id": pipeline_id,
                        "rune_id": rune_id,
                        "status": _NOT_COMPUTABLE,
                        "reason": _BINDING_REASON_MISSING_ROUTE,
                    }
                )
            continue

        pipeline_to_route[pipeline_id] = route_filename
        exposed = exposed_rune_ids.get(pipeline_id, set())
        missing = nodes_missing_rune_id.get(pipeline_id, 0)

        if exposed and missing == 0:
            classification = _EXPLICIT_CLASSIFICATION
            reason = _BINDING_REASON_EXPLICIT
        elif exposed:
            classification = _EXPLICIT_CLASSIFICATION
            reason = _BINDING_REASON_PARTIAL_EXPOSURE
        else:
            classification = _IMPLICIT_CLASSIFICATION
            reason = _BINDING_REASON_UNSUPPORTED

        implicit_bindings.append(
            {
                "pipeline_id": pipeline_id,
                "route": route_filename,
                "reason": reason,
                "classification": classification,
                "exposed_rune_count": str(len(exposed)),
                "nodes_missing_rune_id": str(missing),
            }
        )
        for rune_id in required_runes_by_pipeline[pipeline_id]:
            if rune_id in exposed:
                unsupported_bindings.append(
                    {
                        "pipeline_id": pipeline_id,
                        "rune_id": rune_id,
                        "status": "BOUND",
                        "reason": _BINDING_REASON_EXPLICIT,
                    }
                )
            else:
                unsupported_bindings.append(
                    {
                        "pipeline_id": pipeline_id,
                        "rune_id": rune_id,
                        "status": _NOT_COMPUTABLE,
                        "reason": (
                            f"Required rune not among exposed route rune_ids ({sorted(exposed)})."
                            if exposed
                            else _BINDING_REASON_UNSUPPORTED
                        ),
                    }
                )

    unsupported_bindings.sort(
        key=lambda row: (row["pipeline_id"], row["rune_id"])
    )
    unbound_runes = sorted(
        rune_id for rune_id, pipelines in rune_to_pipelines.items() if not pipelines
    )

    return {
        "schema_version": "YggdrasilCouplingMap.v1",
        "artifact_id": "yggdrasil_coupling_map_001",
        "patch_id": _PATCH_ID,
        "audit_source": _AUDIT_SOURCE,
        "rune_to_pipelines": rune_to_pipelines,
        "pipeline_to_route": pipeline_to_route,
        "implicit_bindings": implicit_bindings,
        "unsupported_bindings": unsupported_bindings,
        "unbound_runes": unbound_runes,
        "seal": _seal(),
        "FORECAST_ROUTING": False,
        "CANON_MUTATION": False,
        "RUNTIME_MUTATION": False,
        "EXECUTION_AUTHORITY": False,
        "PRIVATE_RUNTIME_ROUTES_ALLOWED": False,
        "final_status": _FINAL_STATUS,
    }


def write_rune_route_binding_matrix(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_coupling_map(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def _write_markdown(path: str | Path, lines: list[str]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_rune_route_binding_matrix_markdown(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    bindings = packet["bindings"]
    observed_route_count = sum(1 for row in bindings if row["route_observed"])
    not_computable_count = sum(1 for row in bindings if row["status"] == _NOT_COMPUTABLE)
    explicit_count = packet.get("explicit_binding_count", 0)
    partial_count = packet.get("partial_binding_count", 0)
    lines = [
        "# Yggdrasil Rune Route Binding Matrix 001",
        "",
        f"- artifact_id: {packet['artifact_id']}",
        f"- patch_id: {packet['patch_id']}",
        f"- audit_source: {packet['audit_source']}",
        f"- schema_version: {packet['schema_version']}",
        f"- pipeline_count: {packet['pipeline_count']}",
        f"- catalog_rune_count: {packet['catalog_rune_count']}",
        f"- binding_count: {packet['binding_count']}",
        f"- explicit_binding_count: {explicit_count}",
        f"- partial_binding_count: {partial_count}",
        f"- observed_route_binding_rows: {observed_route_count}",
        f"- not_computable_binding_rows: {not_computable_count}",
        f"- final_status: {packet['final_status']}",
        "",
        "## Seal",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(packet["seal"].items()))
    lines.extend(["", "## Advisory Summary"])
    lines.extend(
        [
            "- Binding rows remain advisory-only and non-authoritative.",
            "- Routes that expose rune_id are classified EXPLICIT for matching required runes.",
            "- Remaining PARTIAL / NOT_COMPUTABLE rows indicate unmapped nodes or required runes not present on the route surface.",
            "- No forecast routing, canon mutation, runtime mutation, or execution authority is granted.",
        ]
    )
    _write_markdown(path, lines)


def write_coupling_map_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Yggdrasil Coupling Map 001",
        "",
        f"- artifact_id: {packet['artifact_id']}",
        f"- patch_id: {packet['patch_id']}",
        f"- audit_source: {packet['audit_source']}",
        f"- schema_version: {packet['schema_version']}",
        f"- rune_count: {len(packet['rune_to_pipelines'])}",
        f"- pipeline_route_count: {len(packet['pipeline_to_route'])}",
        f"- implicit_binding_count: {len(packet['implicit_bindings'])}",
        f"- unsupported_binding_count: {len(packet['unsupported_bindings'])}",
        f"- unbound_rune_count: {len(packet['unbound_runes'])}",
        f"- final_status: {packet['final_status']}",
        "",
        "## Seal",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(packet["seal"].items()))
    lines.extend(["", "## Unbound Runes"])
    if packet["unbound_runes"]:
        lines.extend(f"- {rune_id}" for rune_id in packet["unbound_runes"])
    else:
        lines.append("- NONE")
    lines.extend(["", "## Advisory Summary"])
    lines.extend(
        [
            "- Couplings are advisory-only and describe observed contract gaps.",
            "- Explicit rune_id exposure on routes reduces PARTIAL classifications.",
            "- No forecast routing, canon mutation, runtime mutation, or execution authority is granted.",
        ]
    )
    _write_markdown(path, lines)
