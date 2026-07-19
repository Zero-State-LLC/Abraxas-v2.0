# Harness Phase 2 Implementation Continuation Prompt

Agent-actionable handoff after POST_MERGE_750 closure. Routes the next implementation session to Harness Phase 2 integration tests (priorities 1–3). Advisory-only; no execution authority.

## Context

| Item | Value |
|------|-------|
| Active closure | [`POST_MERGE_750_HARNESS_IMPLEMENTATION_MERGE_NOTION_SYNC_CLOSURE_CONTINUATION_PLAN.md`](POST_MERGE_750_HARNESS_IMPLEMENTATION_MERGE_NOTION_SYNC_CLOSURE_CONTINUATION_PLAN.md) |
| Phase 1 module | [`core/codegen_shadow_replay_harness.py`](../../core/codegen_shadow_replay_harness.py) — **IMPLEMENTED** |
| Phase 1 tests | [`tests/codegen/test_harness.py`](../../tests/codegen/test_harness.py) |
| Authorization record | `ABX_HARNESS_IMPLEMENTATION_AUTHORIZATION_RECORD_001` (`IMPLEMENTATION_APPROVED_RECORD_ONLY`) |
| Gate status | `SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_GRANTED` |
| Harness packet | `ABX_CODEGEN_SHADOW_REPLAY_HARNESS_EMITTED` |

## Validation baseline (pre-implementation)

```bash
python3 scripts/preflight_abx_harness_implementation_authorization_record.py
python3 scripts/codegen/run_abx_codegen_shadow_replay_harness_implementation_authorization_gate.py
python3 -m pytest tests/codegen/test_harness.py tests/test_abx_harness_implementation_authorization_record.py -q
python3 scripts/run_fast_ci.py
```

Expected: preflight **PASS**, gate **GRANTED**, harness tests **PASS**, fast CI **PASS**.

## Authority guardrails

- `valid_for_execution: false` on all harness surfaces
- No runtime, canon, scheduler, or queue mutation
- No P128→P130 `out/research_canary_*` regeneration
- No automated Notion writeback from repo runners
- No meta-gate authorization record creation
- Phase 2+ roadmap blockers remain (`phase_2_plus_pending_separate_authorization`) — **tests only**

---

## Priority 1 — Meta-gate path

**New file:** [`tests/codegen/test_meta_gate.py`](../../tests/codegen/test_meta_gate.py)

### Scope

- Self-modification proposals route to `HOLD_FOR_META_GATE` via `run_codegen_shadow_replay`
- 24-run invariance using `verify_run_invariance` with `META_GATE_RUN_COUNT` (24)
- Receipt recommendation and `promotion_blockers` align with meta-gate fixture expectations
- `meta_gate_extra_checks_passed` proof flag observed for valid self-modification path

### Fixture requirement

Add a valid non-canon-jump self-improvement proposal fixture:

`tests/fixtures/codegen/improvement_proposal_self_improvement_meta_gate.v1.json`

Derive from golden proposal with:

- `proposal_type`: `SELF_IMPROVEMENT`
- `self_modification_risk`: `true`
- `promotion_path`: `ADVISORY` (not `CANON`)
- `operator_decision_required`: `true`

Reference receipt: [`tests/fixtures/codegen/self_improvement_meta_gate_receipt.v1.json`](../../tests/fixtures/codegen/self_improvement_meta_gate_receipt.v1.json)

### Suggested tests

```python
def test_self_improvement_proposal_routes_to_hold_for_meta_gate() -> None: ...
def test_meta_gate_24_run_invariance() -> None: ...
def test_meta_gate_receipt_recommendation_matches_fixture_shape() -> None: ...
```

---

## Priority 2 — Error taxonomy

**New file:** [`tests/codegen/test_error_taxonomy.py`](../../tests/codegen/test_error_taxonomy.py)

### Implemented validation codes (VAL-/GOV-)

| Code | Trigger | Expected outcome |
|------|---------|------------------|
| VAL-001 | invalid `schema_version` | `VALIDATION_FAILED` / `REJECT` |
| VAL-002 | invalid `proposal_id` | `VALIDATION_FAILED` |
| VAL-003 | invalid `source_gap_diagnosis_id` | `VALIDATION_FAILED` |
| VAL-004 | missing provenance | `VALIDATION_FAILED` |
| GOV-001 | CANON promotion without operator | `VALIDATION_FAILED` |
| GOV-002 | self-improvement + CANON jump | `VALIDATION_FAILED` |
| GOV-003 | governance surface target | `VALIDATION_FAILED` |
| GOV-004 | governance policy mutation | `VALIDATION_FAILED` |
| GOV-005 | file write not denied | `VALIDATION_FAILED` |
| GOV-006 | network not denied | `VALIDATION_FAILED` |

Use existing negative fixtures under [`tests/fixtures/codegen/`](../../tests/fixtures/codegen/).

### Recommendation taxonomy (behavioral)

| Recommendation | How to trigger |
|----------------|----------------|
| `REJECT` | validation errors present |
| `BLOCK_POLICY_VIOLATION` | `no_canon_promotion_observed` false |
| `BLOCK_REPLAY_FAILURE` | `codegen_deterministic_output_observed` false |
| `HOLD_FOR_META_GATE` | `self_modification_risk` true with passing flags |
| `HOLD_FOR_OPERATOR` | proof flag blockers or operator review required |

Note: RPL-/META- prefix codes are documented in the harness plan failure taxonomy but not all have string emitters in harness yet. Assert behavior via recommendation + blockers, not unimplemented code strings.

---

## Priority 3 — Schema tests

**New file:** [`tests/codegen/test_schemas.py`](../../tests/codegen/test_schemas.py)

### Scope

- Move/split receipt schema validation from `test_receipt_schema_validates_for_golden_proposal` in [`tests/codegen/test_harness.py`](../../tests/codegen/test_harness.py)
- Golden + negative proposal fixtures vs [`contracts/canon/improvement_proposal.v1.schema.json`](../../contracts/canon/improvement_proposal.v1.schema.json)
- Receipt fixtures vs [`contracts/canon/shadow_improvement_receipt.v1.schema.json`](../../contracts/canon/shadow_improvement_receipt.v1.schema.json)

### Suggested tests

```python
def test_golden_proposal_validates_against_schema() -> None: ...
def test_golden_receipt_validates_against_schema() -> None: ...
def test_meta_gate_receipt_fixture_validates_against_schema() -> None: ...
def test_negative_proposals_fail_schema_or_harness_validation() -> None: ...
```

Strip harness-only fields (`proof_flags`, `advisory_only`, `execution_authority`) before schema validation on receipts.

---

## Priority 4 — Planning artifact refresh (separate follow-up PR)

Do **not** include in the Phase 2 test PR — pinned-hash churn risk.

```bash
python3 scripts/codegen/run_abx_codegen_intelligence_spine_harness_implementation_roadmap_plan.py
python3 scripts/codegen/run_abx_codegen_intelligence_spine_harness_interface_spec_plan.py
python3 scripts/codegen/run_abx_codegen_intelligence_spine_fixture_validation_harness_plan.py
```

Refresh roadmap/interface-spec artifacts to reflect `AUTHORIZED_IN_PROGRESS` Phase 1. No research canary touch.

---

## Implementation workflow

### Branch

```bash
git checkout main && git pull origin main
git checkout -b cursor/harness-phase-2-tests-1234
```

### Validation before PR

```bash
python3 -m pytest tests/codegen/ -q
python3 scripts/run_fast_ci.py
```

### Commit format

```
test(harness): add Phase 2 meta-gate, taxonomy, and schema tests
```

Body lines must be ≤100 characters (commitlint).

### PR deliverables

| Deliverable | Path |
|-------------|------|
| Meta-gate tests | `tests/codegen/test_meta_gate.py` |
| Error taxonomy tests | `tests/codegen/test_error_taxonomy.py` |
| Schema tests | `tests/codegen/test_schemas.py` |
| Self-improvement fixture | `tests/fixtures/codegen/improvement_proposal_self_improvement_meta_gate.v1.json` |

### Post-merge closure (separate docs PR)

After implementation PR merges, create `POST_MERGE_752_HARNESS_PHASE_2_TESTS_CLOSURE_CONTINUATION_PLAN.md` and update `RELEASE_INDEX.md`.

---

## Explicit non-goals

- Harness runtime execution or shadow binding repair
- Meta-gate authorization record creation
- P133 production activation
- Planning artifact regeneration in the same PR as test implementation
- P128→P130 research canary spine regeneration

---

## Operator / Agent Invocation

Copy-paste into a new agent session:

```
Implement Harness Phase 2 per docs/releases/HARNESS_PHASE_2_IMPLEMENTATION_CONTINUATION_PROMPT.md.

Add tests/codegen/test_meta_gate.py, test_error_taxonomy.py, and test_schemas.py per POST_MERGE_750 priorities 1–3. Add improvement_proposal_self_improvement_meta_gate.v1.json fixture if needed.

Preserve authority guardrails: advisory-only, no execution, no research canary regen. Run fast CI before opening PR. Do not refresh planning artifacts in this lane.
```
