# Production Target Architecture 001

**Status:** TARGET (not fully implemented)
**Governance:** Governance V3 · DEVELOPMENT_ACCELERATION
**Activation:** lane-based (`core/governance/activation_policy.py`)
**Production:** `NOT_READY` · EXTERNAL_PRODUCTION operator-gated

## 1. Supported product spine

One end-to-end advisory transaction:

```text
InputEnvelope
  → IngestService
  → EvidenceObject
  → BeliefGraphService
  → [AlembicSpine optional]
  → OracleAnalysisService
  → AdvisoryResult
  → ArtifactRepository
  → CLI / API response
```

Application orchestrator (pure): `core/application/advisory_spine.py`.

## 2. Alembic Spine placement

Alembic is **not** a parallel product kernel.

| Aspect | Target |
| --- | --- |
| Role | Optional specialist for multi-architecture eligibility, routing, verification, fusion |
| Position | After ingest/evidence (and belief context when available); before or alongside Oracle advisory fusion |
| Authority | `ADVISORY_ONLY`; SHADOW isolation preserved |
| CLI | `scripts/alembic/run_alembic_spine.py` classified EXPERIMENTAL until folded into `abraxas` CLI |
| Integration | Reuse `core/alembic/oracle_bridge.py` (read-only); no second ingest pipeline |
| Contracts | `contracts/alembic/*`, pipeline `alembic_spine`, YGGDRASIL route `alembic_spine` |

Rule: **Extend → adapt → merge → replace**. Do not invent a second orchestration framework.

## 3. Activation lanes

| Lane | Default | Auth packet |
| --- | --- | --- |
| LOCAL_DEV | ALLOW | no |
| SANDBOX | ALLOW (isolated/reversible) | no |
| INTERNAL_CANARY | CONDITIONAL | no (operator review + controls) |
| EXTERNAL_PRODUCTION | OPERATOR_GATE | explicit operator approval + release controls |

Hard boundaries (all lanes): no autonomous canon promotion; no silent SHADOW→FORECAST; no unbounded credentials; no fabricated evidence; no public production deploy without operator decision.

## 4. Dependency direction

```text
domain (core/* pure builders)
  ← application (core/application)
  ← adapters/infrastructure (services, storage)
  ← CLI / API (scripts shims, apps/api)
```

Governance policy may be consulted by application orchestration. Domain modules must not depend on Notion/GitHub/API/CLI.

## 5. Supported interfaces (near-term)

**SUPPORTED today (assimilate WS1 + this slice):**

- `core/canonical/json.py`
- `scripts/run_fast_ci.py`
- `core/services/validation_service.py`
- `core/services/artifact_provenance_service.py`
- `core/governance/activation_policy.py`
- `apps/api/main.py` (service process; factory hardening later)

**SUPPORTED (Phase 3–4):**

- `core/application/advisory_spine.py`
- `abraxas.AbraxasClient` / `python -m abraxas` CLI
- `apps.api.create_app(settings)` (+ `/analyze`, `/ready`, `/version`)

**EXPERIMENTAL:**

- Alembic Spine specialist CLI (`scripts/alembic/run_alembic_spine.py`) — prefer `abraxas analyze --alembic-task`
- `api/hybrid_server.py`, `api/sse_server.py`, `api/websocket_server.py`

**Public surfaces:**

```python
from abraxas import AbraxasClient
```

```bash
python -m abraxas analyze --alembic-task fixtures/alembic/example_task.json
python -m abraxas validate --schema-ref contracts/... --payload path.json
python -m abraxas replay --receipt path.json
python -m abraxas status
```

```python
from apps.api.main import create_app
from apps.api.settings import AppSettings
app = create_app(AppSettings())
```

## 6. Artifact classes

See `docs/adr/ADR-0018-ARTIFACT-CLASSIFICATION.md`.

Only `CANONICAL_DOMAIN_ARTIFACT` and `GOVERNANCE_DECISION` normally influence current canonical state. Advisory spine outputs are `AUDIT_EVIDENCE`.

Runtime API:

```python
from core.canonical.json import write_canonical_artifact
from core.canonical.artifact_classification import ArtifactClass

write_canonical_artifact(
    path,
    payload,
    artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    out_root=settings.resolved_out_dir(),
)
```

## 6b. Settings vs paths

- `core.settings.RuntimeSettings` — activation lane, roots, feature flags (explicit load)
- `core.config.RuntimePaths` — filesystem layout catalog derived from settings roots
- Do not treat `RuntimePaths` as the universal DI container

## 7. What must remain separate

Keep boundaries between: canonical serialization; evidence ingest; belief representation; Oracle analysis; Alembic routing/fusion; governance policy; storage; API adapters; observability; experimental research.

The problem is not “too many modules”; it is **too many modules that look equally authoritative**.

## 8. Explicit non-goals for early phases

- Wholesale rewrite
- Mass deletion of runners without reference analysis
- External production activation
- Parallel governance/writer/registry stacks
- Treating Alembic residuals (SSM/generative/SNN stubs) as supported APIs
