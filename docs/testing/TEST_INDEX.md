# Test Index

Map of [`tests/`](../../tests/) coverage by subsystem prefix. ~1,034 `test_*.py` modules (fast-ci subset excludes `slow`, `integration`, `canon`, `artifact` markers).

## How to run

```bash
# Full fast CI (recommended before PR)
python scripts/run_fast_ci.py

# Targeted subsystem
python -m pytest tests/test_abx_codegen_shadow_replay_harness_operator_decision_record_review.py -q

# Marker reference
python -m pytest -q -m "not slow and not integration and not canon and not artifact"
```

## Subsystem coverage map

| Test prefix | Count | Covered subsystem | Purpose |
|-------------|------:|-------------------|---------|
| `test_v2_hygiene_*` | 108 | v2 hygiene phases 1–30 | Stabilization, attestation intake, phase gates |
| `test_overlay_*` | 74 | Overlay firewall/governance/topology | Sandbox projection chains |
| `test_temporal_continuity_*` | 56 | P70–P102 continuity spine | Procedural chain builders |
| `test_abx_codegen_*` | 55 | Codegen intelligence spine | Shadow harness, ODR, intake gate |
| `test_abx_artifact_*` | 44 | Artifact lineage/registry repair | Registry coverage, orphan policy |
| `test_wasserstein_*` | 33 | Wasserstein/geometric operators | Metric operators |
| `test_manual_*` / `test_proposal_*` | 31 each | Manual execution / proposal sandbox | Custody and routing |
| `test_canary_*` / `test_research_canary_*` | 57 | Research canary P103–P130 | Advisory shadow, registry |
| `test_operator_narrative_*` | 23 | P42/P44 operator narrative | Report, UI overlay, archive chain |
| `test_belief_graph_*` | 19 | Belief graph engine | Multi-primitive surface |
| `test_global_ingest_*` / `test_oracle_signal_*` | 26 | Ingest / Oracle Signal | Shadow intake boundaries |
| `test_runtime_integration_*` | ~10 | Runtime integration gate | Shadow wiring hooks |
| `test_chamfer_*` / `test_geodesic_*` | ~30+ | Chamfer/geodesic arc | Historical geometric planning |
| `test_generated_artifact_registry*` | few | Artifact registry policy | Classification stability |

## Cross-cutting tests

| File | Purpose |
|------|---------|
| `test_generated_artifact_registry.py` | Producer classification, drift policy |
| `test_run_fast_ci.py` | Fast CI runner smoke |
| `test_repository_organization_indexes_001.py` | Navigation index link integrity |
| `test_operator_hold_clearance.py` | Operator hold clearance integration |

## Coverage notes

### Missing coverage (documented, not blocking)

- Some sealed P70–P130 lanes have builders but no dedicated tests (historical; change forbidden without operator lane)
- `Scripts/` legacy tree — tests target `scripts/` canonical path

### Dead / historical coverage

- Chamfer v0.1 arc tests remain for regression; arc is archived
- Long temporal continuity P83–P99 recursive chain tests — historical seal

### Duplicate coverage

- Multiple registry classification tests assert same producer maps — intentional stability guards
- Overlapping `test_abx_research_canary_*` and `test_research_canary_*` — different builder surfaces

## Related

- [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
- [`AGENTS.md`](../../AGENTS.md) — test execution order
- [`docs/START_HERE.md`](../START_HERE.md)
