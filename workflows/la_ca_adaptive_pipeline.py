from typing import Any, Dict, List

from core.intelligence.temporal_anomaly_intelligence import TemporalAnomalyIntelligenceLayer


class LACAAdaptivePipeline:
    """
    LA/CA Adaptive Signal Pipeline using the Sprint 5 Temporal + Anomaly Intelligence Layer.

    Designed for monitoring health signals (hantavirus, fires, policy changes),
    detecting regime shifts, and surfacing anomalies with provenance.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "vacuity_threshold": 0.35,
            "bocpd_hazard": 0.01,
            "pitman_yor_stickiness": 0.4,
        }
        self.layer = TemporalAnomalyIntelligenceLayer(config=self.config)
        self.provenance = {
            "pipeline": "LACAAdaptivePipeline",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "intelligence_layer": "TemporalAnomalyIntelligenceLayer"
        }
        self.signal_history: List[Dict[str, Any]] = []

    def process_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single LA/CA signal (e.g. case count, policy event, fire report).
        """
        # Convert signal to simple feature vector for the layer
        features = [
            float(signal.get("value", 0.0)),
            float(signal.get("severity", 0.0)),
            float(signal.get("velocity", 0.0)),
        ]

        result = self.layer.process_stream(features)

        enriched = {
            "signal": signal,
            "intelligence_result": result,
            "change_points": result.get("change_points", []),
            "anomalies": result.get("anomalies", []),
            "provenance": {**self.provenance, **result.get("provenance", {})}
        }

        self.signal_history.append(enriched)
        return enriched

    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            s for s in self.signal_history[-limit:]
            if s.get("anomalies")
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "pipeline_status": "active",
            "signals_processed": len(self.signal_history),
            "config": self.config,
            "provenance": self.provenance
        }


# Example usage for LA/CA monitoring
if __name__ == "__main__":
    pipeline = LACAAdaptivePipeline()

    # Example signals (replace with real LA/CA data feeds)
    signals = [
        {"type": "hantavirus", "value": 12, "severity": 0.7, "velocity": 0.3},
        {"type": "fire", "value": 45, "severity": 0.9, "velocity": 0.8},
        {"type": "policy", "value": 3, "severity": 0.4, "velocity": -0.2},
    ]

    for sig in signals:
        result = pipeline.process_signal(sig)
        print(result)

    print(pipeline.get_status())
