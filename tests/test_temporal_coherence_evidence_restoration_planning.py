from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from core.canonical.json import canonical_hash
from core.temporal_coherence_evidence_restoration_planning import (
    DEFAULT_OUT_PATH,
    STATUS,
    build_temporal_coherence_evidence_restoration_planning,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _assert_canonical_hash(packet: dict[str, object]) -> None:
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("canonical_hash")
    assert packet_hash == canonical_hash(packet_without_hash)


def test_slice49_temporal_coherence_restoration_packet_is_advisory_only() -> None:
    packet = build_temporal_coherence_evidence_restoration_planning(
        repo_root=REPO_ROOT
    )
    _assert_canonical_hash(packet)
    assert packet["status"] == STATUS
    assert packet["brier_score"] == 0.1
    assert "out/audit/temporal_coherence_chain_001.latest.json" in packet[
        "missing_target_evidence_paths"
    ]
    assert packet["sandbox_gate_status"]["phrase_issued_by_this_slice"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_slice49_runner_emits_stable_receipt() -> None:
    result = subprocess.run(
        [sys.executable, "Scripts/run_temporal_coherence_evidence_restoration_planning.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert STATUS in result.stdout
    receipt_path = REPO_ROOT / DEFAULT_OUT_PATH
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    _assert_canonical_hash(receipt)
    assert receipt["status"] == STATUS
