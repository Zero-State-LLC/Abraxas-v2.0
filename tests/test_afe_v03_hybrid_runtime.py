from __future__ import annotations

# pyright: reportMissingImports=false

import sys
from pathlib import Path

AFE_ROOT = Path(__file__).resolve().parents[1] / "abx-afe"
sys.path.insert(0, str(AFE_ROOT))
sys.path.insert(0, str(AFE_ROOT / "scripts"))

from afe.batch import build_hybrid_batch  # noqa: E402
from run_hybrid_cycle import run, validate_hybrid_batch  # noqa: E402


def test_afe_v03_hybrid_runtime_schema_and_payload(tmp_path: Path) -> None:
    out_path = tmp_path / "hybrid.json"
    packet = run(
        batch_id="AFE-BATCH-001",
        runs=3,
        seed_start=42,
        environment_set="baseline,scarcity,high-noise",
        export_target="notion",
        out_path=out_path,
    )

    assert out_path.exists()
    assert packet["artifact_type"] == "AFEHybridBatch.v1"
    assert packet["authority"] == "SHADOW_ONLY_TRACE"
    assert packet["live_notion_writeback"] is False
    assert len(packet["agent_trace_intake_export"]["trace_packets"]) == 3
    assert len(packet["notion_payload_rows"]) == 3
    validate_hybrid_batch(packet)


def test_afe_v03_hybrid_runtime_is_deterministic() -> None:
    first = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=3,
        seed_start=42,
        environment_set=("baseline", "scarcity", "high-noise"),
        export_target="notion",
    )
    second = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=3,
        seed_start=42,
        environment_set=("baseline", "scarcity", "high-noise"),
        export_target="notion",
    )

    assert first == second
    assert first["non_limitation_locks"]["mutate_canon"] is False
