from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseDetector(ABC):
    """
    Abstract base class for all detectors in the intelligence layer.
    """

    @abstractmethod
    def update(self, data: Any) -> Dict[str, Any]:
        pass

    def get_provenance(self) -> Dict[str, Any]:
        return getattr(self, "provenance", {})


class BaseCalibrator(ABC):
    """
    Abstract base class for all calibrators.
    """

    @abstractmethod
    def fit(self, scores: List[float], targets: List[float]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def predict(self, scores: List[float]) -> List[float]:
        pass

    def calibrate(self, scores: List[float]) -> Dict[str, Any]:
        calibrated = self.predict(scores)
        return {
            "calibrated_scores": calibrated,
            "provenance": getattr(self, "provenance", {})
        }

    def get_status(self) -> Dict[str, Any]:
        return getattr(self, "provenance", {})
