"""SHADOW kernel: Neon cycle → envelope → familiar ingest → spine → oracle/belief.

Does not write Oracle queues, mutate BeliefGraph, train a ranker, or grant forecast.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import neon_genie_ingest
import neon_genie_router as router
from core.ingest.familiar_ingestion_receipt import build_familiar_ingestion_receipt
from core.signal.evidence_pack import validate_evidence_pack
from core.signal.familiar_oracle_belief_bridge import build_familiar_oracle_belief_bridge
from core.signal.spine_bridge import build_familiar_spine_touchpoint

SCHEMA_VERSION = "NeonGenieKernelRun.v1"
_DENIED = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_shadow_kernel(
    request: Dict[str, Any],
    *,
    request_id: str = "neon-genie-kernel",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or _repo_root()
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    cycle = router.run_venture_cycle(request)
    envelope = neon_genie_ingest.from_cycle(cycle, request, request_id=request_id)
    pack = envelope["evidence_pack"]
    errors = validate_evidence_pack(pack, repo_root=root)
    receipt = build_familiar_ingestion_receipt(
        pack,
        pack_ref=f"neon:{envelope.get('envelope_id')}",
        repo_root=root,
    )
    touchpoint = build_familiar_spine_touchpoint(receipt)
    bridge = build_familiar_oracle_belief_bridge(touchpoint)
    return {
        "schema_version": SCHEMA_VERSION,
        "lane": "SHADOW",
        "invention_router_id": "neon-genie",
        "not_a_specialist_model": True,
        "cycle": cycle,
        "envelope": envelope,
        "pack_validation_errors": errors,
        "ingestion_receipt": receipt,
        "spine_touchpoint": touchpoint,
        "oracle_belief_bridge": bridge,
        "authority": dict(_DENIED),
        "advisory_only": True,
    }
