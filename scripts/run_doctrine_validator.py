"""Script: run doctrine validator over all Tier-1 contracts.

Usage:
    python scripts/run_doctrine_validator.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.operators.review_queue import build_review_queue
from core.pipelines.registry import load_contracts
from core.pipelines.validator import validate_pipeline_contract
from core.projections.aal_viz import build_projection_packet
from core.runes.registry import load_rune_catalog
from core.yggdrasil.validator import load_route_graphs

CONTRACTS_DIR = Path("contracts/pipelines")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")
ROUTES_DIR = Path("contracts/yggdrasil/routes")

OUT_VALIDATION = Path("out/validation/latest.json")
OUT_AAL_VIZ = Path("out/projections/aal_viz.latest.json")
OUT_QUEUE = Path("out/operator_review/latest.json")


def main() -> None:
    print("Loading rune catalog ...")
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    print(f"  {len(rune_catalog)} runes loaded.")

    print("Loading route graphs ...")
    route_graphs = load_route_graphs(ROUTES_DIR)
    print(f"  {len(route_graphs)} route graphs loaded.")

    print(f"Loading contracts from {CONTRACTS_DIR} ...")
    contracts = load_contracts(CONTRACTS_DIR)
    print(f"  {len(contracts)} contracts loaded.")

    print("Running doctrine validation ...")
    results = []
    for contract in contracts:
        graph_data = (
            route_graphs[contract.pipeline_id].model_dump()
            if contract.pipeline_id in route_graphs
            else None
        )
        result = validate_pipeline_contract(contract, rune_catalog, graph_data)
        results.append(result)
        print(f"  {contract.pipeline_id}: {result['status']}")

    # Build registry for AAL-Viz
    from core.pipelines.registry import build_registry

    registry = build_registry(contracts)

    # Build AAL-Viz projection
    queue = build_review_queue(results)
    projection = build_projection_packet(registry, results, queue)

    validation_doc = {
        "schema_version": "DoctrineValidationRun.v1",
        "contract_count": len(results),
        "results": results,
    }

    write_canonical_json(OUT_VALIDATION, validation_doc)
    write_canonical_json(OUT_AAL_VIZ, projection)
    write_canonical_json(OUT_QUEUE, queue)

    print(f"\nValidation written to   : {OUT_VALIDATION}")
    print(f"AAL-Viz written to      : {OUT_AAL_VIZ}")
    print(f"Review queue written to : {OUT_QUEUE}")
    print(f"\nSummary: {projection['summary']}")


if __name__ == "__main__":
    main()
