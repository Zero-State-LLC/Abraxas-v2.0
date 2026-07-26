# Bug-finding automation memory

Tracked critical-bug reports only (open or rejected). No run history.

## Open

- **doctrine-failed-gates-seal** — `scripts/governance/run_doctrine_validator.py` `_build_summary` computed `seal_recommendation` before counting overlay/extended gate failures, and only inspected five base overlay governance gates. Extended gates (e.g. `overlay_risk_replay_gate`, `external_action_replay_gate`) could be `failed` while `status=ok`, `failed_count=0`, `seal_recommendation=seal`; base-gate failures could yield `status=failed` with `seal_recommendation=seal`. Fix on `cursor/doctrine-failed-gates-seal-c384`.

## Rejected

(none)
