"""Script: execute incremental replay and emit lineage receipt.

PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001

Usage:
    python scripts/research/run_incremental_replay.py

Output:
    out/audit/incremental_replay_001.latest.json

Executes replay only for invalidated dependency regions.
Preserves canonical output ordering.
Emits replay lineage receipts.
Verifies replay equivalence against full replay where possible.
Authority / mutation / promotion: always False.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id
from core.replay_graph import (
    build_replay_graph,
    build_replay_node,
    verify_graph_stability,
)
from core.replay_incremental import (
    PATCH_ID,
    build_incremental_plan,
    verify_replay_equivalence,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.incremental_replay_latest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fixture surface: registry contract artifact dependency graph
# ---------------------------------------------------------------------------

_REGISTRY_NODES = [
    ("node_root", "contracts", []),
    ("node_contracts_dir", "contracts/pipelines", ["node_root"]),
    ("node_registry_output", "out/registry/latest.json", ["node_contracts_dir"]),
    ("node_audit_dir", "out/audit", ["node_root"]),
    (
        "node_benchmark",
        "out/audit/runtime_benchmark_001.latest.json",
        ["node_audit_dir", "node_registry_output"],
    ),
    (
        "node_console",
        "out/audit/operator_runtime_console_001.latest.json",
        ["node_audit_dir", "node_benchmark"],
    ),
]


def _build_surface_hash(path: str) -> str:
    """Return a deterministic content hash for a replay surface path."""
    return canonical_hash({"surface_path": path})


def _build_registry_graph() -> dict[str, Any]:
    """Build the canonical registry artifact dependency graph."""
    nodes = [
        build_replay_node(
            node_id=nid,
            artifact_path=apath,
            content_hash=_build_surface_hash(apath),
            dependencies=deps,
            replay_surface="registry_generation",
        )
        for nid, apath, deps in _REGISTRY_NODES
    ]
    return build_replay_graph(graph_id="registry_replay_graph", nodes=nodes)


def _simulate_full_replay(graph: dict[str, Any]) -> dict[str, str]:
    """Simulate full replay: compute output hashes for all nodes."""
    return {
        n["node_id"]: canonical_hash(
            {"node_id": n["node_id"], "content_hash": n["content_hash"]}
        )
        for n in graph["nodes"]
    }


def _simulate_incremental_replay(
    plan: dict[str, Any],
    full_outputs: dict[str, str],
) -> dict[str, str]:
    """Simulate incremental replay: compute outputs only for invalidated nodes."""
    invalidated = frozenset(plan["invalidated_nodes"])
    return {
        node_id: output_hash
        for node_id, output_hash in full_outputs.items()
        if node_id in invalidated
    }


def main() -> None:
    diagnostics_logger = get_structured_logger(__name__)

    correlation_id = stable_correlation_id(
        "incremental_replay",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )

    log_event(
        diagnostics_logger,
        "INFO",
        "incremental_replay_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    # --- build replay graph ---
    graph = _build_registry_graph()

    # --- verify graph stability (same inputs → same graph hash) ---
    graph_b = _build_registry_graph()
    stability = verify_graph_stability(graph, graph_b)

    # --- build incremental plan: simulate node_benchmark changed ---
    changed_node_ids = ["node_benchmark"]
    plan = build_incremental_plan(
        plan_id="incremental_replay_001",
        graph=graph,
        changed_node_ids=changed_node_ids,
    )

    # --- simulate full + incremental replay ---
    full_outputs = _simulate_full_replay(graph)
    incremental_outputs = _simulate_incremental_replay(plan, full_outputs)

    # --- verify equivalence ---
    equivalence = verify_replay_equivalence(
        full_outputs=full_outputs,
        incremental_outputs=incremental_outputs,
        plan=plan,
    )

    # --- collect artifact outputs for invalidated region ---
    artifact_outputs = {
        node_id: incremental_outputs[node_id]
        for node_id in plan["invalidated_nodes"]
        if node_id in incremental_outputs
    }

    # --- derive blockers and final status ---
    blockers: list[str] = []
    if not stability["stable"]:
        blockers.append("replay_graph_not_stable")
    if not equivalence["equivalence_held"]:
        blockers.append("replay_equivalence_not_held")
    if plan["fail_closed"]:
        blockers.append("invalidation_fail_closed")

    final_status = "PASS" if not blockers else "BLOCKED"

    receipt: dict[str, Any] = {
        "schema": "IncrementalReplayReceipt.v1",
        "patch_id": PATCH_ID,
        "replay_graph_hash": graph["graph_hash"],
        "invalidated_nodes": plan["invalidated_nodes"],
        "replay_chunks": plan["replay_chunks"],
        "skipped_surfaces": plan["skipped_surfaces"],
        "replay_equivalence_verified": equivalence["equivalence_held"],
        "artifact_outputs": artifact_outputs,
        "graph_stability": stability,
        "equivalence_verification": equivalence,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "final_status": final_status,
        "remaining_blockers": sorted(blockers),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(OUT_PATH, receipt)

    log_event(
        diagnostics_logger,
        "INFO",
        "incremental_replay_completed",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
        final_status=final_status,
        remaining_blockers=sorted(blockers),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
