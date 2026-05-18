# P33 Continuity Degradation Explainer

- explainer_id: `continuity_degradation_explainer_001`
- final_status: `ADVISORY_DEGRADED`
- explanation_posture: `PRESSURE_PERSISTENCE`

## Dominant Degradation Vectors
- `CORRIDOR_PRESSURE_PERSISTENCE`
- `WEATHER_URGENCY_ALIGNMENT`
- `ROUTING_PRIORITY_ALIGNMENT`
- `UPSTREAM_BLOCKER_RECURRENCE`

## Reason Chain
- P32 corridor_status=PRESSURE_PERSISTENCE
- P32 pressure_persistence_detected=true
- P31 ledger_posture=STABLE
- P29 weather_posture=BLOCKED attention_urgency=CRITICAL
- P30 routing_posture=BLOCKED review_priority_posture=CRITICAL
- blocker_summary_count=3

## Blockers
- `source_missing:coherence_field_operator_surface`
- `source_missing:temporal_coherence_chain`
- `source_missing:temporal_upstream_evidence`
