from __future__ import annotations

# pyright: reportMissingImports=false

import sys
from pathlib import Path

AFE_ROOT = Path(__file__).resolve().parents[1] / "abx-afe"
sys.path.insert(0, str(AFE_ROOT))
sys.path.insert(0, str(AFE_ROOT / "scripts"))

from run_oracle_annotation import run, validate_oracle_annotation  # noqa: E402


def test_afe_oracle_annotation_runner_writes_observation_panel(tmp_path: Path) -> None:
    out_path = tmp_path / "oracle_annotation.json"
    packet = run(out_path)
    observation = packet["annotation"]["afe_observation"]

    assert out_path.exists()
    assert observation["authority"] == "SHADOW_ONLY_TRACE"
    assert observation["output_effect"] == "ANNOTATION_ONLY"
    assert observation["non_filtering_compliance"] is True
    assert packet["attached_output"]["oracle_output"]["text"] == "Oracle output remains intact."
    validate_oracle_annotation(packet["annotation"])
