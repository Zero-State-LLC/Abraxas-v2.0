# Notion Patch Queue Terminal State

- terminal_state_id: NOTION_PATCH_QUEUE_TERMINAL_STATE_001
- terminal_state_status: QUEUE_TERMINAL_STATE_EMITTED_ADVISORY_ONLY
- queue_is_terminal: True
- terminal_reason: rune registry formalization plan recommended_next_patch is NOT_COMPUTABLE
- safe_to_auto_continue: False
- auto_patch_generation_allowed: False
- notion_writeback_allowed: False
- github_writeback_allowed: False
- recommended_next_patch: NOT_COMPUTABLE
- recommended_next_lane: NOT_COMPUTABLE

## Candidate Holds
- RUNE.PIPELINE.OPERATOR_REVIEW
- RUNE.PIPELINE.STABILIZATION_DECIDE
- RUNE.YGGDRASIL.ROUTE_RECEIPT
- RUNE.YGGDRASIL.UNKNOWN_NODE_GATE

## Blocked Actions
- AUTO_CREATE_NEXT_PATCH
- LIVE_NOTION_WRITEBACK
- GITHUB_PUSH_OR_PR_CREATION
- RUNE_REGISTRATION
- PIPELINE_OR_ROUTE_MUTATION
- RUNTIME_OR_SCHEDULER_MUTATION
- CANON_PROMOTION
