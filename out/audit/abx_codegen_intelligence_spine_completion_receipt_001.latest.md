# ABX Codegen Intelligence Spine Completion Receipt

- receipt_id: ABX_CODEGEN_INTELLIGENCE_SPINE_COMPLETION_RECEIPT_001
- spine_status: ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_COMPUTABLE
- observed_path_count: 20
- required_path_count: 20
- valid_for_execution: False
- valid_for_runtime_activation: False
- valid_for_canon_promotion: False
- Brier Score: 0.10

## Phase Merge Refs
- PHASE_1_CONTRACTS_CODEGEN_SCHEMAS: ee183d1d69539096f4cf1693966151b2b16d7835
- PHASE_2_CORE_CODEGEN_HARNESS: c730750d2846200ea9e05e9cbdb3dd20295ca771
- PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY: a69f87b08237da539e9dd09f02ed3ce7c64c58c1
- PHASE_4_META_GATE_OPERATOR_PROMOTION: 0cc01902ab06d4784755a6032d7bd292e2dcecc8
- PHASE_5_NOTION_RECONCILIATION_DRYRUN: c8ba08fb6c772309b974fc87c5f29557c97d8d26

## Required Paths
- contracts/codegen/__init__.py: OBSERVED
- contracts/codegen/models.py: OBSERVED
- contracts/codegen/validators.py: OBSERVED
- contracts/codegen/schemas/PatchContract.json: OBSERVED
- contracts/codegen/schemas/CodeDropEnvelope.json: OBSERVED
- contracts/codegen/schemas/MetaGateSeal.json: OBSERVED
- contracts/codegen/schemas/CodegenTaskPacket.json: OBSERVED
- contracts/codegen/schemas/ShadowReplayFixture.json: OBSERVED
- core/codegen/__init__.py: OBSERVED
- core/codegen/builder.py: OBSERVED
- core/codegen/runner.py: OBSERVED
- core/codegen/shadow_replay_harness.py: OBSERVED
- core/codegen/fixture_validation.py: OBSERVED
- core/codegen/meta_gate.py: OBSERVED
- core/codegen/notion_reconciliation.py: OBSERVED
- tests/contracts/test_codegen_contracts.py: OBSERVED
- tests/codegen/test_phase2_core_codegen_harness.py: OBSERVED
- tests/codegen/test_phase3_fixture_validation.py: OBSERVED
- tests/codegen/test_phase4_meta_gate.py: OBSERVED
- tests/codegen/test_phase5_notion_reconciliation.py: OBSERVED
