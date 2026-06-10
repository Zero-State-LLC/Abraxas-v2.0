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
    Full Stack Intelligence System with dynamic thresholding support.
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
        if self._initialization_error:
            return {"error": "Initialization failed", "details": self._initialization_error}
        if self.layer is None:
            return {"error": "Layer not available"}
        try:
            return self.layer.process_stream(data, target=target)
        except Exception as e:
            return {"error": "Processing failed", "details": str(e)}

    def analyze(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        return self.get_intelligence_report(data, target=target)

    def get_intelligence_report(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        if self._initialization_error:
            return {"error": "System not initialized", "details": self._initialization_error}
        try:
            result = self.process(data, target=target)
            if "error" in result:
                return result

            report = {
                "result": result,
                "brier_variants": result.get("brier_variants", {}),
                "dynamic_threshold": result.get("dynamic_vacuity_threshold"),
                "provenance": self.provenance,
            }
            if format_brier_summary and "brier_summary" in result:
                report["brier_summary_text"] = format_brier_summary(result["brier_summary"])
            if format_decomposition and result.get("brier_variants"):
                decomp = result["brier_variants"].get("decomposition", {})
                report["decomposition_text"] = format_decomposition(decomp)
            return report
        except Exception as e:
            return {"error": "Report failed", "details": str(e)}

    def get_current_thresholds(self) -> Dict[str, Any]:
        """Return current dynamic threshold information."""
        if self.layer is None:
            return {"error": "Layer not available"}
        try:
            return {
                "global_dynamic_threshold": getattr(self.layer, 'dynamic_vacuity_threshold', None),
                "per_type_thresholds": getattr(self.layer, 'signal_type_thresholds', None),
            }
        except Exception as e:
            return {"error": str(e)}

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
            "provenance": self.provenance,
        }
        if self.layer:
            try:
                status["layer_status"] = self.layer.get_status()
            except Exception as e:
                status["layer_status"] = {"error": str(e)}
        return status

    def run(self, data: Any, target: Optional[float] = None):
        return self.analyze(data, target=target)
