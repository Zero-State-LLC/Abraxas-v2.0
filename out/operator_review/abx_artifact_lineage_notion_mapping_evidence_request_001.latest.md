# ABX Artifact Lineage Notion Mapping Evidence Request

- `status`: `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD`
- `artifact_id`: `ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_001`
- `request_scope`: `NOTION_MAPPING_EVIDENCE_COLLECTION_ONLY`
- `impacted_output_count`: `8`
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

- `out/sync/v2_hygiene_future_phase_placeholder_audit`
- `out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit`
- `out/sync/v2_hygiene_phase1_foundation_backlog_plan`
- `out/sync/v2_hygiene_phase2_module_governance_readiness_audit`
- `out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan`
- `out/sync/v2_hygiene_schema_contract_readiness_audit`
- `out/sync/v2_hygiene_versioning_release_policy_readiness_audit`
- `out/sync/v2_live_notion_surface_reconciliation`

## Blocked Actions

- `NOTION_WRITEBACK`
- `GITHUB_WRITEBACK`
- `NOTION_MAPPING_COMPLETENESS_ASSERTION`
- `CANON_MUTATION`
- `RUNTIME_MUTATION`
- `QUEUE_MUTATION`
- `SCHEDULER_MUTATION`
