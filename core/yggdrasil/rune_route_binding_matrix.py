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
_IMPLICIT_CLASSIFICATION = "PARTIAL"
_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_PATCH_ID = "PATCH-ABX-YGGDRASIL-RUNES-SUBSYSTEM-BINDING-001"
_AUDIT_SOURCE = "ABRAXAS_BINDING_MATRIX_AND_COUPLING_MAP_AUDIT_001"
_FINAL_STATUS = "BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY"


def _routes_with_filenames(
    routes_dir: Path,
) -> tuple[dict[str, str], dict[str, dict[str, bool]], dict[str, int]]:
    filenames: dict[str, str] = {}
    authorities: dict[str, dict[str, bool]] = {}
    rune_node_counts: dict[str, int] = {}
    for route_path in sorted(routes_dir.glob("*.json")):
        graph = load_route_graph(route_path)
        graph.authority.assert_locked()
        filenames[graph.pipeline_id] = route_path.name
        authorities[graph.pipeline_id] = graph.authority.model_dump()
        rune_node_counts[graph.pipeline_id] = sum(
            1 for node in graph.nodes if node.node_type.value == "rune"
        )
    return filenames, authorities, rune_node_counts


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
    route_filenames, route_authorities, route_rune_node_counts = _routes_with_filenames(
        root / "contracts/yggdrasil/routes"
    )

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
                route_authority = locked_authority()
                route_rune_node_count = 0
                route_observed = False
            else:
                status = _NOT_COMPUTABLE
                reason = _BINDING_REASON_UNSUPPORTED
                route_authority = route_authorities[pipeline_id]
                route_rune_node_count = route_rune_node_counts[pipeline_id]
                route_observed = True

            rows.append(
                {
                    "pipeline_id": pipeline_id,
                    "route": route_filename if route_filename is not None else _NOT_COMPUTABLE,
                    "rune_id": rune_id,
                    "status": status,
                    "reason": reason,
                    "classification": (
                        _IMPLICIT_CLASSIFICATION if route_observed else _NOT_COMPUTABLE
                    ),
                    "pipeline_requires_rune": True,
                    "route_observed": route_observed,
                    "route_rune_node_count": route_rune_node_count,
                    "rune_present_in_catalog": rune_present,
                    "authority": {
                        "rune": rune_authority,
                        "pipeline": contract.authority.model_dump(),
                        "route": route_authority,
                    },
                }
            )

    rows.sort(key=lambda row: (str(row["pipeline_id"]), str(row["rune_id"])))
    return {
        "schema_version": "YggdrasilRuneRouteBindingMatrix.v1",
        "artifact_id": "yggdrasil_rune_route_binding_matrix_001",
        "patch_id": _PATCH_ID,
        "audit_source": _AUDIT_SOURCE,
        "pipeline_count": len(contracts),
        "catalog_rune_count": len(catalog),
        "binding_count": len(rows),
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
    route_filenames, _, _ = _routes_with_filenames(root / "contracts/yggdrasil/routes")

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
        implicit_bindings.append(
            {
                "pipeline_id": pipeline_id,
                "route": route_filename,
                "reason": _BINDING_REASON_UNSUPPORTED,
                "classification": _IMPLICIT_CLASSIFICATION,
            }
        )
        for rune_id in required_runes_by_pipeline[pipeline_id]:
            unsupported_bindings.append(
                {
                    "pipeline_id": pipeline_id,
                    "rune_id": rune_id,
                    "status": _NOT_COMPUTABLE,
                    "reason": _BINDING_REASON_UNSUPPORTED,
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
