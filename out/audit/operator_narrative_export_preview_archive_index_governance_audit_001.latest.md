# P53 Operator Narrative Export / Preview Archive Index Governance Audit

- audit_id: `operator_narrative_export_preview_archive_index_governance_audit_001`
- final_status: `FAIL`
- audit_posture: `FAILED`
- audit_hash: `19e2e71d95323cbcdfa6a785d725c16f9a678b6dffbc20215bdce995b3da3860`

## Findings
- `FAIL` `HASH_INTEGRITY` manifest sha256 mismatch for readable file p49_static_preview_governance_audit_json
- `FAIL` `HASH_INTEGRITY` manifest sha256 mismatch for readable file p48_static_preview_markdown
- `FAIL` `HASH_INTEGRITY` manifest sha256 mismatch for readable file p48_static_preview_json
- `FAIL` `HASH_INTEGRITY` manifest sha256 mismatch for readable file p47_export_bundle_governance_audit_json

## Finding Counts
- `PASS`: `0`
- `WARN`: `0`
- `FAIL`: `4`

## Role Order Summary
- expected: `['p46_export_bundle_json', 'p46_export_bundle_markdown', 'p47_export_bundle_governance_audit_json', 'p47_export_bundle_governance_audit_markdown', 'p48_static_preview_json', 'p48_static_preview_markdown', 'p49_static_preview_governance_audit_json', 'p49_static_preview_governance_audit_markdown']`
- observed: `['p46_export_bundle_json', 'p46_export_bundle_markdown', 'p47_export_bundle_governance_audit_json', 'p47_export_bundle_governance_audit_markdown', 'p48_static_preview_json', 'p48_static_preview_markdown', 'p49_static_preview_governance_audit_json', 'p49_static_preview_governance_audit_markdown']`
- manifest_observed: `['p46_export_bundle_json', 'p46_export_bundle_markdown', 'p47_export_bundle_governance_audit_json', 'p47_export_bundle_governance_audit_markdown', 'p48_static_preview_json', 'p48_static_preview_markdown', 'p49_static_preview_governance_audit_json', 'p49_static_preview_governance_audit_markdown']`

## Governance Boundary
- `action_authority`: `False`
- `adaptive_behavior_allowed`: `False`
- `advisory_only`: `True`
- `archive_index_governance_audit_only`: `True`
- `audit_only`: `True`
- `authority_granted`: `False`
- `auto_approve`: `False`
- `auto_execute`: `False`
- `bidirectional_control`: `False`
- `button_allowed`: `False`
- `canon_mutation_allowed`: `False`
- `command_authority`: `False`
- `command_channel`: `False`
- `deterministic_audit`: `True`
- `distribution_claims_allowed`: `False`
- `execution_authority`: `False`
- `external_fetch_allowed`: `False`
- `forecast_authority`: `False`
- `form_allowed`: `False`
- `html_script_allowed`: `False`
- `inference_authority`: `False`
- `mutation_allowed`: `False`
- `non_authoritative`: `True`
- `package_created`: `False`
- `prediction_allowed`: `False`
- `psychological_claims_allowed`: `False`
- `queue_mutation_allowed`: `False`
- `read_only`: `True`
- `readiness_claims_allowed`: `False`
- `recommendation_authority`: `False`
- `routing_change_allowed`: `False`
- `runtime_mutation_allowed`: `False`
- `script_allowed`: `False`
- `source_linked`: `True`
- `speculative_causation_allowed`: `False`
- `trend_prediction_allowed`: `False`
- `ui_command_authority`: `False`
