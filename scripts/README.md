# Scripts layout

Domain-organized runners and helpers. Mass-org waves 1–3 + finish pass.

## Domain packages (`scripts/<domain>/run_*.py`)

| Domain | Role |
|--------|------|
| `artifact` | Artifact contracts / regeneration |
| `belief` | Belief graph / Brier / hyperstition |
| `campaign` | Campaign / external action |
| `codegen` | ABX codegen / grok / hermes spine |
| `geometry` | Chamfer / geodesic / heavy-tail geometry |
| `governance` | Governance / review / proposals |
| `hygiene` | v2 hygiene gates |
| `ingest` | Oracle / ingest |
| `metric` | Metric operators / ranking |
| `notion` | Notion sync / patch queues |
| `operator` | Operator actions / narrative / review queue |
| `preflight` | Operator preflight payload builders (`preflight_*.py`) |
| `readiness` | Production readiness / sole-writer / freeze |
| `research` | Research canary / replay / forecast |
| `runtime` | Runtime inventory / state / validation |
| `temporal` | Temporal continuity / lineage |
| `transport` | Wasserstein / transport |
| `viz` | AAL-viz / overlays / projection builders |

## Root keepers (intentional)

| Path | Why |
|------|-----|
| `run_fast_ci.py` | Primary CI entrypoint (`python scripts/run_fast_ci.py`) — **only** root `run_*` |
| `organize_scripts.py` | Organization tool (this layout) |
| `abx_loop.py`, `abx_hermes_*`, `abx_ledger_frontier.py`, `abraxas_v2.0_codex_governance_loop.py` | Long-lived CLI loop entrypoints (documented in root README) |
| `__init__.py`, `_receipt_runner.py` | Package / shared helpers |
| `tools/` | Optional non-runner helpers (`demo_safe_status.py`, gap-closure utilities) |

## Adding a new runner

1. Place it under the matching domain: `scripts/<domain>/run_<name>.py`
2. If the name prefix is new, add it to `PREFIX_MAP` in `organize_scripts.py` (longest prefixes first)
3. Import as `scripts.<domain>.run_<name>` (or `python -m scripts.<domain>.run_<name>`)
4. Confirm `python scripts/organize_scripts.py status` still reports `complete: true`

## Invocation

Prefer from repo root:

```bash
python -m scripts.<domain>.run_<name>
# or
python scripts/<domain>/run_<name>.py
```

Do **not** put bare `scripts/` alone on `PYTHONPATH` — `scripts/operator/` would shadow the stdlib `operator` module (no `__init__.py` there by design; still avoid the footgun).

## Organization tool

```bash
python scripts/organize_scripts.py status
python scripts/organize_scripts.py dry-run
python scripts/organize_scripts.py execute
```

Status reports `complete: true` when every prefix-mapped `run_*.py` lives under its domain and only root keepers remain at `scripts/`.
