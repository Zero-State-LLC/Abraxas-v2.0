# Bug-finding automation memory

Tracked critical-bug reports only (open or rejected). No run history.

## Open

- `core/research_cross_drop_conflict_scan.py`: non-dict `stabilization_proof_records` satisfied proof-id checks via `str(record)` while the scanner dropped them, yielding a false-clean P99 PASS (`scanned_drop_count=2`) that advanced P100/P101 — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1010 — status: open — recorded: 2026-07-26

## Rejected

(none)
