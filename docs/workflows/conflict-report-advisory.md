# ConflictReport.v1 Advisory Builder

Developer runbook for the advisory CONFLICT_SCAN report builder on `main`.

**Scoped to `main`:** verified against `core/conflict_scan.py` (PR #996 / STATUS row `ConflictReport.v1 builder`).

## Intent

`ConflictReport.v1` records detection and classification only. It never auto-resolves conflicts, never mutates canon/runtime, and always keeps `execution_authority=False`. Operator disposition is required before any resolution.

## Scope (and non-scope)

| Surface | Path | Role |
|---------|------|------|
| Advisory builder | `core/conflict_scan.py` | `ConflictReport` / `build_conflict_report` / `emit_conflict_scan_packet` |
| STATUS pointer | `STATUS.md` | Merge posture for #996 |
| Convergence note | [`../status/REPO_NOTION_CONVERGENCE_2026_07_23.md`](../status/REPO_NOTION_CONVERGENCE_2026_07_23.md) | Board/PR map |

Do **not** confuse with:

- `core/research_cross_drop_conflict_scan.py` — research P98/P99 packet scan lane
- `core/oracle/conflicts.py` / `IntakeConflictPacket` — Oracle intake conflict packets
- Soft Facade hygiene receipts under `core/hygiene/` — optional observability composites

## Public interface

```python
from core.conflict_scan import (
    ConflictFinding,
    build_conflict_report,
    detect_dependency_conflicts,
    detect_hash_conflicts,
    emit_conflict_scan_packet,
)

# Hash / provenance mismatch detection (duplicate IDs, differing hashes)
findings = detect_hash_conflicts(
    [{"id": "a", "hash": "111"}, {"id": "a", "hash": "222"}],
)

# Missing dependency detection
dep_findings = detect_dependency_conflicts(
    required_dependencies=["rune.x"],
    available_dependencies=[],
)

report = build_conflict_report(
    pipeline_id="universal_ingest",
    items=[{"id": "a", "hash": "111"}, {"id": "a", "hash": "222"}],
    required_dependencies=["dep.a"],
    available_dependencies=["dep.b"],
    source_receipts=["receipt-001"],
    producer_system="CODEX",  # GROK | CODEX | MIXED | HUMAN
)

packet = emit_conflict_scan_packet(pipeline_id="universal_ingest", items=[...])
```

### Output fields that matter

| Field | Meaning |
|-------|---------|
| `scan_status` | `PASS` \| `CONFLICTS_DETECTED` \| `NOT_COMPUTABLE` |
| `blocking_conflict_detected` | True when any high/severe finding requires resolution |
| `resolution_required` | True when any finding sets `resolution_required` |
| `recommended_next` | `CONTINUE` or `OPERATOR_REVIEW` |
| `execution_authority` | Always `False` |
| `authority_locks.auto_resolve` | Always `False` |
| `provenance_hash` | SHA-256 over canonicalized report payload (see `finalize`) |

Conflict types currently modeled: `provenance_mismatch`, `normalization_mismatch`, `replay_mismatch`, `lineage_break`, `duplicate_source`, `authority_violation`, `dependency_conflict`, `schema_mismatch`, `unknown`.

## Constraints

- Detection/classification only — no winner selection, merge, or auto-resolve.
- `net_catalog_delta` is fixed at `0` (no rune catalog expansion).
- High/severe findings that require resolution route to `OPERATOR_REVIEW`.
- Report `timestamp` uses wall-clock UTC in the dataclass default; do not treat wall-clock as a deterministic ledger seal for other subsystems.
- Keep Oracle intake conflicts and research cross-drop scans on their own surfaces.

## Troubleshooting

| Symptom | Guidance |
|---------|----------|
| Expected `PASS` but got `CONFLICTS_DETECTED` | Inspect `findings[]` for duplicate IDs / missing deps; fix inputs or escalate to operator review. |
| Want auto-resolve | Not supported. Disposition is operator-owned. |
| Mixing with Soft Facade receipts | Import from `core.conflict_scan`, not `core.hygiene`. |
| Research canary / P99 wording | Use `core.research_cross_drop_conflict_scan`, not this builder. |

## Related

- Soft Facade hygiene: [`../../core/hygiene/README.md`](../../core/hygiene/README.md)
- Source-hash portability (hygiene Phase 1 execution receipt): [`source-hash-line-ending-portability.md`](source-hash-line-ending-portability.md)
- CLI evidence discipline: [`cli-operator-layer.md`](cli-operator-layer.md)
