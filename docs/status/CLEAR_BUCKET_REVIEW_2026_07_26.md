# CLEAR Bucket Review — 2026-07-26

**Role:** Engineering advisory review (not dual-control completion)  
**Draft:** `out/production_convergence/clear_disposition_draft.v1.json`  
**Draft canonical hash:** `a7b5149c7abd80f300a8d68dd6797c6218e8f40ca62fa23f133a5bda84fcf4ff`  
**mass_deletion_authorized:** **false** (unchanged; no deletion proposed)

## Outcome recommendation (operator)

| Bucket | Count | Engineering class | Operator recommendation |
| --- | ---: | --- | --- |
| KEEP | 7 | Keep as-is | **Confirm KEEP** |
| MERGE_CANDIDATE | 12 | Consolidate later | **KEEP for now** · optional MERGE_LATER backlog · **no delete** |
| DEFER_CLEAR | 4 | Experimental / lineage-sensitive | **DEFER** · retain files · **no delete** |
| DEPRECATE_DOCUMENT_ONLY | 1 | Shim | **Document-only deprecation** · **no delete** |

**Global operator disposition (recommended):**

```text
No mass deletion. mass_deletion_authorized remains false.
All 24 entries: non-delete (KEEP / KEEP_PENDING_MERGE / DEFER / DEPRECATE_DOCS_ONLY).
deletions_proposed: 0 · deletions_executed: 0
```

---

## KEEP (7) — confirm

| Path | Notes |
| --- | --- |
| `ARCHITECTURE.md` | Activation/authority policy surface; already reconciled to V3 lanes |
| `GOVERNANCE_V3.md` | Active governance canon |
| `README.md` | Front door; V3-aligned |
| `apps/api/main.py` | Supported FastAPI factory surface |
| `core/governance/activation_policy.py` | Lane activation policy implementation |
| `core/production_readiness/production_activation_authority_gate.py` | Fail-closed activation gate |
| `docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md` | Activation doctrine |

**Blockers:** DUPLICATION_CLUSTER_KEEP · OPERATOR_HOLD · `deletion_proposed: false`

---

## MERGE_CANDIDATE (12) — keep now; merge later if desired

These are **not** delete candidates. “Merge” means consolidate/document, not remove.

| Path | Notes |
| --- | --- |
| `712 scripts/**/run_*.py runners` | Domain runners post-org; keep inventory, no mass delete |
| `core/alembic/oracle_bridge.py` | Alembic advisory bridge |
| `core/canonical/json.py` | Classified writer / hash API |
| `core/config.py` (RuntimePaths) | Runtime path config |
| `core/governance/authority.py` | Authority lock evaluation |
| `core/oracle_signal*.py` | Oracle orchestration family |
| historical `out/operator_review/` decision chains | Provenance/history; do not wipe |
| “missing unified abraxas CLI” | Gap note, not a file to delete — product CLI already on main |
| scattered `os.environ` reads | Inventory gap; not a deletion target |
| schema `authority_locks` on artifacts | Contract pattern; keep |
| `scripts/ingest/run_oracle_*.py` | Oracle ingest runners |
| `scripts/run_fast_ci.py` | Root CI mirror runner (only root `run_*`) |

**Operator recommendation:** KEEP · optional engineering backlog “consolidate docs/inventory” · **no delete**

---

## DEFER_CLEAR (4) — retain experimental surfaces

| Path | Notes |
| --- | --- |
| `api/hybrid_server.py` | Experimental; lineage/hold |
| `api/sse_server.py` | Experimental; lineage/hold |
| `api/websocket_server.py` | Experimental; lineage/hold |
| `scripts/alembic/run_alembic_spine.py` | Experimental spine runner; advisory spine remains |

**Blockers:** OPERATOR_HOLD · PROVENANCE_LINEAGE · `deletion_proposed: false`  
**Operator recommendation:** DEFER (keep on disk) until a future, explicit experimental-surface decision · **no delete**

---

## DEPRECATE_DOCUMENT_ONLY (1)

| Path | Notes |
| --- | --- |
| `scripts/runtime/run_validation_service.py` | Supported library API shim; document deprecation only |

**Blockers:** OPERATOR_HOLD · PROVENANCE_LINEAGE · TEST_REFERENCE  
**Operator recommendation:** Document deprecation in README/scripts map if desired · **file remains** · **no delete**

---

## Dual-control status

| Control | Status |
| --- | --- |
| Engineering bucket review | **Complete** (this document) |
| Control A (human operator) | **Required** — not recorded by this review |
| Control B (second distinct human) | **Required** — not recorded by this review |
| dual_control.status | remains `PENDING` until A and B attest |
| mass_deletion_authorized | **false** |

A single agent or single human cannot satisfy dual-control. After A and B sign the checklist language in `docs/status/CLEAR_DUAL_CONTROL_OPERATOR_CHECKLIST_001.md`, eng can land an advisory dual-control receipt PR.

## Explicit non-authorizations

This review does **not**:

- authorize mass deletion  
- authorize EXTERNAL_PRODUCTION  
- authorize sandbox probe  
- unhold deploy  
- flip `operator_disposition_status` without dual-control receipt  
