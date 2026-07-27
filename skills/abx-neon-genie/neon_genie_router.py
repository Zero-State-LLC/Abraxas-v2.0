"""Neon Genie Umbrella Router (thin coordinator).

Loads stage modules directly (importlib) to support both package and direct-runner execution.
Evidence: prefer EvidencePack.v0 via evidence_pack_path (abx-familiar-signal-forager).
"""

from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Resolve skill dir for direct loading of siblings
_THIS = Path(__file__).resolve()
_SKILL_DIR = _THIS.parent

def _load(name: str, filename: str):
    path = _SKILL_DIR / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load stages (direct)
_intake = _load("neon_genie_intake", "neon_genie_intake.py")
_discover = _load("neon_genie_discover", "neon_genie_discover.py")
_recombine = _load("neon_genie_recombine", "neon_genie_recombine.py")
_differentiate = _load("neon_genie_differentiate", "neon_genie_differentiate.py")
_score = _load("neon_genie_score", "neon_genie_score.py")
_shape = _load("neon_genie_shape", "neon_genie_shape.py")
_package = _load("neon_genie_package", "neon_genie_package.py")
_overlap = _load("overlap_registry", "overlap_registry.py")
_evidence = _load("neon_genie_evidence_pack", "evidence_pack.py")

def classify_mode(request: Dict[str, Any]) -> str:
    return request.get("mode", "PROMPT_LED").upper()

def require_evidence(mode: str, request: Dict[str, Any]) -> bool:
    evidence_modes = {"MARKET_LED", "TREND_LED", "PAINPOINT_LED", "MONETIZATION_LED"}
    return mode in evidence_modes or bool(request.get("require_evidence"))

def run_venture_cycle(request: Dict[str, Any]) -> Dict[str, Any]:
    mode = classify_mode(request)
    needs_evidence = require_evidence(mode, request)

    evidence_pack = _evidence.resolve_evidence_for_request(request, needs_evidence=needs_evidence)

    seeds = _intake.intake(request)
    opportunities = _discover.discover(seeds, evidence_pack)
    candidates = _recombine.recombine(opportunities)
    differentiated = _differentiate.differentiate(candidates)
    scored = _score.score(differentiated, evidence_pack)
    shaped = _shape.shape(scored)
    overlap = _overlap.classify_overlap(shaped)
    venture_packet = _package.package(shaped, overlap, evidence_pack, mode)

    receipt = {
        "schema_version": "NeonGenieRunReceipt.v0.1",
        "run_id": hashlib.sha256(json.dumps(request, sort_keys=True, default=str).encode()).hexdigest()[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_mode": mode,
        "evidence_status": evidence_pack.get("status", "UNKNOWN"),
        "evidence_pack_ref": evidence_pack.get("pack_ref"),
        "evidence_density": evidence_pack.get("evidence_density"),
        "commercial_claims_blocked": bool(evidence_pack.get("commercial_claims_blocked", True)),
        "overlap_classification": overlap.get("classification"),
        "venture_packet": venture_packet,
        "route_decision": {
            "primary_owner": overlap.get("recommended_route", "NeonGenie"),
            "specialist_skills": overlap.get("specialist_skills", []),
        },
        "provenance": {
            "runner": "skills/abx-neon-genie/neon_genie_router.py",
            "skill": "abx-neon-genie",
            "evidence_skill": "abx-familiar-signal-forager",
        },
        "authority": {
            "execution_authority": False,
            "promotion_authorized": False,
            "canon_mutation_allowed": False,
        },
        "status": "CYCLE_COMPLETE" if overlap.get("classification") != "NOT_COMPUTABLE" else "INCOMPLETE",
    }
    return receipt


if __name__ == "__main__":
    example = {"mode": "SYMBOLIC_LED", "seed": "forest of repeating symbols"}
    result = run_venture_cycle(example)
    print(json.dumps(result, indent=2, sort_keys=True)[:1200] + "...")
