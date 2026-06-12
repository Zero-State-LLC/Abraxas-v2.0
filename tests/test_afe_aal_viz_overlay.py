from __future__ import annotations

# pyright: reportMissingImports=false

import sys
from pathlib import Path

AFE_ROOT = Path(__file__).resolve().parents[1] / "abx-afe"
sys.path.insert(0, str(AFE_ROOT))
sys.path.insert(0, str(AFE_ROOT / "scripts"))

from run_aal_viz_overlay import run, validate_aal_viz_overlay  # noqa: E402


def test_afe_aal_viz_overlay_runner_writes_projection_packet(tmp_path: Path) -> None:
    out_path = tmp_path / "aal_viz_overlay.json"
    packet = run(out_path)

    assert out_path.exists()
    assert packet["artifact_type"] == "AFEAALVizOverlayPacket.v1"
    assert packet["output_effect"] == "VISUAL_ANNOTATION_ONLY"
    assert packet["rendering_locks"]["hide_nodes"] is False
    assert packet["rendering_locks"]["auto_filter_high_risk_data"] is False
    validate_aal_viz_overlay(packet)
