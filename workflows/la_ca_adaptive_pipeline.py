from typing import Any, Dict, List

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None


class LACAAdaptivePipeline:
    """
    LA/CA pipeline with per-signal-type dynamic thresholding.
    """

    SUPPORTED_CATEGORIES = [
        "hantavirus", "fire", "chemical", "protest", "infrastructure",
        "health_outbreak", "political", "environmental", "wildfire_smoke",
        "heatwave", "power_outage", "policy", "general"
    ]

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {"calibration_method": "beta"}
        self.system = IntelligenceSystem(config=self.config) if IntelligenceSystem else None
        self.signal_history: List[Dict[str, Any]] = []

        # Per-signal-type dynamic thresholds
        self.signal_type_thresholds: Dict[str, float] = {
            cat: 0.35 for cat in self.SUPPORTED_CATEGORIES
        }

        self.provenance = {
            "pipeline": "LACAAdaptivePipeline",
            "version": "2.2.0",
            "powered_by": "IntelligenceSystem",
            "supported_categories": self.SUPPORTED_CATEGORIES
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
            "dynamic_threshold": result.get("dynamic_vacuity_threshold"),
            "provenance": {**self.provenance, **result.get("provenance", {})}
        }
        self.signal_history.append(enriched)
        return enriched

    def analyze_signal(self, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        if self.system is None:
            return {"error": "IntelligenceSystem not available"}
        features = self._extract_features(signal)
        return self.system.analyze(features, target=target)

    def process_by_type(self, signal_type: str, signal: Dict[str, Any], target: float = None) -> Dict[str, Any]:
        if signal_type not in self.SUPPORTED_CATEGORIES:
            signal_type = "general"

        signal = signal.copy()
        signal["type"] = signal_type
        signal = self._apply_category_logic(signal_type, signal)

        # Use per-signal-type threshold if available
        current_threshold = self.signal_type_thresholds.get(signal_type, 0.35)

        result = self.analyze_signal(signal, target=target)

        # Simple adaptation: adjust threshold based on recent anomaly behavior
        if result.get("anomalies"):
            anomaly_ratio = len(result["anomalies"]) / max(len(signal.get("features", [])), 1)
            # Adapt threshold slightly
            new_threshold = current_threshold * (1 + (anomaly_ratio - 0.1) * 0.1)
            self.signal_type_thresholds[signal_type] = max(min(new_threshold, 0.8), 0.1)

        enriched = {
            "signal": signal,
            "result": result,
            "brier_variants": result.get("brier_variants", {}),
            "dynamic_threshold": self.signal_type_thresholds[signal_type],
            "signal_type": signal_type,
            "provenance": {**self.provenance, **result.get("provenance", {})}
        }
        self.signal_history.append(enriched)
        return enriched

    def _apply_category_logic(self, signal_type: str, signal: Dict[str, Any]) -> Dict[str, Any]:
        s = signal.copy()
        if signal_type == "fire":
            s["severity"] = max(s.get("severity", 0.5), 0.75)
            s["velocity"] = s.get("velocity", 0) * 1.3
        elif signal_type == "hantavirus":
            s["velocity"] = s.get("velocity", 0) * 1.4
            s["confidence"] = min(s.get("confidence", 0.6), 0.5)
        elif signal_type == "chemical":
            s["severity"] = max(s.get("severity", 0.6), 0.85)
            s["confidence"] = s.get("confidence", 0.4)
        elif signal_type == "protest":
            s["velocity"] = abs(s.get("velocity", 0)) * 1.2
        elif signal_type == "infrastructure":
            s["severity"] = s.get("severity", 0.5)
        elif signal_type == "health_outbreak":
            s["velocity"] = s.get("velocity", 0) * 1.5
            s["severity"] = max(s.get("severity", 0.5), 0.7)
        elif signal_type == "political":
            s["confidence"] = s.get("confidence", 0.5)
        elif signal_type == "environmental":
            s["severity"] = max(s.get("severity", 0.4), 0.6)
        elif signal_type == "wildfire_smoke":
            s["severity"] = max(s.get("severity", 0.5), 0.8)
            s["velocity"] = s.get("velocity", 0) * 1.2
        elif signal_type == "heatwave":
            s["severity"] = max(s.get("severity", 0.4), 0.7)
            s["velocity"] = s.get("velocity", 0) * 0.8
        elif signal_type == "power_outage":
            s["severity"] = max(s.get("severity", 0.5), 0.75)
            s["velocity"] = s.get("velocity", 0) * 1.1
        return s

    def _extract_features(self, signal: Dict[str, Any]) -> List[float]:
        return [
            float(signal.get("value", 0.0)),
            float(signal.get("severity", 0.0)),
            float(signal.get("velocity", 0.0)),
            float(signal.get("confidence", 0.5)),
        ]

    def get_recent_anomalies(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [s for s in self.signal_history[-limit:] if s.get("result", {}).get("anomalies")]

    def evaluate_recent_performance(self) -> Dict[str, Any]:
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

    def get_brier_trend(self) -> Dict[str, Any]:
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
            "supported_categories": self.SUPPORTED_CATEGORIES,
            "per_type_thresholds": self.signal_type_thresholds.copy(),
            "brier_trend": self.get_brier_trend(),
            "recent_performance": self.evaluate_recent_performance(),
            "provenance": self.provenance
        }
