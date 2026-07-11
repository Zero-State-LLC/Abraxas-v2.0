#!/usr/bin/env python3
"""
Direct runner for abx-esoteric-intelligence (SHADOW_SYMBOLIC advisory).

Thin orchestrator. Supports analytical, divinatory, and ALife adapter modes.
Delegates to thin alife_adapter (pure functions) for handoff to existing ALife runtime.
Never duplicates ALife lifecycle logic.
"""

from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_alife_adapter():
    """Robustly load alife_adapter.py by path (handles hyphenated dir names)."""
    _repo_root = Path(__file__).resolve().parent.parent
    adapter_file = _repo_root / "skills" / "abx-esoteric-intelligence" / "alife_adapter.py"
    if not adapter_file.exists():
        return False, None, {}
    try:
        spec = importlib.util.spec_from_file_location("alife_adapter", adapter_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        build_fn = getattr(mod, "build_alife_packet", None)
        builders = getattr(mod, "ALIFE_MODE_BUILDERS", {})
        if build_fn and builders:
            return True, build_fn, builders
    except Exception:
        pass
    return False, None, {}


_HAS_ALIFE_ADAPTER, build_alife_packet, ALIFE_MODE_BUILDERS = _load_alife_adapter()


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: python scripts/run_abx_esoteric_intelligence.py "
            "--mode <analytical_symbolic|divinatory_render|organismize|archetype_lineage|"
            "sigil_genotype|population_model|metabolism|synchronicity_ecology> "
            "--input <text> [--output <file>]"
        )
        return 1

    mode = "analytical_symbolic"
    input_data = ""
    output_path = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--mode" and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--input" and i + 1 < len(sys.argv):
            input_data = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    request = {
        "schema_version": "ABX.EsotericAnalysisRequest.v1",
        "request_id": f"req-{hashlib.sha256((input_data + mode).encode()).hexdigest()[:12]}",
        "operation": mode,
        "mode": mode,
        "source_inputs": [{"text": input_data or "Sample symbolic structure"}],
        "selected_traditions": [],
        "selected_corpus_families": ["dream_unconscious_symbol", "modern_memetic_occulture"],
        "operator_context": {},
        "time_context": None,
        "deterministic_seed": None,
        "requested_outputs": ["motifs", "archetype_candidates"],
        "authority_request": "advisory",
        "provenance": {"source": "runner_demo"},
    }

    if mode in ALIFE_MODE_BUILDERS and _HAS_ALIFE_ADAPTER and build_alife_packet:
        # Delegate to thin pure adapter
        alife_obj = build_alife_packet(mode, input_data, request)
        result = {
            "request": request,
            "alife_packet": alife_obj,
            "handoff": f"RUNE.ESOTERIC.{mode.upper()} -> existing ALife",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill": "abx-esoteric-intelligence",
            "version": "0.2.0-alife-adapter",
        }
    elif mode == "organismize" and not _HAS_ALIFE_ADAPTER:
        # Minimal fallback (rare)
        text = input_data or "Sample"
        candidate = {
            "schema_version": "ABX.SymbolicOrganismCandidate.v1",
            "candidate_id": f"SYMORG-{hashlib.sha256(text.encode()).hexdigest()[:8].upper()}",
            "source_analysis_packet_id": request["request_id"],
            "organism_class": "SYMBOL",
            "genotype": {"provenance_hash": hashlib.sha256(text.encode()).hexdigest()[:16]},
            "phenotype": {"observed_expressions": [text[:80]]},
            "governance": {
                "lane": "SHADOW",
                "entity_assertion": False,
                "forecast_authority": False,
                "execution_authority": False,
            },
        }
        result = {
            "request": request,
            "symbolic_organism_candidate": candidate,
            "handoff": "RUNE.ESOTERIC.ORGANISMIZE -> existing ALife (fallback)",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill": "abx-esoteric-intelligence",
            "version": "0.2.0-fallback",
        }
    else:
        # Analytical / divinatory fallback
        packet = {
            "schema_version": "ABX.EsotericAnalysisPacket.v1",
            "packet_id": f"pkt-{hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:12]}",
            "request_id": request["request_id"],
            "mode": mode,
            "operation": request["operation"],
            "observed": {"motifs": ["door", "water", "guide"] if "door" in input_data.lower() else []},
            "computed": {},
            "traditional": {},
            "inferred": {},
            "symbolic_interpretation": {"threshold": "possible"},
            "alternatives": ["ordinary mechanism", "cultural recurrence"],
            "evidence": [{"claim_class": "OPERATOR_REPORTED", "evidence_class": "operator_input"}],
            "derivation_path": ["intake", "motif_extract"],
            "provenance": {
                "observed": ["operator_input"],
                "computed": [],
                "traditional": [],
                "inferred": [],
                "speculative": [],
            },
            "confidence": 0.55,
            "confidence_ceiling": 0.62,
            "drift_risk": "MEDIUM",
            "authority": {"truth": False, "forecast": False, "execution": False, "canon_mutation": False},
            "status": "COMPLETE",
        }
        result = {
            "request": request,
            "packet": packet,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill": "abx-esoteric-intelligence",
            "version": "0.1.0",
        }

    if output_path:
        Path(output_path).write_text(json.dumps(result, indent=2, sort_keys=True))
        print(f"Wrote {output_path}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
