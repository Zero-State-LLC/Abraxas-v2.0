---
name: abx-hermes-skill-evolution
description: "Observes Abraxas operations, aggregates skill-performance evidence, detects recurring failure or inefficiency patterns, and generates versioned candidate skill patches for replay, canary evaluation, and operator-approved promotion. Never mutates active skills directly. Produces SkillEvolutionCandidate and SkillPatchCandidate artifacts only."
version: 0.1.0
author: Abraxas Governed Operator
license: Proprietary
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, hermes, skill-evolution, operation-trace, performance-ledger, replay, canary, promotion-gate, abraxas-ingest]
    related_skills: [abx-familiar-signal-forager, abraxas-repo-intel, abraxas-validation-routing, abraxas-automated-production-governance, abx-runes-yggdrasil-manager]
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# ABX Hermes Skill Evolution

Status: CANDIDATE / SHADOW, advisory only. Operations may generate
SkillEvolutionCandidate, SkillPatchCandidate and SkillMemoryCandidate artifacts;
they may not rewrite active skills, promote candidates, or authorize deployment.

## Bounded procedure
1. Select an explicit current checkout commit, task, trace corpus and output
   directory. Resolve missing evidence as NOT_COMPUTABLE; historical counts,
   ready states, old grants and prior process logs are not current evidence.
2. Normalize real OperationTrace inputs with source paths, content hashes,
   commands, outcomes and validation return codes. Separate synthetic replay
   fixtures from live data. No fabricated Brier/performance values.
3. Generate a minimal reversible candidate patch and rollback plan in an isolated
   shadow workspace. For stabilization use FAILURE.CLASS.* and only
   PATCH_MODE.MINIMAL_COMPATIBILITY_REPAIR, preserving public behavior by default.
4. Replay old vs candidate on explicitly frozen cases; then shadow-canary without
   replacing active skills. Compare regressions, false completions and measured
   cost. Missing metrics remain null, not zero. Brier applies only to genuinely
   settled forecasts, not deterministic code verification.
5. Present the immutable review packet to the human. Never fill human fields,
   force acknowledgments, rewrite the packet to make a decision validate, or
   reuse a historical grant. Require fresh explicit human CONFIRM bound to the
   full canonical review SHA-256. Any changed packet requires a new review.
6. Independently validate decision provenance, all required acknowledgments,
   identity, exact review binding and timestamp (within 24 hours, not future).
   This is record consistency, not cryptographic proof of human identity:
   keep decision intake under trusted operator control. A successful advisory
   decision grants no production, active replacement or automatic transition.
7. Verify freshly produced receipts and targeted tests. Stop on missing input,
   drift, invalid decisions, active_skill_modified != false or unauthorized write.

## Supported local check
```bash
python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_decision_safety.py -q
```
Tests use temporary synthetic decisions and do not request or synthesize real
operator approval. Human-only builder (run in a dedicated disposable checkout;
it writes checkout-local out/operator_input and .working state):
```bash
python skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_builder.py --interactive
```
Agents must not drive this prompt on behalf of a human. Independent validator:
`skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_validator.py`.
Use only the exact review at out/audit/abx_hermes_formal_operator_review_packet_v2_6.latest.json.
Do not treat the validator process exit alone as proof: require receipt status
VALIDATED and binding_verified true, all authority boundaries false.

## Legacy runner location / limitations
The moved runners are `scripts/codegen/run_abx_hermes_skill_evolution_cycle.py`
and `scripts/codegen/run_unattended_abx_continuation.py`. They are legacy,
checkout-bound workflows, not recommended smoke tests or implicit startup jobs.
They read and overwrite fixed out/audit artifacts and run synthetic/stub stages;
a zero exit or old receipt does not establish current live training success.
Do not launch unattended/nohup jobs from this skill. Before any explicitly
requested legacy run, inspect runner dependencies, isolate a disposable full
checkout, create logs and out/audit, capture actual subprocess return codes and
inventory/hash all newly written receipts; stop if prerequisite paths are missing.
The supported safety regression command above does not run these legacy cycles.

## Optional references
- `references/historical-notes.md`: quarantined obsolete logs, never authority.
- `references/bennett-weakness-hypothesis-2024.md`: research hypothesis; do not
  universalize a paper's limited formal assumptions into a mandatory optimizer.
