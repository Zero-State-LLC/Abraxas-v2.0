"""Script: run doctrine validator over all Tier-1 contracts."""

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
from core.spine.milestone_continuity import validate_milestone_continuity
from core.spine.milestone_registry import derive_registry_from_artifacts
from core.spine.milestone_validator import validate_active_milestone
from core.yggdrasil.validator import load_route_graphs

CONTRACTS_DIR = Path("contracts/pipelines")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")
ROUTES_DIR = Path("contracts/yggdrasil/routes")

OUT_VALIDATION = Path("out/validation/latest.json")
OUT_AAL_VIZ = Path("out/projections/aal_viz.latest.json")
OUT_QUEUE = Path("out/operator_review/latest.json")
OUT_MILESTONE_REG = Path("out/spine/milestone_registry.latest.json")
OUT_MILESTONE_VAL = Path("out/spine/milestone_validation.latest.json")


def _build_summary(results: list[dict], active_milestone: str = "unknown", milestone_status: str = "passed") -> dict[str, object]:
    counts = {
        "doctrine_compliant": sum(1 for r in results if r["status"] == "doctrine_compliant"),
        "repair_required": sum(1 for r in results if r["status"] == "repair_required"),
        "legacy_contract_posture": sum(1 for r in results if r["status"] == "legacy_contract_posture"),
        "not_computable": sum(1 for r in results if r["status"] == "not_computable"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
    }
    if milestone_status != "passed":
        counts["failed"] += 1
    seal = "repair" if counts["failed"] > 0 or counts["repair_required"] > 0 else ("hold" if counts["legacy_contract_posture"] > 0 else "seal")
    return {
        "schema_version": "DoctrineValidationSummary.v1",
        "compliant_count": counts["doctrine_compliant"],
        "repair_required_count": counts["repair_required"],
        "legacy_contract_posture_count": counts["legacy_contract_posture"],
        "not_computable_count": counts["not_computable"],
        "failed_count": counts["failed"],
        "active_milestone": active_milestone,
        "seal_recommendation": seal,
        "status": "failed" if counts["failed"] > 0 else "ok",
    }


def main() -> None:
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    route_graphs = load_route_graphs(ROUTES_DIR)
    contracts = load_contracts(CONTRACTS_DIR)
    continuity = validate_milestone_continuity()

    results = []
    for contract in contracts:
        graph_data = route_graphs[contract.pipeline_id].model_dump() if contract.pipeline_id in route_graphs else None
        results.append(validate_pipeline_contract(contract, rune_catalog, graph_data, continuity.model_dump()))

    from core.pipelines.registry import build_registry

    registry = build_registry(contracts)
    queue = build_review_queue(results)
    milestone_registry = derive_registry_from_artifacts()
    milestone_validation = validate_active_milestone({"active_milestone": milestone_registry.active_milestone}, milestone_registry.model_dump())
    summary = _build_summary(results, milestone_registry.active_milestone, str(milestone_validation["status"]))
    projection = build_projection_packet(
        registry,
        results,
        queue,
        continuity.model_dump(),
        doctrine_posture_summary={
            "doctrine_compliant": summary["compliant_count"],
            "repair_required": summary["repair_required_count"],
            "legacy_contract_posture": summary["legacy_contract_posture_count"],
            "not_computable": summary["not_computable_count"],
            "failed": summary["failed_count"],
            "seal_recommendation": summary["seal_recommendation"],
        },
        milestone_summary={
            "active_milestone": milestone_registry.active_milestone,
            "stabilized_milestones": milestone_registry.stabilized_milestones,
            "latest_stable_hash": milestone_registry.latest_stable_hash,
            "lineage_depth": len(milestone_registry.milestone_lineage),
            "milestone_validator_status": milestone_validation["status"],
        },
    )

    write_canonical_json(OUT_VALIDATION, {"schema_version": "DoctrineValidationRun.v1", "contract_count": len(results), "results": results, "summary": summary})
    write_canonical_json(OUT_AAL_VIZ, projection)
    write_canonical_json(OUT_QUEUE, queue)
    write_canonical_json(OUT_MILESTONE_REG, milestone_registry.model_dump())
    write_canonical_json(OUT_MILESTONE_VAL, milestone_validation)


if __name__ == "__main__":
    main()
