# Operator Decision Record: Temporal + Anomaly Intelligence Layer (Sprint 5)

**Date:** 2026-06-10  
**Status:** Merged into main  
**Decision:** Approve integration of the new intelligence layer

## Summary
Unified provenance-tagged temporal + anomaly intelligence layer added to core/.

## Modules
- core/anomaly/evidential_hdbscan_detector.py
- core/temporal/bayesian_online_change_point_detector.py
- core/clustering/neural_sticky_pitman_yor.py + online_variational_hdp.py
- core/intelligence/temporal_anomaly_intelligence.py (facade)

## Integration
`TemporalAnomalyIntelligenceLayer.process_stream()` and `.get_status()`

**Ready for downstream pipelines.**
