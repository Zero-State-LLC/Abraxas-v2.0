# P56 Operator Narrative Archive Chain Stability Receipt

- receipt_id: `operator_narrative_archive_chain_stability_receipt_001`
- final_status: `FAIL`
- stability_posture: `FAILED`
- stability_hash: `9e6e95f7d563579ea96abfca381e0f79b3c82da82d815a260cecc173dc68ca2b`

## Baseline Hashes
- `archive_index_hash`: `12809f78208673c1e6c8c855b4574ebc6af600faef93092f30a1ae2cbd35d57c`
- `archive_governance_audit_hash`: `c71a4431d269d0cfe224d30240ecc6b8716f67ffe0cfc053014034f74fb3e6a6`
- `archive_closure_hash`: `8204d552460d40e5cfcebd06cd6bbf370632b485eb4331a11f9207f88896b6c2`

## Replay Results
- replay `1`: p52=`cab10ce202cccb2e371e63efc2f7c417ba8fed37318e5a98604be0d5d235c56f` p53=`09e0cb4503ffd5f8c0749f3dc640eb6638230a722e947fb3ca1b93287478b490` p55=`8204d552460d40e5cfcebd06cd6bbf370632b485eb4331a11f9207f88896b6c2`
- replay `2`: p52=`cab10ce202cccb2e371e63efc2f7c417ba8fed37318e5a98604be0d5d235c56f` p53=`09e0cb4503ffd5f8c0749f3dc640eb6638230a722e947fb3ca1b93287478b490` p55=`8204d552460d40e5cfcebd06cd6bbf370632b485eb4331a11f9207f88896b6c2`
- replay `3`: p52=`cab10ce202cccb2e371e63efc2f7c417ba8fed37318e5a98604be0d5d235c56f` p53=`09e0cb4503ffd5f8c0749f3dc640eb6638230a722e947fb3ca1b93287478b490` p55=`8204d552460d40e5cfcebd06cd6bbf370632b485eb4331a11f9207f88896b6c2`

## Invariance Summary
- `archive_index_hash_stable`: `False`
- `archive_governance_audit_hash_stable`: `False`
- `archive_closure_hash_stable`: `True`

## Blockers
- `replay 1 archive_index_hash mismatch`
- `replay 1 audit_hash mismatch`
- `replay 2 archive_index_hash mismatch`
- `replay 2 audit_hash mismatch`
- `replay 3 archive_index_hash mismatch`
- `replay 3 audit_hash mismatch`

## Governance Boundary
- `stability_receipt_only`: `True`
- `advisory_only`: `True`
- `read_only`: `True`
- `non_authoritative`: `True`
- `source_linked`: `True`
- `deterministic_receipt`: `True`
- `replay_invariance_only`: `True`
- `blocker_preservation_checked`: `True`
- `html_script_allowed`: `False`
- `external_fetch_allowed`: `False`
- `action_authority`: `False`
- `runtime_mutation_allowed`: `False`
- `speculative_causation_allowed`: `False`
- `command_channel`: `False`
- `execution_authority`: `False`
- `readiness_claims_allowed`: `False`
- `auto_approve`: `False`
- `queue_mutation_allowed`: `False`
- `ui_command_authority`: `False`
- `routing_change_allowed`: `False`
- `adaptive_behavior_allowed`: `False`
- `forecast_authority`: `False`
- `mutation_allowed`: `False`
- `prediction_allowed`: `False`
- `recommendation_authority`: `False`
- `command_authority`: `False`
- `distribution_claims_allowed`: `False`
- `release_readiness_claimed`: `False`
- `script_allowed`: `False`
- `trend_prediction_allowed`: `False`
- `auto_execute`: `False`
- `form_allowed`: `False`
- `package_created`: `False`
- `psychological_claims_allowed`: `False`
- `authority_granted`: `False`
- `button_allowed`: `False`
- `inference_authority`: `False`
- `canon_mutation_allowed`: `False`
- `bidirectional_control`: `False`
