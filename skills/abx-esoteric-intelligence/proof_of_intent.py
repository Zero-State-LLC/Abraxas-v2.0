"""Public Proof-of-Intent surface for Abraxas ingest (Phase-0).

Uses Sigil-Forge commitment + Merkle helpers when the engine is on disk.
Never returns the commitment nonce. Never claims efficacy. Per-run salt means
sigil_root here is not a genotype identity — intent_digest is.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, Optional

import sigil_forge_bridge as bridge

_DENIED = {
    "forecast_authority": False,
    "canon_authority": False,
    "execution_authority": False,
}


def _skipped(reason: str) -> Dict[str, Any]:
    return {
        "sigil_root": None,
        "sigil_root_scope": None,
        "intent_commitment": None,
        "zk_provenance": {
            "schema_version": "ABX_ZK_PROVENANCE_V1",
            "status": "skipped",
            "proof": None,
            "circuit": None,
            "public_inputs": None,
            "note": reason,
            "authority": dict(_DENIED),
        },
    }


def _load_engine_module(name: str) -> Optional[Any]:
    for scripts in bridge.engine_script_dirs():
        path = scripts / f"{name}.py"
        if not path.is_file():
            continue
        s = str(scripts)
        if s not in sys.path:
            sys.path.insert(0, s)
        try:
            return __import__(name)
        except Exception:
            continue
    return None


def public_surface(
    *,
    normalized: str,
    digest: str,
    construction: str,
    engine: str,
) -> Dict[str, Any]:
    """Public PoI leaves only. Caller must not persist `normalized` on the envelope."""
    if engine != "sigil-forge" or construction == "NOT_COMPUTABLE":
        return _skipped(
            "Phase-0 skipped: engine not sigil-forge or construction NOT_COMPUTABLE. "
            "Not efficacy."
        )
    commitment_mod = _load_engine_module("commitment")
    root_mod = _load_engine_module("artifact_root")
    if commitment_mod is None or root_mod is None:
        return _skipped(
            "Phase-0 skipped: Sigil-Forge commitment/artifact_root helpers unavailable. "
            "Not efficacy."
        )
    record = commitment_mod.commit_intent(normalized)
    public = commitment_mod.public_commitment(record)
    del record  # nonce must not escape
    root_info = root_mod.build_sigil_root(
        {
            "intent_digest": digest,
            "intent_commitment": public["value"],
            "construction": construction,
        }
    )
    root = root_info["sigil_root"]
    return {
        "sigil_root": root,
        "sigil_root_scope": "public_genotype_leaves",
        "intent_commitment": public,
        "zk_provenance": {
            "schema_version": "ABX_ZK_PROVENANCE_V1",
            "status": "commitment",
            "proof": None,
            "circuit": None,
            "public_inputs": {
                "intent_digest": digest,
                "intent_commitment": public["value"],
                "sigil_root": root,
            },
            "note": (
                "Phase-0 public commitment over genotype leaves "
                "(digest + commitment + construction). "
                "Not a full forge-run root (no glyph/manifest). Not efficacy."
            ),
            "authority": dict(_DENIED),
        },
    }
