from typing import Any, Dict, List, Optional

class TemporalSlicingAPI:
    """
    Temporal Slicing API for the intelligence layer.
    Allows slicing data streams by time windows, regimes, or custom conditions.
    """

    def __init__(self):
        self.provenance = {
            "module": "TemporalSlicingAPI",
            "version": "2.2.0",
            "sprint": "Sprint 5"
        }

    def slice_by_regime(self, data: List[Dict[str, Any]], regime_labels: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        """Group data points by regime labels."""
        slices: Dict[int, List[Dict[str, Any]]] = {}
        for point, label in zip(data, regime_labels):
            if label not in slices:
                slices[label] = []
            slices[label].append(point)
        return slices

    def slice_by_time_window(self, data: List[Dict[str, Any]], start: int, end: int, time_key: str = "timestamp") -> List[Dict[str, Any]]:
        """Simple time window slicing."""
        return [p for p in data if start <= p.get(time_key, 0) <= end]

    def get_status(self) -> Dict[str, Any]:
        return {"status": "active", "provenance": self.provenance}
