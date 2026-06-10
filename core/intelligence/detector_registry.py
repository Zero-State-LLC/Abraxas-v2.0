from typing import Any, Dict, Optional, Type

# Detector imports
try:
    from core.anomaly.evidential_hdbscan_detector import EvidentialHDBSCANDetector
    from core.temporal.bayesian_online_change_point_detector import BayesianOnlineChangePointDetector
    from core.clustering.neural_sticky_pitman_yor import NeuralStickyPitmanYor
    from core.clustering.online_variational_hdp import OnlineVariationalHDP
except ImportError:
    EvidentialHDBSCANDetector = None
    BayesianOnlineChangePointDetector = None
    NeuralStickyPitmanYor = None
    OnlineVariationalHDP = None


DETECTOR_REGISTRY: Dict[str, Optional[Type]] = {
    "hdbscan": EvidentialHDBSCANDetector,
    "bocpd": BayesianOnlineChangePointDetector,
    "pitman_yor": NeuralStickyPitmanYor,
    "hdp": OnlineVariationalHDP,
}


def get_detector(name: str, config: Optional[Dict[str, Any]] = None):
    """
    Factory function to get a detector instance by name.
    """
    cls = DETECTOR_REGISTRY.get(name)
    if cls is None:
        return None
    config = config or {}
    if name == "hdbscan":
        return cls(vacuity_threshold=config.get("vacuity_threshold", 0.35))
    elif name == "bocpd":
        return cls(hazard=config.get("bocpd_hazard", 0.01))
    elif name == "pitman_yor":
        return cls(stickiness=config.get("pitman_yor_stickiness", 0.4))
    else:
        return cls()


def list_available_detectors() -> list:
    return [k for k, v in DETECTOR_REGISTRY.items() if v is not None]
