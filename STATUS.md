# ABRAXAS Repository Status

> **Last Updated:** 2026-07-23 — repository/Notion convergence and bounded activation policy

This document is the current human- and agent-readable operational snapshot for Abraxas v2.0. GitHub `main` governs implementation and merge evidence. Notion governs architecture, registered state, and operator-facing context.

## Current engineering posture

| Area | Current state | Evidence / boundary |
|---|---|---|
| Governance | **Governance V3 — ACTIVE** | Implementation-first; see [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md) |
| Local development | `DEV_ACTIVATION_ALLOWED` | Tests and reproducibility remain mandatory |
| Sandbox execution | `SANDBOX_ACTIVATION_ALLOWED` | Must be isolated, observable, and reversible |
| Internal canary | `INTERNAL_CANARY_CONDITIONAL` | Requires commit-specific validation, rollback, bounded credentials, and observability |
| External production | `EXTERNAL_PRODUCTION_OPERATOR_GATED` | Requires explicit operator approval and environment-specific evidence |
| Canon mutation | **Not implied by execution** | Promotion and authority remain separately governed |
| SHADOW → FORECAST | **No automatic escalation** | Explicit evidence and promotion remain required |

The bounded activation policy is defined in [`docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md`](docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md).

## July 23 integration baseline

| Surface | Status | Evidence |
|---|---|---|
| Soft Facades (`core/hygiene/`) | **MERGED** · optional observability only | PRs #990–#994 |
| YGGDRASIL full catalog IDs | **MERGED** | PR #993 |
| YGGDRASIL scan route pilot | **MERGED** on `universal_ingest` | PR #995 |
| `ConflictReport.v1` builder | **MERGED** · detection only | PR #996 |
| Oracle intake conflict population | **MERGED** · no auto-resolution | PR #997 |
| Research cross-drop conflict dimensions | **MERGED** · advisory | PR #998 |
| Repo ↔ Notion convergence and bounded activation | **MERGED** | PR #999 |
| MemEIC compositional-memory assimilation | **IN REVALIDATION** | PR #986; fast CI must pass before merge |
| Oracle compositional-memory adapter | **DEPENDENCY-BLOCKED** | PR #987; retarget to `main` only after #986 merges |
| Multi-agent artifact metadata | **RECONCILED / DRAFT** | PR #989; executable companion only, no competing prose contract |

## Conflict doctrine

```text
Detect → Classify → Operator disposition
```

Conflict surfaces do not auto-select winners, auto-merge contradictory claims, or grant authority.

## CI health

CI statements are commit-specific rather than universal.

- `main` is the implementation baseline.
- Each PR must be evaluated using its own workflow run and head SHA.
- Fast CI validates artifact drift, filtered pytest, and Ruff; additional workflows may include CodeQL, Dependency Review, security scans, AAL-Viz checks, and canon validation.
- A passing historical run does not prove a newer branch is green.
- PR #986 remains blocked while its current fast-CI run is failing.

Do not describe CI/CD as unconditionally “excellent” without naming the commit or workflow evidence being evaluated.

## Production-candidate evidence

Historical production-readiness artifacts remain available under [`out/production_readiness/`](out/production_readiness/), including:

- [`docs/production_readiness/ENGINEERING_GUIDEBOOK.md`](docs/production_readiness/ENGINEERING_GUIDEBOOK.md)
- [`out/production_readiness/ws8/release_decision.v1.json`](out/production_readiness/ws8/release_decision.v1.json)
- [`out/production_readiness/ws8/candidate_deploy_readiness.v1.json`](out/production_readiness/ws8/candidate_deploy_readiness.v1.json)

These artifacts are evidence snapshots, not permanent global locks. Under the bounded activation model:

- local development and sandbox activation are permitted;
- internal canaries are conditionally permitted;
- external production remains separately operator-gated.

Candidate status, merge status, runtime activation, and external deployment are distinct states.

## Preserved engineering invariants

Routine engineering does not require new authorization packets or procedural seal chains. The following controls remain mandatory:

- deterministic serialization and canonical hashes;
- provenance and artifact lineage;
- schema validation for contract-bound surfaces;
- targeted tests for touched behavior;
- commit-specific CI evidence;
- rollback for stateful or destructive changes;
- no fabricated data or unverifiable evidence;
- no producer identity–based authority escalation.

## Grok + Codex cooperative engineering

Grok, Codex, human, mixed, and imported contributions are peer provenance classes within one architecture.

- Producer identity records lineage; it does not establish precedence.
- Overlapping work is reconciled through tests, current operator intent, existing canon, and implementation evidence.
- Valid Grok-authored surfaces must not be wrapped, replaced, or duplicated merely because a Codex implementation exists.
- Machine-readable metadata may complement the canonical prose contract but may not fork it.

## Hygiene and authority boundaries

The v2 hygiene layer includes OBSERVED / INFERRED / SPECULATIVE registers, provenance enforcement, loop-awareness, hyperstition tagging, adversarial audit surfaces, and optional Soft Facade receipts.

Unless explicitly promoted elsewhere:

- hygiene receipts are advisory;
- projection surfaces do not grant authority;
- SHADOW outputs remain shadow context;
- execution does not mutate canon;
- internal activation does not imply external deployment.

## Historical governance archive

The P70–P130 continuity chain and related `out/operator_review/` surfaces are preserved as historical governance research. They are not prerequisites for routine Governance V3 engineering unless a current task explicitly reactivates one of those contracts.

Known historical archive findings, including temporal-chain gaps and legacy global-verification failures, remain provenance records rather than blanket blockers on unrelated development.

## Update rule

Update this file after material architecture, activation-policy, release, CI, or subsystem-state changes. Use live GitHub evidence for implementation claims and synchronize material registered-state changes to the existing Notion canon surfaces without creating duplicate page hierarchies.
