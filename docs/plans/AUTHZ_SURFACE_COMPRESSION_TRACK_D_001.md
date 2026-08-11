# Track D — Authorization Surface Compression (Light)

**Status:** CLOSED_AS_POLICY · `ADVISORY_ONLY` · docs + inventory only
**Date:** 2026-07-31
**Parent:** [`ABRAXAS_UNIFICATION_PLAN_002.md`](ABRAXAS_UNIFICATION_PLAN_002.md) §5 Track D
**Authority:** `canon_mutation=false` · `runtime_mutation=false` · `execution_authority=false` · no plan-tree auto-unhold

## 0. Purpose

Stop **recursive plan → gate → plan** growth from blocking kernel and Track B work. Prefer **one terminal disposition** (review seed / hold receipt) over nested authorization trees.

This document is the **front-door residual map** for Track D (light). It does not delete plans, rewrite history, or grant CLEAR/production authority. Closeout is surfaced by `abraxas os authz-compression` and [`docs/status/AUTHZ_SURFACE_COMPRESSION_TRACK_D_CLOSEOUT.md`](../status/AUTHZ_SURFACE_COMPRESSION_TRACK_D_CLOSEOUT.md).

## 1. Observed plan surface (repo)

Inventory under `docs/plans/` (counted on 2026-07-31 `main`):

| Family | Count (approx.) | Role after Track D |
|--------|-----------------|--------------------|
| Temporal continuity P-chain (`P7x`–`P102*`) | ~39 | **HISTORICAL / SEALED** unless operator reopens with Track D citation |
| Planning-gate P-chain (`P40`–`P71` static archive / narrative) | ~13 | **HISTORICAL / SEALED** archive companions |
| Continuity namespace docs | ~5 | Keep as namespace policy; no new recursive gates |
| Unification / Alembic front doors | 2 | **ACTIVE** — plan 001 historical multi-arch; plan 002 whole-system front door |
| Other / misc | ~7+ | Link to Track A–D or mark HISTORICAL on touch |
| **Total** | **~67** | — |

Related operational evidence (not plans, but same compression pressure):

- `out/operator_review/` — large recursive hold/receipt families (hundreds of artifacts)
- Doctrine: terminal external-operator hold is **enough**; do not spawn nested plan→gate chains without new OBSERVED pressure

## 2. Terminal-hold rule (mandatory for new eng work)

```text
IF work needs operator disposition:
  THEN emit ONE review/hold seed (FamiliarOperatorReviewPacket.v0,
       operator decision request, or existing sealed hold receipt)
  AND stop repo automation
ELSE IF work is ordinary eng under Governance V3:
  THEN Feature → Code → Test → PR → Merge
  AND do NOT generate authorization trees
```

**Forbidden without explicit operator packet:**

- Creating `P{N}_…_authorization_gate` → `…_record_creation_plan` → `…_dry_run` cascades
- Re-opening sealed continuity chains to “progress” without new evidence
- Mixing CLEAR dual-control / EXTERNAL_PRODUCTION unhold into AI OS eng PRs

## 3. Classification labels (for new or touched plans)

| Label | Meaning |
|-------|---------|
| `ACTIVE` | Front door or live eng track (must cite Track A/B/C/D) |
| `HISTORICAL` | Completed/sealed; keep for provenance; do not extend |
| `SEALED_HOLD` | Terminal hold; further work `NOT_COMPUTABLE` until operator attestation |
| `SUPERSEDED` | Replaced by a named ACTIVE doc |

When editing a plan file, add a one-line status if missing:

```markdown
**Track D class:** HISTORICAL · sealed · do not extend without operator packet
```

## 4. Active front doors (do not fork)

| Concern | Canonical surface |
|---------|-------------------|
| Whole-system next action | `docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md` |
| AI OS kernel evidence | `docs/architecture/AI_OS_KERNEL_AUDIT_001.md` |
| Alembic behavior | `docs/alembic/ALEMBIC_SPINE.md` |
| Ownership / contracts | `docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md` |
| Familiar review seed | `python -m abraxas forage operator-review --pack PATH` |
| Alembic residuals | `python -m abraxas os alembic-residuals` |
| Authorization compression receipt | `python -m abraxas os authz-compression` |

## 5. Compression backlog (operator-gated, not auto)

1. Bulk-label historical P-chains as `HISTORICAL` in index only (optional table refresh) — no mass rewrite of bodies.
2. Prefer `out/operator_review/*chain_compression*` / terminal hold receipts over new gates.
3. New workstreams must name Track A/B/C/D in PR body.

## 6. Success criteria (Track D light)

| Metric | Target |
|--------|--------|
| New recursive authz chains | Zero without operator packet |
| Contributor time-to-route | Use plan 002 + STATUS, not P100–P102 tree |
| Existing sealed holds | Remain held |

## 7. Seal

Policy / navigation surface only. Does **not** authorize deletion of plans, mass archive moves, CLEAR dual-control, recursive authorization-tree generation, or production unhold.

## 8. Issue #1120 closeout

Track D is closed as policy, not as production authority. New plan work must cite Track A/B/C/D or be terminally classified (`HISTORICAL`, `SEALED_HOLD`, or `SUPERSEDED`). If operator disposition is needed, emit one decision record plus one hold receipt and stop repo automation. Bulk-hold families remain held unless an explicit operator attestation exists.
