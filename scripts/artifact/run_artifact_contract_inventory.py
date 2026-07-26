from __future__ import annotations

from pathlib import Path

from core.audit_artifact_contract_inventory import build_inventory
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.config import RuntimePaths
from core.performance import RuntimeProfiler


def main() -> None:
    profiler = RuntimeProfiler(RuntimePaths.from_env().runtime_performance_profile_latest)
    inventory_path = Path("out/contracts/artifact_contract_inventory.latest.json")
    report_path = Path("out/contracts/artifact_contract_inventory_report.latest.json")
    gaps_path = Path("out/contracts/artifact_contract_inventory_gaps.latest.json")
    profiler.record_artifact("inventory_output", inventory_path)
    profiler.record_artifact("inventory_report_output", report_path)
    profiler.record_artifact("inventory_gaps_output", gaps_path)
    with profiler.measure("artifact_contract_inventory", "build_inventory"):
        inv = build_inventory(Path("."))
    with profiler.measure("artifact_contract_inventory", "write_inventory_outputs"):
        write_classified_json(inventory_path, inv, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    report = {
        "schema": "ArtifactContractInventoryReport.v1",
        "status": inv["status"],
        "counts": inv["counts"],
        "top_gaps": inv["gaps"][:10],
        "inventory_hash": inv["inventory_hash"],
    }
    with profiler.measure("artifact_contract_inventory", "write_report_outputs"):
        write_classified_json(report_path, report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
        write_classified_json(
            gaps_path,
            {
                "schema": "ArtifactContractInventoryGaps.v1",
                "gaps": inv["gaps"],
            },
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        )
    profiler.write()
    print(f"artifact contract inventory: {inv['status']}")


if __name__ == "__main__":
    main()
