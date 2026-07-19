"""TD Wave 3: soft CI gate acceptance (accept residual for candidate track)."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_soft_ci_gate_acceptance"
OUT_DIR_REL = Path("out/production_readiness/ws6")


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


def build_soft_ci_gate_acceptance(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    gates = [
        {
            "gate": "Rune integrity scanner (report-only)",
            "path": ".github/workflows/ci.yml",
            "decision": "ACCEPT_RESIDUAL",
            "rationale": "Historical non-blocking scanner; not freeze P0 for candidate track.",
        },
        {
            "gate": "P64 manifest source hash gate",
            "path": ".github/workflows/ci.yml",
            "decision": "ACCEPT_RESIDUAL",
            "rationale": "Documented historical drift; reseal is separate operator lane.",
        },
        {
            "gate": "status-pages deterministic output",
            "path": ".github/workflows/status-pages.yml",
            "decision": "ACCEPT_RESIDUAL",
            "rationale": "Softened for flakiness; not production activation gate.",
        },
        {
            "gate": "fast-ci advisory readiness probes",
            "path": "scripts/run_fast_ci.py",
            "decision": "ACCEPT_RESIDUAL",
            "rationale": (
                "Boundary/sole-writer/neon remain report-only until operator enables "
                "fail-closed after green unauthorized=0 window."
            ),
        },
    ]

    packet: dict[str, Any] = {
        "schema_version": "soft_ci_gate_acceptance.v1",
        "artifact_type": "soft_ci_gate_acceptance",
        "work_package": "TD_WAVE3_SOFT_CI_ACCEPTANCE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "status": "CLOSED_BY_ACCEPTANCE",
        "fail_closed_promotions": 0,
        "gates": gates,
        "summary": {
            "gate_count": len(gates),
            "accepted": sum(1 for g in gates if g["decision"] == "ACCEPT_RESIDUAL"),
            "remediated": 0,
        },
        "notes": [
            "Acceptance is residual closeout, not silence.",
            "Does not authorize fail-closed flips.",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "soft_ci_gate_acceptance.v1.json", packet)

    return packet
