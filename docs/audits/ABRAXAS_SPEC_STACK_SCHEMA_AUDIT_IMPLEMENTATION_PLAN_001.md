# ABRAXAS Spec Stack Schema Audit Implementation Plan 001

Advisory-only schema audit lane for five spec-stack domains. This lane observes
contract files, alignment artifacts, and documented shadow-binding gaps. It does
not grant execution authority, create missing bindings, or mutate canon/runtime.

## Purpose

Emit deterministic audit packets for:

1. **belief_graph** — `BELIEF_GRAPH_ENGINE_001`
2. **codegen_spine** — `ABX_CODEGEN_INTELLIGENCE_SPINE_001`
3. **ingest** — `GLOBAL_INGEST_ADAPTER_SPINE_001`
4. **binding** — Yggdrasil binding matrix + cross-spine shadow binding refs
5. **situation_runtime** — `SITUATION_RUNTIME_ENGINE_001`

A composite receipt aggregates all five domain audits.

## Governance posture

Every artifact carries the shared advisory envelope:

- `advisory_only: true`
- `execution_allowed: false`
- `authority_granted: false`
- `runtime_mutation_allowed: false`
- `canon_mutation_allowed: false`
- `scheduler_allowed: false`
- `queue_mutation_allowed: false`
- `notion_writeback_allowed: false`
- `github_writeback_allowed: false`
- `downstream_status: NOT_COMPUTABLE`

## Runners

```bash
python scripts/run_abraxas_spec_stack_belief_graph_schema_audit.py
python scripts/run_abraxas_spec_stack_codegen_spine_schema_audit.py
python scripts/run_abraxas_spec_stack_ingest_schema_audit.py
python scripts/run_abraxas_spec_stack_binding_schema_audit.py
python scripts/run_abraxas_spec_stack_situation_runtime_schema_audit.py
python scripts/run_abraxas_spec_stack_schema_audit_receipt.py
```

The receipt orchestrator runs all five domain builders and emits the composite
receipt at `out/audit/abraxas_spec_stack_schema_audit_receipt_001.latest.json`.

## Outputs

| Domain | JSON artifact |
|--------|---------------|
| belief_graph | `out/audit/abraxas_spec_stack_belief_graph_schema_audit_001.latest.json` |
| codegen_spine | `out/audit/abraxas_spec_stack_codegen_spine_schema_audit_001.latest.json` |
| ingest | `out/audit/abraxas_spec_stack_ingest_schema_audit_001.latest.json` |
| binding | `out/audit/abraxas_spec_stack_binding_schema_audit_001.latest.json` |
| situation_runtime | `out/audit/abraxas_spec_stack_situation_runtime_schema_audit_001.latest.json` |
| composite | `out/audit/abraxas_spec_stack_schema_audit_receipt_001.latest.json` |

## Gap posture

Missing shadow binding artifacts are **documented as gaps**, not auto-created:

- `out/audit/belief_graph_engine_shadow_binding_001.latest.json`
- `out/ingest/global_ingest_adapter_spine_shadow_binding_001.latest.json`
- `out/audit/situation_runtime_engine_shadow_binding_001.latest.json`
- Additional cross-spine refs from `core/runtime_integration_gate_shadow_wiring_hooks.py`

The binding domain audit inventories all seven `projection_binding_ref` paths.

## Explicit non-goals

- Runtime implementation of belief graph, ingest, codegen harness, or situation engine
- Creating missing shadow binding JSON files
- Schema repair, canon mutation, or dependency changes
- Notion/GitHub writeback
- Harness implementation authorization
- Regenerating `out/research_canary_*`

## Validation

```bash
python scripts/run_abraxas_spec_stack_schema_audit_receipt.py
python -m pytest tests/test_abraxas_spec_stack_schema_audit.py -q
python scripts/run_fast_ci.py
```
