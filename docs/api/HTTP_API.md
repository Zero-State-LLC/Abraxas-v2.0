# Abraxas HTTP API (supported surface)

Human guide for the **supported** FastAPI app factory: `apps.api.create_app`.

| Field | Value |
|-------|--------|
| **Candidate status** | `NOT_READY` (see frozen contract) |
| **Activation** | LOCAL_DEV / SANDBOX only for routine use; EXTERNAL_PRODUCTION held |
| **Network at import** | None — providers stay denied/fixture unless explicitly configured |
| **Contract** | [`contracts/api/openapi_supported_surface.v1.json`](../../contracts/api/openapi_supported_surface.v1.json) |

Live OpenAPI may grow routes; it **must not shrink** the frozen supported set below.

---

## Run locally

```bash
# from repo root, with venv active
pip install -r requirements.txt
uvicorn apps.api.main:app --reload --port 8000
```

Factory form (tests / embedding):

```python
from apps.api.main import create_app
app = create_app()
```

---

## Supported routes

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/ready` | Readiness probe |
| `GET` | `/health` | Liveness / health |
| `GET` | `/version` | App version string |
| `GET` | `/registry` | Registry observation surface |
| `GET` | `/validation` | Validation service observation surface |
| `POST` | `/analyze` | Advisory analyze (e.g. Alembic task envelope) |

OpenAPI UI (when server running): `http://127.0.0.1:8000/docs`  
Machine OpenAPI: `http://127.0.0.1:8000/openapi.json`

---

## Example calls

```bash
curl -s http://127.0.0.1:8000/ready
curl -s http://127.0.0.1:8000/version
curl -s http://127.0.0.1:8000/health

# Analyze (fixture task; no production authority)
curl -s -X POST http://127.0.0.1:8000/analyze \
  -H 'content-type: application/json' \
  -d @fixtures/alembic/example_task.json
```

Prefer the product CLI for the same LOCAL_DEV spine when you do not need HTTP:

```bash
python -m abraxas status
python -m abraxas analyze --alembic-task fixtures/alembic/example_task.json
```

---

## Authority notes

- Responses are **advisory / observation** unless a lane and dual-control process authorize more.
- Do not treat HTTP success as production activation or deploy unhold.
- Default provider port is fail-closed / denied; fixture lanes are for tests and demos.
- Service hardening: request-id middleware, sanitized 500s, authn/rate-limit seams — see `apps/api/middleware.py`, `apps/api/boundaries.py`.

---

## Related

- Product CLI: `python -m abraxas` · [`abraxas/cli.py`](../../abraxas/cli.py)
- Settings: `apps/api/settings.py`
- OpenAPI freeze contract: `contracts/api/openapi_supported_surface.v1.json`
- Live readiness: [`STATUS.md`](../../STATUS.md)
