# Operator Decision Request — RDI Live Wiring 001

**Status:** AWAITING_OPERATOR_DECISION
**Requested from:** Daniel Meyer (operator)
**Requested by:** engineering (producer_system: MIXED; provenance only, not authority)
**Date:** 2026-08-10
**Authority note:** This document requests decisions. It grants nothing, and no
work listed below may begin from this document alone. Each decision requires
its own operator decision record under `operator_input/` per Governance V3.

---

## Context

RDI-0 through RDI-5 are landed on `main` (#1104, #1105, #1108, #1109): the
settlement binding bridge, the instantiation SHADOW detector and projection
view, the synthetic fixture experiment harness, and the AAL-Viz console panel
with its feed builder. Everything runs LAB-only over synthetic fixtures with
projection-only/advisory authority.

Two follow-on steps are **gated on operator decisions**, not on engineering.
Both default to fail-closed: absent a decision, nothing changes.

---

## Decision 1 — Live (non-fixture) evidence into the SHADOW RDI detector

**Question:** May `core/instantiation/shadow.py` be wired to real ingest
evidence (Oracle intake / familiar ingest receipts) instead of synthetic
fixtures only, and under which activation lane?

**What it would and would not do:**
- Would: build `InstantiationState/Transition` payloads from sourced evidence
  registers and run anomaly-only detection over them; publish advisory
  artifacts and the console feed from live inputs.
- Would not: explain, forecast, intervene, settle, score, or touch canon.
  The detector's authority block stays hard-false; contaminated transitions
  stay ineligible for independent confirmation.

**Options:**
- **A. DENY / DEFER** (current state; default)
- **B. SANDBOX only** — live-source dry runs, artifacts under `out/`, no
  console feed change
- **C. SANDBOX + console feed** — as B, and the AAL-Viz panel renders the
  live-derived view (still projection-only)

**Required before execution regardless of option:** operator decision record
in `operator_input/`, construct definitions via CFAR for any real construct
`H`, and evidence-source scoping (which registers, which windows).

## Decision 2 — Retire the legacy binding-status scoring path

**Question:** Once resolver flows emit `SettlementVerdict.v1` everywhere, may
`core/brier/runtime.py::build_brier_ledger` drop its legacy direct
`binding_status` outcome derivation so all scoring passes through the
score-ready settlement gate (`core/settlement/binding_bridge.py`)?

**Precondition (not yet met):** resolver/settlement flows producing verdicts
for every scored outcome. Until then the legacy path remains for callers
without settlement coverage.

**Options:**
- **A. DEFER** until the precondition is demonstrated (default)
- **B. Approve in principle** — engineering may remove the legacy path in the
  same change that lands full verdict coverage, with a deprecation test
  proving no caller depends on raw binding status

**Note:** Brier remains telemetry-only under either option.

---

## Requested response format

For each decision: chosen option, any scope constraints, and (if not DENY /
DEFER) an operator decision record under `operator_input/` that downstream
gates can bind by hash. Silence keeps both at their fail-closed defaults.
