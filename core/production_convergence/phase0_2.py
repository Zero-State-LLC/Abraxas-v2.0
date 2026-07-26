"""Build and optionally write Production Convergence Phase 0–2 package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.production_convergence.baseline import build_baseline
from core.production_convergence.deprecation_ledger import build_deprecation_ledger
from core.production_convergence.duplication import build_duplication_clusters
from core.production_convergence.golden_path import build_golden_path_trace
from core.production_convergence.governance_map import (
    build_governance_contradiction_map,
)
from core.production_convergence.inventory import (
    build_entrypoint_inventory,
    build_interface_inventory,
)

OUT_DIR_REL = Path("out/production_convergence")


def build_phase0_2_package(
    repo_root: Path,
    *,
    write: bool = True,
    run_validation: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    out_dir = root / OUT_DIR_REL

    artifacts = {
        "baseline.v1.json": build_baseline(root, run_validation=run_validation),
        "entrypoint_inventory.v1.json": build_entrypoint_inventory(root),
        "interface_inventory.v1.json": build_interface_inventory(root),
        "duplication_clusters.v1.json": build_duplication_clusters(),
        "golden_path_trace.v1.json": build_golden_path_trace(),
        "governance_contradiction_map.v1.json": build_governance_contradiction_map(),
        "deprecation_ledger.v1.json": build_deprecation_ledger(),
    }

    if write:
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, payload in artifacts.items():
            write_canonical_json(out_dir / name, payload)

    return {
        "output_dir": OUT_DIR_REL.as_posix(),
        "artifacts": {name: payload.get("canonical_hash") for name, payload in artifacts.items()},
        "package": artifacts,
    }
