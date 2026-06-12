from __future__ import annotations

# pyright: reportMissingImports=false

import sys
from pathlib import Path

AFE_ROOT = Path(__file__).resolve().parents[1] / "abx-afe"
sys.path.insert(0, str(AFE_ROOT))
sys.path.insert(0, str(AFE_ROOT / "scripts"))

from run_non_filtering_doctrine import run, validate_non_filtering_doctrine  # noqa: E402


def test_afe_non_filtering_doctrine_runner_writes_observation_packet(tmp_path: Path) -> None:
    out_path = tmp_path / "non_filtering_doctrine.json"
    packet = run(out_path)

    assert out_path.exists()
    assert packet["artifact_type"] == "AFENonFilteringObservationDoctrine.v1"
    assert packet["output_effect"] == "OBSERVATION_ONLY"
    assert packet["required_output_handling_pattern"]["metric_trigger_filters_output"] is False
    assert packet["forbidden_metric_effects"]["filter_output"] is False
    assert packet["forbidden_metric_effects"]["rewrite_output"] is False
    validate_non_filtering_doctrine(packet)
