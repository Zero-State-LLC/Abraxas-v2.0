from typing import Any, Dict, List, Optional

try:
    from core.intelligence.base_classes import BaseDetector, BaseCalibrator
    from core.intelligence.detector_registry import get_detector, list_available_detectors
    from core.intelligence.provenance import build_layer_provenance
    from core.intelligence.brier_scorer import BrierScorer
    from core.intelligence.config import IntelligenceLayerConfig
    from core.ensemble.multi_model_ensemble import MultiModelEnsemble
    from core.calibration.isotonic_regression_calibrator import IsotonicRegressionCalibrator
    from core.calibration.platt_scaling_calibrator import PlattScalingCalibrator
    from core.calibration.beta_calibrator import BetaCalibrator
    from core.calibration.dirichlet_calibrator import DirichletCalibrator
except ImportError:
    BaseDetector = None
    BaseCalibrator = None
    get_detector = None
    list_available_detectors = None
    build_layer_provenance = None
    BrierScorer = None
    IntelligenceLayerConfig = None
    MultiModelEnsemble = None
    IsotonicRegressionCalibrator = None
    PlattScalingCalibrator = None
    BetaCalibrator = None
    DirichletCalibrator = None


CALIBRATION_REGISTRY = {
    "isotonic": IsotonicRegressionCalibrator,
    "platt": PlattScalingCalibrator,
    "beta": BetaCalibrator,
    "dirichlet": DirichletCalibrator,
}


def get_calibrator(method: str):
    cls = CALIBRATION_REGISTRY.get(method)
    return cls() if cls else None


class TemporalAnomalyIntelligenceLayer:
    """
    Intelligence layer with optional multi-model ensemble support.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if IntelligenceLayerConfig and isinstance(config, dict):
            self.config_obj = IntelligenceLayerConfig.from_dict(config)
            self.config = self.config_obj.to_dict()
        else:
            self.config_obj = None
            self.config = config or {}

        self.detectors = self._build_detectors()
        self.calibrator = get_calibrator(self.config.get("calibration_method"))
        self.brier_scorer = BrierScorer() if BrierScorer else None
        self.provenance = self._build_provenance()

        # Dynamic thresholding
        self.recent_vacuity_scores: List[float] = []
        self.dynamic_vacuity_threshold: float = self.config.get("vacuity_threshold", 0.35)

        # Multi-model ensemble
        self.use_ensemble = self.config.get("use_ensemble", False)
        self.ensemble = None
        if self.use_ensemble and MultiModelEnsemble:
            self.ensemble = MultiModelEnsemble(strategy=self.config.get("ensemble_strategy", "weighted"))
            for name in self.detectors.keys():
                if self.detectors[name]:
                    self.ensemble.register_model(name)

    def _build_detectors(self) -> Dict[str, Any]:
        if get_detector is None:
            return {}
        return {
            "hdbscan": get_detector("hdbscan", self.config),
            "bocpd": get_detector("bocpd", self.config),
            "pitman_yor": get_detector("pitman_yor", self.config),
            "hdp": get_detector("hdp", self.config),
        }

    def _build_provenance(self) -> Dict[str, Any]:
        if build_layer_provenance is None:
            return {"layer": "TemporalAnomalyIntelligenceLayer"}
        return build_layer_provenance(
            detectors=list(self.detectors.keys()),
            calibration_method=self.config.get("calibration_method"),
            extra={"available_detectors": list_available_detectors() if list_available_detectors else []}
        )

    def _update_dynamic_threshold(self, vacuity_score: float):
        self.recent_vacuity_scores.append(vacuity_score)
        if len(self.recent_vacuity_scores) > 20:
            self.recent_vacuity_scores.pop(0)

        if len(self.recent_vacuity_scores) >= 5:
            avg = sum(self.recent_vacuity_scores) / len(self.recent_vacuity_scores)
            self.dynamic_vacuity_threshold = min(max(avg * 1.15, 0.1), 0.8)

    def process_stream(self, data: Any, target: Optional[float] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "change_points": [],
            "anomalies": [],
            "clusters": [],
            "regime_labels": [],
            "provenance": self.provenance.copy(),
            "dynamic_vacuity_threshold": self.dynamic_vacuity_threshold,
            "ensemble_used": self.use_ensemble
        }

        model_anomaly_outputs = {}

        if self.detectors.get("bocpd") and isinstance(data, (int, float)):
            out = self.detectors["bocpd"].update(float(data))
            result["change_points"] = out.get("change_points", [])

        if self.detectors.get("hdbscan") and isinstance(data, list):
            out = self.detectors["hdbscan"].fit_predict(data)
            anomalies = [i for i, lbl in enumerate(out.get("labels", [])) if lbl == -1]
            result["anomalies"] = anomalies
            model_anomaly_outputs["hdbscan"] = [1 if i in anomalies else 0 for i in range(len(data))]

            if "vacuity_scores" in out:
                for score in out["vacuity_scores"]:
                    self._update_dynamic_threshold(score)

        if self.detectors.get("pitman_yor") and isinstance(data, list):
            for point in data:
                out = self.detectors["pitman_yor"].assign(point)
                result["clusters"].append(out.get("cluster_id"))

        if self.detectors.get("hdp") and isinstance(data, list):
            for point in data:
                out = self.detectors["hdp"].update(point)
                result["regime_labels"].append(out.get("assigned_topic"))

        # Ensemble combination
        if self.use_ensemble and self.ensemble and model_anomaly_outputs:
            try:
                ensemble_anomalies = self.ensemble.combine_anomaly_scores(model_anomaly_outputs)
                result["ensemble_anomalies"] = ensemble_anomalies
                result["anomalies"] = [i for i, val in enumerate(ensemble_anomalies) if val == 1]
            except Exception:
                pass  # Fall back to individual detector results

        if self.calibrator and result.get("anomalies"):
            scores = [float(i) for i in result["anomalies"]]
            cal_out = self.calibrator.calibrate(scores)
            result["calibrated_anomalies"] = cal_out.get("calibrated_scores", [])

        if target is not None and result.get("anomalies") is not None and self.brier_scorer:
            n = len(data) if isinstance(data, list) else 10
            pred = len(result["anomalies"]) / max(n, 1)
            brier = self.brier_scorer.update(pred, target)
            result["brier_score"] = brier
            result["brier_summary"] = self.brier_scorer.get_summary()
            result["brier_variants"] = self.brier_scorer.get_full_variants()

        return result

    def get_brier_summary(self) -> Dict[str, Any]:
        if self.brier_scorer:
            return self.brier_scorer.get_summary()
        return {"status": "no_brier_scorer"}

    def get_brier_variants(self) -> Dict[str, Any]:
        if self.brier_scorer:
            return self.brier_scorer.get_full_variants()
        return {}

    def get_status(self) -> Dict[str, Any]:
        status = {
            "status": "active",
            "config": self.config,
            "dynamic_vacuity_threshold": self.dynamic_vacuity_threshold,
            "ensemble_enabled": self.use_ensemble,
            "brier_summary": self.get_brier_summary(),
            "provenance": self.provenance
        }
        if self.ensemble:
            status["ensemble_status"] = self.ensemble.get_status()
        return status

    @staticmethod
    def available_calibration_methods() -> list:
        return list(CALIBRATION_REGISTRY.keys())
