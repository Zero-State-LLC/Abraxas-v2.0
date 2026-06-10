from typing import Any, Dict, List

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None


class LACAAdaptivePipeline:
    """
    Advanced LA/CA Adaptive Pipeline with rich signal categorization.
    """

    SUPPORTED_CATEGORIES = [
        "hantavirus",
        "fire",
        "chemical",
        "protest",
        "infrastructure",
        "health_outbreak",
        "political",
        "environmental",
        "policy",
        "general"
    ]

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {"calibration_method": "beta"}
        self.system = IntelligenceSystem(config=self.config) if IntelligenceSystem else None
        self.signal_history: List[Dict[str, Any]] = []
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
        return self.analyze_signal(signal, target=target)

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
            "brier_trend": self.get_brier_trend(),
            "recent_performance": self.evaluate_recent_performance(),
            "provenance": self.provenance
        }


# ============================================================
# Code Examples for Each Signal Type
# ============================================================

if __name__ == "__main__":
    pipeline = LACAAdaptivePipeline()

    print("=== LA/CA Signal Processing Examples ===\n")

    # 1. Hantavirus
    hantavirus_signal = {
        "value": 18,
        "severity": 0.65,
        "velocity": 0.35,
        "confidence": 0.55
    }
    result = pipeline.process_by_type("hantavirus", hantavirus_signal, target=0.2)
    print("Hantavirus:", result.get("result", {}).get("brier_score"))

    # 2. Fire
    fire_signal = {
        "value": 120,
        "severity": 0.8,
        "velocity": 0.6
    }
    result = pipeline.process_by_type("fire", fire_signal, target=0.4)
    print("Fire:", result.get("result", {}).get("brier_score"))

    # 3. Chemical Event
    chemical_signal = {
        "value": 75,
        "severity": 0.7,
        "velocity": 0.25,
        "confidence": 0.45
    }
    result = pipeline.process_by_type("chemical", chemical_signal, target=0.3)
    print("Chemical:", result.get("result", {}).get("brier_score"))

    # 4. Protest / Civil Unrest
    protest_signal = {
        "value": 45,
        "severity": 0.55,
        "velocity": 0.8
    }
    result = pipeline.process_by_type("protest", protest_signal, target=0.15)
    print("Protest:", result.get("result", {}).get("brier_score"))

    # 5. Infrastructure Failure
    infra_signal = {
        "value": 30,
        "severity": 0.6,
        "velocity": -0.2
    }
    result = pipeline.process_by_type("infrastructure", infra_signal, target=0.25)
    print("Infrastructure:", result.get("result", {}).get("brier_score"))

    # 6. Health Outbreak (non-hantavirus)
    health_signal = {
        "value": 95,
        "severity": 0.7,
        "velocity": 0.5
    }
    result = pipeline.process_by_type("health_outbreak", health_signal, target=0.35)
    print("Health Outbreak:", result.get("result", {}).get("brier_score"))

    # 7. Political Signal
    political_signal = {
        "value": 12,
        "severity": 0.4,
        "velocity": 0.1,
        "confidence": 0.6
    }
    result = pipeline.process_by_type("political", political_signal, target=0.1)
    print("Political:", result.get("result", {}).get("brier_score"))

    # 8. Environmental
    env_signal = {
        "value": 40,
        "severity": 0.5,
        "velocity": 0.3
    }
    result = pipeline.process_by_type("environmental", env_signal, target=0.2)
    print("Environmental:", result.get("result", {}).get("brier_score"))

    print("\nPipeline Status:", pipeline.get_status())
