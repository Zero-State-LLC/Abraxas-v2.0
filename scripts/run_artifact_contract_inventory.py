from __future__ import annotations

from pathlib import Path

from core.audit_artifact_contract_inventory import build_inventory
from core.canonical.json import write_canonical_json


def main() -> None:
    inv = build_inventory(Path('.'))
    write_canonical_json('out/contracts/artifact_contract_inventory.latest.json', inv)
    report = {
        'schema': 'ArtifactContractInventoryReport.v1',
        'status': inv['status'],
        'counts': inv['counts'],
        'top_gaps': inv['gaps'][:10],
        'inventory_hash': inv['inventory_hash'],
    }
    write_canonical_json('out/contracts/artifact_contract_inventory_report.latest.json', report)
    write_canonical_json('out/contracts/artifact_contract_inventory_gaps.latest.json', {'schema': 'ArtifactContractInventoryGaps.v1', 'gaps': inv['gaps']})
    print(f"artifact contract inventory: {inv['status']}")


if __name__ == '__main__':
    main()
