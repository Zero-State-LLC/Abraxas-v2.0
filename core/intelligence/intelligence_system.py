from typing import Any, Dict, List, Optional

try:
    from core.intelligence.temporal_anomaly_intelligence import TemporalAnomalyIntelligenceLayer
    from core.intelligence.temporal_slicing import TemporalSlicingAPI
    from core.intelligence.brier_scorer import BrierScorer
    from core.intelligence.brier_visualization import (
        format_brier_summary,
        format_decomposition,
        format_reliability_diagram,
    )
except ImportError:
    TemporalAnomalyIntelligenceLayer = None
    TemporalSlicingAPI = None
    BrierScorer = None
    format_brier_summary = None
    format_decomposition = None
    format_reliability_diagram = None


class IntelligenceSystem:
    """
    Full Stack Intelligence System.

    Unified high-level interface that brings together:
    - TemporalAnomalyIntelligenceLayer (detectors + calibration + scoring)
    - TemporalSlicingAPI
    - Rich Brier + Proper Scoring diagnostics
    - Visualization helpers

    This is the main entry point for the Sprint 5 intelligence stack.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.layer = TemporalAnomalyIntelligenceLayer(config) if TemporalAnomalyIntelligenceLayer else None
        self.slicer = TemporalSlicingAPI() if TemporalSlicingAPI else None
        self.provenance = {
            "system": "IntelligenceSystem",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "components": [
                "TemporalAnomalyIntelligenceLayer",
                "TemporalSlicingAPI",
                "BrierScorer + variants + Log/Sp\u00e8reical",
                "Calibration (Isotonic/Platt/Beta)",
                "Visualization helpers"
            ]
        }

    def process(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        """Main processing entry point."""
        if self.layer is None:
            return {"error": "Layer not available"}
        return self.layer.process_stream(data, target=target)

    def get_intelligence_report(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        """Returns a rich diagnostic report."""
        if self.layer is None:
            return {"error": "Layer not available"}

        result = self.layer.process_stream(data, target=target)

        report = {
            "result": result,
            "brier_variants": result.get("brier_variants", {}),
            "provenance": self.provenance,
        }

        # Add formatted summaries if available
        if format_brier_summary and "brier_summary" in result:
            report["brier_summary_text"] = format_brier_summary(result["brier_summary"])

        if format_decomposition and "brier_variants" in result:
            decomp = result["brier_variants"].get("decomposition", {})
            report["decomposition_text"] = format_decomposition(decomp)

        return report

    def slice_data(self, data: List[Dict[str, Any]], regime_labels: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        if self.slicer is None:
            return {}
        return self.slicer.slice_by_regime(data, regime_labels)

    def get_status(self) -> Dict[str, Any]:
        status = {
            "status": "active",
            "config": self.config,
            "provenance": self.provenance,
        }
        if self.layer:
            status["layer_status"] = self.layer.get_status()
        return status
