from typing import Any, Dict, List

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None


class LACAAdaptivePipeline:
    """
    Production-ready LA/CA Adaptive Pipeline powered by IntelligenceSystem.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {"calibration_method": "beta"}
        self.system = IntelligenceSystem(config=self.config) if IntelligenceSystem else None
        self.signal_history: List[Dict[str, Any]] = []
        self.provenance = {
            "pipeline": "LACAAdaptivePipeline",
            "version": "2.2.0",
            "powered_by": "IntelligenceSystem v2.2.0"
        }

    def process_signal(self, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        if self.system is None:
            return {"error": "IntelligenceSystem not available"}

        features = self._extract_features(signal)
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
        """Recommended high-level analysis method."""
        if self.system is None:
            return {"error": "IntelligenceSystem not available"}
        features = self._extract_features(signal)
        return self.system.analyze(features, target=target)

    def _extract_features(self, signal: Dict[str, Any]) -> List[float]:
        """Extract consistent feature vector from various LA/CA signal types."""
        return [
            float(signal.get("value", 0.0)),
            float(signal.get("severity", 0.0)),
            float(signal.get("velocity", 0.0)),
            float(signal.get("confidence", 0.5)),
        ]

    def process_by_type(self, signal_type: str, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        """Process signal with type-specific handling."""
        signal = signal.copy()
        signal["type"] = signal_type

        # Type-specific adjustments (can be expanded)
        if signal_type == "fire":
            signal["severity"] = max(signal.get("severity", 0.5), 0.7)
        elif signal_type == "hantavirus":
            signal["velocity"] = signal.get("velocity", 0) * 1.2
        elif signal_type == "policy":
            signal["confidence"] = signal.get("confidence", 0.6)

        return self.analyze_signal(signal, target=target)

    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [s for s in self.signal_history[-limit:] if s.get("result", {}).get("anomalies")]

    def get_brier_trend(self) -> Dict[str, Any]:
        briers = [s.get("result", {}).get("brier_score") for s in self.signal_history if s.get("result", {}).get("brier_score") is not None]
        if not briers:
            return {"status": "no_brier_scores"}
        return {
            "mean_brier": sum(briers) / len(briers),
            "latest_brier": briers[-1],
            "n_samples": len(briers)
        }

    def evaluate_recent_performance(self) -> Dict[str, Any]:
        """Basic evaluation of recent pipeline performance."""
        if len(self.signal_history) < 5:
            return {"status": "insufficient_data"}

        recent = self.signal_history[-20:]
        brier_scores = [s.get("result", {}).get("brier_score") for s in recent if s.get("result", {}).get("brier_score") is not None]

        return {
            "signals_evaluated": len(recent),
            "mean_brier": sum(brier_scores) / len(brier_scores) if brier_scores else None,
            "anomaly_rate": sum(1 for s in recent if s.get("result", {}).get("anomalies")) / len(recent),
            "trend": self.get_brier_trend()
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "active",
            "signals_processed": len(self.signal_history),
            "brier_trend": self.get_brier_trend(),
            "recent_performance": self.evaluate_recent_performance(),
            "provenance": self.provenance
        }
