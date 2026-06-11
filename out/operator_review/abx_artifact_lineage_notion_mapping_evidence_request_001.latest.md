# ABX Artifact Lineage Notion Mapping Evidence Request

- `status`: `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD`
- `artifact_id`: `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_001`
- `request_scope`: `NOTION_MAPPING_EVIDENCE_COLLECTION_ONLY`
- `impacted_output_count`: `30`
- `notion_writeback_allowed`: `False`
- `notion_completeness_claim_allowed`: `False`
- `execution_authority`: `False`
- `downstream_status`: `HELD_FOR_EVIDENCE`
- `recommended_next_lane`: `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_COLLECTION_PLAN`

## Required Evidence Fields

- `notion_page_id_or_url`
- `notion_surface_title`
- `mapped_repo_output_family`
- `evidence_capture_method`
- `operator_or_import_receipt_id`

## Impacted Outputs

- `out/sync/abx_artifact_lineage_registry_completion_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_approval_dry_run`
- `out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run`
- `out/sync/abx_artifact_lineage_registry_direct_repair_approval_validation_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_batch`
- `out/sync/abx_artifact_lineage_registry_direct_repair_completion_hold_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run`
- `out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_dry_run`
- `out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_validation_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run`
- `out/sync/abx_artifact_lineage_registry_direct_repair_implementation_plan`
- `out/sync/abx_artifact_lineage_registry_direct_repair_validation_dry_run`
- `out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan`
- `out/sync/abx_artifact_lineage_registry_repair_execution_plan`
- `out/sync/abx_artifact_lineage_registry_repair_plan`
- `out/sync/abx_artifact_lineage_registry_traceability_audit`
- `out/sync/global_ingest_adapter_spine_alignment_plan`
- `out/sync/notion_operator_decision_backlog`
- `out/sync/notion_patch_queue_terminal_state`
- `out/sync/notion_spec_completion_queue`
- `out/sync/notion_writeback_authorization_gate`
- `out/sync/notion_writeback_dry_run_plan`
- `out/sync/oracle_confidence_calibration_contract_dry_run`

## Blocked Actions

- `NOTION_WRITEBACK`
- `GITHUB_WRITEBACK`
- `NOTION_MAPPING_COMPLETENESS_ASSERTION`
- `CANON_MUTATION`
- `RUNTIME_MUTATION`
- `QUEUE_MUTATION`
- `SCHEDULER_MUTATION`
