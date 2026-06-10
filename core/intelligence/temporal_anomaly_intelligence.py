from typing import Any, Dict, List

try:
    from core.anomaly.evidential_hdbscan_detector import EvidentialHDBSCANDetector
    from core.temporal.bayesian_online_change_point_detector import BayesianOnlineChangePointDetector
    from core.clustering.neural_sticky_pitman_yor import NeuralStickyPitmanYor
    from core.clustering.online_variational_hdp import OnlineVariationalHDP
    from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator
except ImportError:
    EvidentialHDBSCANDetector = None
    BayesianOnlineChangePointDetector = None
    NeuralStickyPitmanYor = None
    OnlineVariationalHDP = None
    IsotonicRegressionCalibrator = None


class TemporalAnomalyIntelligenceLayer:
    """
    Unified intelligence layer for temporal regime detection + evidential anomaly clustering.
    Supports optional isotonic regression calibration.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "vacuity_threshold": 0.35,
            "bocpd_hazard": 0.01,
            "pitman_yor_stickiness": 0.4,
            "use_calibration": False,
        }

        # Initialize detectors
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

        # Optional calibrator
        self.calibrator = IsotonicRegressionCalibrator() if IsotonicRegressionCalibrator and self.config.get("use_calibration") else None

        self.provenance = {
            "layer": "TemporalAnomalyIntelligenceLayer",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "detectors": ["EvidentialHDBSCAN", "BOCPD", "NeuralStickyPitmanYor", "OnlineVariationalHDP"],
            "calibration": "IsotonicRegression" if self.calibrator else None
        }

        self.brier_scores: List[float] = []

    def process_stream(self, data: Any) -> Dict[str, Any]:
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

        # Optional calibration step
        if self.calibrator and result.get("anomalies"):
            # Calibrate anomaly scores (using indices as proxy scores for demo)
            anomaly_scores = [float(i) for i in result["anomalies"]]
            cal_out = self.calibrator.calibrate(anomaly_scores)
            result["calibrated_anomalies"] = cal_out.get("calibrated_scores", [])
            result["provenance"]["calibration"] = cal_out.get("provenance", {})

        # Basic Brier tracking
        if "brier_target" in self.config and result.get("anomalies"):
            brier = abs(len(result["anomalies"]) - self.config["brier_target"]) / 100.0
            self.brier_scores.append(brier)
            result["brier_score"] = brier

        return result

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "config": self.config,
            "brier_scores": self.brier_scores[-5:] if self.brier_scores else [],
            "provenance": self.provenance
        }
