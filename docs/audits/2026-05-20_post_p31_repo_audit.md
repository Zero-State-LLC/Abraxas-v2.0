# Post-P31 Repository Audit Note (2026-05-20)

## Scope

- Audit repository state against Notion-canonical chain P27–P31.
- Update documentation surfaces (`README.md`, `AGENTS.md`, `PLANS.md`) to reflect post-P31 edge.
- Run requested validation commands and record exact outcomes.

## P31 surface verification

Present:

- `core/operator_attention_ledger.py`
- `scripts/run_operator_attention_ledger.py`
- `contracts/operator_attention/operator_attention_ledger.v1.schema.json`
- `tests/test_operator_attention_ledger.py`
- `core/config.py`
- `core/generated_artifact_registry.py`
- `out/projections/operator_attention_ledger_001.latest.md`

Absent in this checkout snapshot:

- `out/projections/operator_attention_ledger_001.latest.json`

## Command outcomes

Succeeded:

- `python -m pip install -e .`
- `python scripts/run_operator_attention_weather.py`
- `python scripts/run_operator_review_routing_enhancer.py`
- `python scripts/run_operator_attention_ledger.py`
- `python scripts/run_artifact_regeneration.py --full --validation-only`
- `python scripts/run_artifact_regeneration.py --check-drift`

Failed due to environment dependency:

- `pytest tests/test_operator_attention_ledger.py`
- `pytest tests/test_operator_attention_weather.py`
- `pytest tests/test_operator_review_routing_enhancer.py`
- `pytest -q`

Exact failure text:

- `bash: line 1: pytest: command not found`
- `/usr/bin/python: No module named pytest`

## Canonical edge statement

- Treat P27–P31 as `COMPLETE_AND_STABLE` for this documentation alignment pass.
- Resume edge is post-P31.
- Next implementation work must begin with explicit planning/audit, not blind feature execution.
