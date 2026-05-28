# P56 Operator Narrative Archive Chain Stability Receipt

- receipt_id: `operator_narrative_archive_chain_stability_receipt_001`
- final_status: `FAIL`
- stability_posture: `FAILED`
- stability_hash: `398da8d2261b4193e8ff6a29e119b36a4c86feef381d1d9dd803065db3f5e290`

## Baseline Hashes
- `archive_index_hash`: `824d91b2fdd5fcf264b12ecdb5fd5290ff7dd8ade64a817664c16b2c119efb96`
- `archive_governance_audit_hash`: `19e2e71d95323cbcdfa6a785d725c16f9a678b6dffbc20215bdce995b3da3860`
- `archive_closure_hash`: `06bcfecc23dc145dfd115559e03e4a45f7ce3c06f24524f73be6a888449a708b`

## Replay Results
- replay `1`: p52=`74e656ceecbbb07a8dc1807f57c375754dfaf18a8209375da2cd82c83516cc07` p53=`19e2e71d95323cbcdfa6a785d725c16f9a678b6dffbc20215bdce995b3da3860` p55=`06bcfecc23dc145dfd115559e03e4a45f7ce3c06f24524f73be6a888449a708b`
- replay `2`: p52=`74e656ceecbbb07a8dc1807f57c375754dfaf18a8209375da2cd82c83516cc07` p53=`19e2e71d95323cbcdfa6a785d725c16f9a678b6dffbc20215bdce995b3da3860` p55=`06bcfecc23dc145dfd115559e03e4a45f7ce3c06f24524f73be6a888449a708b`
- replay `3`: p52=`74e656ceecbbb07a8dc1807f57c375754dfaf18a8209375da2cd82c83516cc07` p53=`19e2e71d95323cbcdfa6a785d725c16f9a678b6dffbc20215bdce995b3da3860` p55=`06bcfecc23dc145dfd115559e03e4a45f7ce3c06f24524f73be6a888449a708b`

## Invariance Summary
- `archive_index_hash_stable`: `False`
- `archive_governance_audit_hash_stable`: `True`
- `archive_closure_hash_stable`: `True`

## Blockers
- `p53 PASS/CLEAN preservation violated`
- `p55 closure posture not sealed`
- `replay 1 archive_index_hash mismatch`
- `replay 2 archive_index_hash mismatch`
- `replay 3 archive_index_hash mismatch`

## Governance Boundary
- `stability_receipt_only`: `True`
- `advisory_only`: `True`
- `read_only`: `True`
- `non_authoritative`: `True`
- `source_linked`: `True`
- `deterministic_receipt`: `True`
- `replay_invariance_only`: `True`
- `blocker_preservation_checked`: `True`
- `authority_granted`: `False`
- `auto_execute`: `False`
- `command_authority`: `False`
- `runtime_mutation_allowed`: `False`
- `bidirectional_control`: `False`
- `button_allowed`: `False`
- `distribution_claims_allowed`: `False`
- `external_fetch_allowed`: `False`
- `auto_approve`: `False`
- `html_script_allowed`: `False`
- `speculative_causation_allowed`: `False`
- `canon_mutation_allowed`: `False`
- `script_allowed`: `False`
- `routing_change_allowed`: `False`
- `prediction_allowed`: `False`
- `queue_mutation_allowed`: `False`
- `recommendation_authority`: `False`
- `execution_authority`: `False`
- `package_created`: `False`
- `release_readiness_claimed`: `False`
- `adaptive_behavior_allowed`: `False`
- `trend_prediction_allowed`: `False`
- `forecast_authority`: `False`
- `psychological_claims_allowed`: `False`
- `form_allowed`: `False`
- `command_channel`: `False`
- `mutation_allowed`: `False`
- `inference_authority`: `False`
- `ui_command_authority`: `False`
- `readiness_claims_allowed`: `False`
- `action_authority`: `False`
