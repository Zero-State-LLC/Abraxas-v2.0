# core/hygiene — Soft Facade Advisory Receipts

Optional observability composites sealed during the 2026-07-23 Compression Track.

Related (not Soft Facade): advisory `ConflictReport.v1` lives in `core/conflict_scan.py` — see [`../../docs/workflows/conflict-report-advisory.md`](../../docs/workflows/conflict-report-advisory.md).

## Guarantees

- `execution_authority` is hard-coded `False` on every surface
- `net_catalog_delta = 0`
- No new runes
- Individual runes remain the sole authority for gating and execution
- Modules are completely optional; no production wiring

## Surfaces

| Module | Composite over |
|--------|----------------|
| `output_hygiene_receipt.py` | PROVENANCE_ENFORCE, OUTPUT_REGISTER_ENFORCE, LOOP_AWARENESS, HYPERSTITION_TAG, ADVERSARIAL_AUDIT |
| `yggdrasil_scan_receipt.py` | DEPENDENCY_SCAN, LANE_BOUNDARY_SCAN, EDGE_VALIDATION, UNKNOWN_NODE_GATE |
| `common_pipeline_receipt.py` | PARSE → IR_BUILD → VALIDATE → RECEIPT spine |
| `proof_pair_receipt.py` | POSITIVE_PROOF, NEGATIVE_PROOF |
| `hygiene_receipt_checklist.py` | Uniform field assert helper |

## Activation Instructions (Opt-In Only)

Soft Facades are **never required**. Activation means “import and emit a receipt for observability.” It does **not** grant execution authority, open locks, or wire into any runner or gate.

### 1. Import only what you need

```python
from core.hygiene import (
    emit_output_hygiene_receipt,
    emit_yggdrasil_scan_receipt,
    emit_common_pipeline_receipt,
    emit_proof_pair_receipt,
    assert_hygiene_receipt,
)
```

### 2. Emit after the real work has already run

Call the individual runes / pipeline stages first. Then optionally record what was applied:

```python
# After Output Enforcer runes have already executed
receipt = emit_output_hygiene_receipt(
    applied=["PROVENANCE_ENFORCE", "OUTPUT_REGISTER_ENFORCE", "LOOP_AWARENESS"],
    source_receipts=["rec_001", "rec_002"],
    notes="optional context",
    producer_system="GROK",  # or CODEX / MIXED / HUMAN
)
assert_hygiene_receipt(receipt.to_dict())
```

```python
# YGGDRASIL scan coverage (short names or full catalog IDs)
scan = emit_yggdrasil_scan_receipt(
    applied=["DEPENDENCY_SCAN", "LANE_BOUNDARY_SCAN", "EDGE_VALIDATION"],
    outcomes={
        "DEPENDENCY_SCAN": "PASS",
        "LANE_BOUNDARY_SCAN": "PASS",
        "EDGE_VALIDATION": "PASS",
    },
)
# Equivalent with full catalog IDs:
# applied=["RUNE.YGGDRASIL.DEPENDENCY_SCAN", ...]
```

```python
# Common Pipeline spine summary
pipe = emit_common_pipeline_receipt(
    pipeline_id="research_intake",
    applied_stages=["PARSE", "IR_BUILD", "VALIDATE", "RECEIPT"],
    stage_outcomes={
        "PARSE": "PASS",
        "IR_BUILD": "PASS",
        "VALIDATE": "PASS",
        "RECEIPT": "EMITTED",
    },
)
```

```python
# Proof polarity summary
proof = emit_proof_pair_receipt(
    applied=["POSITIVE_PROOF"],
    source_receipts=["proof_rec_001"],
)
```

### 3. What activation does *not* do

- Does not open `FORECAST_ROUTING`, `CANON_MUTATION`, `RUNTIME_MUTATION`, or `EXECUTION_AUTHORITY`
- Does not modify any route graph or binding matrix
- Does not require Soft Facades in CI, runners, or gates
- Does not elevate Soft Facades above individual runes

### 4. Edge / Jetson posture

Soft Facades are pure Python, no network, no GPU, no disk writes. Safe to import on Jetson Orin Nano / OpenClaw nodes. Keep them opt-in; do not auto-wire into edge runners without an explicit operator decision.

### 5. Production activation boundary

System-level production activation remains **HELD_FOR_OPERATOR** (see `STATUS.md` and production readiness package). Soft Facade usage is independent of that gate and never constitutes production activation.

## Yggdrasil Scan ID Map

`emit_yggdrasil_scan_receipt` accepts **either** Soft Facade short names **or** full catalog rune_ids. Both normalize to the short key in the receipt payload.

| Soft Facade key | Catalog rune_id |
|-----------------|-----------------|
| `DEPENDENCY_SCAN` | `RUNE.YGGDRASIL.DEPENDENCY_SCAN` |
| `LANE_BOUNDARY_SCAN` | `RUNE.YGGDRASIL.LANE_BOUNDARY_SCAN` |
| `EDGE_VALIDATION` | `RUNE.YGGDRASIL.EDGE_VALIDATION` |
| `UNKNOWN_NODE_GATE` | `RUNE.YGGDRASIL.UNKNOWN_NODE_GATE` |

## Related

- Compression Track Closure + Soft Facade Promotion Complete (Notion Atlas)
- `ARCHITECTURE.md` — Recent Advisory Surfaces + directory map
- Shared Multi-Agent Engineering Contract (`producer_system` tagging)
