# Bug-finding automation memory

Tracked critical-bug reports only (open or rejected). No run history.

## Open

<<<<<<< HEAD
- **doctrine-failed-gates-seal** — `scripts/governance/run_doctrine_validator.py` `_build_summary` computed `seal_recommendation` before counting overlay/extended gate failures, and only inspected five base overlay governance gates. Extended gates (e.g. `overlay_risk_replay_gate`, `external_action_replay_gate`) could be `failed` while `status=ok`, `failed_count=0`, `seal_recommendation=seal`; base-gate failures could yield `status=failed` with `seal_recommendation=seal`. Fix on `cursor/doctrine-failed-gates-seal-c384`.
- `core/human_decision_ledger|continuity` + `core/manual_execution*` + sole-writers: empty upstream lists discarded and synthetic `status=passed` packets emitted with sentinel hashes; replay helpers regenerated the same — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1015 — status: open — recorded: 2026-07-26
=======
- **doctrine-failed-gates-seal** — `scripts/governance/run_doctrine_validator.py` `_build_summary` counted only five base overlay gates and computed `seal_recommendation` before failure counting; extended gate failures could leave `seal` — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1016
- **operator-spine-empty-upstream** — `core/operator_queue|review_resolution|external_action_proposals` + sole-writers: empty upstream lists discarded and synthetic `status=passed` packets emitted with sentinel hashes; replay helpers regenerated the same — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1018
>>>>>>> origin/main

## Rejected

(none)
