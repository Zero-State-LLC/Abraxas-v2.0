# ABRAXAS Repository Status

> **Last Updated:** 2026-06-18

This document provides a high-level operational status of the Abraxas v2.0 repository. It is intended to be human- and agent-readable.

## Current Development State (Governance V3)

| Area | Status | Notes |
|------|--------|-------|
| Governance model | **Governance V3 — ACTIVE** | Implementation-first development |
| Workflow | Feature → Code → Test → Commit → PR → Merge → Notion Update | See [`GOVERNANCE_V3.md`](GOVERNANCE_V3.md) |
| Preserved controls | Provenance, lineage, schema validation, testing, changelog | Mandatory for all changes |
| CI/CD | Excellent | Fast CI passes on `main` |
| Product version | **2.5.0** | PR #710–#716 merged — see [`docs/releases/PRODUCT_2_5_0_RELEASE_READY.md`](docs/releases/PRODUCT_2_5_0_RELEASE_READY.md) |
| Documentation | Updated | Migration receipt: [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md) |

## v2.0 Hygiene Compliance (Product 2.5.0)

This repository implements the v2 hygiene foundation under `abraxas/v2/` with advisory-only posture.

- **Registers:** OBSERVED, INFERRED, SPECULATIVE output tiers on high-signal surfaces
- **Loop dynamics:** `loop_dynamics` assessment with `loop_dynamics_assessment_complete` coverage in hygiene runes
- **Hyperstitional charge:** `hyperstitional_charge` metadata with `hyperstitional_charge_evaluated` tagging via `RUNE.HYPERSTITION_TAG`
- **v2 modules registered:** Retrocausal Hygiene, Output Schema Enforcer, Self-Adversarial Loop, Hyperstition Evaluator (see `V2_MODULE_REGISTRY` in `core/pipelines/registry.py`)
- **v2 runes documented:** `RUNE.LOOP_AWARENESS`, `RUNE.HYPERSTITION_TAG`, `RUNE.PROVENANCE_ENFORCE`, `RUNE.ADVERSARIAL_AUDIT`, `RUNE.OUTPUT_REGISTER_ENFORCE` in `contracts/runes/catalog.v1.json`
- **Core Directive:** [Abraxas v2.0 Core Directive](https://www.notion.so/) linked from projection surfaces
- **Projection notes:** v2.0 compliance and freshness sync documented on STATUS and README
- **Authority:** advisory-only; no execution authority, canon mutation, or forecast routing

**Development model:**

```yaml
development_model: implementation_first
governance_mode: DEVELOPMENT_ACCELERATION
status: active
```

Routine engineering work does **not** require authorization packets, approval chains, execution eligibility gates, or operator decision artifacts before implementation.

## CI Health Summary

Fast CI (`run_fast_ci.py`) passes on `main` for filtered pytest, drift, ruff, and pyright. Full unfiltered pytest runs green after writer-test isolation (post-#706). P57 global verification hash drift and P64 manifest gate remain historical archive blockers documented below — they do not block routine development under Governance V3.

## Current Overall State

| Area                    | Status          | Last Major Change                              | Notes |
|-------------------------|-----------------|------------------------------------------------|-------|
| CI/CD Stability         | Excellent       | Reusable workflows + cleanup of all temp flags | Very clean and efficient |
| Governance              | Governance V3   | GOVERNANCE_SIMPLIFICATION_001                  | Implementation-first |
| Automation & Tooling    | Excellent       | organize_scripts.py + completions + benchmarks | Strong tooling + performance testing |
| Security Posture        | Strong          | CodeQL + Dependency Review blocking            | Proper gates |
| Documentation           | Excellent       | Governance V3 migration                        | See GOVERNANCE_V3.md |
| Release Process         | Excellent       | Full semantic-release with release.config.js   | Fully automated |

## Governance & Process

- Implementation-first development under Governance V3
- Preserved: determinism, schema validation, artifact lineage, testing, changelog
- Strong tooling ecosystem and CLI operator layer
- Fully automated semantic release process

## How Releases Work

Pushes to `main` following Conventional Commits will automatically:
- Analyze commits and determine next version
- Update CHANGELOG.md
- Commit the changelog back to the repository
- Create Git tag and GitHub Release

---

## Historical Governance Archive

*Archived reference — not required for routine development.*

The P70–P130 continuity chain and related operator review surfaces are preserved as project history under `out/`. They document the prior procedural governance model (FROZEN / ADVISORY_ONLY pre-implementation gates).

```yaml
P70-P130:
  status: HISTORICAL
  purpose: governance_research_archive
```

### Prior governance boundary (archived)

The repo previously maintained an advisory-only continuation state with operator hold frontiers. Historical artifacts remain at their original paths:

- `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` — P95 seal review (held)
- `out/research_canary_final_activation_authorization_review/latest.json` — P130 research canary (held)
- `out/operator_review/*` — v2 hygiene and operator review surfaces
- `out/audit/governance_freeze_baseline_001.latest.json` — prior FROZEN baseline

### Operator Hold Ledger (archived reference)

| Frontier | Artifact | Historical disposition |
|----------|----------|------------------------|
| P95 temporal seal review | `out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json` | Held for operator — archived |
| P102F operator decision reconciliation | `out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json` | Held — archived |
| P130 research canary | `out/research_canary_final_activation_authorization_review/latest.json` | Formal hold preserved — archived |
| Runtime integration dry-run review | `out/audit/runtime_integration_gate_operator_review_dry_run_review_001.latest.json` | External operator attestation — archived |
| v2 hygiene phase1 compression audit | `out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json` | Terminal hold — archived |

### Archive technical debt (observation-only)

- P55/P56/P67/P68 narrative archive degradation persists (`GLOBAL_VERIFICATION_FAIL`)
- Missing `out/audit/temporal_coherence_chain_001.latest.json` remains a blocking upstream input for historical P77/P78 lanes
- P64 manifest gate runs with `continue-on-error` until atomic P52→P57→P64 re-seal
- Archive repair and `run_temporal_coherence_chain.py` execution were not performed under the prior governance model and remain historical observation surfaces

## How to Update This File

Update when major changes occur.
