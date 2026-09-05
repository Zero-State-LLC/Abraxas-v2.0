#!/usr/bin/env python3
"""
Thin governed runner for abx-noctis-dream-functions (SHADOW_SYMBOLIC).

This is the canonical entry point. It enforces all boundaries and
produces the delivery receipt.

It currently provides stubs/adapters. Real NOCTIS core functions
should be wired in via the runes/contracts when present.
"""

from __future__ import annotations
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.noctis.dream_operator_packet import (  # noqa: E402
    build_dream_operator_packet_from_input,
    extract_motifs,
    normalize_dream,
)


def compute_stable_id(dream_id: str | None, narrative: str, seed: str) -> str:
    base = (dream_id or "") + narrative + seed
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def build_delivery(
    mode: str,
    dream_input: dict[str, Any],
    motifs: list[dict[str, Any]],
) -> dict[str, Any]:
    dream_id = dream_input.get("dream_id") or compute_stable_id(
        None, dream_input.get("narrative_raw", ""), dream_input.get("seed", "0")
    )

    authority = {
        "lane": "SHADOW_SYMBOLIC",
        "non_governing": True,
        "memory_candidate_only": True,
        "forecast_authority": False,
        "medical_authority": False,
        "promotion_authority": False,
        "runtime_mutation_allowed": False,
    }

    registers = {
        "observed": [],
        "inferred": [f"motif_count={len(motifs)} (INFERRED from text)"],
        "speculative": [],
        "not_computable": [] if dream_input.get("narrative_raw") else ["empty narrative"],
    }

    artifacts = {
        "dream_packet_ref": f"dream_packet:{dream_id}",
        "analysis_ref": f"noctis_analysis:{dream_id}",
        "motif_packet_ref": f"motifs:{dream_id}" if motifs else None,
        "symbolic_graph_ref": None,
        "continuity_ref": None,
        "artifact_intent_ref": None,
        "probe_candidate_ref": None,
        "projection_ref": f"aal_viz:noctis:{dream_id}",
    }

    status = {
        "analysis_status": "STUB_EXECUTED" if dream_input.get("narrative_raw") else "NOT_COMPUTABLE",
        "validation_status": "NOT_RUN",
        "unresolved_conflicts": [],
        "unvalidated_surfaces": ["real_noctis_core_functions"] if True else [],
    }

    operator_packet = build_dream_operator_packet_from_input(
        dream_input,
        mode=mode,
        motifs=motifs,
    )

    delivery = {
        "schema_version": "NoctisDreamDelivery.v1",
        "mode": mode,
        "dream_id": dream_id,
        "source": dream_input.get("source", "UNKNOWN"),
        "privacy_tier": dream_input.get("privacy_tier", "PRIVATE"),
        "artifacts": artifacts,
        "registers": registers,
        "authority": authority,
        "operator_packet": operator_packet,
        "provenance": {
            "input_sha256": hashlib.sha256(
                json.dumps(dream_input, sort_keys=True).encode()
            ).hexdigest(),
            "runner_ref": "scripts/research/run_noctis_dream.py",
            "skill": "abx-noctis-dream-functions",
            "operator_packet_module": "core.noctis.dream_operator_packet",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "status": status,
    }
    return delivery


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="DreamInput JSON file")
    source.add_argument("--synthetic-fixture", action="store_true")
    parser.add_argument("--mode", default="HUMAN_DREAM")
    parser.add_argument("--output", type=Path, default=Path("/tmp/noctis_dream_delivery.json"))
    args = parser.parse_args()

    if args.input:
        dream_input = json.loads(args.input.read_text())
    else:
        # Minimal synthetic fixture for validation
        dream_input = {
            "schema_version": "DreamInput.v1",
            "dream_id": "synth_001",
            "source": "SYSTEM",
            "synthetic": True,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "privacy_tier": "PUBLIC_SYNTHETIC",
            "narrative_raw": "I was walking through a forest of glowing symbols that kept repeating the same phrase about continuity.",
            "narrative_normalized": "",
            "seed": "test-seed-42",
            "authority": {"lane": "SHADOW_SYMBOLIC"},
        }

    if args.synthetic_fixture:
        args.mode = "SYSTEM_DREAM"
    narrative = dream_input.get("narrative_raw", "")
    if not narrative or not narrative.strip():
        delivery = {"status": "NOT_COMPUTABLE", "reason": "empty narrative"}
        args.output.write_text(json.dumps(delivery, indent=2))
        print(json.dumps(delivery, indent=2))
        return 0

    normalized = normalize_dream(narrative)
    dream_input["narrative_normalized"] = normalized

    motifs = extract_motifs(normalized, dream_input.get("dream_id", "unknown"))

    delivery = build_delivery(args.mode, dream_input, motifs)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(delivery, indent=2, sort_keys=True))
    print(json.dumps(delivery, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
