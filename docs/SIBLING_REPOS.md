# Sibling repositories and ownership

**Decided 2026-10-10 (operator).** This file is the source of truth for which repository owns what.

## Ownership

| Repository | Role | Supported? |
| --- | --- | --- |
| **Zero-State-LLC/Abraxas-v2.0** (this repo) | **Doctrine and reference.** It holds Governance V3, AGENTS/SKILLS routing, architecture decisions, contracts, specs, the atlas and continuity spine, and **reference code** (`abraxas/` CLI, `apps/api`, `core/`). | Doctrine: yes. Code: **no**. The reference code shows how the doctrine is meant to execute; it is not a supported product or deployment. |
| [**Zero-State-LLC/Abraxas**](https://github.com/Zero-State-LLC/Abraxas) `main` | **Canonical execution repository.** It holds the supported runtime, live proof, deployments and product versions. | Yes |
| [Zero-State-LLC/Sigil-Forge](https://github.com/Zero-State-LLC/Sigil-Forge) | Executable specialist mounted as SHADOW (see `specs/013-sigil-forge-construct/BIND.md`). | In its own repo |
| [Zero-State-LLC/pawl](https://github.com/Zero-State-LLC/pawl) | Ratchet test gate used by the canonical runtime's CI. | In its own repo |
| `scrimshawlife-ctrl/Abraxas`, `scrimshawlife-ctrl/Abraxas-v2.0` | Old locations. GitHub redirects them to Zero-State-LLC. | — |
| `scrimshawlife-ctrl/Sigil-Forge`, `scrimshawlife-ctrl/Hyperlex` | Archived old copies. They are **not** redirects; do not bind to them. | No |

## Rules

- **No product claims here.** This repo publishes doctrine revisions, not product versions. See [`docs/releases/VERSION_STRATEGY.md`](releases/VERSION_STRATEGY.md). Readiness and activation statements in STATUS describe reference code under the doctrine, not a running service.
- **Executable work moves by port.** Valuable reference code reaches the canonical runtime through a reviewed, tested port PR in Zero-State-LLC/Abraxas. Never copy blindly. Before porting:
  1. Check the dependencies the code drags along.
  2. Check provenance.
  3. Check whether the upstream already has an equivalent; map onto it rather than adding a parallel taxonomy.
- **No removal before the port.** Reference code is not deleted here until its port has landed upstream, or it has been retired with a recorded reason. Deletions beyond targeted dead files need the two-operator sign-off (CLEAR).
- **No smash-merge.** One system, two remotes. A landing in the runtime repo does not promote anything here, and EXTERNAL_PRODUCTION stays operator-gated.
- "Abraxas v2.0" in the Notion Core Directive names the hygiene pattern (registers + loop tagging), not this remote alone.

## Port queue

The queue is ranked by value against the dependencies each item drags along. Status is tracked in [`PLANS.md`](../PLANS.md) under "Architecture coherence phases". Evidence is in [`docs/architecture/ARCHITECTURE_COHERENCE_AUDIT_001.md`](architecture/ARCHITECTURE_COHERENCE_AUDIT_001.md) §11.

1. **Canonical JSON hashing** (`core/canonical/json.py`): NaN rejection and number normalization. Upstream `abraxas/core/canonical.py` lacks both, and `webpanel/policy.py` has a second copy.
2. **`/analyze`-style access policy** (`apps/api/boundaries.py`). Upstream `POST /api/oracle/run` has no authentication, rate limit or body limit. Use the upstream `X-ABX-Token` header and its loopback guard.
3. **Independent canary evidence** (`core/governance/activation_evidence.py`). Map it onto the upstream `abx/lifecycle_policy.py` SHADOW→CANARY→ACTIVE lanes, which accept self-reported booleans today. The upstream HMAC receipts (`shared/signing.py`) silently fall back to unsigned; they must fail closed.
4. **Validation service** (`core/services/validation_service.py`).
5. **Advisory spine** (`core/application/advisory_spine.py`). Last, if at all: it brings in `core/alembic` (29 files).
