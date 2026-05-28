# P33 Continuity Degradation Explainer

- explainer_id: `continuity_degradation_explainer_001`
- final_status: `ADVISORY_DEGRADED`
- explanation_posture: `PRESSURE_PERSISTENCE`

## Dominant Degradation Vectors
- `CORRIDOR_PRESSURE_PERSISTENCE`
- `UPSTREAM_BLOCKER_RECURRENCE`

## Reason Chain
- P32 corridor_status=PRESSURE_PERSISTENCE
- P32 pressure_persistence_detected=true
- P31 ledger_posture=WATCH
- P29 weather_posture=WATCH attention_urgency=MEDIUM
- P30 routing_posture=WATCH review_priority_posture=MEDIUM
- blocker_summary_count=2

## Blockers
- `source_missing:coherence_field_operator_surface`
- `source_missing:operator_attention_weather`
