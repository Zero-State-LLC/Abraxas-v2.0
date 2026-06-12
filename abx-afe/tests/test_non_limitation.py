from __future__ import annotations

from afe.trace import attach_observation_to_abraxas_output


def test_high_drift_observation_does_not_rewrite_abraxas_output() -> None:
    output = {"body": "raw Abraxas output", "forecast_weight": 0.5}
    trace = {
        "authority": "SHADOW_ONLY_TRACE",
        "metrics": {"MDI": 1.0, "SES": 0.0},
        "shadow_diagnostic_candidates": ["MANIPULATION_DRIFT_OBSERVED"],
    }

    attached = attach_observation_to_abraxas_output(output, trace)

    assert attached["abraxas_output"] == output
    assert attached["afe_observation"] == trace
    assert attached["non_filtering_observation_lock"] is True

