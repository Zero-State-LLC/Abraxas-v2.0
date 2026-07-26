# Alembic Spine Implementation Report

**Final status:** `ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS`  
**Authority:** `ADVISORY_ONLY` · no silent authority expansion  
**Date:** 2026-07-26

## 18.1 Implementation summary

| Bucket | Items |
| --- | --- |
| Implemented | Domain models, schemas, registry, eligibility, scoring, router, hybrid plans, adapters (4 real + 3 stubs + operator review), normalize, verify, fusion, shadow compare, metrics, proposals, evaluation harness, CLI, ingest metadata hooks, docs |
| Reconciled | Unification plan status; README/STATUS/ARCHITECTURE/PLANS; scripts PREFIX_MAP; rune reuse mapping |
| Deprecated | none |
| Removed | none |
| Deferred | Live `RUNE.ARCHITECTURE_*` catalog entries; deep YGGDRASIL alembic pipeline/route; external SSM/generative/SNN backends |
| Not computable | Production readiness of external specialist backends |

## 18.2 File manifest (high level)

**Created**
- `core/alembic/**` — canonical spine implementation
- `contracts/alembic/**` — schemas, registry snapshot, router policy, rune proposals
- `scripts/alembic/run_alembic_spine.py` — single CLI entrypoint
- `fixtures/alembic/example_task.json`
- `tests/test_alembic_spine.py`, `tests/test_run_alembic_spine.py`
- `docs/alembic/ALEMBIC_SPINE.md`, `AUDIT_AND_RECONCILIATION_001.md`, this report

**Modified**
- `scripts/organize_scripts.py`, `scripts/README.md`
- `README.md`, `STATUS.md`, `ARCHITECTURE.md`, `PLANS.md`
- `docs/plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md`

**Why:** Prior state was plan-only. Implementation consolidates missing Alembic capabilities into one advisory owner without forking governance/receipt/Brier/ingest stacks.

## 18.3 Validation report

| Check | Command | Result |
| --- | --- | --- |
| Unit/integration | `uv run pytest tests/test_alembic_spine.py tests/test_run_alembic_spine.py -q` | PASS (23) |
| Evaluation matrix | `python -m scripts.alembic.run_alembic_spine evaluate` | PASS (12/12) |
| Example advisory run | `... execute-advisory --task fixtures/alembic/example_task.json` | PASS |
| Lint | `uv run ruff check core/alembic scripts/alembic tests/test_alembic_*.py` | PASS |
| Script layout | `python scripts/organize_scripts.py status` | `complete: true` |
| Deterministic replay | covered by equal decision/receipt hashes in tests | PASS |
| Schema validation | jsonschema checks in unit tests | PASS |

## 18.4 Architecture coverage matrix

| Architecture family | Descriptor | Adapter | Routing | Normalization | Verification | Evaluation | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| symbolic_expert | yes | real | yes | yes | yes | yes | implemented |
| deterministic_tool | yes | real | yes | yes | yes | yes | implemented |
| statistical_ml | yes | real | yes | yes | yes | yes | implemented |
| graph_neural | yes | heuristic | yes | yes | yes | yes | implemented |
| state_space_sequence | yes | stub | filtered | stub normalize | n/a | yes | NOT_IMPLEMENTED stub |
| generative | yes | stub | filtered | stub normalize | n/a | yes | NOT_IMPLEMENTED stub |
| spiking_neuromorphic | yes | stub | filtered | stub normalize | n/a | yes | UNAVAILABLE stub |
| human_operator_review | yes | abstain | yes | yes | yes | yes | implemented |
| transformer / vision / world_model / agentic / neuro_symbolic / composite | taxonomy only | — | extensible | — | — | — | deferred descriptors |

## 18.5 Governance verification

- Authority locks hard-coded false across decisions/fusion/receipts
- `FINAL_STATUS=ALEMBIC_SPINE_ADVISORY_ONLY` on active outputs
- SHADOW comparison cannot promote or mutate policy; shadow contributions rejected from active fusion
- Router proposals remain `DRAFT` with `operator_gate_required=true`
- Missing eligibility / authority / calibration / ties abstain fail-closed
- Live rune catalog not mutated; proposals stay advisory

## 18.6 Residual register

| residual_id | classification | description | cause | risk | blocked_by | recommended_next_action | authority_required |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RES-RUNE-001 | OBSERVED | Alembic-native runes not in live catalog | unbound_runes invariant | low | YGGDRASIL pipeline/route binding | Author alembic pipeline + bindings, then add catalog entries | operator |
| RES-YGG-001 | INFERRED | No dedicated YGGDRASIL alembic route | scope consolidation | medium | route/pipeline design | Add advisory route after rune binding plan | operator |
| RES-ORACLE-001 | INFERRED | Intake hooks only; not wired into live oracle runner | avoid second ingest pipeline | low | product priority | Optional metadata field plumbing in oracle intake | engineering |
| RES-SSM-001 | SPECULATIVE | SSM adapter stub | no in-repo backend | medium | backend + eval evidence | Keep stub until specialist available | operator for promotion |
| RES-GEN-001 | SPECULATIVE | Generative adapter stub | no in-repo backend | medium | backend + eval evidence | Keep stub / shadow experiments | operator for promotion |
| RES-SNN-001 | SPECULATIVE | SNN/neuromorphic stub UNAVAILABLE | experimental path | medium | simulator/hardware evidence | Shadow-only until justified | operator for promotion |
| RES-HIST-001 | NOT_COMPUTABLE | Rich historical metrics ledger per architecture | no prior Alembic telemetry | low | runtime history accumulation | Feed metrics refs as runs accumulate | none |

## 18.7 Final status

`ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS`
