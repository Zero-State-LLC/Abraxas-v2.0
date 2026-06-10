from typing import Any, Dict, List, Optional

try:
    from core.intelligence.base_classes import BaseDetector, BaseCalibrator
    from core.intelligence.detector_registry import get_detector, list_available_detectors
    from core.intelligence.provenance import build_layer_provenance
    from core.intelligence.brier_scorer import BrierScorer
    from core.intelligence.config import IntelligenceLayerConfig
    from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator
    from core.calibration.platt_scaling_calibrator import PlattScalingCalibrator
    from core.calibration.beta_calibrator import BetaCalibrator
except ImportError:
    BaseDetector = None
    BaseCalibrator = None
    get_detector = None
    list_available_detectors = None
    build_layer_provenance = None
    BrierScorer = None
    IntelligenceLayerConfig = None
    IsotonicRegressionCalibrator = None
    PlattScalingCalibrator = None
    BetaCalibrator = None


CALIBRATION_REGISTRY = {
    "isotonic": IsotonicRegressionCalibrator,
    "platt": PlattScalingCalibrator,
    "beta": BetaCalibrator,
}


def get_calibrator(method: str):
    """Factory for calibration strategies."""
    cls = CALIBRATION_REGISTRY.get(method)
    return cls() if cls else None


class TemporalAnomalyIntelligenceLayer:
    """
    Modular, extensible intelligence layer for temporal regime detection
    and evidential anomaly clustering.

    Features:
    - Pluggable detectors via DetectorRegistry
    - Multiple calibration methods (isotonic, platt, beta)
    - Structured configuration via IntelligenceLayerConfig
    - Dedicated Brier scoring component
    - Centralized provenance tracking

    Example:
        layer = TemporalAnomalyIntelligenceLayer(config={
            "calibration_method": "beta",
            "vacuity_threshold": 0.4
        })

        result = layer.process_stream([0.2, 0.8, 0.5], target=0.3)
        print(result["brier_summary"])
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if IntelligenceLayerConfig and isinstance(config, dict):
            self.config_obj = IntelligenceLayerConfig.from_dict(config)
            self.config = self.config_obj.to_dict()
        else:
            self.config_obj = None
            self.config = config or {}

        self.detectors = self._build_detectors()
        self.calibrator = get_calibrator(self.config.get("calibration_method"))
        self.brier_scorer = BrierScorer() if BrierScorer else None
        self.provenance = self._build_provenance()

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
        if build_layer_provenance is None:
            return {"layer": "TemporalAnomalyIntelligenceLayer"}
        return build_layer_provenance(
            detectors=list(self.detectors.keys()),
            calibration_method=self.config.get("calibration_method"),
            extra={"available_detectors": list_available_detectors() if list_available_detectors else []}
        )

    def process_stream(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        """
        Process a data stream through detectors + optional calibration.

        Args:
            data: Input data (list for clustering/anomaly, float for BOCPD)
            target: Optional ground truth for Brier scoring

        Returns:
            Dictionary with change_points, anomalies, clusters, regime_labels,
            calibrated_anomalies (if enabled), brier_score, and provenance.
        """
        result: Dict[str, Any] = {
            "change_points": [],
            "anomalies": [],
            "clusters": [],
            "regime_labels": [],
            "provenance": self.provenance.copy()
        }

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

        if self.calibrator and result.get("anomalies"):
            scores = [float(i) for i in result["anomalies"]]
            cal_out = self.calibrator.calibrate(scores)
            result["calibrated_anomalies"] = cal_out.get("calibrated_scores", [])
            result["provenance"]["calibration"] = cal_out.get("provenance", {})

        if target is not None and result.get("anomalies") is not None and self.brier_scorer:
            n = len(data) if isinstance(data, list) else 10
            pred = len(result["anomalies"]) / max(n, 1)
            brier = self.brier_scorer.update(pred, target)
            result["brier_score"] = brier
            result["brier_summary"] = self.brier_scorer.get_summary()

        return result

    def get_brier_summary(self) -> Dict[str, Any]:
        if self.brier_scorer:
            return self.brier_scorer.get_summary()
        return {"status": "no_brier_scorer"}

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "config": self.config,
            "brier_summary": self.get_brier_summary(),
            "provenance": self.provenance
        }

    @staticmethod
    def available_calibration_methods() -> list:
        """Returns list of supported calibration methods."""
        return list(CALIBRATION_REGISTRY.keys())
