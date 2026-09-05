---
name: abraxas-repo-intel
description: "Use when mapping Abraxas-v2.0 structure, gaps, ownership, call paths, or architecture before coding. Prefer codebase-memory MCP + rg/fd; emit smallest evidence packet."
version: 0.1.0
author: Hermes / Abraxas Governed Operator
license: Proprietary
platforms: [linux, macos]
metadata:
  hermes:
    tags: [abraxas, repo-intel, architecture, discovery, evidence]
    related_skills: [abraxas-master-loop-workflow, abx-familiar-signal-forager, codebase-inspection]
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# abraxas-repo-intel

Structural intelligence for the Abraxas repository. Repository-local procedure with a shipped heuristic builder; not a standalone graph service.

## When to Use

- Before non-trivial edits: where does this surface live?
- Ownership / pipeline / contract questions
- Gap analysis vs STATUS.md / PLANS.md / contracts/

## Workflow

1. Read `AGENTS.md`, `STATUS.md`, `PLANS.md` (mandatory router).
2. Prefer `codebase-memory-mcp` if available; else `rg` / `fd` / `search_files`.
3. Check `docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md` and `core/pipelines/registry.py`.
4. Emit a **small evidence packet**: paths, symbols, contracts, open gaps — not a full tree dump.
5. Hand off to `abraxas-master-loop-workflow` or task skills.

## Guardrails

- Do not invent DENIED/NO_GO flips; quote STATUS evidence.
- Do not regenerate sealed canary/continuity artifacts.
- Identity ≠ authority for any multi-agent findings.

## Scripts

The real helper takes no required arguments and writes checkout-local out/repo_intel. Run only in a disposable full checkout when regeneration is explicitly requested:

```bash
env -u PYTHONPATH -u PYTHONHOME python skills/abraxas-repo-intel/scripts/build_repo_intel.py
```


The helper is heuristic: graph relations from naming/import matching are not
proven execution traces. Its COMPLETE status only describes emitted inventory,
not repository correctness or satisfied governance. Verify nonempty manifest
files, each source path/hash, and exact expected outputs; never infer a live
process or authority from prior receipts. Prefer Graft map/ask before source
reads when an existing graph is available. For offline synthetic helper checks:
`python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_repo_intel_safety.py -q`.
