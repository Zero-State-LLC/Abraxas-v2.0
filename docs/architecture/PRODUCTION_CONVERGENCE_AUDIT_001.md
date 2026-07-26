# Production Convergence Audit 001

**Program:** ABRAXAS PRODUCTION CONVERGENCE
**Modes completed in this slice:** OPEN · ALIGN (partial ASCEND for Phases 0–2)
**Branch:** `cursor/production-convergence-spine-6a0a`
**Baseline SHA:** see `out/production_convergence/baseline.v1.json`
**Candidate status:** `NOT_READY`
**External production authorized:** `false`

## Provenance labels

- **OBSERVED** — directly verified in repository files or command output
- **INFERRED** — derived from OBSERVED evidence
- **NOT_COMPUTABLE** — static evidence insufficient

## OPEN — Baseline

**OBSERVED:**

- Default branch tip at start: merge of Alembic YGGDRASIL/Oracle binding (#1020).
- Governance V3 + bounded activation docs are active.
- WS1 interface registry lists 4 SUPPORTED interfaces (canonical_json, run_fast_ci, validation_service, artifact_provenance_service).
- `scripts/**/run_*.py` count ≈ 712 across domain packages.
- Supported service surface exists at `apps/api/main.py` (health/registry/validation/metrics).
- Alembic Spine exists under `core/alembic/` with advisory status `ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS`.
- Canonical writer: `core/canonical/json.py`.

Machine package: `out/production_convergence/baseline.v1.json`.

## ALIGN — Architecture truth

### Entrypoint inventory

**OBSERVED:** Full classified inventory in `out/production_convergence/entrypoint_inventory.v1.json`.

Heuristic classes include SUPPORTED_*, INTERNAL_ENGINEERING_TOOL, GENERATED_RUNNER, EXPERIMENTAL, etc. UNKNOWN paths are listed explicitly and must not be ignored in CLEAR phases.

**INFERRED:** The dominant executable surface is engineering/ceremony tooling, not a product CLI.

### Interface inventory

**OBSERVED:** `out/production_convergence/interface_inventory.v1.json` assimilates WS1 SUPPORTED set and adds:

- `activation_policy` → SUPPORTED library
- `apps_api` → SUPPORTED service (factory hardening still Phase 8)
- `advisory_spine` → INTERNAL application orchestrator
- `alembic_spine` → EXPERIMENTAL specialist
- `abraxas` package root → ACCIDENTALLY_PUBLIC (empty client)

### Duplication clusters

**OBSERVED:** `out/production_convergence/duplication_clusters.v1.json`.

Highest-priority conflicts:

1. Activation/authority doctrine (V3 vs ARCHITECTURE/README)
2. Multiple FastAPI servers (`apps/api` vs `api/*`)
3. Hundreds of CLI runners vs missing unified `abraxas` CLI
4. `out/` overloaded as state + audit + workflow + history

**NOT_COMPUTABLE:** Exhaustive bypass scan of every `json.dumps` / `os.environ` / network client in this slice.

### Golden-path trace

**OBSERVED:** `out/production_convergence/golden_path_trace.v1.json`.

Target spine:

```text
InputEnvelope
  → IngestService
  → EvidenceObject
  → BeliefGraphService
  → AlembicSpine?          # optional specialist
  → OracleAnalysisService
  → AdvisoryResult
  → ArtifactRepository
  → CLI/API response
```

Alembic fit: optional architecture route/fuse after evidence/belief context and before/alongside Oracle advisory fusion. Read-only Oracle bridge already exists; no second ingest pipeline.

### Governance contradiction map

**OBSERVED:** `out/production_convergence/governance_contradiction_map.v1.json`.

Primary defect: artifact-chain authorization presented as universal runtime law while Governance V3 removes that ceremony for LOCAL_DEV/SANDBOX.

## ASCEND — Implemented in this slice

1. `core/governance/activation_policy.py` + exhaustive lane tests
2. `core/application/advisory_spine.py` golden-path orchestrator (pure; wires validation + optional Alembic)
3. `core/production_convergence/*` inventories + Phase 0–2 package builder
4. `scripts/readiness/run_production_convergence_phase0_2.py`
5. ADRs 0017 (activation) and 0018 (artifact classes)
6. Target architecture doc with Alembic placement
7. Documentation reconciliation for ARCHITECTURE/README/STATUS/PLANS

## CLEAR

No mass deletion. Ceremony runners classified as `GENERATED_RUNNER` / engineering tools for later shim/archive work.

## SEAL (slice)

- Candidate status remains `NOT_READY`
- Next action: Phase 3–4 — harden advisory spine integration tests, begin unified CLI command tree behind shims, continue writer consolidation planning
