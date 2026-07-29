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

# abraxas-repo-intel

Structural intelligence for the Abraxas repository. **Restore stub** — full graph builders may live under `scripts/`; this skill is the Hermes-facing procedure.

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

Inspect `skills/abraxas-repo-intel/scripts/` for any local helpers; run scrubbed:

```bash
env -u PYTHONPATH -u PYTHONHOME python ...
```
