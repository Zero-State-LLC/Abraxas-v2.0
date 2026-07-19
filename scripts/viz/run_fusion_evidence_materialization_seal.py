from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.json import canonical_hash, write_canonical_json

OUT_PATH = Path("out/audit/fusion_evidence_materialization_seal_001.latest.json")


def build_receipt() -> dict[str, Any]:
    packet: dict[str, Any] = {
        "schema_version": "FusionEvidenceMaterializationSealReceipt.v1",
        "seal_id": "fusion_evidence_materialization_seal_001",
        "status": "SEALED",
        "classification": "BLOCKER_FREE_ADVISORY_FUSION",
        "run_count": 12,
        "summary_hash": "32691a04eb6cf8bfcb9df1c6cc301364026e93f3a2e11b78c6d6a7277d203f8e",
        "artifact_hashes": {
            "temporal_state_diff_pulse_ledger": "fc05c29510a75ed8ea0ed0e55725d0b3f6939cce0c340d587c75cdf6a87845e9",
            "temporal_lineage_pulse_ledger": "9a8697c4901a7b1dda8020ee90acdc98a56986e800b29a25903efc4f91e567c9",
            "cross_run_topology_fusion": "f0c1f8e09d2554910c4bf000c9887eb7568773614c0f1430f9ab3f3bc69f2a42",
        },
        "final_fusion_status": "ADVISORY_ONLY",
        "remaining_blockers": [],
        "authority_invariants": {
            "advisory_only": True,
            "projection_only": True,
            "authority_granted": False,
            "forecast_authority": False,
            "mutation_allowed": False,
        },
        "tests_run": [
            "python scripts/viz/run_fusion_evidence_materialization.py",
            "python scripts/run_fast_ci.py",
            "python -m pytest -q tests/test_fusion_evidence_materialization.py tests/test_temporal_state_diff_pulse_ledger.py tests/test_temporal_lineage_pulse_ledger.py tests/test_cross_run_topology_fusion.py",
            "python -m ruff check .",
            "pyright",
        ],
        "remaining_risks": [
            "local fixture cadence may require future extension if upstream topology surfaces expand",
            "seal receipt encodes audited hashes and must be regenerated if audited artifacts intentionally change",
        ],
        "recommended_next_lane": "P103_SEAL_RECURSIVE_AUTHORIZATION_CHAIN",
        "advisory_only": True,
        "projection_only": True,
        "authority_granted": False,
        "forecast_authority": False,
        "mutation_allowed": False,
    }
    packet["receipt_hash"] = canonical_hash(packet)
    return packet


def _build_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Fusion Evidence Materialization Seal Receipt",
        "",
        f"- seal_id: `{packet['seal_id']}`",
        f"- status: `{packet['status']}`",
        f"- classification: `{packet['classification']}`",
        f"- run_count: `{packet['run_count']}`",
        f"- summary_hash: `{packet['summary_hash']}`",
        f"- final_fusion_status: `{packet['final_fusion_status']}`",
        f"- remaining_blockers: `{packet['remaining_blockers']}`",
        f"- receipt_hash: `{packet['receipt_hash']}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    packet = build_receipt()
    write_canonical_json(OUT_PATH, packet)
    OUT_PATH.with_suffix(".md").write_text(_build_markdown(packet), encoding="utf-8")
    print(json.dumps({"status": packet["status"], "receipt_hash": packet["receipt_hash"]}, sort_keys=True))


if __name__ == "__main__":
    main()
