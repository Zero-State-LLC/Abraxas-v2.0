from typing import Any, Dict, List

from core.intelligence.temporal_anomaly_intelligence import TemporalAnomalyIntelligenceLayer


class LACAAdaptivePipeline:
    """
    Enhanced LA/CA Adaptive Pipeline with Brier monitoring and multi-signal support.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {"calibration_method": "beta"}
        self.layer = TemporalAnomalyIntelligenceLayer(config=self.config)
        self.signal_history: List[Dict[str, Any]] = []
        self.provenance = {
            "pipeline": "LACAAdaptivePipeline",
            "version": "2.2.0",
            "sprint": "Sprint 5"
        }

    def process_signal(self, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        features = [
            float(signal.get("value", 0.0)),
            float(signal.get("severity", 0.0)),
            float(signal.get("velocity", 0.0)),
        ]
        result = self.layer.process_stream(features, target=target)

        enriched = {
            "signal": signal,
            "result": result,
            "brier_summary": result.get("brier_summary"),
            "provenance": {**self.provenance, **result.get("provenance", {})}
        }
        self.signal_history.append(enriched)
        return enriched

    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [s for s in self.signal_history[-limit:] if s.get("result", {}).get("anomalies")]

    def get_brier_trend(self) -> Dict[str, Any]:
        if not self.signal_history:
            return {"status": "no_data"}
        briers = [s.get("result", {}).get("brier_score") for s in self.signal_history if s.get("result", {}).get("brier_score") is not None]
        if not briers:
            return {"status": "no_brier_scores"}
        return {
            "mean_brier": sum(briers) / len(briers),
            "latest_brier": briers[-1],
            "n_samples": len(briers)
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "signals_processed": len(self.signal_history),
            "brier_trend": self.get_brier_trend(),
            "provenance": self.provenance
        }
