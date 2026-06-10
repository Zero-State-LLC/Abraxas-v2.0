from typing import Any, Dict, List, Optional


def build_layer_provenance(
    layer_name: str = "TemporalAnomalyIntelligenceLayer",
    version: str = "2.2.0",
    sprint: str = "Sprint 5",
    detectors: Optional[List[str]] = None,
    calibration_method: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Centralized provenance builder for intelligence layers.
    """
    prov = {
        "layer": layer_name,
        "version": version,
        "sprint": sprint,
        "detectors": detectors or [],
        "calibration_method": calibration_method,
    }
    if extra:
        prov.update(extra)
    return prov


def merge_provenance(base: Dict[str, Any], additional: Dict[str, Any]) -> Dict[str, Any]:
    merged = base.copy()
    merged.update(additional)
    return merged
