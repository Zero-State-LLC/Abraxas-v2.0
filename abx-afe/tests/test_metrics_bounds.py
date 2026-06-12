from __future__ import annotations

from afe.models import AFEInteractionEvent
from afe.metrics import compute_metrics


def test_metrics_remain_bounded() -> None:
    metrics = compute_metrics(
        (
            AFEInteractionEvent("e1", "a", "b", "x", 2.0, 2.0, 2.0),
            AFEInteractionEvent("e2", "a", "b", "x", -1.0, -1.0, -1.0),
        )
    )

    assert all(0.0 <= value <= 1.0 for value in metrics.__dict__.values())

