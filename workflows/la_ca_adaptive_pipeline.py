from typing import Any, Dict, List

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None


class LACAAdaptivePipeline:
    """
    LA/CA Adaptive Pipeline powered by the full IntelligenceSystem.
    Recommended way to use the intelligence stack for LA/CA monitoring.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {"calibration_method": "beta"}
        self.system = IntelligenceSystem(config=self.config) if IntelligenceSystem else None
        self.signal_history: List[Dict[str, Any]] = []
        self.provenance = {
            "pipeline": "LACAAdaptivePipeline",
            "version": "2.2.0",
            "powered_by": "IntelligenceSystem"
        }

    def process_signal(self, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        if self.system is None:
            return {"error": "IntelligenceSystem not available"}

        features = [
            float(signal.get("value", 0.0)),
            float(signal.get("severity", 0.0)),
            float(signal.get("velocity", 0.0)),
        ]

        result = self.system.process(features, target=target)

        enriched = {
            "signal": signal,
            "result": result,
            "brier_variants": result.get("brier_variants", {}),
            "provenance": {**self.provenance, **result.get("provenance", {})}
        }
        self.signal_history.append(enriched)
        return enriched

    def analyze_signal(self, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        """Recommended high-level method."""
        if self.system is None:
            return {"error": "IntelligenceSystem not available"}
        return self.system.analyze(
            [
                float(signal.get("value", 0.0)),
                float(signal.get("severity", 0.0)),
                float(signal.get("velocity", 0.0)),
            ],
            target=target
        )

    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            s for s in self.signal_history[-limit:]
            if s.get("result", {}).get("anomalies")
        ]

    def get_brier_trend(self) -> Dict[str, Any]:
        briers = [
            s.get("result", {}).get("brier_score")
            for s in self.signal_history
            if s.get("result", {}).get("brier_score") is not None
        ]
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
