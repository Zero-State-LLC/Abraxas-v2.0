# Notion Reconciliation Snapshot — 2026-07-31

**Status:** ADVISORY · operator paste source · **no autonomous Notion writeback**  
**Repo SHA (landed at doc authoring):** see `origin/main` after #1072 + #1073 (tiered ownership + familiar queue dry-run)  
**Authority:** GitHub = implementation evidence · Notion = registered architecture · live repo wins on conflict

Use this page to refresh Notion without inventing a second source of truth. Operator may paste sections into:

- [Master Index + Ownership Map](https://app.notion.com/p/7fbc6e1c1ddd4c74bc01df72f15d959e)
- [Subsystem Inventory / Canon Spine](https://app.notion.com/p/73460b504dfd4cc393e7906559678624)
- [Technical Debt & Engineering Direction Board](https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254)
- [Engineering Quality — Main Scope Audit](https://app.notion.com/p/686b03d9e4b14fed9b8c3ea299e4804b)

---

## 1. Live repo baseline (replace 2026-07-23 snapshots)

```yaml
repo: scrimshawlife-ctrl/Abraxas-v2.0
default_branch: main
ai_os_kernel: ACTIVE_SHADOW
external_production_authorized: false
track_b_packet_missing_contract: 0
ownership_tiers:
  ALIGNED: 10
  CONTRACT_V0: 7
  REVIEW_V0: 1   # abx-familiar (receipt+bridge+review+queue dry-run)
  MISSING_CONTRACT: 0
alembic: ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS
```

**Merged since mid-July Notion snapshots (selected):**

| Area | Evidence |
|------|----------|
| AI OS kernel path | EvidencePack → ingest → spine → oracle/belief bridge → operator-review → **queue dry-run** (#1072) |
| Track B operator packets | Neon, Noctis, Holler, Memetic, Level99, BeatOven, Phonomicon CONTRACT_V0 |
| Projection truth | Tiered ownership matrix/health (#1073) |
| Stale Notion open-PR list | #986 **merged**; #987/#989 **closed** (not still open) |

**Open PRs to main (check live):** use GitHub; do not trust old Notion open-stack lists.

---

## 2. Debt board reinterpretation (D1–D6)

| Debt | Notion intent | Repo state 2026-07-31 |
|------|---------------|------------------------|
| D1 docs topology | Single entry | Largely landed; residual = Notion lag |
| D2 artifact registry | Classify lifecycle | Ongoing; not a MISSING_CONTRACT issue |
| D3 continuity compression | Lineage map | Present; historical |
| D4 ownership matrix | Map ownership | **Closed at packet tier** (0 true MISSING) |
| D5 test visibility | Subsystem→test | Medium priority residual |
| D6 runtime readiness | Planned→Integrated | SHADOW/advisory; production denied |

**Not current focus (still correct):** new governance layers, authz chains, canon expansion, production activation.

---

## 3. AI OS kernel (register on Canon Spine / Master Index)

```text
forage → EvidencePack.v0
  → FamiliarIngestionReceipt.v0
  → FamiliarSpineTouchpoint.v0
  → FamiliarOracleBeliefBridge.v0
  → FamiliarOperatorReviewPacket.v0
  → FamiliarOperatorReviewQueueDryRun.v0  (no out/operator_review_queue write)
```

CLI:

```bash
python -m abraxas os status
python -m abraxas forage operator-review-dry-run --pack PATH
python -m abraxas os main-audit --execute-smoke --write
```

---

## 4. Main-scope engineering-quality audit (close PARTIAL)

Repo emitters (this PR track):

| Receipt | Path | Builder |
|---------|------|---------|
| Main cleanliness | `out/audit/main_cleanliness.latest.json` | `core.audit.main_cleanliness_receipt` |
| Fast CI (smoke or injected) | `out/audit/fast_ci.latest.json` | `core.audit.fast_ci_receipt` |

```bash
python scripts/readiness/run_main_cleanliness_receipt.py
python scripts/readiness/run_fast_ci_receipt.py --execute-smoke
# or
python -m abraxas os main-audit --execute-smoke --write
```

**PASS rule (Notion):** both receipts bound to the **same** `commit_sha` / `origin_main_sha`.  
Smoke scope ≠ full `scripts/run_fast_ci.py`; full CI remains GitHub `fast-ci` job.  
Hard gates (rune primacy / binding / green) stay separate pointers unless later embedded.

---

## 5. Explicit non-goals

- Autonomous Notion/GitHub writeback from agents  
- Live operator_review_queue write without dual-control  
- Alembic unstub / EXTERNAL_PRODUCTION  
- Reopening Track B as if packets were missing  

---

## Seal

Advisory reconciliation aid only. Does not mutate Notion, grant authority, or flip production readiness.
