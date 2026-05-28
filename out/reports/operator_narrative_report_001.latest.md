# P42 Operator Narrative Report

- report_id: `operator_narrative_report_001`
- final_status: `REPORT_DEGRADED`
- report_posture: `DEGRADED`

## Executive Signal State
- section_id: `executive_signal_state`
- status: `REPORT_DEGRADED`
- source_refs: `fusion_governance_audit`
- final_status: `REPORT_DEGRADED`
- p41_final_status: `NOT_COMPUTABLE`
- report_posture: `DEGRADED`

## Weather + Routing
- section_id: `weather_routing`
- status: `OBSERVED`
- source_refs: `operator_attention_weather`, `operator_review_routing_enhancer`
- attention_urgency: `MEDIUM`
- review_priority_posture: `CRITICAL`
- routing_posture: `BLOCKED`
- weather_posture: `WATCH`

## Memory + Corridor
- section_id: `memory_corridor`
- status: `OBSERVED`
- source_refs: `operator_attention_ledger`, `operator_fatigue_corridor`
- corridor_final_status: `ADVISORY_DEGRADED`
- corridor_status: `PRESSURE_PERSISTENCE`
- ledger_final_status: `NOT_COMPUTABLE`
- ledger_posture: `BLOCKED`

## Degradation + Climatology
- section_id: `degradation_climatology`
- status: `OBSERVED`
- source_refs: `continuity_degradation_explainer`, `operator_climatology_summary`
- climatology_posture: `PRESSURE_PERSISTENCE`
- dominant_degradation_vectors: `['CORRIDOR_PRESSURE_PERSISTENCE', 'WEATHER_URGENCY_ALIGNMENT', 'ROUTING_PRIORITY_ALIGNMENT', 'UPSTREAM_BLOCKER_RECURRENCE']`
- explanation_posture: `PRESSURE_PERSISTENCE`
- observed_distribution_summary: `{'blocker_count': 4, 'signal_family_count': 8, 'source_packet_count': 5}`

## Motifs + Motif Governance
- section_id: `motifs_motif_governance`
- status: `OBSERVED`
- source_refs: `motif_governance_audit`, `pressure_motif_registry`
- motif_count: `29`
- motif_governance_final_status: `NOT_COMPUTABLE`
- motif_governance_posture: `NOT_COMPUTABLE`
- registry_posture: `PRESSURE_PERSISTENCE`

## Seasonality
- section_id: `seasonality`
- status: `OBSERVED`
- source_refs: `operator_load_seasonality`
- recurrence_summary: `{'pressure_persistence_observed': True, 'repeated_class_count': 10, 'source_packet_count': 6}`
- seasonality_final_status: `ADVISORY_DEGRADED`
- seasonality_posture: `PRESSURE_PERSISTENCE`

## Fusion Overlay + Fusion Governance
- section_id: `fusion_overlay_fusion_governance`
- status: `OBSERVED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `fusion_governance_audit`
- fusion_audit_final_status: `NOT_COMPUTABLE`
- fusion_audit_posture: `NOT_COMPUTABLE`
- fusion_final_status: `PROJECTION_DEGRADED`
- fusion_posture: `PRESSURE_PERSISTENCE`

## Blockers
- section_id: `blockers`
- status: `OBSERVED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `continuity_degradation_explainer`, `fusion_governance_audit`, `motif_governance_audit`, `operator_attention_ledger`, `operator_attention_weather`, `operator_climatology_summary`, `operator_fatigue_corridor`, `operator_load_seasonality`, `operator_review_routing_enhancer`, `pressure_motif_registry`
- blocker_count: `29`
- blocker_summary: `['edge reference source_node_id unresolved: climate.node.climatology', 'edge reference source_node_id unresolved: climate.node.corridor', 'edge reference source_node_id unresolved: climate.node.explainer', 'edge reference source_node_id unresolved: climate.node.ledger', 'edge reference source_node_id unresolved: climate.node.routing', 'edge reference source_node_id unresolved: climate.node.weather', 'edge reference source_node_id unresolved: motif.node.motif.motif.degradation_vector.corridor_pressure_persistence', 'edge reference target_node_id unresolved: climate.node.climatology', 'edge reference target_node_id unresolved: climate.node.corridor', 'edge reference target_node_id unresolved: climate.node.explainer', 'edge reference target_node_id unresolved: climate.node.ledger', 'edge reference target_node_id unresolved: climate.node.routing', 'edge reference target_node_id unresolved: motif.node.motif.motif.degradation_vector.corridor_pressure_persistence', 'missing required lineage ref p37_overlay_hash', 'missing source_hashes entry aal_viz_climate_motif_fusion_overlay', 'p36 governance flag advisory_only must be true', 'p36 governance flag non_authoritative must be true', 'p36 governance flag projection_only must be true', 'p37 governance flag advisory_only must be true', 'p37 governance flag non_authoritative must be true', 'p37 governance flag projection_only must be true', 'registry source_hash_lineage missing or not object', 'required source aal_viz_pressure_motif_overlay is missing', 'required source pressure_motif_registry is missing', 'source_missing:coherence_field_operator_surface', 'source_missing:operator_attention_ledger', 'source_missing:operator_attention_weather', 'source_missing:temporal_coherence_chain', 'source_missing:temporal_upstream_evidence']`

## Governance Boundary
- section_id: `governance_boundary`
- status: `BOUNDARY_LOCKED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `continuity_degradation_explainer`, `fusion_governance_audit`, `motif_governance_audit`, `operator_attention_ledger`, `operator_attention_weather`, `operator_climatology_summary`, `operator_fatigue_corridor`, `operator_load_seasonality`, `operator_review_routing_enhancer`, `pressure_motif_registry`
- governance_summary: `{'report_only': True, 'advisory_only': True, 'non_authoritative': True, 'mutation_allowed': False, 'forecast_authority': False, 'readiness_claims_allowed': False}`

## Source Lineage
- section_id: `source_lineage`
- status: `OBSERVED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `continuity_degradation_explainer`, `fusion_governance_audit`, `motif_governance_audit`, `operator_attention_ledger`, `operator_attention_weather`, `operator_climatology_summary`, `operator_fatigue_corridor`, `operator_load_seasonality`, `operator_review_routing_enhancer`, `pressure_motif_registry`
- source_hash_lineage: `{'weather_hash': 'bea12a5215f702ff93da07d2e2806a527cca8d1af2d0bcbade0dde113fee8d3e', 'enhancer_hash': '9111a71e2ef0c13212e812d3f87bbcab046a3886ccc9ab6baa76be31991b2f3a', 'ledger_hash': '1e109aa815028d916a3445f30d758862ac1a263d9087e245096b81a3f3cdd498', 'corridor_hash': '274d9fe3dac707e26637293558c0381f563cff9bf5141ca9360b5ed89575745b', 'explainer_hash': '4626a3eb46511fb1e499344b9ec1b28bf6c15d77d40112af065c94ab139d3dcf', 'summary_hash': 'c09ae18ea9e03229599f702e549aafbd59f585111b147886123ceba9408f6ce9', 'registry_hash': 'f4c15ac9f1fd0194536a73752903bbb24296c57bf716eec22c55986351ece9df', 'motif_audit_hash': '0ced29af14c78762934adbdff74297a5ea07902a51164f9c3316e0f0b882e0bd', 'seasonality_hash': '8ac81a94458112bdee752a474df0fe79babdc21214cc40cfe476ef2cd2fd6e4f', 'fusion_hash': '3de09b185e61775f399b2a684288226652e8c60c96abbc038e8c6593c19d1c63', 'fusion_audit_hash': '116223861abeaffc1d1c7c49c5bc39b6649918b9c2201fb0e5372bceca9b2743'}`
- source_hashes: `{'aal_viz_climate_motif_fusion_overlay': '452f9018b50cc273552e9791dd4bd0f942cdaa8b1cd5746250ced20e0d471372', 'continuity_degradation_explainer': 'ebb8c9a336aadf5c4a4b13464d2c0a96b786e58e2f5358c571d3675c765fbe3f', 'fusion_governance_audit': '9a6672cf3f3c606cb33cbc44ab8f070daff3f40bc865ce4d0d92adf83219e7ca', 'motif_governance_audit': '30858a41788b929ab40c7185a88933a6ffa7abe45cad01745f470026eb9a2af1', 'operator_attention_ledger': '4ad6c2787e47dcaf371201ae57fb4842e02c2769a851e4bff4f764b642f8689c', 'operator_attention_weather': '08999f29d42ba89f18f71ef2ea8d493212473c9a188598b420dd564b8f53f397', 'operator_climatology_summary': '4e78a831ddc5fdd80630966309a4fb73a9f90cf23012fb5a825328abbf36d6ad', 'operator_fatigue_corridor': 'd0dc92534ebea50c7cf7f34d19f7ccd38700f4c256b65df0108aa8e9dc6622bd', 'operator_load_seasonality': 'd9066f681a2601470316f952835770db5ad026b4ac5b4855c029cc1120552217', 'operator_review_routing_enhancer': 'ba35bd8b00d995d3bbc01cbc579f0cffe9695316e4a19aea95bf364f524813c9', 'pressure_motif_registry': '6e093b3c99bb36e2233268bda738ae68a9dad2d262c96e92807d3cc20b1bfbe9'}`
