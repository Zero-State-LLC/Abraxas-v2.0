# core/shadow_map_generator_stub.py
# Advisory Shadow Map generator for rune_id exposure and related hygiene.
# Reads route graphs + optional binding hints; never writes routes.
# expansion_performed is always false.

from __future__ import annotations
from typing import Any, Dict, List, Mapping, Optional, Sequence
from datetime import datetime, timezone
import json

# High-confidence name heuristics (node_id fragment → rune_id)
_HEURISTICS: List[tuple[str, str]] = [
    ("parser", "RUNE.PIPELINE.PARSE"),
    ("ir_builder", "RUNE.PIPELINE.IR_BUILD"),
    ("validator", "RUNE.PIPELINE.VALIDATE"),
    ("conflict_scanner", "RUNE.PIPELINE.CONFLICT_SCAN"),
    ("canon_sync", "RUNE.PIPELINE.CANON_SYNC"),
    ("aal_viz_projector", "RUNE.PIPELINE.AAL_VIZ_PROJECT"),
    ("promotion_lock", "RUNE.GOVERNANCE.PROMOTION_LOCK"),
    ("mutation_lock", "RUNE.GOVERNANCE.RUNTIME_MUTATION_LOCK"),
    ("operator_review", "RUNE.PIPELINE.OPERATOR_REVIEW"),
    ("review", "RUNE.PIPELINE.OPERATOR_REVIEW"),
]


class ShadowMapGenerator:
    """Advisory stub: route graph → ShadowMap.v1 proposal. No writes."""

    VERSION = "0.1-advisory-stub"

    def __init__(self):
        self.execution_authority = False

    def generate_rune_id_map(
        self,
        route: Mapping[str, Any],
        map_id: Optional[str] = None,
        target_surface: Optional[str] = None,
    ) -> Dict[str, Any]:
        pipeline_id = route.get("pipeline_id", "unknown")
        nodes = route.get("nodes", [])
        entries: List[Dict[str, Any]] = []
        unmapped: List[str] = []

        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("node_id", ""))
            node_type = str(node.get("node_type", ""))
            existing = node.get("rune_id")

            # Only map rune or review_gate nodes missing rune_id
            if node_type not in ("rune", "review_gate"):
                continue
            if existing:
                continue

            proposed_id, confidence, rationale = self._infer(node_id, node_type)
            if proposed_id is None:
                unmapped.append(node_id)
                continue

            entries.append({
                "node_id": node_id,
                "node_type": node_type,
                "current": {"rune_id": None},
                "proposed": {"rune_id": proposed_id},
                "rationale": rationale,
                "confidence": confidence,
            })

        return {
            "schema_version": "ShadowMap.v1",
            "map_id": map_id or f"shadow-map-{pipeline_id}-rune-id-001",
            "target_surface": target_surface or f"contracts/yggdrasil/routes/{pipeline_id}.route.v1.json",
            "hygiene_kind": "RUNE_ID_EXPOSURE",
            "status": "PROPOSED",
            "net_catalog_delta": 0,
            "expansion_performed": False,
            "execution_authority": False,
            "entries": entries,
            "unmapped_nodes": unmapped,
            "operator_seal": None,
            "provenance": f"{self.VERSION} | shadow_map_generator_stub",
            "recommended_next": "OPERATOR_REVIEW",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _infer(self, node_id: str, node_type: str) -> tuple[Optional[str], str, str]:
        lower = node_id.lower()
        for fragment, rune_id in _HEURISTICS:
            if fragment in lower:
                return (
                    rune_id,
                    "HIGH",
                    f"Node id contains '{fragment}'; mapped to existing catalog rune",
                )
        return (
            None,
            "NOT_COMPUTABLE",
            "No high-confidence heuristic match; left unmapped",
        )


if __name__ == "__main__":
    sample = {
        "pipeline_id": "example",
        "nodes": [
            {"node_id": "ex.parser", "node_type": "rune", "lane": "SHADOW"},
            {"node_id": "ex.unknown", "node_type": "rune", "lane": "SHADOW"},
            {"node_id": "ex.trigger", "node_type": "pipeline", "lane": "SHADOW"},
        ],
    }
    gen = ShadowMapGenerator()
    print(json.dumps(gen.generate_rune_id_map(sample), indent=2))
