# Operator Decision Record: Temporal + Anomaly Intelligence Layer (Sprint 5)

**Date:** 2026-06-10  
**Branch:** feature/sprint5-temporal-anomaly-layer  
**Status:** Ready for merge into main (PR #548)  
**Decision:** Approve integration of the new intelligence layer

## Summary
A unified, provenance-tagged temporal + anomaly intelligence layer has been wired into the existing `core/` architecture. This provides streaming-capable regime detection and evidential anomaly clustering for downstream forecasting, operator decision surfaces, and pipeline systems.

## Modules Integrated
- `core/anomaly/evidential_hdbscan_detector.py` — Density-based clustering with explicit vacuity (ignorance) modeling
- `core/temporal/bayesian_online_change_point_detector.py` — Bayesian online change-point / regime detection
- `core/clustering/neural_sticky_pitman_yor.py` — Discount-aware dynamic clustering with neural stickiness
- `core/clustering/online_variational_hdp.py` — Streaming hierarchical Dirichlet process clustering

## Integration Facade
`core/intelligence/temporal_anomaly_intelligence.py`

```python
from core.intelligence.temporal_anomaly_intelligence import TemporalAnomalyIntelligenceLayer

layer = TemporalAnomalyIntelligenceLayer(config={
    "hdbscan": {"vacuity_threshold": 0.35},
    "bocpd": {"hazard": 0.01},
    "pitman_yor": {"stickiness": 0.4},
})

result = layer.process_stream(data)  # returns change_points, anomalies, clusters, regime_labels + provenance
status = layer.get_status()
```

## Rationale
Extends the existing governance, artifact lineage, and operator decision systems with modern nonparametric streaming intelligence without disrupting prior structure. New directories keep the surface clean and modular.

## Provenance & Compatibility
- All outputs include `provenance` dicts consistent with repo conventions
- No breaking changes to existing `core/` modules
- Feature branch is strict superset of main

## Audit Notes
- Full audit performed 2026-06-10
- No merge conflicts expected
- All prior top-of-conversation work (governance, lineage, continuity, etc.) preserved
- Ready for continuation and merge

**Operator Authorization:** Approved for merge.
