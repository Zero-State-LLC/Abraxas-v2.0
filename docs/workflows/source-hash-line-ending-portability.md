# Source-Hash Line-Ending Portability

Developer runbook for raw-byte SHA-256 checks on hygiene source chains when working across Linux and Windows checkouts.

## Intent

Sealed hygiene receipts pin upstream files with `source_records[].file_hash` (raw SHA-256 of on-disk bytes). Windows checkouts that rewrite newlines to CRLF can change those bytes without changing JSON meaning. Validators must stay fail-closed on content edits while remaining portable for **line-ending-only** drift.

## Scope (verified in code)

| Surface | Path |
|---------|------|
| Validator | `core/sync/v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.py` |
| Tests | `tests/test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.py` |
| Runner | `scripts/hygiene/run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.py` |
| Evidence receipt | [`../audits/codebase-efficiency-2026/18_PHASE5_LINEENDING_PORTABILITY_REPAIR_RECEIPT.md`](../audits/codebase-efficiency-2026/18_PHASE5_LINEENDING_PORTABILITY_REPAIR_RECEIPT.md) |

This page documents **Phase 1 completion-validation execution receipt** hash matching only. Do not assume every hygiene module shares the same CRLF fallback unless its source shows `_file_hash_matches_expected` (or equivalent).

## Architecture

```text
implementation_receipt.source_records[].file_hash  (raw bytes at seal time)
        │
        ▼
_source_chain_hash_blockers()
        │
        ▼
_file_hash_matches_expected(path, expected)
        ├─ sha256(raw bytes) == expected          → accept
        └─ else sha256(CRLF/CR → LF only) == expected → accept
           else → blocker: implementation_receipt_source_hash_mismatch:<path>
```

Recording vs validation:

- **Emit / record:** `_sha256(path)` still stores the **raw-byte** hash. Sealed artifacts are not rewritten for portability.
- **Validate:** exact raw match first; LF-normalized match second; any other byte change fails closed.

Normalization is byte-level only:

```text
data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
```

No JSON re-canonicalization, whitespace trimming, or encoding changes.

## Usage

### Targeted regression suite

```bash
# Prefer scrubbed env if Hermes/agent PYTHONPATH is present
env -u PYTHONPATH -u PYTHONHOME python -m pytest -q \
  tests/test_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt.py
```

Covered cases (see tests):

- exact LF hash succeeds
- CRLF-equivalent content succeeds
- one-byte mutation fails
- JSON field mutation fails

### Build receipt without writing sealed paths

```bash
python - <<'PY'
from pathlib import Path
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt import (
    build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt,
)
packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(Path("."))
print(packet["status"], packet.get("source_blockers"))
PY
```

### Write to an isolated out root (safe local dry-run)

```bash
python - <<'PY'
from pathlib import Path
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt import (
    write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt,
)
write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_execution_receipt(
    Path("."),
    out_root=Path("/tmp/hygiene-receipt-dryrun"),
)
print("wrote under /tmp/hygiene-receipt-dryrun")
PY
```

Do **not** regenerate tracked `out/operator_review/*` or `out/archive/*` to “fix” hashes on Windows. Prefer validator-side acceptance or git line-ending configuration.

## Constraints

- Advisory / SHADOW posture: receipt builders do not grant execution, writeback, or promotion authority.
- Fail closed on semantic content changes (field flips, one-byte edits).
- CRLF tolerance is one-directional on observed bytes: normalize **observed** content to LF, then compare to the sealed hash (typically LF from Linux seal).
- `.gitattributes` in this repo does not currently force LF for `out/operator_review/**`; do not invent `autocrlf` policy in docs that the repo does not enforce.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `implementation_receipt_source_hash_mismatch:out/operator_review/...` on Windows only | Checkout rewrote LF→CRLF | Confirm fix is present (`_file_hash_matches_expected`). Re-run targeted pytest above. Do not rewrite sealed JSON. |
| Same blocker on Linux and Windows | Real content drift or wrong path | Diff against the sealed source path; restore from git; do not loosen validators further without operator approval. |
| Ready path becomes `BLOCKED` after editing an upstream gate JSON | Expected fail-closed | Undo the edit or open an authorized repair lane; do not regenerate the whole hygiene chain casually. |
| Fast CI / pytest import oddities under agent shells | Inherited `PYTHONPATH` / `PYTHONHOME` | `env -u PYTHONPATH -u PYTHONHOME python -m pytest ...` (see `AGENTS.md`). |
| In-repo `.venv` breaks worktree snapshot tooling | Local venv inside checkout | Use an external venv (outside the repo root) for long CI runs. |

## Related

- [`../testing/TEST_INDEX.md`](../testing/TEST_INDEX.md) — hygiene test map
- [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) — `scripts/hygiene/` runners
- [`../../AGENTS.md`](../../AGENTS.md) — determinism + no sealed-artifact cosmetics
- Artifact newline normalization elsewhere: `core/generated_artifact_registry.py` (`_normalize_newlines`) — **different surface**; do not conflate with hygiene source-record hashing
