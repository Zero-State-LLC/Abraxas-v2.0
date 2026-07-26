# Alembic Spine

**Status:** `ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS`  
**Authority:** `ADVISORY_ONLY` · fail-closed · receipt-gated · no canon/runtime mutation

## 1. Purpose

Alembic Spine is Abraxas v2.0’s governed architectural-selection and fusion layer. It routes, composes, verifies, calibrates, and compares multiple computational paradigms while preserving the symbolic/governance backbone.

It is **not** a generic AI framework, autonomous agent wrapper, or LLM router.

## 2. Non-goals

- Production authority or silent promotion of architectures
- Parallel governance, receipt, artifact, registry, or calibration stacks
- Self-modifying router weights
- Treating stub/unavailable adapters as successful executions
- Converting SHADOW results into active results

## 3. Architecture taxonomy

Supported families (extensible via descriptors, not hard-coded router branches):

- symbolic_expert, statistical_ml, transformer, state_space_sequence
- graph_neural, convolutional_vision, generative, world_model, agentic
- neuro_symbolic, spiking_neuromorphic, deterministic_tool
- human_operator_review, composite_hybrid

## 4. System boundaries

| Surface | Canonical owner |
| --- | --- |
| Domain models / pipeline | `core/alembic/` |
| Contracts / policy / registry snapshot | `contracts/alembic/` |
| CLI | `scripts/alembic/run_alembic_spine.py` |
| Canonical JSON / hashing | `core/canonical/json.py` |
| Brier (probabilistic only) | `core/scoring/brier.py` |
| Ingest integration | metadata hooks only → existing ingest/Oracle |
| Live runes | reuse `contracts/runes/catalog.v1.json` |
| Proposed Alembic runes | `contracts/alembic/rune_proposals.v1.json` (not live) |

## 5. Task lifecycle

```text
TaskEnvelope
  → validate
  → eligibility filter
  → rank eligible candidates
  → hybrid plan (optional)
  → adapter invoke
  → normalize → ArchitectureContribution
  → symbolic verify
  → deterministic fuse
  → metrics / receipts / replay manifest
```

Invalid or underspecified tasks abstain or route to operator review.

## 6–8. Routing: eligibility before ranking

1. Eliminate candidates that violate contract, modality, authority, privacy/security, determinism, health, budgets, runes, allow/deny lists, or stub status.
2. Score survivors with explicit versioned weights (`contracts/alembic/router_policy.json`).
3. Abstain on empty eligibility, ties without tie-break policy, missing required calibration, or authority escalation attempts.

## 9. Adapter contract

Each adapter exposes: `descriptor`, `validate_task`, `estimate`, `invoke`, `normalize` / `normalize_with_task`, `health`.

| Family | Adapter | Status |
| --- | --- | --- |
| symbolic_expert | local verifier | implemented |
| deterministic_tool | local solver | implemented |
| statistical_ml | shrinkage calibrator | implemented |
| graph_neural | local graph heuristic | implemented |
| state_space_sequence | stub | NOT_IMPLEMENTED |
| generative | stub | NOT_IMPLEMENTED |
| spiking_neuromorphic | stub | UNAVAILABLE |
| human_operator_review | abstain-to-operator | implemented |

## 10–11. Verification and fusion

Verification returns `PASS | PASS_WITH_RESIDUALS | FAIL | ABSTAIN | NOT_COMPUTABLE`.  
Fusion accepts only canonical contributions, preserves lineage/uncertainty, records typed conflicts, and never force-averages incompatible confidences. Failed verification and SHADOW lanes cannot become accepted active fusion inputs.

## 12. SHADOW and FORECAST

- SHADOW may compare and surface divergence; cannot promote, mutate policy, or influence active fusion.
- FORECAST remains separated; Alembic does not treat shadow anomalies as facts.
- Oracle/ingest integration is metadata-only via `core/alembic/ingest_hooks.py`.

## 13. Brier and calibration

Brier applies only to probabilistic forecast contributions with outcomes. Raw confidence, calibrated confidence, and missing calibration are explicit and distinct.

## 14. Governance and authority

All outputs carry `FINAL_STATUS=ALEMBIC_SPINE_ADVISORY_ONLY` and locked authority flags. Router-change proposals are `DRAFT` and require an operator gate; nothing auto-applies.

## 15. Receipts and replay

Each run emits task, registry snapshot, routing decision, contributions, verification, fusion, metrics, receipt, and replay manifest under `out/alembic/`. Replay is deterministic for local advisory adapters; stubs are typed irreproducible dependencies.

## 16. Configuration

- `contracts/alembic/architecture_registry.json`
- `contracts/alembic/router_policy.json`

Unknown score-weight fields and shadow promotion flags fail closed.

## 17. CLI

```bash
python -m scripts.alembic.run_alembic_spine validate-registry
python -m scripts.alembic.run_alembic_spine inspect-architectures
python -m scripts.alembic.run_alembic_spine route --task fixtures/alembic/example_task.json
python -m scripts.alembic.run_alembic_spine execute-advisory \
  --task fixtures/alembic/example_task.json \
  --registry contracts/alembic/architecture_registry.json \
  --policy contracts/alembic/router_policy.json \
  --out out/alembic/example_run
python -m scripts.alembic.run_alembic_spine evaluate --out out/alembic/evaluation
python -m scripts.alembic.run_alembic_spine propose-router-update --out out/alembic/proposals
```

## 18. Failure and abstention

Abstention is a first-class outcome with typed reasons (`no_eligible_candidates`, `candidate_tie_without_tie_break_policy`, `unsupported_authority_request`, etc.).

## 19. Extension guide

1. Add a descriptor-backed adapter under `core/alembic/adapters/`.
2. Register it in `DEFAULT_ADAPTERS` and `architecture_registry.json`.
3. Keep authority advisory; stubs must set `is_stub=True` and non-success status.
4. Add focused tests; do not invent parallel registries.

## 20. Current implementation status

| Capability | Status |
| --- | --- |
| Contracts / domain model | implemented |
| Registry / router / hybrid | implemented |
| Local adapters | implemented |
| Specialist stubs | explicit stubs |
| Verification / fusion / shadow compare | implemented |
| Evaluation harness | implemented |
| CLI | implemented |
| Live Alembic-native runes | deferred (proposals only; reuse existing runes) |
| Deep Oracle/YGGDRASIL pipeline binding | deferred residual |
| External neuromorphic/SSM/generative backends | deferred experimental |

See also: [`docs/plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md`](../plans/ALEMBIC_SPINE_UNIFICATION_PLAN_001.md).
