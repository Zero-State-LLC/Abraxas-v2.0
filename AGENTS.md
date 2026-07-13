# AGENTS OPERATING DOCTRINE

This repository uses **Governance V3** — implementation-first development with deterministic execution and preserved quality controls. See [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md).

## Development workflow

Routine engineering work:

```text
Feature Request → Code → Test → Commit → PR → Merge → Notion Update
```

Do **not** generate authorization, approval, review, eligibility, or seal packets for ordinary development work.

## Mandatory pre-change reads

Before proposing or making changes, coding agents should read:

1. [`README.md`](README.md)
2. [`PLANS.md`](PLANS.md)
3. [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md)

Consult `out/` artifacts when working on surfaces that depend on historical provenance or lineage.

## Preserved controls

- **Determinism:** preserve `canonical_hash` provenance and deterministic serialization.
- **Schema validation:** contract-bound surfaces must pass schema checks.
- **Artifact lineage:** maintain traceability between generators, outputs, and registry entries.
- **Testing:** run targeted tests for touched surfaces; run fast CI before PRs.
- **Changelog:** semantic-release updates `CHANGELOG.md` on merge to `main`.

## Test execution order

- Run targeted tests first for touched surfaces.
- Run broader/full tests only after targeted checks pass or when explicitly requested.
- If environment constraints block tests, record exact command failures without claiming success.

## Determinism and serialization rules

- Preserve deterministic serialization and hash behavior across packet/artifact writers.
- Never introduce wall-clock, UUID, filesystem-order, randomness, or network dependency into deterministic surfaces.
- Keep canonical ordering and stable field shapes intact.

## Governance and authority boundaries

- Keep SHADOW and FORECAST surfaces separated.
- Historical advisory/projection artifacts under `out/` retain their original locks — do not reinterpret them as live execution authorization.
- Do not fabricate evidence, fake data, or unverifiable claims.
- Brier scoring remains telemetry-only; do not resolve Brier outcomes or escalate authority locks.

## Failure and drift reporting

- Record broken surfaces explicitly; never hide or silently bypass them.
- Prefer fail-closed reporting with concrete blocker reasons.
- Do not fabricate artifact/test outcomes.

## CLI Operator Layer

Before asking an AI agent to inspect or modify the repo, prefer targeted CLI operators.

- `OP.SEARCH_SIGNAL`
- `OP.FIND_PATH`
- `OP.JSON_EXTRACT`
- `OP.YAML_EXTRACT`
- `OP.PR_CONTROL`
- `OP.DIFF_COMPRESS`
- `OP.REPO_PACK`
- `OP.STRUCTURAL_SEARCH`
- `OP.STATIC_SCAN`
- `OP.LOC_METRIC`

Rule: "Send AI the smallest complete evidence packet, not a full repo dump."

For full agentic coding, orchestration, autonomous loops, or loop engineering, load `@/abraxas-master-loop-workflow` (Jamon 0-18 + Anthropic 5-block loop engineering fused with Abraxas governance, Brier, provenance, runes, ingest-first, and structured workflow). It mandates this AGENTS.md router + all mandatory pre-change reads.


Reference: [`docs/workflows/cli-operator-layer.md`](docs/workflows/cli-operator-layer.md)

## Research canary spine-refresh isolation guardrail

**Rule:** Do NOT regenerate `out/research_canary_*` artifacts during a spine-refresh run unless the full canary chain (P128 source → P129 → P130) is intentionally replayed from a validated, current P128 source.

**Mechanism of failure:** Spine-refresh scripts can downgrade canary artifacts (`COMPLETE_AND_STABLE` → `NOT_COMPUTABLE`), triggering cascading CI failure.

**Correct procedure:**
- Run spine-refresh scripts in isolation, scoped only to the temporal-continuity chain.
- Before any spine-refresh, confirm that `out/research_canary_activation_readiness_evidence_record/latest.json` (P129) and `out/research_canary_final_activation_authorization_review/latest.json` (P130) will NOT be touched.
- If canary artifacts are accidentally degraded, restore from the last known good commit.

## Historical governance archive

P70–P130 continuity artifacts and `out/operator_review/*` surfaces are **archived project history**. They are preserved for provenance and audit but are **not required** for routine development.

For migration context, see [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md).

Historical notes (do not delete artifacts):
- Registry coverage repair chain (#681–#688) is sealed on `main`.
- Orphan output registry policy and Track A4b inclusion are sealed separately.
- Artifact-lineage direct repair chain is sealed.
- P130 research canary hold artifacts remain under `out/research_canary_*`.

If a user asks for audit/docs-only work, do not perform feature implementation.

## Temporal continuity P102 handoff (historical archive)

When working on sealed temporal-continuity repair lanes, consult these runners and outputs:

- P102A: `python scripts/run_temporal_continuity_p101_readiness_repair_plan.py` → `out/temporal_continuity_p101_readiness_repair_plan/latest.json`
- P102 compression audit: `python scripts/run_temporal_continuity_recursive_authorization_chain_compression_audit.py` → `out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json`
- P102B router: `python scripts/run_temporal_continuity_repair_execution_plan_router.py`
- P102C selected plan: `python scripts/run_temporal_continuity_selected_repair_execution_plan.py`

When `chain_recommendation` is `SEAL_RECURSIVE_AUTHORIZATION_CHAIN` or `COMPRESS_TO_GENERIC_TEMPLATE`, do not add another hand-written recursive authorization lane; route to the recommended P103 lane instead.

---

## PR validation discipline

Before opening or updating a PR, run:

```bash
python scripts/run_fast_ci.py
```

This enforces deterministic fast checks (artifact validation-only + drift, fast pytest subset, Ruff, Pyright) without full artifact regeneration.
Do not treat schedule/manual workflow runs as fast-ci substitutes; those are canon-validation lanes.

## Local pytest environment hygiene

Hermes shells can inherit `PYTHONPATH` / `PYTHONHOME` from the agent runtime and accidentally import the Hermes venv instead of the repo venv. If pytest starts failing in collection with imports resolving under `~/.hermes/hermes-agent/venv`, run repo tests with those variables cleared:

```bash
env -u PYTHONPATH -u PYTHONHOME uv run pytest tests/test_*.py
```

Use the same environment scrub when debugging collection failures so the result reflects the repo workspace, not the assistant runtime.

## Cross-platform script imports

The canonical package path for new code is lowercase `scripts.*`. Legacy mixed-case `Scripts.*` imports are still accepted for compatibility because this repo is regularly used across devices and filesystems with different case-sensitivity behavior. Prefer `scripts.*` in new edits, but keep the compatibility shim until all consumers are safely migrated.
