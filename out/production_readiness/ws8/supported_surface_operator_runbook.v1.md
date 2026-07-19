# SUPPORTED Surface Operator Runbook

Produced: 2026-07-19T03:15:14Z  
SHA: `ad6ba88e13764de3d9b858dff9dc5a00cb0f2628`  

## Safety

- Do not set production_activation_authorized true from this runbook
- Do not enable ABRAXAS_BOUNDARY_FAIL_CLOSED without operator approval
- Prefer scripts/run_* and SUPPORTED services over ad-hoc core writers
- Writes must go through sole-writer / artifact service under out/

## Procedures

### canonical_json

Deterministic JSON serialize/hash/write under policy

```bash
python -c "from core.canonical.json import canonical_hash; print(canonical_hash({'a':1}))"
```

Tests: `tests/test_canonical_json.py`

_Library call; prefer service facade for path-gated writes._

### run_fast_ci

Mandatory local/CI validation entry point

```bash
export PATH="$(pwd)/.venv/bin:$PATH"
python scripts/run_fast_ci.py
```

Tests: `tests/test_run_fast_ci.py`

_Advisory readiness gates fail-open; exit 0 required for G1._

### validation_service.v1

Schema validation (contracts/ only schema_ref)

```bash
python scripts/run_validation_service.py --help
```

Tests: `tests/test_validation_service.py`

_SUPPORTED service; no production authority grant._

### artifact_and_provenance_service.v0

Hash/dumps/write via canonical_json; out/ only

```bash
python scripts/artifact/run_artifact_provenance_service.py --help
python scripts/artifact/run_artifact_provenance_service.py --operation hash --payload '{"x":1}'
```

Tests: `tests/test_artifact_provenance_service.py`

_PATH_DENIED outside out/; organized under scripts/artifact/._

### readiness_scorecard_and_decision

Freeze gates + binding release decision

```bash
python scripts/run_freeze_gate_scorecard.py
python scripts/run_release_decision.py --help
python scripts/run_candidate_deploy_readiness.py
python scripts/readiness/run_production_activation_authority_gate.py
```

Tests: `tests/test_freeze_gate_scorecard.py`, `tests/test_release_decision.py`

_CANDIDATE_APPROVED still deploy-held; activation gate DENIED._

