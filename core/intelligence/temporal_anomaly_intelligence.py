from typing import Any, Dict, List, Optional, Type

# Detectors
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

# Calibration strategies
try:
    from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator
    from core.calibration.platt_scaling_calibrator import PlattScalingCalibrator
    from core.calibration.beta_calibrator import BetaCalibrator
except ImportError:
    IsotonicRegressionCalibrator = None
    PlattScalingCalibrator = None
    BetaCalibrator = None


# ============================================================
# Calibration Strategy Registry (for easy extension)
# ============================================================
CALIBRATION_REGISTRY: Dict[str, Type] = {
    "isotonic": IsotonicRegressionCalibrator,
    "platt": PlattScalingCalibrator,
    "beta": BetaCalibrator,
}


class TemporalAnomalyIntelligenceLayer:
    """
    Modular unified intelligence layer.
    - Detectors are initialized based on config
    - Calibration is pluggable via registry
    - Clear separation of concerns
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._init_detectors()
        self._init_calibrator()
        self._build_provenance()

        # Brier state
        self.brier_scores: List[float] = []

    def _init_detectors(self):
        self.hdbscan = EvidentialHDBSCANDetector(
            vacuity_threshold=self.config.get("vacuity_threshold", 0.35)
        ) if EvidentialHDBSCANDetector else None

        self.bocpd = BayesianOnlineChangePointDetector(
            hazard=self.config.get("bocpd_hazard", 0.01)
        ) if BayesianOnlineChangePointDetector else None

        self.pitman_yor = NeuralStickyPitmanYor(
            stickiness=self.config.get("pitman_yor_stickiness", 0.4)
        ) if NeuralStickyPitmanYor else None

        self.hdp = OnlineVariationalHDP() if OnlineVariationalHDP else None

    def _init_calibrator(self):
        method = self.config.get("calibration_method")
        calibrator_cls = CALIBRATION_REGISTRY.get(method) if method else None
        self.calibrator = calibrator_cls() if calibrator_cls else None

    def _build_provenance(self):
        self.provenance = {
            "layer": "TemporalAnomalyIntelligenceLayer",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "detectors": ["EvidentialHDBSCAN", "BOCPD", "NeuralStickyPitmanYor", "OnlineVariationalHDP"],
            "calibration_method": self.config.get("calibration_method")
        }

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process_stream(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "change_points": [],
            "anomalies": [],
            "clusters": [],
            "regime_labels": [],
            "provenance": self.provenance.copy()
        }

        # Run detectors
        if self.bocpd and isinstance(data, (int, float)):
            out = self.bocpd.update(float(data))
            result["change_points"] = out.get("change_points", [])

        if self.hdbscan and isinstance(data, list):
            out = self.hdbscan.fit_predict(data)
            result["anomalies"] = [i for i, lbl in enumerate(out.get("labels", [])) if lbl == -1]

        if self.pitman_yor and isinstance(data, list):
            for point in data:
                out = self.pitman_yor.assign(point)
                result["clusters"].append(out.get("cluster_id"))

        if self.hdp and isinstance(data, list):
            for point in data:
                out = self.hdp.update(point)
                result["regime_labels"].append(out.get("assigned_topic"))

        # Apply calibration if available
        if self.calibrator and result.get("anomalies"):
            scores = [float(i) for i in result["anomalies"]]
            cal_out = self.calibrator.calibrate(scores)
            result["calibrated_anomalies"] = cal_out.get("calibrated_scores", [])
            result["provenance"]["calibration"] = cal_out.get("provenance", {})

        # Brier scoring
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
    def available_calibration_methods() -> List[str]:
        return list(CALIBRATION_REGISTRY.keys())
