# Bounded Product Activation Policy

**Status:** ACTIVE ENGINEERING POLICY
**Effective:** 2026-07-23
**Authority:** Operator-approved under Governance V3

## Decision

Abraxas no longer treats all product activation as one binary production gate.

Activation is separated into bounded lanes so engineering can move quickly without treating internal experimentation as external production deployment.

**Runtime authority:** [`core/governance/activation_policy.py`](../../core/governance/activation_policy.py) (ADR-0017).

## Activation lanes

| Lane | Default | Permitted scope | Required evidence |
|---|---|---|---|
| `LOCAL_DEV` | ALLOW | Local execution, fixtures, migrations, adapters, UI, runners, and integration tests | Targeted tests for touched surfaces |
| `SANDBOX` | ALLOW | Isolated runtime activation using non-production data and revocable configuration | Fast CI or equivalent scoped validation; receipts where the surface already emits them |
| `INTERNAL_CANARY` | CONDITIONAL_ALLOW | Limited operator-controlled use against explicitly selected services or datasets | Passing CI on the candidate commit, rollback path, bounded credentials, observable failure mode |
| `EXTERNAL_PRODUCTION` | OPERATOR_GATE | Public deployment, persistent external automation, customer/user data, irreversible mutation, billing, or broad network authority | Explicit operator decision plus release, security, rollback, and monitoring evidence |

## Engineering acceleration rule

Routine implementation may execute through `LOCAL_DEV` and `SANDBOX` without generating authorization packets, seal chains, or production-readiness artifacts solely to begin work.

Internal canaries may proceed when the change is reversible, scoped, observable, and supported by commit-specific validation. A new governance artifact is required only when a real trust boundary is crossed.

## Preserved hard boundaries

The relaxed posture does **not** authorize:

- autonomous canon promotion;
- SHADOW-to-FORECAST escalation without the existing promotion path;
- broad or persistent external writeback;
- unbounded credentials or secret exposure;
- destructive mutation without rollback;
- fabricated evidence or fake readiness claims;
- public production deployment without operator approval.

## Classification rule

Classify by actual blast radius, not by subsystem name.

A runtime path is not automatically `EXTERNAL_PRODUCTION`. A local runner, sandbox service, deterministic replay, internal UI, or isolated adapter belongs to the lowest lane matching its real effects.

When uncertain, choose the least restrictive lane that still contains the observed blast radius and document the assumption in the PR.

## Merge and release behavior

- Merge to `main` remains evidence-gated by tests and repository checks.
- Merge does not itself authorize external production deployment.
- Sandbox activation can occur before a formal release when isolated and reversible.
- Internal canary activation may use a release candidate or commit SHA.
- External production activation remains a distinct operator decision.

## Canonical status vocabulary

Use these terms instead of blanket `DENIED` where appropriate:

- `DEV_ACTIVATION_ALLOWED`
- `SANDBOX_ACTIVATION_ALLOWED`
- `INTERNAL_CANARY_CONDITIONAL`
- `EXTERNAL_PRODUCTION_OPERATOR_GATED`

Historical artifacts that say `production activation = DENIED` remain valid for the exact evidence package and date they describe. They do not override this newer lane-based policy for routine engineering.
