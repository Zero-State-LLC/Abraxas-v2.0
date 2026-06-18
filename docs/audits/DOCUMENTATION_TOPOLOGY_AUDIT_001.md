# Documentation Topology Audit 001

Advisory-only audit of documentation entrypoints, duplicates, conflicts, and link health. Emitted 2026-06-18 (post-#741).

## Authoritative entrypoints (read order)

| Priority | Document | Authority |
|----------|----------|-----------|
| 1 | [`docs/START_HERE.md`](../START_HERE.md) | New contributor 30-minute path (created in sweep) |
| 2 | [`README.md`](../../README.md) | Repository overview, architecture, workflow |
| 3 | [`docs/releases/POST_2_5_0_CONTINUATION_AUDIT.md`](../releases/POST_2_5_0_CONTINUATION_AUDIT.md) | **Current** continuation baseline |
| 4 | [`PLANS.md`](../../PLANS.md) | Canonical roadmap edge + implemented lanes |
| 5 | [`AGENTS.md`](../../AGENTS.md) | Agent/coding doctrine, guardrails |
| 6 | [`docs/INDEX.md`](../INDEX.md) | Navigation hub (expanded in sweep) |
| 7 | [`docs/releases/POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md`](../releases/POST_MERGE_739_INTAKE_CLEARED_CONTINUATION_PLAN.md) | Post-#739/#741 routing |

## Historical entrypoints (context only)

| Document | Status |
|----------|--------|
| `docs/plans/P71–P99_*` | Historical temporal continuity procedural chain |
| `AGENTS.md` P70–P130 archive section | Sealed research-canary spine |
| `docs/audits/REPO_*_v0_1` | Archived geometric/chamfer arc |
| `POST_MERGE_720_*` through `POST_MERGE_724_*` | Superseded by later merge plans |

---

## Duplicate explanations

| Topic | Locations | Recommendation |
|-------|-----------|----------------|
| Repository topology | README §09, atlas, INDEX | START_HERE → INDEX → README for depth |
| Governance posture | GOVERNANCE_V3, PLANS, AGENTS | PLANS for edge; AGENTS for agent rules |
| Operator attestation | templates/README, CODEGEN audit, POST_MERGE_738/739 | operator_input/README consolidates payloads |
| Continuation state | POST_2_5_0, continuation frontier JSON, PLANS | POST_2_5_0 is prose baseline; JSON is evidence |
| CLI operator layer | README, docs/workflows/cli-operator-layer.md | Single spec in workflows doc |

---

## Conflicting instructions (repaired in sweep)

| Conflict | Before | After |
|----------|--------|-------|
| ODR bridge status | POST_2_5_0, POST_MERGE_739, PLANS said "#741 pending" | #741 merged; ODR `INTAKE_CLEARED_OBSERVED` |
| Codegen intake | templates/README said "pending external attestation" | Payload **CLEARED**; intake **VALIDATED** |
| POST_MERGE_739 ODR table | `HELD_FOR_OPERATOR (stale)` | `INTAKE_CLEARED_OBSERVED` |

---

## Broken links (sample audit)

Scanned markdown links in README, PLANS, AGENTS, INDEX, releases, audits, operator templates.

| Source | Target | Issue |
|--------|--------|-------|
| `docs/INDEX.md` | `skill-work/` | Directory may not exist or is empty |
| `docs/releases/PRODUCT_2_5_0_RELEASE_READY.md` | `docs/notion/...` | Wrong relative path from releases/ (needs `../notion/`) |
| `docs/releases/FULL_FEATURES_RELEASE_ROADMAP_COMPLETION.md` | multiple `core/*` paths | Some paths use release-relative prefix incorrectly |
| `docs/releases/POST_MERGE_739_*` | `../core/...` | Resolves to `docs/core/` — should be `../../core/` |

**Sweep action:** Fixed POST_MERGE_739 core link during stale-ref repair. Remaining broken links in historical release docs are cataloged here; repair deferred to avoid churn in sealed plans.

---

## Coverage gaps (addressed in sweep)

| Gap | Resolution |
|-----|------------|
| No START_HERE | Created |
| INDEX missing releases/artifacts/testing | Expanded |
| No audit/release indexes | AUDIT_INDEX, RELEASE_INDEX created |
| No artifact classification doc | ARTIFACT_INDEX created |
| No test subsystem map | TEST_INDEX created |
| operator_input/ no root README | Created |

---

## Recommended maintenance

1. After each major merge chain (#7xx), update POST_2_5_0 baseline table only — not every historical POST_MERGE doc.
2. Point new docs at INDEX/START_HERE rather than duplicating topology in README.
3. Use relative paths from `docs/releases/` as `../` or `../../` consistently.
4. Run link-integrity test: `tests/test_repository_organization_indexes_001.py`.

---

## Governance note

Advisory-only. No authority, runtime, or canary regeneration implied.
