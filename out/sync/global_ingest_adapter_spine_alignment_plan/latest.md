# Global Ingest Adapter Spine Alignment Plan

- plan_id: GLOBAL_INGEST_ADAPTER_SPINE_ALIGNMENT_PLAN_001
- plan_status: ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY
- patch_id: PATCH-ABX-GLOBAL-INGEST-ADAPTER-SPINE-ALIGNMENT-PLAN-001
- target_surface: Global Ingest Adapter Spine
- recommended_next_patch: NOT_COMPUTABLE
- recommended_next_action: Global Ingest operator decision and implementation spec chain are already observed; hold with implementation authority denied
- safe_to_auto_continue: False
- implementation_allowed: False
- notion_writeback_allowed: False
- github_writeback_allowed: False

## Observed Entrypoints
- scripts/ingest/run_ingest_once.py - single-run ingest entrypoint
- scripts/ingest/run_oracle_intake.py - oracle intake entrypoint

## Missing Paths
- core/oracle_signal.py

## Alignment Steps
- INGEST-ALIGN-001: Preserve existing ingest runners as observed entrypoints before any shared adapter contract.
- INGEST-ALIGN-002: Define core/oracle_signal.py as the future adapter-spine contract boundary.
- INGEST-ALIGN-003: Require a governed implementation decision before creating adapter code or routing hooks.

## Acceptance Gates
- INGEST-GATE-001: OPERATOR_DECISION_REQUIRED before core/oracle_signal.py creation
- INGEST-GATE-002: SEPARATE_IMPLEMENTATION_PR_REQUIRED before runner behavior changes
- INGEST-GATE-003: AUTHORITY_DENIED before route, scheduler, or runtime integration
