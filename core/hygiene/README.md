# core/hygiene — Soft Facade Advisory Receipts

Optional observability composites sealed during the 2026-07-23 Compression Track.

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

## Yggdrasil Scan ID Map

`emit_yggdrasil_scan_receipt` accepts **either** Soft Facade short names **or** full catalog rune_ids. Both normalize to the short key in the receipt payload.

| Soft Facade key | Catalog rune_id |
|-----------------|-----------------|
| `DEPENDENCY_SCAN` | `RUNE.YGGDRASIL.DEPENDENCY_SCAN` |
| `LANE_BOUNDARY_SCAN` | `RUNE.YGGDRASIL.LANE_BOUNDARY_SCAN` |
| `EDGE_VALIDATION` | `RUNE.YGGDRASIL.EDGE_VALIDATION` |
| `UNKNOWN_NODE_GATE` | `RUNE.YGGDRASIL.UNKNOWN_NODE_GATE` |

Example:

```python
from core.hygiene import emit_yggdrasil_scan_receipt

# Short names
emit_yggdrasil_scan_receipt(applied=["DEPENDENCY_SCAN", "EDGE_VALIDATION"])

# Full catalog IDs (equivalent)
emit_yggdrasil_scan_receipt(
    applied=[
        "RUNE.YGGDRASIL.DEPENDENCY_SCAN",
        "RUNE.YGGDRASIL.EDGE_VALIDATION",
    ]
)
```

## Activation boundary

Activation = opt-in import + emit receipt for observability only.
Does **not** grant execution authority, open locks, or wire into runners/gates.
System production activation remains HELD_FOR_OPERATOR (see STATUS.md).

See Soft Facade Activation Instructions and Yggdrasil Scan Integration Exploration in the Abraxas Notion Atlas.
