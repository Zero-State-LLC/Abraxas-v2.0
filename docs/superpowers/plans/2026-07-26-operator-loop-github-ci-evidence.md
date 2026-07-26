# Operator-loop GitHub/CI Evidence Gatherer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit `gh`-based gatherer that writes compact GitHub/CI evidence files under `out/operator_loop/evidence/`, so the existing projection builder and live-console panel can show an operator status glance without granting any authority.

**Architecture:** Thin gatherer script shells out to `gh` only when invoked, writes `github.v1.json` and `ci.v1.json`. Projection stays offline (`collect_local_truth_surfaces` already loads those files). Console gets light polish for `open_pr` / `pr_checks_summary` item kinds. No network in `core/operator_loop.py` or on import.

**Tech Stack:** Python 3.12, `subprocess` + `gh` CLI, existing `json`/pathlib patterns, pytest, Vitest + React panel, `scripts/viz/` adapters.

**Spec:** `docs/superpowers/specs/2026-07-26-operator-loop-github-ci-evidence-design.md`

## Global Constraints

- Projection-only: never assign, approve, merge, or deploy.
- Every evidence item and surface keeps `authority_implication: "none"` and `can_assign/approve/merge/deploy: false` after projection normalization.
- No network calls inside `core/operator_loop.py` or on module import.
- CI tests must not call live GitHub; use fixtures/mocks only.
- No `scripts/operator/__init__.py`.
- Do not claim production go-live or unhold deploy/activation.
- Open PR cap default **15**, newest first.
- Two-step operator workflow remains explicit: gather, then build projection.

## File map

| Path | Responsibility |
| --- | --- |
| `scripts/viz/gather_operator_loop_github_ci_evidence.py` | CLI: invoke `gh`, write evidence JSON |
| `core/operator_loop_github_ci_evidence.py` | Pure builders: shape evidence from structured inputs (testable without `gh`) |
| `tests/test_operator_loop_github_ci_evidence.py` | Unit tests for pure builders + missing-`gh` path |
| `tests/fixtures/operator_loop_gh/` | Sample `gh` JSON fixtures |
| `apps/aal-viz-live-console/src/components/OperatorLoopProjectionPanel.tsx` | Friendly rows for open PR / check summary |
| `apps/aal-viz-live-console/src/components/OperatorLoopProjectionPanel.test.tsx` | Panel polish tests |
| `apps/aal-viz-live-console/README.md` | Two-step glance docs |
| `AGENTS.md` | One-line pointer under multi-agent / projection |
| `docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md` | Note gatherer as sequence 9 extension if needed |

---

### Task 1: Pure evidence builders (TDD)

**Files:**
- Create: `core/operator_loop_github_ci_evidence.py`
- Create: `tests/test_operator_loop_github_ci_evidence.py`
- Create: `tests/fixtures/operator_loop_gh/pr_list.json`
- Create: `tests/fixtures/operator_loop_gh/pr_checks_pass_fail.txt`
- Create: `tests/fixtures/operator_loop_gh/main_runs.json`

**Interfaces:**
- Consumes: none (new module)
- Produces:
  - `DEFAULT_PR_CAP: int = 15`
  - `build_github_evidence(*, repo: str, main_sha: str | None, main_branch: str, open_prs: list[dict], gathered_at: str, notes: list[str] | None = None, cap: int = DEFAULT_PR_CAP) -> dict[str, Any]`
  - `build_ci_evidence(*, main_runs: list[dict], pr_check_summaries: list[dict], gathered_at: str, notes: list[str] | None = None) -> dict[str, Any]`
  - `summarize_pr_checks(check_rows: list[dict[str, str]]) -> dict[str, Any]`  
    where each row has keys `name`, `state` (values like `pass`/`fail`/`pending`/`skipping` matching `gh pr checks` TSV/table parse)
  - `not_computable_evidence(*, surface: str, notes: list[str], gathered_at: str) -> dict[str, Any]`
  - `parse_gh_pr_checks_table(text: str) -> list[dict[str, str]]`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_operator_loop_github_ci_evidence.py
from __future__ import annotations

import json
from pathlib import Path

from core.operator_loop_github_ci_evidence import (
    DEFAULT_PR_CAP,
    build_ci_evidence,
    build_github_evidence,
    not_computable_evidence,
    parse_gh_pr_checks_table,
    summarize_pr_checks,
)

FIX = Path("tests/fixtures/operator_loop_gh")


def test_build_github_evidence_caps_and_shapes_open_prs() -> None:
    prs = [
        {
            "number": i,
            "title": f"PR {i}",
            "isDraft": i % 2 == 0,
            "mergeable": "MERGEABLE",
            "headRefName": f"feat/{i}",
            "baseRefName": "main",
            "url": f"https://example.com/{i}",
        }
        for i in range(1, 20)
    ]
    out = build_github_evidence(
        repo="scrimshawlife-ctrl/Abraxas-v2.0",
        main_sha="a" * 40,
        main_branch="main",
        open_prs=prs,
        gathered_at="2026-07-26T00:00:00Z",
        cap=DEFAULT_PR_CAP,
    )
    assert out["status"] == "PRESENT"
    assert out["source"] == "gh_cli"
    assert out["cap"] == 15
    assert out["repo"] == "scrimshawlife-ctrl/Abraxas-v2.0"
    open_items = [i for i in out["items"] if i["kind"] == "open_pr"]
    assert len(open_items) == 15
    assert all(i["authority_implication"] == "none" for i in out["items"])
    tip = next(i for i in out["items"] if i["kind"] == "git_tip")
    assert tip["sha"] == "a" * 40


def test_summarize_pr_checks_counts() -> None:
    rows = parse_gh_pr_checks_table(
        "fast-ci\tpass\t1m\thttps://x\n"
        "lint\tfail\t10s\thttps://y\n"
        "scan\tpending\t0\thttps://z\n"
    )
    summary = summarize_pr_checks(rows)
    assert summary["pass"] == 1
    assert summary["fail"] == 1
    assert summary["pending"] == 1
    assert summary["primary"] == "fail"


def test_not_computable_when_gh_missing() -> None:
    gh = not_computable_evidence(
        surface="github",
        notes=["gh CLI not found on PATH"],
        gathered_at="2026-07-26T00:00:00Z",
    )
    assert gh["status"] == "NOT_COMPUTABLE"
    assert gh["items"] == []
    assert "gh CLI" in gh["notes"][0]


def test_build_ci_evidence_includes_main_and_pr_summaries() -> None:
    out = build_ci_evidence(
        main_runs=[
            {
                "name": "ci",
                "conclusion": "success",
                "status": "completed",
                "headSha": "b" * 40,
                "url": "https://example.com/run/1",
            }
        ],
        pr_check_summaries=[
            {
                "pr_number": 42,
                "pass": 3,
                "fail": 0,
                "pending": 0,
                "primary": "pass",
            }
        ],
        gathered_at="2026-07-26T00:00:00Z",
    )
    assert out["status"] == "PRESENT"
    kinds = {i["kind"] for i in out["items"]}
    assert "main_workflow" in kinds
    assert "pr_checks_summary" in kinds
    assert all(i.get("authority_implication") == "none" for i in out["items"])
```

Write fixture files with minimal valid content (can be empty arrays `[]` for pr_list if unused by first tests).

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd /home/scrimshawlife/Abraxas-v2.0
.venv/bin/python -m pytest tests/test_operator_loop_github_ci_evidence.py -q --tb=short
```

Expected: `ModuleNotFoundError` or import errors for `core.operator_loop_github_ci_evidence`.

- [ ] **Step 3: Implement pure module**

```python
# core/operator_loop_github_ci_evidence.py
"""Build operator-loop GitHub/CI evidence snapshots (projection-only).

Pure helpers: no network, no gh subprocess. The gatherer script shells out
to gh and calls these builders. Authority locks always false / none.
"""

from __future__ import annotations

from typing import Any

DEFAULT_PR_CAP = 15


def not_computable_evidence(
    *,
    surface: str,
    notes: list[str],
    gathered_at: str,
) -> dict[str, Any]:
    return {
        "status": "NOT_COMPUTABLE",
        "source": "none",
        "gathered_at": gathered_at,
        "items": [],
        "notes": list(notes),
        "surface": surface,
    }


def build_github_evidence(
    *,
    repo: str,
    main_sha: str | None,
    main_branch: str,
    open_prs: list[dict[str, Any]],
    gathered_at: str,
    notes: list[str] | None = None,
    cap: int = DEFAULT_PR_CAP,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    if main_sha:
        items.append(
            {
                "kind": "git_tip",
                "sha": main_sha[:40],
                "branch": main_branch,
                "authority_implication": "none",
            }
        )
    # newest first: assume caller sorted; still re-sort by number desc
    sorted_prs = sorted(
        open_prs,
        key=lambda p: int(p.get("number") or 0),
        reverse=True,
    )[:cap]
    for pr in sorted_prs:
        items.append(
            {
                "kind": "open_pr",
                "number": int(pr["number"]),
                "title": str(pr.get("title") or ""),
                "is_draft": bool(pr.get("isDraft", pr.get("is_draft", False))),
                "mergeable": str(
                    pr.get("mergeable") or "UNKNOWN"
                ).upper()
                if pr.get("mergeable") is not None
                else "UNKNOWN",
                "head_branch": str(
                    pr.get("headRefName") or pr.get("head_branch") or ""
                ),
                "base_branch": str(
                    pr.get("baseRefName") or pr.get("base_branch") or "main"
                ),
                "url": str(pr.get("url") or ""),
                "authority_implication": "none",
            }
        )
    status = "PRESENT" if items else "NOT_COMPUTABLE"
    return {
        "status": status,
        "source": "gh_cli",
        "gathered_at": gathered_at,
        "repo": repo,
        "cap": cap,
        "items": items,
        "notes": list(notes or []),
    }


def parse_gh_pr_checks_table(text: str) -> list[dict[str, str]]:
    """Parse `gh pr checks` default tab-separated rows: name, state, ..."""
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            parts = line.split()
        if len(parts) < 2:
            continue
        rows.append({"name": parts[0], "state": parts[1].lower()})
    return rows


def summarize_pr_checks(check_rows: list[dict[str, str]]) -> dict[str, Any]:
    pass_n = fail_n = pending_n = 0
    for row in check_rows:
        state = (row.get("state") or "").lower()
        if state in {"fail", "failure", "cancelled", "timed_out", "action_required", "error"}:
            fail_n += 1
        elif state in {"pending", "in_progress", "queued"}:
            pending_n += 1
        elif state in {"pass", "success", "skipping", "skip", "neutral"}:
            pass_n += 1
        else:
            pending_n += 1
    if fail_n > 0:
        primary = "fail"
    elif pending_n > 0 and pass_n > 0:
        primary = "mixed"
    elif pending_n > 0:
        primary = "pending"
    else:
        primary = "pass"
    return {
        "pass": pass_n,
        "fail": fail_n,
        "pending": pending_n,
        "primary": primary,
        "authority_implication": "none",
    }


def build_ci_evidence(
    *,
    main_runs: list[dict[str, Any]],
    pr_check_summaries: list[dict[str, Any]],
    gathered_at: str,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for run in main_runs:
        items.append(
            {
                "kind": "main_workflow",
                "workflow": str(run.get("name") or run.get("workflow") or "ci"),
                "conclusion": str(run.get("conclusion") or ""),
                "status": str(run.get("status") or ""),
                "head_sha": str(run.get("headSha") or run.get("head_sha") or "")[:40],
                "url": str(run.get("url") or ""),
                "authority_implication": "none",
            }
        )
    for summary in pr_check_summaries:
        items.append(
            {
                "kind": "pr_checks_summary",
                "pr_number": int(summary["pr_number"]),
                "pass": int(summary.get("pass") or 0),
                "fail": int(summary.get("fail") or 0),
                "pending": int(summary.get("pending") or 0),
                "primary": str(summary.get("primary") or "pending"),
                "authority_implication": "none",
            }
        )
    status = "PRESENT" if items else "NOT_COMPUTABLE"
    return {
        "status": status,
        "source": "gh_cli",
        "gathered_at": gathered_at,
        "items": items,
        "notes": list(notes or []),
    }
```

**Implementer note:** Fix `summarize_pr_checks` logic so it is clear and matches the tests (fail dominates; pending without fail → pending or mixed). Do not leave dead nested ifs.

- [ ] **Step 4: Run tests — expect PASS**

```bash
.venv/bin/python -m pytest tests/test_operator_loop_github_ci_evidence.py -q --tb=short
.venv/bin/python -m ruff check core/operator_loop_github_ci_evidence.py tests/test_operator_loop_github_ci_evidence.py
```

- [ ] **Step 5: Commit**

```bash
git add core/operator_loop_github_ci_evidence.py tests/test_operator_loop_github_ci_evidence.py tests/fixtures/operator_loop_gh/
git commit -m "feat(operator-loop): pure GitHub/CI evidence builders for status glance"
```

---

### Task 2: Gatherer CLI script

**Files:**
- Create: `scripts/viz/gather_operator_loop_github_ci_evidence.py`
- Modify: `tests/test_operator_loop_github_ci_evidence.py` (add gatherer unit tests with mocked subprocess)

**Interfaces:**
- Consumes: `build_github_evidence`, `build_ci_evidence`, `not_computable_evidence`, `parse_gh_pr_checks_table`, `summarize_pr_checks` from Task 1
- Produces: CLI `main(argv: list[str] | None = None) -> int` writing:
  - `{evidence_dir}/github.v1.json`
  - `{evidence_dir}/ci.v1.json`

- [ ] **Step 1: Write failing test for missing gh**

```python
def test_gather_writes_not_computable_when_gh_missing(tmp_path, monkeypatch) -> None:
    from scripts.viz import gather_operator_loop_github_ci_evidence as gather

    monkeypatch.setattr(gather, "gh_available", lambda: False)
    code = gather.main(["--evidence-dir", str(tmp_path), "--repo", "o/r"])
    assert code == 0
    github = json.loads((tmp_path / "github.v1.json").read_text())
    ci = json.loads((tmp_path / "ci.v1.json").read_text())
    assert github["status"] == "NOT_COMPUTABLE"
    assert ci["status"] == "NOT_COMPUTABLE"
```

**Import note:** If `scripts.viz` is not a package, test by importing via importlib from path, or put a thin `run_gather(...)` function in `core/operator_loop_github_ci_evidence.py` / gatherer module loaded with:

```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "gather_ol",
    "scripts/viz/gather_operator_loop_github_ci_evidence.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
```

Prefer implementing `gather_and_write(...)` in `core/operator_loop_github_ci_evidence.py` so tests import cleanly, and keep the script as a thin CLI.

- [ ] **Step 2: Run test — expect FAIL** (module/function missing)

- [ ] **Step 3: Implement `gather_and_write` + CLI**

In `core/operator_loop_github_ci_evidence.py` add:

```python
def gather_and_write(
    *,
    evidence_dir: Path,
    gh_runner: Callable[[list[str]], tuple[int, str, str]] | None = None,
    gh_on_path: bool | None = None,
    max_prs: int = DEFAULT_PR_CAP,
    now_iso: str | None = None,
    repo: str | None = None,
) -> dict[str, Path]:
    """Write github.v1.json and ci.v1.json. Never grants authority.

    gh_runner(argv) -> (returncode, stdout, stderr). If None, use subprocess.
    """
```

Behavior:
1. `gathered_at = now_iso or utc_now_iso()`
2. If `gh_on_path is False` or `gh` missing: write two `not_computable_evidence` files; return paths.
3. Else:
   - `repo = repo or run gh repo view --json nameWithOwner -q .nameWithOwner`
   - main tip: `gh api repos/{repo}/commits/main --jq .sha` (or `git rev-parse origin/main` if gh fails — prefer gh; on failure note it)
   - open PRs: `gh pr list --state open --limit {max_prs} --json number,title,isDraft,mergeable,headRefName,baseRefName,url`
   - main runs: `gh run list --branch main --limit 5 --json name,conclusion,status,headSha,url,databaseId,workflowName` filter to workflow named `ci` or name `fast-ci` / display contains `ci`
   - for each PR: `gh pr checks {n}` → parse → summarize; attach `pr_number`
4. Write JSON with `indent=2, sort_keys=True`.

CLI script:

```python
#!/usr/bin/env python3
"""Gather GitHub/CI evidence for operator-loop projection (explicit, offline-write)."""
# sys.path insert ROOT like other scripts/viz/*
# argparse: --evidence-dir, --max-prs, --repo
# call gather_and_write; print paths; exit 0 even on NOT_COMPUTABLE (fail-visible files)
```

- [ ] **Step 4: Tests for happy path with fake `gh_runner`**

```python
def test_gather_with_fake_gh(tmp_path) -> None:
    def fake(argv: list[str]) -> tuple[int, str, str]:
        if argv[:3] == ["gh", "repo", "view"]:
            return 0, "owner/repo\n", ""
        if "pr" in argv and "list" in argv:
            return 0, json.dumps([{
                "number": 7,
                "title": "feat x",
                "isDraft": False,
                "mergeable": "MERGEABLE",
                "headRefName": "feat/x",
                "baseRefName": "main",
                "url": "https://example.com/7",
            }]), ""
        if "checks" in argv:
            return 0, "fast-ci\tpass\t1s\thttps://x\n", ""
        if "run" in argv and "list" in argv:
            return 0, json.dumps([{
                "name": "fast-ci",
                "conclusion": "success",
                "status": "completed",
                "headSha": "c" * 40,
                "url": "https://example.com/run",
                "workflowName": "ci",
            }]), ""
        if "commits" in argv or (len(argv) > 2 and "api" in argv):
            return 0, "d" * 40 + "\n", ""
        return 1, "", "unknown"
    paths = gather_and_write(
        evidence_dir=tmp_path,
        gh_runner=fake,
        gh_on_path=True,
        now_iso="2026-07-26T12:00:00Z",
        repo="owner/repo",
    )
    github = json.loads(paths["github"].read_text())
    assert github["status"] == "PRESENT"
    assert any(i["kind"] == "open_pr" and i["number"] == 7 for i in github["items"])
```

Adjust `fake` branches to match the actual argv the implementation uses.

- [ ] **Step 5: Run tests + ruff — expect PASS**

```bash
.venv/bin/python -m pytest tests/test_operator_loop_github_ci_evidence.py -q --tb=short
.venv/bin/python -m ruff check core/operator_loop_github_ci_evidence.py scripts/viz/gather_operator_loop_github_ci_evidence.py tests/test_operator_loop_github_ci_evidence.py
```

- [ ] **Step 6: Commit**

```bash
git add core/operator_loop_github_ci_evidence.py scripts/viz/gather_operator_loop_github_ci_evidence.py tests/test_operator_loop_github_ci_evidence.py
git commit -m "feat(viz): gather operator-loop GitHub/CI evidence via gh CLI"
```

---

### Task 3: Integration with projection (smoke)

**Files:**
- Modify: `tests/test_operator_loop_contracts.py` (or add cases in evidence tests)
- No change required to `collect_local_truth_surfaces` if files already load — verify only

**Interfaces:**
- Consumes: evidence files from Task 2 + `collect_local_truth_surfaces` / `build_operator_loop_projection`
- Produces: assertion that projection `truth_surfaces.github.items` includes `open_pr`

- [ ] **Step 1: Write failing integration test**

```python
def test_projection_loads_gathered_github_evidence(tmp_path: Path) -> None:
    from core.operator_loop import build_operator_loop_projection, collect_local_truth_surfaces
    from core.operator_loop_github_ci_evidence import build_github_evidence, build_ci_evidence

    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "github.v1.json").write_text(
        json.dumps(
            build_github_evidence(
                repo="o/r",
                main_sha="e" * 40,
                main_branch="main",
                open_prs=[{
                    "number": 9,
                    "title": "t",
                    "isDraft": False,
                    "mergeable": "MERGEABLE",
                    "headRefName": "f",
                    "baseRefName": "main",
                    "url": "https://x/9",
                }],
                gathered_at="2026-07-26T00:00:00Z",
            )
        ),
        encoding="utf-8",
    )
    (evidence / "ci.v1.json").write_text(
        json.dumps(
            build_ci_evidence(
                main_runs=[{
                    "name": "ci",
                    "conclusion": "success",
                    "status": "completed",
                    "headSha": "e" * 40,
                    "url": "https://x/run",
                }],
                pr_check_summaries=[{
                    "pr_number": 9,
                    "pass": 2,
                    "fail": 0,
                    "pending": 0,
                    "primary": "pass",
                }],
                gathered_at="2026-07-26T00:00:00Z",
            )
        ),
        encoding="utf-8",
    )
    surfaces = collect_local_truth_surfaces(
        evidence_dir=evidence,
        include_local_git=False,
    )
    proj = build_operator_loop_projection(truth_surfaces=surfaces)
    assert proj["truth_surfaces"]["github"]["status"] == "PRESENT"
    assert proj["summary"]["github_item_count"] >= 2
    assert proj["authority"]["assignment_authority"] is False
```

- [ ] **Step 2: Run test — expect PASS** if loader already works; if FAIL, fix `collect_local_truth_surfaces` only as needed (still no network).

- [ ] **Step 3: Commit if any code change; otherwise skip commit**

```bash
git add tests/test_operator_loop_contracts.py  # or evidence test file
git commit -m "test(operator-loop): projection loads gathered GitHub/CI evidence"
```

---

### Task 4: Console polish for status glance rows

**Files:**
- Modify: `apps/aal-viz-live-console/src/components/OperatorLoopProjectionPanel.tsx`
- Modify: `apps/aal-viz-live-console/src/components/OperatorLoopProjectionPanel.test.tsx`
- Modify: `apps/aal-viz-live-console/src/styles.css` (minimal)

**Interfaces:**
- Consumes: projection `truth_surfaces.*.items` with `kind: open_pr | pr_checks_summary | git_tip | main_workflow`
- Produces: readable rows; still no action buttons

- [ ] **Step 1: Extend panel test with open_pr sample item**

```tsx
// In SAMPLE.truth_surfaces.github.items:
{ kind: 'open_pr', number: 42, title: 'feat: example', is_draft: false, mergeable: 'MERGEABLE', primary: undefined },
// And ci items:
{ kind: 'pr_checks_summary', pr_number: 42, pass: 3, fail: 0, pending: 0, primary: 'pass' },

it('renders open PR title for status glance', async () => {
  // ...fetch SAMPLE
  await waitFor(() => {
    expect(screen.getByText(/#42/)).toBeInTheDocument();
    expect(screen.getByText(/feat: example/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run vitest — expect FAIL** (raw JSON only)

```bash
cd apps/aal-viz-live-console && npm test -- --run src/components/OperatorLoopProjectionPanel.test.tsx
```

- [ ] **Step 3: Implement `renderItem(item)` helper**

```tsx
function renderItem(item: Record<string, unknown>): string {
  const kind = String(item.kind || '');
  if (kind === 'open_pr') {
    const n = item.number;
    const title = item.title;
    const draft = item.is_draft ? 'draft' : 'ready';
    const mergeable = item.mergeable ?? 'UNKNOWN';
    return `#${n} ${title} · ${draft} · ${mergeable}`;
  }
  if (kind === 'pr_checks_summary') {
    return `PR #${item.pr_number} checks · ${item.primary} (pass=${item.pass} fail=${item.fail} pending=${item.pending})`;
  }
  if (kind === 'git_tip') {
    return `tip ${String(item.sha).slice(0, 7)} @ ${item.branch}`;
  }
  if (kind === 'main_workflow') {
    return `${item.workflow} · ${item.conclusion || item.status}`;
  }
  return JSON.stringify(item);
}
```

Use `renderItem` instead of `JSON.stringify` in the surface item list. Raise item slice from 4 to 8 for glance usefulness. Keep the “DISPLAY ONLY — NO ASSIGNMENT…” footer.

- [ ] **Step 4: Run vitest — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add apps/aal-viz-live-console/src/components/OperatorLoopProjectionPanel.tsx \
  apps/aal-viz-live-console/src/components/OperatorLoopProjectionPanel.test.tsx \
  apps/aal-viz-live-console/src/styles.css
git commit -m "feat(aal-viz): status-glance rows for open PR and CI summaries"
```

---

### Task 5: Docs

**Files:**
- Modify: `apps/aal-viz-live-console/README.md` (preserve CRLF if present)
- Modify: `AGENTS.md` (Projection / multi-agent section)
- Optional: one line in `docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md` under sequence 9 pointing at the gatherer

- [ ] **Step 1: Update console README**

Add after operator-loop projection paragraph:

```markdown
Live GitHub/CI glance (optional, explicit):

```bash
python3 scripts/viz/gather_operator_loop_github_ci_evidence.py
python3 scripts/viz/build_aal_viz_operator_loop_projection.py
```

Requires authenticated `gh` on PATH. Writes `out/operator_loop/evidence/github.v1.json` and `ci.v1.json`. Projection and console remain display-only.
```

- [ ] **Step 2: Update AGENTS.md**

Under multi-agent / projection, add:

```markdown
- Operator-loop GitHub/CI glance (optional): `python3 scripts/viz/gather_operator_loop_github_ci_evidence.py` then projection builder; evidence under `out/operator_loop/evidence/`; never grants merge/assign authority
```

- [ ] **Step 3: Commit**

```bash
git add apps/aal-viz-live-console/README.md AGENTS.md docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md
git commit -m "docs: operator-loop GitHub/CI evidence gather workflow"
```

---

### Task 6: End-to-end verification + PR

- [ ] **Step 1: Full local verification**

```bash
cd /home/scrimshawlife/Abraxas-v2.0
.venv/bin/python -m pytest tests/test_operator_loop_github_ci_evidence.py tests/test_operator_loop_contracts.py -q --tb=short
.venv/bin/python -m ruff check core/operator_loop_github_ci_evidence.py scripts/viz/gather_operator_loop_github_ci_evidence.py
cd apps/aal-viz-live-console && npm test -- --run src/components/OperatorLoopProjectionPanel.test.tsx
# optional live smoke (only if gh authenticated; do not require for CI):
# python3 scripts/viz/gather_operator_loop_github_ci_evidence.py && python3 scripts/viz/build_aal_viz_operator_loop_projection.py
```

- [ ] **Step 2: Open PR**

```bash
git push -u origin HEAD
gh pr create --base main --title "feat(operator-loop): GitHub/CI evidence gatherer for status glance" --body "$(cat <<'EOF'
## Summary
Implements docs/superpowers/specs/2026-07-26-operator-loop-github-ci-evidence-design.md:
explicit gh gatherer → evidence files → existing projection/console.

## Test plan
- [x] unit tests with fixtures/mocks
- [x] projection loads evidence
- [x] console polish tests
- [ ] CI green
EOF
)"
```

- [ ] **Step 3: Merge only when CI green** (human or orchestrator REST merge; no force)

---

## Plan self-review

| Spec section | Task coverage |
| --- | --- |
| Explicit gatherer via `gh` | Task 2 |
| Evidence schemas compact pack | Task 1 builders |
| Cap 15 open PRs | Task 1 `DEFAULT_PR_CAP` + tests |
| Missing `gh` → NOT_COMPUTABLE | Task 1 + Task 2 |
| Offline projection reuse | Task 3 |
| Console light polish | Task 4 |
| Docs two-step workflow | Task 5 |
| No network in core | Task 1 pure; gatherer isolated |
| No assign/approve/merge | All builders set `authority_implication: none`; projection locks unchanged |
| Tests without live GitHub | Fixtures + `gh_runner` injection |

**Placeholder scan:** none intentional.  
**Type consistency:** `build_github_evidence` / `build_ci_evidence` / `gather_and_write` names stable across tasks.
