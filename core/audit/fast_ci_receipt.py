"""Main-scope fast-CI receipt (advisory).

Normalizes check outcomes into ``out/audit/fast_ci.latest.json`` for the Notion
main-scope engineering-quality audit. Does not grant production authority.

Full suite remains ``python scripts/run_fast_ci.py`` / GitHub ``fast-ci`` job.
This receipt may record injected results or run a bounded smoke set.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "FastCiReceipt.v0"
DEFAULT_OUT_PATH = "out/audit/fast_ci.latest.json"
AUTHORITATIVE_FULL_CI_COMMAND = "python scripts/run_fast_ci.py"
GITHUB_JOB = "fast-ci"

AUTHORITY = {
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "production_activation_allowed": False,
    "notion_writeback_allowed": False,
}

CheckRunner = Callable[[Sequence[str], Path], dict[str, Any]]


def _default_runner(cmd: Sequence[str], repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        list(cmd),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "exit_code": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-500:],
        "stderr_tail": (completed.stderr or "")[-500:],
    }


def smoke_check_commands(python: str = sys.executable) -> list[dict[str, Any]]:
    """Bounded smoke set for main-scope packaging (not full CI)."""
    return [
        {
            "name": "pytest_main_scope_audit_receipts",
            "command": [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/test_main_scope_audit_receipts.py",
            ],
            "required": True,
        },
        {
            "name": "ruff_audit_modules",
            "command": [
                python,
                "-m",
                "ruff",
                "check",
                "core/audit/main_cleanliness_receipt.py",
                "core/audit/fast_ci_receipt.py",
                "tests/test_main_scope_audit_receipts.py",
            ],
            "required": True,
        },
        {
            "name": "import_abraxas_cli",
            "command": [python, "-c", "import abraxas.cli"],
            "required": True,
        },
    ]


def run_checks(
    check_specs: Sequence[Mapping[str, Any]],
    *,
    repo_root: Path,
    runner: CheckRunner | None = None,
) -> list[dict[str, Any]]:
    run = runner or _default_runner
    results: list[dict[str, Any]] = []
    for spec in check_specs:
        cmd = list(spec["command"])
        raw = run(cmd, repo_root)
        exit_code = int(raw.get("exit_code", 1))
        # ruff missing → NOT_COMPUTABLE rather than hard FAIL for optional tools
        stderr = str(raw.get("stderr_tail") or "")
        if exit_code != 0 and "No module named ruff" in stderr:
            status = "NOT_COMPUTABLE"
        else:
            status = "PASS" if exit_code == 0 else "FAIL"
        results.append(
            {
                "name": str(spec["name"]),
                "command": cmd,
                "required": bool(spec.get("required", True)),
                "exit_code": exit_code,
                "status": status,
                "stdout_tail": raw.get("stdout_tail"),
                "stderr_tail": raw.get("stderr_tail"),
            }
        )
    return results


def _aggregate_status(checks: Sequence[Mapping[str, Any]]) -> str:
    if not checks:
        return "NOT_COMPUTABLE"
    required = [c for c in checks if c.get("required", True)]
    pool = required or list(checks)
    if any(c.get("status") == "FAIL" for c in pool):
        return "FAIL"
    if any(c.get("status") == "NOT_COMPUTABLE" for c in pool):
        return "NOT_COMPUTABLE"
    if all(c.get("status") == "PASS" for c in pool):
        return "PASS"
    return "NOT_COMPUTABLE"


def build_fast_ci_receipt(
    *,
    repo_root: str | Path = ".",
    commit_sha: str | None = None,
    origin_main_sha: str | None = None,
    check_results: Sequence[Mapping[str, Any]] | None = None,
    execute_smoke: bool = False,
    runner: CheckRunner | None = None,
    mode: str = "record",
) -> dict[str, Any]:
    """Build FastCiReceipt.v0.

    - ``check_results``: precomputed outcomes (preferred for tests / CI inject)
    - ``execute_smoke=True``: run bounded smoke checks under ``repo_root``
    - neither: status NOT_COMPUTABLE (meta-only packaging receipt)
    """
    root = Path(repo_root).resolve()

    def _git_sha(ref: str) -> str | None:
        completed = subprocess.run(
            ["git", "rev-parse", ref],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip() if completed.returncode == 0 else None

    if commit_sha is None:
        commit_sha = _git_sha("HEAD")
    if origin_main_sha is None:
        origin_main_sha = _git_sha("origin/main")

    if check_results is not None:
        checks = [dict(item) for item in check_results]
        mode = "injected"
    elif execute_smoke:
        checks = run_checks(smoke_check_commands(), repo_root=root, runner=runner)
        mode = "smoke_execute"
    else:
        checks = []
        mode = "meta_only"

    status = _aggregate_status(checks) if checks else "NOT_COMPUTABLE"
    reasons: list[str] = []
    if not checks:
        reasons.append("no_check_results_execute_smoke_or_inject_required")
    for item in checks:
        if item.get("status") == "FAIL":
            reasons.append(f"fail:{item.get('name')}")
        if item.get("status") == "NOT_COMPUTABLE":
            reasons.append(f"not_computable:{item.get('name')}")

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "mode": mode,
        "commit_sha": commit_sha,
        "origin_main_sha": origin_main_sha,
        "authoritative_full_ci_command": AUTHORITATIVE_FULL_CI_COMMAND,
        "github_job": GITHUB_JOB,
        "smoke_scope": "main_scope_audit_receipts_ruff_import",
        "checks": checks,
        "required_check_count": sum(1 for c in checks if c.get("required", True)),
        "pass_count": sum(1 for c in checks if c.get("status") == "PASS"),
        "fail_count": sum(1 for c in checks if c.get("status") == "FAIL"),
        "not_computable_count": sum(
            1 for c in checks if c.get("status") == "NOT_COMPUTABLE"
        ),
        "reasons": reasons,
        "gate_run_summary": {
            "note": (
                "Hard gates (rune primacy / binding / green-state) remain separate "
                "receipts; this packet packages hygiene checks only."
            ),
            "rune_registry_primacy": "NOT_COMPUTABLE",
            "binding_validator": "NOT_COMPUTABLE",
            "green_state_attestation": "NOT_COMPUTABLE",
        },
        "authority": dict(AUTHORITY),
        "advisory_only": True,
        "projection_only": True,
        "lane": "SHADOW",
        "producer": {
            "module": "core.audit.fast_ci_receipt",
            "purpose": "notion_main_scope_engineering_quality_audit",
        },
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def write_fast_ci_receipt(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
