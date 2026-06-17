# ABX Codegen Intelligence Spine Artifact Registry Integration Plan

- plan_id: ABX_CODEGEN_INTELLIGENCE_SPINE_ARTIFACT_REGISTRY_INTEGRATION_PLAN_001
- artifact_registry_integration_plan_status: ABX_CODEGEN_ARTIFACT_REGISTRY_INTEGRATION_PLAN_READY
- recommended_next_lane: NOT_COMPUTABLE
- safe_to_auto_continue: False
- execution_authority: False
- valid_for_implementation: False

## Artifact Types To Register
- ImprovementProposal.v1: PLANNING_ONLY (registration_authorized=False)
- ShadowImprovementReceipt.v1: PLANNING_ONLY (registration_authorized=False)
- CodegenOperatorDecisionRecord.v1: PLANNING_ONLY (registration_authorized=False)
- MetaGateAuthorizationRecord.v1: PLANNING_ONLY (registration_authorized=False)
- MetaGateChainSeal.v1: PLANNING_ONLY (registration_authorized=False)

## Registration Requirements
- timestamp_policy: Notion field named timestamp is represented as source_observed_timestamp; wall-clock generation time is forbidden for deterministic repo artifacts
- registration_write_authorized: False
