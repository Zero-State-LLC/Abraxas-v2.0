from typing import Any, Dict, List, Optional

try:
    from core.intelligence.detector_registry import get_detector, list_available_detectors
    from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator
    from core.calibration.platt_scaling_calibrator import PlattScalingCalibrator
    from core.calibration.beta_calibrator import BetaCalibrator
except ImportError:
    get_detector = None
    list_available_detectors = None
    IsotonicRegressionCalibrator = None
    PlattScalingCalibrator = None
    BetaCalibrator = None


CALIBRATION_REGISTRY = {
    "isotonic": IsotonicRegressionCalibrator,
    "platt": PlattScalingCalibrator,
    "beta": BetaCalibrator,
}


def get_calibrator(method: str):
    cls = CALIBRATION_REGISTRY.get(method)
    return cls() if cls else None


class TemporalAnomalyIntelligenceLayer:
    """
    Highly modular intelligence layer.
    Uses registries for detectors and calibration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.detectors = self._build_detectors()
        self.calibrator = get_calibrator(self.config.get("calibration_method"))
        self.provenance = self._build_provenance()
        self.brier_scores: List[float] = []

    def _build_detectors(self) -> Dict[str, Any]:
        if get_detector is None:
            return {}
        return {
            "hdbscan": get_detector("hdbscan", self.config),
            "bocpd": get_detector("bocpd", self.config),
            "pitman_yor": get_detector("pitman_yor", self.config),
            "hdp": get_detector("hdp", self.config),
        }

    def _build_provenance(self) -> Dict[str, Any]:
        return {
            "layer": "TemporalAnomalyIntelligenceLayer",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "detectors": list(self.detectors.keys()),
            "calibration_method": self.config.get("calibration_method"),
            "available_detectors": list_available_detectors() if list_available_detectors else [],
        }

    def process_stream(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "change_points": [],
            "anomalies": [],
            "clusters": [],
            "regime_labels": [],
            "provenance": self.provenance.copy()
        }

        # Detectors
        if self.detectors.get("bocpd") and isinstance(data, (int, float)):
            out = self.detectors["bocpd"].update(float(data))
            result["change_points"] = out.get("change_points", [])

        if self.detectors.get("hdbscan") and isinstance(data, list):
            out = self.detectors["hdbscan"].fit_predict(data)
            result["anomalies"] = [i for i, lbl in enumerate(out.get("labels", [])) if lbl == -1]

        if self.detectors.get("pitman_yor") and isinstance(data, list):
            for point in data:
                out = self.detectors["pitman_yor"].assign(point)
                result["clusters"].append(out.get("cluster_id"))

        if self.detectors.get("hdp") and isinstance(data, list):
            for point in data:
                out = self.detectors["hdp"].update(point)
                result["regime_labels"].append(out.get("assigned_topic"))

        # Calibration
        if self.calibrator and result.get("anomalies"):
            scores = [float(i) for i in result["anomalies"]]
            cal_out = self.calibrator.calibrate(scores)
            result["calibrated_anomalies"] = cal_out.get("calibrated_scores", [])
            result["provenance"]["calibration"] = cal_out.get("provenance", {})

        # Brier
        if target is not None and result.get("anomalies") is not None:
            n = len(data) if isinstance(data, list) else 10
            pred = len(result["anomalies"]) / max(n, 1)
            brier = (pred - target) ** 2
            self.brier_scores.append(brier)
            result["brier_score"] = brier
            result["brier_mean"] = sum(self.brier_scores) / len(self.brier_scores)

        return result

    def get_brier_summary(self) -> Dict[str, Any]:
        if not self.brier_scores:
            return {"status": "no_scores_yet"}
        return {
            "n_scores": len(self.brier_scores),
            "mean_brier": sum(self.brier_scores) / len(self.brier_scores),
            "latest_brier": self.brier_scores[-1],
            "min_brier": min(self.brier_scores),
            "max_brier": max(self.brier_scores),
            "provenance": self.provenance
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "config": self.config,
            "brier_summary": self.get_brier_summary(),
            "provenance": self.provenance
        }

    @staticmethod
    def available_calibration_methods() -> list:
        from core.intelligence.temporal_anomaly_intelligence import CALIBRATION_REGISTRY
        return list(CALIBRATION_REGISTRY.keys())
