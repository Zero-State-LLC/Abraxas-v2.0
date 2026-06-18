from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan import BLOCKED_ACTIONS
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionAuthorizationGate.v1"
GATE_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_001"
SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan_001.latest.json"
)
GATE_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate_001.latest.json"
)
GATE_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate_001.latest.md"
)
AUTHORIZATION_RECORD_LANE = (
    "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_001"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    spec_plan = _read_json(root / SPEC_PLAN_JSON_PATH)
    spec_plan_ready = (
        spec_plan.get("schema_version") == "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionSpecPlan.v1"
        and spec_plan.get("status") == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_READY"
        and spec_plan.get("registry_mutation_performed") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": GATE_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
            if spec_plan_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_BLOCKED"
        ),
        "authorization_gate_id": GATE_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authorization_gate_only": True,
        "source_spec_plan": {
            "path": str(SPEC_PLAN_JSON_PATH),
            "hash": str(spec_plan.get("spec_plan_hash", NOT_COMPUTABLE)),
            "status": str(spec_plan.get("status", NOT_COMPUTABLE)),
            "observed": spec_plan_ready,
        },
        "authorization_scope": "ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_ONLY",
        "operator_authorization_required": True,
        "operator_authorization_observed": False,
        "authorization_granted": False,
        "execution_authority": False,
        "registry_mutation_performed": False,
        "blocked_actions": list(dict.fromkeys([*spec_plan.get("blocked_actions", []), *BLOCKED_ACTIONS])),
        "recommended_next_lane": AUTHORIZATION_RECORD_LANE if spec_plan_ready else NOT_COMPUTABLE,
        "downstream_status": "READY_FOR_INCLUSION_EXECUTION_AUTHORIZATION_RECORD" if spec_plan_ready else NOT_COMPUTABLE,
    }
    return {**packet, "authorization_gate_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# ABX Research Canary Orphan Output Registry Inclusion Execution Authorization Gate 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
    ]


def write_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(root)
    write_canonical_json(target_root / GATE_JSON_PATH, packet)
    _write_markdown(target_root / GATE_MD_PATH, render_markdown(packet))
    return packet
