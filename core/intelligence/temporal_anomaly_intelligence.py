"""Temporal + Anomaly Intelligence Layer (Sprint 5)

Unified facade that wires together:
- Evidential HDBSCAN (anomaly detection with vacuity)
- BOCPD (Bayesian online change point / regime detection)
- Neural Sticky Pitman-Yor (dynamic clustering)
- Online Variational HDP (streaming hierarchical clustering)

Designed to integrate with existing Abraxas v2.0 governance, provenance, and operator decision systems.
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, List, Optional, Tuple

try:
    from core.anomaly.evidential_hdbscan_detector import EvidentialHDBSCANDetector
    from core.temporal.bayesian_online_change_point_detector import BayesianOnlineChangePointDetector
    from core.clustering.neural_sticky_pitman_yor import NeuralStickyPitmanYor
    from core.clustering.online_variational_hdp import OnlineVariationalHDP
except ImportError:
    # Allow import during development before all modules are present
    EvidentialHDBSCANDetector = None
    BayesianOnlineChangePointDetector = None
    NeuralStickyPitmanYor = None
    OnlineVariationalHDP = None


class TemporalAnomalyIntelligenceLayer:
    """
    High-level integration layer for temporal regime detection + nonparametric anomaly intelligence.

    This class provides a unified interface that existing pipelines, operator decision
    records, and governance systems can call.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.hdbscan = EvidentialHDBSCANDetector(**self.config.get("hdbscan", {})) if EvidentialHDBSCANDetector else None
        self.bocpd = BayesianOnlineChangePointDetector(**self.config.get("bocpd", {})) if BayesianOnlineChangePointDetector else None
        self.pitman_yor = NeuralStickyPitmanYor(**self.config.get("pitman_yor", {})) if NeuralStickyPitmanYor else None
        self.vhdp = OnlineVariationalHDP(**self.config.get("vhdp", {})) if OnlineVariationalHDP else None

    def process_stream(self, data: np.ndarray, timestamps: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Process a streaming window of data through the full temporal + anomaly stack.

        Returns a rich result dict with change points, clusters, anomalies, and provenance.
        """
        result: Dict[str, Any] = {
            "change_points": [],
            "clusters": [],
            "anomalies": [],
            "regime_labels": [],
            "provenance": {
                "layer": "sprint5_temporal_anomaly_intelligence",
                "modules_used": []
            }
        }

        if self.bocpd is not None:
            cp_result = self.bocpd.detect(data)
            result["change_points"] = cp_result.get("change_points", [])
            result["regime_labels"] = cp_result.get("regime_labels", [])
            result["provenance"]["modules_used"].append("bocpd")

        if self.hdbscan is not None:
            anomaly_result = self.hdbscan.detect(data)
            result["anomalies"] = anomaly_result.get("anomalies", [])
            result["provenance"]["modules_used"].append("evidential_hdbscan")

        if self.pitman_yor is not None:
            cluster_result = self.pitman_yor.fit_predict(data)
            result["clusters"] = cluster_result.get("clusters", [])
            result["provenance"]["modules_used"].append("neural_sticky_pitman_yor")

        if self.vhdp is not None:
            vhdp_result = self.vhdp.update(data)
            result["hierarchical_clusters"] = vhdp_result.get("clusters", [])
            result["provenance"]["modules_used"].append("online_variational_hdp")

        return result

    def get_status(self) -> Dict[str, Any]:
        return {
            "layer": "Sprint 5 - Temporal + Anomaly Intelligence",
            "modules": {
                "evidential_hdbscan": self.hdbscan is not None,
                "bocpd": self.bocpd is not None,
                "neural_sticky_pitman_yor": self.pitman_yor is not None,
                "online_variational_hdp": self.vhdp is not None,
            },
            "config": self.config
        }
