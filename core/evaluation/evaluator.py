from typing import Any, Dict, List, Optional

try:
    from core.intelligence.intelligence_system import IntelligenceSystem
except ImportError:
    IntelligenceSystem = None


class IntelligenceEvaluator:
    """
    Basic evaluation and backtesting harness for the IntelligenceSystem.
    """

    def __init__(self, system: Optional[Any] = None):
        self.system = system or (IntelligenceSystem() if IntelligenceSystem else None)
        self.results: List[Dict[str, Any]] = []

    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the system on a dataset of {'data': ..., 'target': ...} items.
        """
        if self.system is None:
            return {"error": "No IntelligenceSystem available"}

        brier_scores = []
        log_scores = []

        for item in dataset:
            data = item.get("data")
            target = item.get("target")
            if data is None:
                continue

            result = self.system.process(data, target=target)
            if "brier_score" in result:
                brier_scores.append(result["brier_score"])
            if result.get("brier_variants"):
                log = result["brier_variants"].get("log_score")
                if log is not None:
                    log_scores.append(log)

            self.results.append(result)

        return {
            "n_samples": len(dataset),
            "mean_brier": sum(brier_scores) / len(brier_scores) if brier_scores else None,
            "mean_log_score": sum(log_scores) / len(log_scores) if log_scores else None,
            "samples_with_brier": len(brier_scores)
        }

    def backtest(self, dataset: List[Dict[str, Any]], window: int = 10) -> List[Dict[str, Any]]:
        """
        Simple walk-forward style backtest.
        """
        results = []
        for i in range(window, len(dataset)):
            train = dataset[:i]
            test_item = dataset[i]

            # For now just evaluate on current item (can be expanded)
            eval_result = self.evaluate([test_item])
            results.append({
                "index": i,
                "evaluation": eval_result
            })
        return results

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_evaluations": len(self.results),
            "last_result": self.results[-1] if self.results else None
        }
