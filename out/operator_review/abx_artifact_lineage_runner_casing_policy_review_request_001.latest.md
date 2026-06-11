# ABX Artifact Lineage Runner Casing Policy Review Request

- `status`: `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_HELD`
- `artifact_id`: `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_REVIEW_REQUEST_001`
- `review_scope`: `RUNNER_CASING_POLICY_DECISION_ONLY`
- `impacted_runner_count`: `478`
- `runner_casing_policy_override_allowed`: `False`
- `runner_path_normalization_allowed`: `False`
- `execution_authority`: `False`
- `downstream_status`: `HELD_FOR_OPERATOR_POLICY_DECISION`
- `recommended_next_lane`: `ABX_ARTIFACT_LINEAGE_RUNNER_CASING_POLICY_DECISION_PLAN`

## Decision Options

- `KEEP_CASE_SENSITIVE_RUNNER_DISCOVERY`
- `AUTHORIZE_CASE_INSENSITIVE_RUNNER_EQUIVALENCE_POLICY`
- `AUTHORIZE_REPO_WIDE_RUNNER_PATH_NORMALIZATION_PLAN`
- `REQUEST_ADDITIONAL_RUNNER_CASE_EVIDENCE`

## Sample Impacted Runners

- `run_aal_viz_climate_motif_fusion_overlay.py`
- `run_aal_viz_geometric_renderer.py`
- `run_aal_viz_geometric_renderer_canvas.py`
- `run_aal_viz_geometric_renderer_contract_spec.py`
- `run_aal_viz_geometric_renderer_implementation_plan.py`
- `run_aal_viz_geometric_renderer_planning.py`
- `run_aal_viz_geometric_renderer_svg.py`
- `run_aal_viz_geometric_renderer_viewmodel_adapter_spec.py`
- `run_aal_viz_geometric_renderer_webgl.py`
- `run_aal_viz_geometric_renderer_wp001_implementation_boundary.py`
- `run_aal_viz_graph_render_packet.py`
- `run_aal_viz_ingest_projection_pack.py`
- `run_aal_viz_operator_climate_overlay.py`
- `run_aal_viz_pressure_motif_overlay.py`
- `run_aal_viz_runtime_projection.py`
- `run_abx_artifact_lineage_registry_completion_plan.py`
- `run_abx_artifact_lineage_registry_direct_repair_approval_dry_run.py`
- `run_abx_artifact_lineage_registry_direct_repair_approval_plan.py`
- `run_abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run.py`
- `run_abx_artifact_lineage_registry_direct_repair_approval_validation_plan.py`
- `run_abx_artifact_lineage_registry_direct_repair_batch.py`
- `run_abx_artifact_lineage_registry_direct_repair_completion_hold_plan.py`
- `run_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate.py`
- `run_abx_artifact_lineage_registry_direct_repair_execution_authorization_record.py`
- `run_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run.py`

## Blocked Actions

- `RUNNER_CASING_POLICY_OVERRIDE`
- `RUNNER_PATH_NORMALIZATION`
- `SCRIPT_DISCOVERY_SEMANTICS_CHANGE`
- `CANON_MUTATION`
- `RUNTIME_MUTATION`
- `QUEUE_MUTATION`
- `SCHEDULER_MUTATION`
