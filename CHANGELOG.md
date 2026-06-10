# [1.3.0](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/compare/v1.2.1...v1.3.0) (2026-06-10)


### Features

* Add LA/CA Adaptive Pipeline integration with TemporalAnomalyIntelligenceLayer (Sprint 5) ([df82dff](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/commit/df82dffa15c8b79181c5d11c85bf4e9cebe62a9f))
* Wire individual detectors into TemporalAnomalyIntelligenceLayer + add basic Brier tracking ([5b1757c](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/commit/5b1757c1cb68caf0a1160aa1a042a7e0a8198b9f))

## [1.2.1](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/compare/v1.2.0...v1.2.1) (2026-06-10)


### Bug Fixes

* Make Sprint 5 detectors dependency-free (pure Python) to resolve CI failures ([f697082](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/commit/f6970823f39e71a35b0fe2c458e46418ddc28f04))

# [1.2.0](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/compare/v1.1.0...v1.2.0) (2026-06-10)


### Features

* Add full detector implementations for Sprint 5 (Evidential HDBSCAN, BOCPD, Neural Sticky Pitman-Yor, Online Variational HDP) ([311e3da](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/commit/311e3dadaca6134c99e34b60b244c6f3ea267fb0))

# [1.1.0](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/compare/v1.0.0...v1.1.0) (2026-06-10)


### Features

* Re-add Sprint 5 Temporal + Anomaly Intelligence Layer (post-merge recovery) - v2.2.0 ([6aa78f1](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/commit/6aa78f11fb29ba51da34505753c848a883b752c3))

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
