# Memetic Ops D0 — Route Intent Design (SHADOW)

**Status:** ADVISORY DESIGN · implementation-bound  
**Date:** 2026-07-31  
**Lane:** SHADOW · `advisory_only`  
**Authority:** None — does **not** open MemeticOpsGate, grant publish/execution, or EXTERNAL_PRODUCTION  

**Parent forensics:** C spine + C′ + C6 (OpsGate always DENIED)  
**Parent dual-function:** [`2026-07-31-memetic-forensics-dual-function-design.md`](2026-07-31-memetic-forensics-dual-function-design.md) §8  

---

## 1. Goal

First **ops-series** slice that is safe under the C′ seal:

- Compose forensics disposition into a **route intent** for Level 99 / Neon **as seed targets only**.
- Keep `MemeticOpsGate.v0.gate_status` **always DENIED** (do not version-break C′).
- Never set `execution_authorized` or `publish_authorized` true.
- Optional dual-control **shape** fields on intent (for future series), not live attestation.

**Success:** Fixture READY → route intent `LEVEL99_CONTENT_SEED` with `ops_gate_status: DENIED` and `execution_authorized: false`. HOLD → `NONE`.

## 2. Non-goals

- Changing MemeticOpsGate.v0 always-DENIED semantics  
- Live Level 99 / Neon publish or platform mutation  
- CLEAR dual-control deletion track  
- EXTERNAL_PRODUCTION / auto-approve  
- Full dual-control receipt verification against remote identity  

## 3. Packet: `MemeticOpsRouteIntent.v0`

| Field | Constraint |
|-------|------------|
| `schema_version` | const `MemeticOpsRouteIntent.v0` |
| `route_intent` | `NONE` \| `LEVEL99_CONTENT_SEED` \| `NEON_IDEATION_SEED` |
| `route_status` | `BLOCKED` \| `WOULD_ROUTE_IF_OPERATOR` |
| `ops_gate_status` | const `DENIED` |
| `disposition` | READY \| HOLD \| NOT_COMPUTABLE \| `""` |
| `source_run_hash` / `source_disposition_hash` | 64-hex or empty |
| `pack_id` | string or null |
| `target_pipeline` | `""` \| `level99_content` \| `neon_genie_ideation` |
| `execution_authorized` | const `false` |
| `publish_authorized` | const `false` |
| `advisory_only` | const `true` |
| `lane` | const `SHADOW` |
| `authority` | forensics DEFAULT_AUTHORITY all false |
| `canonical_hash` | 64-hex |

### Routing rules (v0)

| Disposition | route_intent | route_status | target_pipeline |
|-------------|--------------|--------------|-----------------|
| READY | `LEVEL99_CONTENT_SEED` | `WOULD_ROUTE_IF_OPERATOR` | `level99_content` |
| HOLD / NOT_COMPUTABLE / empty | `NONE` | `BLOCKED` | `""` |

Optional `prefer_neon=True` kwarg (tests/future): READY → `NEON_IDEATION_SEED` / `neon_genie_ideation` instead. Default false.

## 4. Files

| Path | Role |
|------|------|
| `contracts/forensics/memetic_ops_route_intent.v0.schema.json` | Schema |
| `core/forensics/ops_route.py` | Pure builders |
| `core/forensics/__init__.py` | Export |
| `tests/test_forensics_ops_route.py` | Tests |
| `abraxas/cli.py` | `os forensics route --pack PATH` |
| `tests/test_forensics_cli.py` | CLI smoke |
| `contracts/forensics/README.md` | Row |
| `STATUS.md` | Active objective pointer |

## 5. CLI

```text
python -m abraxas os forensics route --pack PATH [--out PATH]
```

Exit: 0 if READY (would-route intent), 2 if HOLD|NOT_COMPUTABLE, 1 hard fail.  
Summary always `ops_gate_status: DENIED`, `execution_authorized: false`.

## 6. Later series (not D0)

- **D1:** Operator override receipt schema with dual-control fields (still no execution)  
- **D2:** Seed Level99ContentOperatorPacket from pack topic under route intent  
- **D3+:** Real dual-control attestation + gated publish (separate design)  

## Seal

Design + eng surface only. Does not open OpsGate or authorize production.
