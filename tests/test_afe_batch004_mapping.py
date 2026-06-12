from __future__ import annotations

# pyright: reportMissingImports=false

import sys
from pathlib import Path

AFE_ROOT = Path(__file__).resolve().parents[1] / "abx-afe"
sys.path.insert(0, str(AFE_ROOT))
sys.path.insert(0, str(AFE_ROOT / "scripts"))

from run_batch004_mapping import run, validate_batch004_mapping  # noqa: E402


def test_afe_batch004_runner_writes_annotation_only_packet(tmp_path: Path) -> None:
    out_path = tmp_path / "batch004.json"
    packet = run(out_path)

    assert out_path.exists()
    assert packet["artifact_type"] == "AFERealWorldMappingBatch.v1"
    assert packet["authority"] == "SHADOW_ONLY_TRACE"
    assert packet["output_effect"] == "ANNOTATION_ONLY"
    assert packet["live_ingestion_performed"] is False
    assert packet["forbidden_effects"]["filter_output"] is False
    validate_batch004_mapping(packet)
