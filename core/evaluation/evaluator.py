from typing import Any, Dict, List, Optional

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None


class IntelligenceEvaluator:
    """
    Evaluation and backtesting harness for the IntelligenceSystem.
    """

    def __init__(self, system: Optional[Any] = None):
        self.system = system or (IntelligenceSystem() if IntelligenceSystem else None)
        self.results: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []

    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the system on a list of {'data': ..., 'target': ...} items.
        """
        if self.system is None:
            return {"error": "No IntelligenceSystem available"}

        brier_scores = []
        log_scores = []
        anomaly_counts = []

        for item in dataset:
            data = item.get("data")
            target = item.get("target")
            if data is None:
                continue

            result = self.system.process(data, target=target)

            if "brier_score" in result:
                brier_scores.append(result["brier_score"])

            variants = result.get("brier_variants", {})
            if variants.get("log_score") is not None:
                log_scores.append(variants["log_score"])

            if result.get("anomalies"):
                anomaly_counts.append(len(result["anomalies"]))

            self.results.append(result)

        summary = {
            "n_samples": len(dataset),
            "mean_brier": sum(brier_scores) / len(brier_scores) if brier_scores else None,
            "mean_log_score": sum(log_scores) / len(log_scores) if log_scores else None,
            "total_anomalies_detected": sum(anomaly_counts),
            "samples_with_brier": len(brier_scores)
        }

        self.history.append(summary)
        return summary

    def backtest(self, dataset: List[Dict[str, Any]], train_size: int = None) -> List[Dict[str, Any]]:
        """
        Simple expanding window backtest.
        """
        results = []
        start = train_size or max(5, len(dataset) // 4)

        for i in range(start, len(dataset)):
            train_data = dataset[:i]
            test_item = dataset[i]

            # Evaluate on current point
            eval_result = self.evaluate([test_item])
            results.append({
                "index": i,
                "evaluation": eval_result
            })

        return results

    def get_summary(self) -> Dict[str, Any]:
        if not self.history:
            return {"status": "no_evaluations_yet"}

        return {
            "total_evaluations": len(self.history),
            "latest": self.history[-1],
            "history": self.history[-5:]  # last 5 evaluations
        }

    def reset(self):
        self.results.clear()
        self.history.clear()
