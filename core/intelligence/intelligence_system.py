from typing import Any, Dict, List, Optional

try:
    from core.intelligence.temporal_anomaly_intelligence import TemporalAnomalyIntelligenceLayer
    from core.intelligence.temporal_slicing import TemporalSlicingAPI
    from core.intelligence.brier_visualization import (
        format_brier_summary,
        format_decomposition,
    )
except ImportError as e:
    TemporalAnomalyIntelligenceLayer = None
    TemporalSlicingAPI = None
    format_brier_summary = None
    format_decomposition = None
    _import_error = str(e)
else:
    _import_error = None


class IntelligenceSystem:
    """
    Full Stack Intelligence System with robust error handling.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.layer = None
        self.slicer = None
        self._initialization_error = None

        try:
            if TemporalAnomalyIntelligenceLayer:
                self.layer = TemporalAnomalyIntelligenceLayer(config)
            if TemporalSlicingAPI:
                self.slicer = TemporalSlicingAPI()
        except Exception as e:
            self._initialization_error = str(e)

        self.provenance = {
            "system": "IntelligenceSystem",
            "version": "2.2.0",
            "sprint": "Sprint 5",
            "initialization_error": self._initialization_error,
        }

    def process(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        """Main processing entry point with error handling."""
        if self._initialization_error:
            return {
                "error": "Initialization failed",
                "details": self._initialization_error,
                "provenance": self.provenance
            }

        if self.layer is None:
            return {
                "error": "Intelligence layer not available",
                "provenance": self.provenance
            }

        try:
            result = self.layer.process_stream(data, target=target)
            return result
        except Exception as e:
            return {
                "error": "Processing failed",
                "details": str(e),
                "data_type": str(type(data)),
                "provenance": self.provenance
            }

    def get_intelligence_report(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        """Returns a rich diagnostic report with error handling."""
        if self._initialization_error:
            return {
                "error": "System not properly initialized",
                "details": self._initialization_error
            }

        try:
            result = self.process(data, target=target)

            if "error" in result:
                return result  # propagate error

            report = {
                "result": result,
                "brier_variants": result.get("brier_variants", {}),
                "provenance": self.provenance,
            }

            if format_brier_summary and "brier_summary" in result:
                report["brier_summary_text"] = format_brier_summary(result["brier_summary"])

            if format_decomposition and result.get("brier_variants"):
                decomp = result["brier_variants"].get("decomposition", {})
                report["decomposition_text"] = format_decomposition(decomp)

            return report

        except Exception as e:
            return {
                "error": "Report generation failed",
                "details": str(e),
                "provenance": self.provenance
            }

    def slice_data(self, data: List[Dict[str, Any]], regime_labels: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        if self.slicer is None:
            return {}
        try:
            return self.slicer.slice_by_regime(data, regime_labels)
        except Exception:
            return {}

    def get_status(self) -> Dict[str, Any]:
        status = {
            "status": "active" if not self._initialization_error else "degraded",
            "config": self.config,
            "provenance": self.provenance,
        }
        if self.layer:
            try:
                status["layer_status"] = self.layer.get_status()
            except Exception as e:
                status["layer_status"] = {"error": str(e)}
        return status
