from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class IntelligenceLayerConfig:
    """
    Structured configuration for TemporalAnomalyIntelligenceLayer.
    Makes initialization cleaner and more explicit.
    """

    vacuity_threshold: float = 0.35
    bocpd_hazard: float = 0.01
    pitman_yor_stickiness: float = 0.4
    calibration_method: Optional[str] = None  # 'isotonic', 'platt', 'beta', or None
    brier_target: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vacuity_threshold": self.vacuity_threshold,
            "bocpd_hazard": self.bocpd_hazard,
            "pitman_yor_stickiness": self.pitman_yor_stickiness,
            "calibration_method": self.calibration_method,
            "brier_target": self.brier_target,
            **self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntelligenceLayerConfig":
        return cls(
            vacuity_threshold=data.get("vacuity_threshold", 0.35),
            bocpd_hazard=data.get("bocpd_hazard", 0.01),
            pitman_yor_stickiness=data.get("pitman_yor_stickiness", 0.4),
            calibration_method=data.get("calibration_method"),
            brier_target=data.get("brier_target"),
            extra={k: v for k, v in data.items() if k not in [
                "vacuity_threshold", "bocpd_hazard", "pitman_yor_stickiness",
                "calibration_method", "brier_target"
            ]}
        )
