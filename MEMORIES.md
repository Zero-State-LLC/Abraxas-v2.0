# Bug-finding automation memory

Tracked critical-bug reports only (open or rejected). No run history.

## Open

- **doctrine-failed-gates-seal** — `scripts/governance/run_doctrine_validator.py` `_build_summary` counted only five base overlay gates and computed `seal_recommendation` before failure counting; extended gate failures could leave `seal` — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1016
- **operator-spine-empty-upstream** — `core/operator_queue|review_resolution|external_action_proposals` + sole-writers: empty upstream lists discarded and synthetic `status=passed` packets emitted with sentinel hashes; replay helpers regenerated the same — branch `cursor/operator-spine-empty-upstream-c384`

## Rejected

(none)
