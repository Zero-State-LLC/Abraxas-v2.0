# P57 Operator Narrative Archive Chain Global Verification Sweep

- verification_id: `operator_narrative_archive_chain_global_verification_001`
- final_status: `GLOBAL_VERIFICATION_FAIL`
- verification_posture: `FAILED`
- verification_hash: `0fc9df3a84a92b1e9241d413e2b67d26eecdb889d126736d01b6334c17740c9d`

## Command Results
- `pytest -q` exit=`1` passed=`False` timed_out=`False` duration_ms=`206680`
- `pyright` exit=`0` passed=`True` timed_out=`False` duration_ms=`37431`
- `ruff check .` exit=`0` passed=`True` timed_out=`False` duration_ms=`33`
- `python scripts/run_artifact_regeneration.py --full --validation-only` exit=`0` passed=`True` timed_out=`False` duration_ms=`610`
- `python scripts/run_artifact_regeneration.py --check-drift` exit=`0` passed=`True` timed_out=`False` duration_ms=`537`

## Blockers
- `command failed: pytest -q`
- `p56 final_status invalid for sealed degraded continuity`
- `p56 stability_posture invalid for observed-blocker continuity`

## Governance Boundary
- `global_verification_only`: `True`
- `verification_receipt_only`: `True`
- `advisory_only`: `True`
- `read_only`: `True`
- `non_authoritative`: `True`
- `source_linked`: `True`
- `deterministic_receipt`: `True`
- `no_architecture_expansion`: `True`
- `readiness_claims_allowed`: `False`
- `execution_authority`: `False`
- `form_allowed`: `False`
- `forecast_authority`: `False`
- `mutation_allowed`: `False`
- `auto_approve`: `False`
- `distribution_claims_allowed`: `False`
- `script_allowed`: `False`
- `ui_command_authority`: `False`
- `html_script_allowed`: `False`
- `command_channel`: `False`
- `runtime_mutation_allowed`: `False`
- `package_created`: `False`
- `routing_change_allowed`: `False`
- `bidirectional_control`: `False`
- `authority_granted`: `False`
- `prediction_allowed`: `False`
- `trend_prediction_allowed`: `False`
- `recommendation_authority`: `False`
- `adaptive_behavior_allowed`: `False`
- `speculative_causation_allowed`: `False`
- `button_allowed`: `False`
- `inference_authority`: `False`
- `action_authority`: `False`
- `queue_mutation_allowed`: `False`
- `release_readiness_claimed`: `False`
- `command_authority`: `False`
- `canon_mutation_allowed`: `False`
- `external_fetch_allowed`: `False`
- `psychological_claims_allowed`: `False`
- `auto_execute`: `False`
