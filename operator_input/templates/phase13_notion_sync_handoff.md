# Phase 13 Notion Sync Handoff

This packet is documentation only. It is not a Notion writeback request, webhook
trigger, authorization record, evidence bundle, implementation request, mutation
request, activation request, promotion request, registration request, or execution
request.

## Files

- Sync packet output: `out/sync/phase13_notion_sync_packet_001.latest.json`
- Phase 13 entry receipt: `out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json`
- Continuity spine: `docs/status/continuity-spine.json`
- Preflight command: `python3 scripts/preflight_notion_phase13_sync_packet.py`
- Generator command: `python3 scripts/run_phase13_notion_sync_packet.py`

## Manual Operator Steps

1. Run the Phase 13 entry receipt generator if the receipt is stale:
   `python3 scripts/run_v2_hygiene_phase13_operator_intelligence_entry_receipt.py`
2. Run the Notion sync packet preflight:
   `python3 scripts/preflight_notion_phase13_sync_packet.py`
3. Open `out/sync/phase13_notion_sync_packet_001.latest.json`
4. Copy `spine_hash`, `phase13_receipt_hash`, `phase13_status`, and
   `operator_review_posture` into the operator's Notion review page manually.

## Authority Denials

- `notion_writeback_allowed: false`
- `github_writeback_allowed: false`
- `manual_operator_copy_paste_only: true`
- No bidirectional webhook sync in Phase 13
- No auto-writeback or durable Notion automation

## Do Not Change Authority Boundary

The packet must preserve:

- `operator_review_posture: ACTIVE`
- `downstream: NOT_COMPUTABLE`
- `advisory_only: true`
- `non_authoritative: true`
