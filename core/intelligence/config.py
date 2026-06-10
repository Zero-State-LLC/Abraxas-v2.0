from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


@dataclass
class IntelligenceLayerConfig:
    """
    Structured and validated configuration for the intelligence layer.
    """

    vacuity_threshold: float = 0.35
    bocpd_hazard: float = 0.01
    pitman_yor_stickiness: float = 0.4
    calibration_method: Optional[str] = None
    brier_target: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    # Allowed values
    ALLOWED_CALIBRATION_METHODS: List[str] = field(default_factory=lambda: ["isotonic", "platt", "beta", "dirichlet"])

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not (0.0 <= self.vacuity_threshold <= 1.0):
            raise ValueError("vacuity_threshold must be between 0.0 and 1.0")

        if not (0.0 < self.bocpd_hazard < 1.0):
            raise ValueError("bocpd_hazard must be between 0 and 1 (exclusive)")

        if not (0.0 <= self.pitman_yor_stickiness <= 1.0):
            raise ValueError("pitman_yor_stickiness must be between 0.0 and 1.0")

        if self.calibration_method is not None:
            if self.calibration_method not in self.ALLOWED_CALIBRATION_METHODS:
                raise ValueError(
                    f"calibration_method must be one of {self.ALLOWED_CALIBRATION_METHODS}, "
                    f"got '{self.calibration_method}'"
                )

        if self.brier_target is not None and not (0.0 <= self.brier_target <= 1.0):
            raise ValueError("brier_target must be between 0.0 and 1.0 or None")

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
