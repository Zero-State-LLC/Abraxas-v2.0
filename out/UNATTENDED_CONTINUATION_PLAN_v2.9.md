# Unattended Continuation Plan — v2.9 Decision-Aware Promotion Eligibility + Traceable Decision Ledger

**Owner**: Governed Operator (appliedalchemylabs)  
**Date**: 2026-07-11 (morning errands window)  
**Goal**: Advance abx-hermes-skill-evolution from current v2.8 baseline through v2.9 phases autonomously for 2–3 hours while operator is away.  
**Constraints** (mandatory):
- All Python/pytest commands use scrubbed environment:
  `env -i PATH="$PATH" HOME="$HOME" USER="$USER" UV_CACHE_DIR="$HOME/.cache/uv" uv run ...`
- Reference count must stay at exactly 3 (policy-only `Scripts/` refs in core lineage files).
- `active_skill_modified` must remain **False** at all times.
- No interactive input. No promotion/activation. Advisory/SHADOW only.
- Emit dated receipts in `out/audit/`.
- Preserve determinism and existing cycle artifacts.

## Current Baseline (verified at handoff)
- Refs: 3
- cycle_rc: 0
- active_modified: False
- live_traces: 16
- Decision ledger: present (v2.9)
- Validator: functional
- Pytest (abx evolution suite): 34/34 passing

## 5-Phase Unattended Workstream (v2.9)

**Phase 1 (Decision Ledger Consumption)**  
- Ensure promotion readiness assessor and gate read the new ledger.
- Emit updated readiness artifact that records `operator_decision_value`, `operator_decision_validated`, and any advisory impact.
- Update cycle receipt with ledger decision.

**Phase 2 (Decision-Aware Eligibility Gate)**  
- Light update to `abx_skill_promotion_gate_stub.py` or readiness logic to treat a VALIDATED `APPROVE_EXTENDED_OBSERVATION` as a positive signal (still advisory only).
- Produce a new `abx_hermes_decision_aware_eligibility_v2_9.latest.json`.

**Phase 3 (Targeted Tests + Ledger Tests)**  
- Add 4–6 new tests in `tests/test_abx_skill_evolution_decision_ledger.py` (happy path, drift detection, authority blocking, resume after ledger).
- Run full scrubbed `test_abx_skill_evolution*.py`.

**Phase 4 (Live Traces + Recurring Integration)**  
- Run multiple clean cycles to grow live_traces (target +8–12).
- Emit recurring lane recommendation that now references the decision ledger.
- Update SKILL.md with v2.9 progress.

**Phase 5 (Handoff Receipt + Re-audit)**  
- Final scrubbed re-audit (refs, active_modified, pytest, cycle).
- Emit `V2_9_UNATTENDED_COMPLETE.json` + `NEXT_CONTINUATION_AUDIT_v2.9.json`.
- Leave clear next-5-phase suggestion.

## Unattended Runner Script
Location: `scripts/run_unattended_abx_continuation.py`

Behavior:
- Runs 8 cycles (≈ 2h40m with 20min sleep).
- Each cycle:
  1. Scrubbed run of `scripts/codegen/run_abx_hermes_skill_evolution_cycle.py`
  2. Scrubbed refs count check
  3. Scrubbed targeted pytest (`tests/test_abx_skill_evolution*.py`)
  4. Ledger + validator quick sanity
  5. Emit `out/audit/unattended_cycle_00N_YYYYMMDD_HHMM.json`
- Sleeps 20 minutes between cycles.
- Logs to `logs/unattended_continuation_$(date +%Y%m%d_%H%M).log`
- Stops cleanly on any hard failure or after max cycles.
- Never touches active skill.

## How to Launch (before leaving)
```bash
mkdir -p logs out/audit
nohup env -i PATH="$PATH" HOME="$HOME" USER="$USER" UV_CACHE_DIR="$HOME/.cache/uv" \
  uv run python scripts/run_unattended_abx_continuation.py \
  > logs/unattended_$(date +%Y%m%d_%H%M).log 2>&1 &
echo $! > logs/unattended.pid
```

Monitor while away:
```bash
tail -f logs/unattended_*.log
# or
ls -l out/audit/unattended_*.json
```

Kill if needed:
```bash
kill $(cat logs/unattended.pid)
```

## Safety & Exit Criteria
- If refs != 3 → stop and emit blocker receipt.
- If active_modified == True → hard stop.
- If pytest fails on abx suite → stop.
- All decisions remain advisory. No promotion path is activated.

## Post-Errands Next Steps (for when you return)
1. `cat out/audit/V2_9_UNATTENDED_COMPLETE.json` (or latest receipt)
2. Run one manual scrubbed re-audit.
3. Decide on v2.10 (e.g. live brier consumption of operator decision, cross-surface with holler, or promotion simulation with decision present).

**Handoff timestamp**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Status**: Ready for unattended launch.
