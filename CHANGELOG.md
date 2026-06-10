# Changelog

All notable changes to this project will be documented in this file.

## [2.2.0] — 2026-06-10

### Sprint 5: Temporal + Anomaly Intelligence Layer

- Integrated Evidential HDBSCAN (vacuity-aware anomaly detection)
- Integrated Bayesian Online Change Point Detector (regime/shift detection)
- Integrated Neural Sticky Pitman-Yor (dynamic clustering with stickiness)
- Integrated Online Variational HDP (streaming hierarchical clustering)
- New unified facade in `core/intelligence/temporal_anomaly_intelligence.py`
- Clean package structure: `core/anomaly/`, `core/temporal/`, `core/clustering/`
- All components provenance-tagged and operator-friendly
- `TemporalAnomalyIntelligenceLayer.process_stream(data)` and `.get_status()` ready for pipelines

**Usage Example:**
```python
from core.intelligence.temporal_anomaly_intelligence import TemporalAnomalyIntelligenceLayer

layer = TemporalAnomalyIntelligenceLayer(config={
    "hdbscan": {"vacuity_threshold": 0.35},
    "bocpd": {"hazard": 0.01},
    "pitman_yor": {"stickiness": 0.4},
})

result = layer.process_stream(data_array)
print(result["change_points"], result["anomalies"])
print(layer.get_status())
```

See `core/intelligence/temporal_anomaly_intelligence.py` and the new subpackages for details.

## [2.1.0] — 2026-06

(Previous history preserved from main)
