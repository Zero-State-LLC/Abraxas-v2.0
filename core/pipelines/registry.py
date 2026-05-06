"""Pipeline registry for ABRAXAS v2.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_REGISTRY
from core.pipelines.models import PipelineContractV11


def load_pipeline_contract(path: str | Path) -> PipelineContractV11:
    """Load and validate a single pipeline contract from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return PipelineContractV11.model_validate(data)


def load_contracts(directory: str | Path) -> list[PipelineContractV11]:
    """Load all *.json pipeline contracts from *directory*."""
    contracts = []
    for p in sorted(Path(directory).glob("*.json")):
        contracts.append(load_pipeline_contract(p))
    return contracts


def build_registry(contracts: list[PipelineContractV11]) -> dict[str, Any]:
    """Build the global pipeline registry document from a list of contracts."""
    # Validate for duplicates first
    validate_registry_contracts(contracts)

    pipelines = [c.model_dump() for c in contracts]
    # Determine recommended state: all shadow-only lanes -> eligible, else repair
    all_ok = all(
        c.lane.value in ("SHADOW", "GOVERNANCE", "GOVERNANCE_SHADOW", "PROJECTION")
        for c in contracts
    )
    recommended = "eligible_for_shadow_stabilization" if all_ok else "repair"

    return {
        "schema_version": SCHEMA_VERSION_REGISTRY,
        "status": "shadow_candidate",
        "pipeline_count": len(contracts),
        "pipelines": pipelines,
        "authority": locked_authority(),
        "recommended_next_state": recommended,
    }


def validate_registry_contracts(contracts: list[PipelineContractV11]) -> None:
    """Raise ValueError on duplicate pipeline_id or trigger."""
    seen_ids: set[str] = set()
    seen_triggers: set[str] = set()
    for c in contracts:
        if c.pipeline_id in seen_ids:
            raise ValueError(f"Duplicate pipeline_id: {c.pipeline_id}")
        if c.trigger in seen_triggers:
            raise ValueError(f"Duplicate trigger: {c.trigger}")
        seen_ids.add(c.pipeline_id)
        seen_triggers.add(c.trigger)


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    """Validate the registry document structure; return the registry unchanged."""
    if registry.get("schema_version") != SCHEMA_VERSION_REGISTRY:
        raise ValueError("Invalid registry schema_version")
    if not isinstance(registry.get("pipelines"), list):
        raise ValueError("Registry missing pipelines list")
    return registry
