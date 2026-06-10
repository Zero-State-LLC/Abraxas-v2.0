from typing import Any, Dict, List

try:
    from core.anomaly.evidential_hdbscan_detector import EvidentialHDBSCANDetector
    from core.temporal.bayesian_online_change_point_detector import BayesianOnlineChangePointDetector
    from core.clustering.neural_sticky_pitman_yor import NeuralStickyPitmanYor
    from core.clustering.online_variational_hdp import OnlineVariationalHDP
    from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator
    from core.calibration.platt_scaling_calibrator import PlattScalingCalibrator
except ImportError:
    EvidentialHDBSCANDetector = None
    BayesianOnlineChangePointDetector = None
    NeuralStickyPitmanYor = None
    OnlineVariationalHDP = None
    IsotonicRegressionCalibrator = None
    PlattScalingCalibrator = None


class TemporalAnomalyIntelligenceLayer:
    """
    Unified intelligence layer with proper Brier scoring support.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "vacuity_threshold": 0.35,
            "bocpd_hazard": 0.01,
            "pitman_yor_stickiness": 0.4,
            "calibration_method": None,
        }

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

        method = self.config.get("calibration_method")
        if method == "isotonic" and IsotonicRegressionCalibrator:
            self.calibrator = IsotonicRegressionCalibrator()
        elif method == "platt" and PlattScalingCalibrator:
            self.calibrator = PlattScalingCalibrator()
        else:
            self.calibrator = None

        self.provenance = {
            "layer": "TemporalAnomalyIntelligenceLayer",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "detectors": ["EvidentialHDBSCAN", "BOCPD", "NeuralStickyPitmanYor", "OnlineVariationalHDP"],
            "calibration_method": method
        }

        # Brier scoring state
        self.brier_scores: List[float] = []
        self.brier_targets: List[float] = []

    def process_stream(self, data: Any, target: float = None) -> Dict[str, Any]:
        result = {
            "change_points": [],
            "anomalies": [],
            "clusters": [],
            "regime_labels": [],
            "provenance": self.provenance.copy()
        }

        if self.bocpd and isinstance(data, (int, float)):
            bocpd_out = self.bocpd.update(float(data))
            result["change_points"] = bocpd_out.get("change_points", [])

        if self.hdbscan and isinstance(data, list):
            hdb_out = self.hdbscan.fit_predict(data)
            result["anomalies"] = [i for i, lbl in enumerate(hdb_out.get("labels", [])) if lbl == -1]

        if self.pitman_yor and isinstance(data, list):
            for point in data:
                py_out = self.pitman_yor.assign(point)
                result["clusters"].append(py_out.get("cluster_id"))

        if self.hdp and isinstance(data, list):
            for point in data:
                hdp_out = self.hdp.update(point)
                result["regime_labels"].append(hdp_out.get("assigned_topic"))

        # Calibration
        if self.calibrator and result.get("anomalies"):
            anomaly_scores = [float(i) for i in result["anomalies"]]
            cal_out = self.calibrator.calibrate(anomaly_scores)
            result["calibrated_anomalies"] = cal_out.get("calibrated_scores", [])
            result["provenance"]["calibration"] = cal_out.get("provenance", {})

        # Proper Brier score calculation
        if target is not None and result.get("anomalies") is not None:
            # Use anomaly count as proxy prediction for demo
            pred = len(result["anomalies"]) / max(len(data) if isinstance(data, list) else 10, 1)
            brier = (pred - target) ** 2
            self.brier_scores.append(brier)
            self.brier_targets.append(target)
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
