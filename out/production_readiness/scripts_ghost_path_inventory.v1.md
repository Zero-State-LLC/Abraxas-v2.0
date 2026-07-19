# Scripts Ghost Path Inventory v1

- inventory_id: `SCRIPTS_GHOST_PATH_INVENTORY_001`
- produced_at: `2026-07-19T07:45:03Z`
- core/scripts hits: **15**
- tests hits: **145**
- unique missing basenames (core/scripts): **12**
- relocatable (core/scripts): **0**

## Policy

- Do **not** invent stub runners to silence strings.
- `MISSING_PLAN_ONLY`: historical/planned path; leave or annotate.
- `RELOCATABLE`: basename exists under a domain — rewrite reference.
- `TEST_FIXTURE_PLACEHOLDER`: synthetic names in tests — ignore.

## Core / scripts findings

| Kind | Source | Referenced path |
|------|--------|-----------------|
| MISSING_PLAN_ONLY | `core/abx_codegen_intelligence_spine_gap_analysis_plan.py` | `scripts/run_abx_codegen_intelligence_spine.py` |
| MISSING_PLAN_ONLY | `core/abx_codegen_intelligence_spine_module_surface_plan.py` | `scripts/run_codegen_contract_audit.py` |
| MISSING_PLAN_ONLY | `core/abx_codegen_intelligence_spine_module_surface_plan.py` | `scripts/run_codegen_handoff_packet.py` |
| MISSING_PLAN_ONLY | `core/belief_graph_engine_advisory_receipt_contract_plan.py` | `scripts/run_belief_graph_engine_advisory_receipt.py` |
| MISSING_PLAN_ONLY | `core/belief_graph_engine_advisory_receipt_implementation_plan.py` | `scripts/run_belief_graph_engine_advisory_receipt.py` |
| MISSING_PLAN_ONLY | `core/belief_graph_engine_advisory_receipt_implementation_plan.py` | `scripts/run_belief_graph_engine_advisory_receipt.py` |
| MISSING_PLAN_ONLY | `core/belief_graph_engine_advisory_spec_plan.py` | `scripts/run_belief_graph_engine_advisory_receipt.py` |
| MISSING_PLAN_ONLY | `core/generated_artifact_registry.py` | `scripts/run_temporal_coherence_evidence_restoration_planning.py` |
| MISSING_PLAN_ONLY | `core/global_ingest_separate_implementation_spec_plan.py` | `scripts/run_global_ingest_adapter_spine_implementation_spec.py` |
| MISSING_PLAN_ONLY | `core/global_pipeline_repo_execution_prep.py` | `scripts/run_global_operator_review_queue.py` |
| MISSING_PLAN_ONLY | `core/global_pipeline_repo_execution_prep.py` | `scripts/run_global_pipeline_repo_execution_prep.py` |
| MISSING_PLAN_ONLY | `core/heavy_tail_fixture_corpus_creation_receipt.py` | `scripts/run_heavy_tail_fixture_corpus_creation_receipt.py` |
| MISSING_PLAN_ONLY | `core/runtime_integration_gate_receipt.py` | `scripts/run_belief_graph_engine_advisory_spec_plan.py` |
| MISSING_PLAN_ONLY | `core/runtime_integration_gate_receipt.py` | `scripts/run_temporal_regime_transition_detector_contract.py` |
| MISSING_PLAN_ONLY | `core/sync/oracle_confidence_calibration_plan.py` | `scripts/run_oracle_confidence_calibration.py` |

## Unique missing basenames (core/scripts)

- `run_abx_codegen_intelligence_spine.py`
- `run_belief_graph_engine_advisory_receipt.py`
- `run_belief_graph_engine_advisory_spec_plan.py`
- `run_codegen_contract_audit.py`
- `run_codegen_handoff_packet.py`
- `run_global_ingest_adapter_spine_implementation_spec.py`
- `run_global_operator_review_queue.py`
- `run_global_pipeline_repo_execution_prep.py`
- `run_heavy_tail_fixture_corpus_creation_receipt.py`
- `run_oracle_confidence_calibration.py`
- `run_temporal_coherence_evidence_restoration_planning.py`
- `run_temporal_regime_transition_detector_contract.py`

## Regenerate

```bash
python scripts/tools/run_scripts_ghost_path_inventory.py
```

