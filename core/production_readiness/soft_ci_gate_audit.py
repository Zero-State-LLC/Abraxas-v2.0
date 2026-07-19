"""WP-N: inventory soft (continue-on-error / non-blocking) CI gates."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_soft_ci_gate_audit"
OUT_DIR_REL = Path("out/production_readiness/ws6")

CONTINUE_ON_ERROR_RE = re.compile(
    r"^\s*continue-on-error\s*:\s*(true|True|yes|1)\s*(?:#\s*(.*))?$",
    re.MULTILINE,
)
# Report-only steps in run_fast_ci (advisory, exit ignored)
ADVISORY_FAST_CI_MARKERS = (
    "ADVISORY_REPORT_ONLY_COMMANDS",
    "_run_advisory_report_only_gates",
    "ABRAXAS_BOUNDARY_FAIL_CLOSED",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _classify_workflow_gate(workflow: str, step_comment: str | None) -> dict[str, str]:
    comment = (step_comment or "").lower()
    name = workflow.lower()
    if "rune" in comment or "rune" in name:
        return {
            "disposition": "KEEP_REPORT_ONLY",
            "rationale": "Historical rune integrity is intentionally non-blocking.",
            "priority": "P2",
        }
    if "p64" in comment or "p64" in name or "manifest" in comment:
        return {
            "disposition": "KEEP_UNTIL_OPERATOR_RESEAL",
            "rationale": "Documented historical P57/P64 hash drift; operator lane required.",
            "priority": "P1",
        }
    if "flak" in comment or "speed" in comment:
        return {
            "disposition": "REVIEW_HARDEN",
            "rationale": "Softened for flakiness; reassess whether P0 quality is masked.",
            "priority": "P1",
        }
    return {
        "disposition": "REVIEW",
        "rationale": "continue-on-error without clear readiness justification.",
        "priority": "P1",
    }


def scan_workflow_soft_gates(repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    workflows = sorted((repo_root / ".github" / "workflows").rglob("*.yml"))
    workflows += sorted((repo_root / ".github" / "workflows").rglob("*.yaml"))
    for wf in workflows:
        rel = str(wf.relative_to(repo_root)).replace("\\", "/")
        try:
            text = wf.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in CONTINUE_ON_ERROR_RE.finditer(text):
            # Approximate step name: search backwards for "- name:"
            start = match.start()
            prefix = text[:start]
            name_match = re.findall(r"-\s*name:\s*(.+)", prefix)
            step_name = name_match[-1].strip() if name_match else "(unknown step)"
            comment = match.group(2)
            classification = _classify_workflow_gate(rel + " " + step_name, comment)
            # line number
            line_no = text.count("\n", 0, start) + 1
            findings.append(
                {
                    "kind": "workflow_continue_on_error",
                    "path": rel,
                    "line": line_no,
                    "step_name": step_name,
                    "comment": comment,
                    **classification,
                }
            )
    return findings


def scan_fast_ci_advisory(repo_root: Path) -> list[dict[str, Any]]:
    path = repo_root / "scripts" / "run_fast_ci.py"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    findings: list[dict[str, Any]] = []
    for marker in ADVISORY_FAST_CI_MARKERS:
        if marker in text:
            findings.append(
                {
                    "kind": "fast_ci_advisory_fail_open",
                    "path": "scripts/run_fast_ci.py",
                    "marker": marker,
                    "disposition": "KEEP_REPORT_ONLY",
                    "rationale": (
                        "Intentionally fail-open readiness probes; promotion to fail-closed "
                        "requires operator approval (WP-E / sole-writer criteria)."
                    ),
                    "priority": "P0_TRACKED",
                }
            )
    # List advisory commands if present
    if "ADVISORY_REPORT_ONLY_COMMANDS" in text:
        cmds = re.findall(
            r'\[\s*"python"\s*,\s*"([^"]+)"\s*\]',
            text[text.find("ADVISORY_REPORT_ONLY_COMMANDS") : text.find("ADVISORY_REPORT_ONLY_COMMANDS") + 800],
        )
        for cmd in cmds:
            findings.append(
                {
                    "kind": "fast_ci_advisory_command",
                    "path": "scripts/run_fast_ci.py",
                    "command": cmd,
                    "disposition": "KEEP_REPORT_ONLY",
                    "rationale": "Report-only gate; exit ignored by design.",
                    "priority": "P1",
                }
            )
    return findings


def build_soft_ci_gate_audit(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    workflow_findings = scan_workflow_soft_gates(repo_root)
    fast_ci_findings = scan_fast_ci_advisory(repo_root)
    all_findings = workflow_findings + fast_ci_findings

    by_disp: dict[str, int] = {}
    for f in all_findings:
        d = f.get("disposition", "UNKNOWN")
        by_disp[d] = by_disp.get(d, 0) + 1

    audit: dict[str, Any] = {
        "schema_version": "soft_ci_gate_audit.v1",
        "artifact_type": "soft_ci_gate_audit",
        "work_package": "WP-N_SOFT_CI_GATE_AUDIT",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "summary": {
            "finding_count": len(all_findings),
            "workflow_continue_on_error_count": len(workflow_findings),
            "fast_ci_advisory_count": len(fast_ci_findings),
            "by_disposition": by_disp,
            "p0_blocking_soft_gates": 0,
        },
        "findings": all_findings,
        "recommendations": [
            {
                "id": "REC-N-001",
                "action": "Keep rune integrity and advisory readiness probes report-only until allow-lists stable",
                "priority": "P1",
            },
            {
                "id": "REC-N-002",
                "action": "Revisit P64 continue-on-error after operator reseal of historical hash chain",
                "priority": "P1",
            },
            {
                "id": "REC-N-003",
                "action": "Do not enable ABRAXAS_BOUNDARY_FAIL_CLOSED in shared CI without operator approval",
                "priority": "P0",
            },
            {
                "id": "REC-N-004",
                "action": "Track sole-writer fail-closed separately; not part of this audit scope",
                "priority": "P0",
            },
        ],
        "notes": [
            "Soft gates are not automatically defects; they must not silently mask P0 production blockers.",
            "fast_ci advisory steps intentionally ignore non-zero exits.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v3.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "soft_ci_gate_audit.v1.json", audit)

    return audit
