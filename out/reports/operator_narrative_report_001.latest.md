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
- attention_urgency: `CRITICAL`
- review_priority_posture: `CRITICAL`
- routing_posture: `BLOCKED`
- weather_posture: `BLOCKED`

## Memory + Corridor
- section_id: `memory_corridor`
- status: `OBSERVED`
- source_refs: `operator_attention_ledger`, `operator_fatigue_corridor`
- corridor_final_status: `ADVISORY_DEGRADED`
- corridor_status: `PRESSURE_PERSISTENCE`
- ledger_final_status: `ADVISORY_ONLY`
- ledger_posture: `STABLE`

## Degradation + Climatology
- section_id: `degradation_climatology`
- status: `OBSERVED`
- source_refs: `continuity_degradation_explainer`, `operator_climatology_summary`
- climatology_posture: `PRESSURE_PERSISTENCE`
- dominant_degradation_vectors: `['CORRIDOR_PRESSURE_PERSISTENCE', 'WEATHER_URGENCY_ALIGNMENT', 'ROUTING_PRIORITY_ALIGNMENT', 'UPSTREAM_BLOCKER_RECURRENCE']`
- explanation_posture: `PRESSURE_PERSISTENCE`
- observed_distribution_summary: `{'blocker_count': 3, 'signal_family_count': 8, 'source_packet_count': 5}`

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
- fusion_final_status: `NOT_COMPUTABLE`
- fusion_posture: `NOT_COMPUTABLE`

## Blockers
- section_id: `blockers`
- status: `OBSERVED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `continuity_degradation_explainer`, `fusion_governance_audit`, `motif_governance_audit`, `operator_attention_ledger`, `operator_attention_weather`, `operator_climatology_summary`, `operator_fatigue_corridor`, `operator_load_seasonality`, `operator_review_routing_enhancer`, `pressure_motif_registry`
- blocker_count: `25`
- blocker_summary: `['edge reference source_node_id unresolved: climate.node.climatology', 'edge reference source_node_id unresolved: climate.node.corridor', 'edge reference source_node_id unresolved: climate.node.explainer', 'edge reference source_node_id unresolved: climate.node.ledger', 'edge reference source_node_id unresolved: climate.node.routing', 'edge reference source_node_id unresolved: climate.node.weather', 'edge reference source_node_id unresolved: motif.node.motif.motif.degradation_vector.corridor_pressure_persistence', 'edge reference target_node_id unresolved: climate.node.climatology', 'edge reference target_node_id unresolved: climate.node.corridor', 'edge reference target_node_id unresolved: climate.node.explainer', 'edge reference target_node_id unresolved: climate.node.ledger', 'edge reference target_node_id unresolved: climate.node.routing', 'edge reference target_node_id unresolved: motif.node.motif.motif.degradation_vector.corridor_pressure_persistence', 'missing required lineage ref p37_overlay_hash', 'missing source_hashes entry aal_viz_climate_motif_fusion_overlay', 'p37 governance flag advisory_only must be true', 'p37 governance flag non_authoritative must be true', 'p37 governance flag projection_only must be true', 'required source aal_viz_pressure_motif_overlay is missing', 'source_missing:aal_viz_pressure_motif_overlay', 'source_missing:coherence_field_operator_surface', 'source_missing:operator_attention_ledger', 'source_missing:operator_attention_weather', 'source_missing:temporal_coherence_chain', 'source_missing:temporal_upstream_evidence']`

## Governance Boundary
- section_id: `governance_boundary`
- status: `BOUNDARY_LOCKED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `continuity_degradation_explainer`, `fusion_governance_audit`, `motif_governance_audit`, `operator_attention_ledger`, `operator_attention_weather`, `operator_climatology_summary`, `operator_fatigue_corridor`, `operator_load_seasonality`, `operator_review_routing_enhancer`, `pressure_motif_registry`
- governance_summary: `{'report_only': True, 'advisory_only': True, 'non_authoritative': True, 'mutation_allowed': False, 'forecast_authority': False, 'readiness_claims_allowed': False}`

## Source Lineage
- section_id: `source_lineage`
- status: `OBSERVED`
- source_refs: `aal_viz_climate_motif_fusion_overlay`, `continuity_degradation_explainer`, `fusion_governance_audit`, `motif_governance_audit`, `operator_attention_ledger`, `operator_attention_weather`, `operator_climatology_summary`, `operator_fatigue_corridor`, `operator_load_seasonality`, `operator_review_routing_enhancer`, `pressure_motif_registry`
- source_hash_lineage: `{'weather_hash': '924f85c6fb1fb241e9177a7955bcfb01ac08b0aa854ccd7fece230c01af77e0f', 'enhancer_hash': '9111a71e2ef0c13212e812d3f87bbcab046a3886ccc9ab6baa76be31991b2f3a', 'ledger_hash': '62cc173c0b422146e61191a3845fde0298b0a13ec44f5695160868db4c862f38', 'corridor_hash': 'e3257596b4c67e32c86fd8a8cc2b465dc1c4b480e246e19d106d632fd1d1f22c', 'explainer_hash': '4626a3eb46511fb1e499344b9ec1b28bf6c15d77d40112af065c94ab139d3dcf', 'summary_hash': '8996b0a6ff331c699c69db5c60765a1ca52a0fe3181e04dd7f83db1705c8bfe4', 'registry_hash': 'be8670a84048615c9d0c640969ebd7b847bef658cecb02cafd889ddfcb7343c9', 'motif_audit_hash': 'eba3e0d191925e59b330bd53c0873a6d58f7b31cb50bca9ca2663937ee88a082', 'seasonality_hash': 'c8e9b1e31dd97959709c57e11090a18dad11bccb5cfed52db0209b785a18927f', 'fusion_hash': '65527afb9eea57a9037af4dfd8232df1447a073b3439487d5006f64a87c55210', 'fusion_audit_hash': '26efeee2c24f7410f5d6c080193c761491efd7fd4fe8bfe5f30add4f2b8c1e0a'}`
- source_hashes: `{'aal_viz_climate_motif_fusion_overlay': '3fa9549f1cd2942987b480a9bacb280742924f53cf7644dffdf90c0aa1a0ce41', 'continuity_degradation_explainer': 'ebb8c9a336aadf5c4a4b13464d2c0a96b786e58e2f5358c571d3675c765fbe3f', 'fusion_governance_audit': '02bbead79940767aae4cea97e814422ba31fc887fc154ff765b8477a2d923bbd', 'motif_governance_audit': '11382ca559be9b9ef77f6284661b44dfecf25d0d6d594ca47a459c3f9e53e95a', 'operator_attention_ledger': '0a744b8c46b8c2f00ff1b9e6e1a57ee112f5586a4d3bff7d7784dae05d7fa757', 'operator_attention_weather': '952d186c198185415f7c69cba996917fcf60aa81d6f824899855a0ef1f676fa9', 'operator_climatology_summary': '6f2f3bbd9585b6fbb3e6909ba33c9a32b9933d9dad75a281ec076e80e935d124', 'operator_fatigue_corridor': '519c635a5569eab06681faf2ac1a03efb3c5b857b025c2216af476f5fc9d3570', 'operator_load_seasonality': '4df598d249fb0f28e8a114ca10bc94571433ae7907ab3647b394e0bd1cc5e60e', 'operator_review_routing_enhancer': 'ba35bd8b00d995d3bbc01cbc579f0cffe9695316e4a19aea95bf364f524813c9', 'pressure_motif_registry': '5bc0eeec1cb29c2e49fbc098c0e2a4e05ddf02c9c14808e916f3fc2f9e2bcca2'}`
