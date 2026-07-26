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

### Phase 0–2
1. `core/governance/activation_policy.py` + exhaustive lane tests
2. `core/application/advisory_spine.py` golden-path orchestrator (pure; wires validation + optional Alembic)
3. `core/production_convergence/*` inventories + package builder
4. ADRs 0017 / 0018 + architecture docs + top-level doc reconciliation

### Phase 3–4
1. Hardened advisory spine (FORECAST escalation denied; authority_locks)
2. Golden-path integration tests vs direct Alembic pipeline
3. Supported CLI: `python -m abraxas` analyze/validate/replay/status
4. `abraxas.AbraxasClient` library facade
5. `apps.api.create_app(settings)` + `/analyze` `/ready` `/version`
6. Deprecation warnings on Alembic specialist CLI + validation service shim
7. `out/production_convergence/deprecation_ledger.v1.json`

### Phase 5
1. `core/canonical/artifact_classification.py` + ADR-0018 enforcement API
2. `write_canonical_artifact` / `prepare_canonical_artifact` (path confinement, append-only)
3. Migrated CLI outputs + convergence package to classified writer
4. `core.settings.RuntimeSettings` shared by CLI/API/client; `RuntimePaths` stays path-only
5. Advisory bypass scanner `run_canonical_writer_bypass_check.py`

### Phase 6
1. Clock/storage ports (`core/ports/*`) + `RuntimeContext` injection into `AbraxasClient`
2. High-traffic writer migrations: artifact provenance service + Alembic specialist CLI
3. Service hardening slice: request-id + security headers, sanitized 500s, fail-closed authn/rate-limit seams on `POST /analyze`
4. OpenAPI route presence check + minimal recovery-drill (FixedClock + storage rewrite)

### Phase 7
1. `write_classified_json` migration helper + runtime/readiness sole-writer migrations
2. Provider port (`DeniedProvider` fail-closed; no network at import/construct)
3. OpenAPI supported-surface freeze contract `contracts/api/openapi_supported_surface.v1.json`
4. Recovery drill: analyze → persist → replay (`core/production_convergence/recovery_drill.py`)

### Phase 8
1. Fourteen spine-adjacent sole-writers migrated to `write_classified_json` (ingest/oracle, brier, forecast, operator, proposal/review, campaign)
2. `FixtureProvider` + `gated_invoke` (EXTERNAL_PRODUCTION always denied; `ABRAXAS_ALLOW_PROVIDER_INVOKE` default false)
3. Receipt: `out/production_convergence/phase8_writer_migration.v1.json`
4. Deferred: `*_replay.py`, viz overlays, artifact-contract repair, doctrine validator, research_canary

### Phase 9
1. Twelve spine-paired/adjacent `*_replay.py` writers → `write_classified_json`
2. Eight viz WP-D sole-writers (overlays + execution firewall) → `write_classified_json`
3. Advisory CLEAR reference analysis: `out/production_convergence/clear_reference_analysis.v1.json` (`mass_deletion_authorized: false`)
4. Receipt: `out/production_convergence/phase9_writer_migration.v1.json`
5. Deferred: viz `*_replay.py`, canary WP-D research runners, doctrine validator, research_canary, mass deletion

## CLEAR

No mass deletion. Compatibility shims emit DeprecationWarning and retain behavior. Legacy `write_canonical_json` callers remain during migration. CLEAR reference analysis is advisory-only until operator review.

## SEAL (slice)

- Candidate status remains `NOT_READY`
- Pre–Phase 10 issue backlog closed advisarily (#546 #547 #881 #892); `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` remains unissued — see `docs/status/ISSUE_BACKLOG_CLOSURE_001.md`
- Next action: Phase 10+ — residual canary/viz replays; CLEAR operator review before any deletion; live providers only when authorized
