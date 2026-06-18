# ABX Artifact Lineage Registry Traceability Audit

- `audit_id`: `ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_001`
- `source_completion_plan`: `ABX_ARTIFACT_LINEAGE_REGISTRY_COMPLETION_PLAN_001`
- `recommended_next_plan`: `ABX_ARTIFACT_LINEAGE_REGISTRY_REPAIR_PLAN_001`
- `downstream`: `NOT_COMPUTABLE`
- `canon_status`: `ADVISORY_ONLY`

## Findings
- `detect_artifacts_with_outputs_but_no_registry_entry`: `PASS` (0 impacted)
- `detect_registry_entries_with_no_runner`: `PASS` (0 impacted)
- `detect_uppercase_Scripts_runner_discovery_gaps`: `PASS` (0 impacted)
- `detect_runner_paths_with_no_schema`: `PASS` (0 impacted)
- `detect_schemas_with_no_tests`: `PASS` (0 impacted)
- `detect_json_outputs_without_schema`: `PASS` (0 impacted)
- `detect_markdown_outputs_without_json_pair`: `DRIFT` (1 impacted)
- `detect_generated_outputs_with_no_notion_surface`: `NOT_COMPUTABLE` (8 impacted)
- `detect_docs_references_to_missing_artifacts`: `DRIFT` (23 impacted)
- `detect_generated_outputs_with_no_notion_surface`: `NOT_COMPUTABLE` (8 impacted)

## Unresolved Cases
- `notion_mapping_evidence_external_to_repo`
- `runner_to_schema_binding_heuristic_only`
