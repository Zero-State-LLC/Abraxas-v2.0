from typing import Any, Dict, List

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


class TemporalAnomalyIntelligenceLayer:
    """
    Unified intelligence layer for temporal regime detection + evidential anomaly clustering.
    Wires all four Sprint 5 detectors and provides combined output with provenance.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "vacuity_threshold": 0.35,
            "bocpd_hazard": 0.01,
            "pitman_yor_stickiness": 0.4,
        }

        # Initialize detectors (graceful fallback if modules missing)
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

        self.provenance = {
            "layer": "TemporalAnomalyIntelligenceLayer",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "detectors": ["EvidentialHDBSCAN", "BOCPD", "NeuralStickyPitmanYor", "OnlineVariationalHDP"]
        }

        # Basic Brier tracking
        self.brier_scores: List[float] = []

    def process_stream(self, data: Any) -> Dict[str, Any]:
        """
        Process data through all detectors and return combined intelligence result.
        """
        result = {
            "change_points": [],
            "anomalies": [],
            "clusters": [],
            "regime_labels": [],
            "provenance": self.provenance.copy()
        }

        # BOCPD (temporal regime detection)
        if self.bocpd and isinstance(data, (int, float)):
            bocpd_out = self.bocpd.update(float(data))
            result["change_points"] = bocpd_out.get("change_points", [])
            result["provenance"]["bocpd"] = bocpd_out.get("provenance", {})

        # HDBSCAN (evidential anomaly clustering)
        if self.hdbscan and isinstance(data, list):
            hdb_out = self.hdbscan.fit_predict(data)
            result["anomalies"] = [i for i, lbl in enumerate(hdb_out.get("labels", [])) if lbl == -1]
            result["provenance"]["hdbscan"] = hdb_out.get("provenance", {})

        # Pitman-Yor + HDP (clustering)
        if self.pitman_yor and isinstance(data, list):
            for point in data:
                py_out = self.pitman_yor.assign(point)
                result["clusters"].append(py_out.get("cluster_id"))

        if self.hdp and isinstance(data, list):
            for point in data:
                hdp_out = self.hdp.update(point)
                result["regime_labels"].append(hdp_out.get("assigned_topic"))

        # Simple Brier placeholder (can be expanded)
        if "brier_target" in self.config:
            brier = abs(sum(result.get("anomalies", [])) - self.config["brier_target"]) / 100.0
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
