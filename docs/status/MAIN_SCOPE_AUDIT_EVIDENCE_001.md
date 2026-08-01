# Main-Scope Engineering Quality Audit Evidence — 001

**Status:** ADVISORY · evidence pointer · no production authority  
**Companion:** Notion [Engineering Quality — Main Scope Audit](https://app.notion.com/p/686b03d9e4b14fed9b8c3ea299e4804b)  
**Tooling:** `python -m abraxas os main-audit --execute-smoke --write`

## Latest observed run (this commit series)

| Field | Value |
|-------|--------|
| `commit_sha` | `4160db42f98686be3832faa895201dbf37dad51b` |
| `origin_main_sha` | `4160db42f98686be3832faa895201dbf37dad51b` |
| Main cleanliness | **PASS** · `out/audit/main_cleanliness.latest.json` |
| Fast CI (smoke) | **PASS** · `out/audit/fast_ci.latest.json` · mode `smoke_execute` |
| Same-SHA bound | **YES** |
| Full `run_fast_ci.py` | **Not claimed** by smoke receipt |
| Hard gates (primacy/binding/green) | **NOT_COMPUTABLE** in smoke packet (separate receipts) |

### Command

```bash
git checkout main && git pull --ff-only
python -m abraxas os main-audit --execute-smoke --write
```

### Semantics

- **PASS_SMOKE** = cleanliness PASS + smoke checks PASS on the same SHA  
- Does **not** replace GitHub `fast-ci` job or full `scripts/run_fast_ci.py`  
- Untracked local dirs (e.g. `.hermes/`) do not fail cleanliness  
- Re-emit after merges; hashes must match the SHA under audit  

### Boundary

No Notion writeback, no production unlock, no queue/ledger/memory mutation.
