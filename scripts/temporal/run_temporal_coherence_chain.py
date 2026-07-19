"""Script: deterministic canonical temporal coherence chain runner."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from scripts.operator import (
    run_coherence_field_operator_surface,
)
from scripts.temporal import (
    run_cross_run_topology_fusion,
)
from scripts.temporal import (
    run_temporal_resonance_coherence,
    run_temporal_stability_pressure,
    run_temporal_state_diff,
    run_temporal_topology_cartography,
    run_temporal_upstream_evidence,
)

_PATHS = RuntimePaths.from_env()
CHAIN_JSON_PATH = Path("out/audit/temporal_coherence_chain_001.latest.json")
CHAIN_MD_PATH = Path("out/audit/temporal_coherence_chain_001.latest.md")
UPSTREAM_EVIDENCE_PATH = Path("out/audit/temporal_upstream_evidence_001.latest.json")


_STAGE_DEFS = (
    (
        "cross_run_topology_fusion",
        run_cross_run_topology_fusion.main,
        _PATHS.cross_run_topology_fusion_latest,
        "cross_run_topology_fusion_status",
    ),
    (
        "temporal_stability_pressure",
        run_temporal_stability_pressure.main,
        _PATHS.temporal_stability_pressure_latest,
        "temporal_stability_pressure_status",
    ),
    (
        "temporal_state_diff",
        run_temporal_state_diff.main,
        _PATHS.temporal_state_diff_latest,
        "temporal_state_diff_status",
    ),
    (
        "temporal_topology_cartography",
        run_temporal_topology_cartography.main,
        _PATHS.temporal_topology_cartography_latest,
        "temporal_topology_cartography_status",
    ),
    (
        "temporal_resonance_coherence",
        run_temporal_resonance_coherence.main,
        _PATHS.temporal_resonance_coherence_latest,
        "final_status",
    ),
    (
        "coherence_field_operator_surface",
        run_coherence_field_operator_surface.main,
        _PATHS.coherence_field_operator_surface_latest,
        "coherence_field_operator_surface_status",
    ),
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _receipt_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# Temporal Coherence Chain Receipt",
        "",
        f"- chain_id: `{receipt['chain_id']}`",
        f"- final_chain_status: `{receipt['final_chain_status']}`",
        f"- no_authority_escalation: `{receipt['governance_flags']['no_authority_escalation']}`",
        f"- upstream_evidence_status: `{receipt['upstream_evidence']['final_evidence_status']}`",
        f"- upstream_evidence_receipt: `{receipt['upstream_evidence']['receipt_path']}`",
        f"- live_projection_refresh_evidence_state: `{receipt['upstream_evidence']['live_projection_refresh_evidence_state']}`",
        "",
        "## Stages",
        "",
    ]
    for stage in receipt["stages"]:
        lines.append(f"- `{stage['stage_name']}` → `{stage['observed_status']}`")
        if stage["blockers"]:
            lines.append(f"  - blockers: {', '.join(stage['blockers'])}")
    return "\n".join(lines) + "\n"


def run_chain() -> dict[str, Any]:
    stages: list[dict[str, Any]] = []
    halted = False
    chain_blockers: list[str] = []

    run_temporal_upstream_evidence.main([])
    upstream_evidence = _load_json(UPSTREAM_EVIDENCE_PATH)
    upstream_status = "NOT_READY"
    live_projection_evidence_status = "MISSING"
    if isinstance(upstream_evidence, dict):
        upstream_status = str(upstream_evidence.get("final_evidence_status", "NOT_READY"))
        checked = upstream_evidence.get("checked_artifacts", [])
        if isinstance(checked, list):
            for item in checked:
                if isinstance(item, dict) and item.get("artifact_key") == "live_projection_refresh":
                    live_projection_evidence_status = str(item.get("evidence_state", "MISSING"))
                    break

    for name, runner, artifact_path, status_field in _STAGE_DEFS:
        blockers: list[str] = []
        if halted:
            observed_status = "SKIPPED_DUE_TO_UPSTREAM"
            completed = False
        else:
            try:
                runner([])
            except Exception as exc:  # fail-closed
                blockers.append(f"runner_exception:{name}:{type(exc).__name__}")
            payload = _load_json(artifact_path)
            if payload is None:
                blockers.append(f"missing_or_corrupt_artifact:{artifact_path.as_posix()}")
                observed_status = "NOT_COMPUTABLE"
                completed = False
            else:
                observed_status = str(payload.get(status_field, "NOT_COMPUTABLE"))
                payload_blockers = payload.get("remaining_blockers")
                if isinstance(payload_blockers, list):
                    blockers.extend(sorted(str(item) for item in payload_blockers))
                completed = observed_status not in {"BLOCKED", "NOT_COMPUTABLE"}
            if not completed:
                halted = True

        stage = {
            "stage_name": name,
            "command_or_runner": f"scripts.run_{name}.main",
            "artifact_paths": [artifact_path.as_posix()],
            "observed_status": observed_status,
            "blockers": sorted(set(blockers)),
            "completed": completed,
        }
        stages.append(stage)
        chain_blockers.extend(stage["blockers"])

    all_completed = all(item["completed"] for item in stages)
    if all_completed and upstream_status == "READY":
        final_chain_status = "ADVISORY_ONLY"
    elif all_completed and upstream_status == "DEGRADED_READY":
        final_chain_status = "ADVISORY_DEGRADED"
    else:
        final_chain_status = "BLOCKED"
    return {
        "schema_version": "TemporalCoherenceChainReceipt.v1",
        "chain_id": "temporal_coherence_chain_001",
        "stages": stages,
        "upstream_evidence": {
            "receipt_path": UPSTREAM_EVIDENCE_PATH.as_posix(),
            "final_evidence_status": upstream_status,
            "live_projection_refresh_evidence_state": live_projection_evidence_status,
        },
        "final_chain_status": final_chain_status,
        "governance_flags": {
            "no_authority_escalation": True,
            "advisory_only": True,
            "projection_only": True,
            "mutation_allowed": False,
            "authority_granted": False,
        },
        "blockers": sorted(set(chain_blockers)),
    }


def main() -> None:
    receipt = run_chain()
    write_canonical_json(CHAIN_JSON_PATH, receipt)
    CHAIN_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHAIN_MD_PATH.write_text(_receipt_markdown(receipt), encoding="utf-8")
    logging.info("temporal_coherence_chain_completed final_chain_status=%s", receipt["final_chain_status"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
