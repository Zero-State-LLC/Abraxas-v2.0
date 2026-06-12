from __future__ import annotations

from afe.models import AFEInteractionEvent, AFEMetricFrame


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 6)))


def compute_metrics(events: tuple[AFEInteractionEvent, ...]) -> AFEMetricFrame:
    if not events:
        return AFEMetricFrame(ACS=0.0, MDI=0.0, SES=0.0, SLI=0.0, ECI=0.0)

    count = float(len(events))
    cooperation = sum(event.cooperation for event in events) / count
    manipulation = sum(event.manipulation for event in events) / count
    drift = sum(event.drift for event in events) / count
    stability = 1.0 - ((manipulation + drift) / 2.0)
    loop_integrity = (cooperation + stability) / 2.0
    emergent_constraint = cooperation * stability
    return AFEMetricFrame(
        ACS=_clamp(cooperation),
        MDI=_clamp(manipulation),
        SES=_clamp(stability),
        SLI=_clamp(loop_integrity),
        ECI=_clamp(emergent_constraint),
    )

