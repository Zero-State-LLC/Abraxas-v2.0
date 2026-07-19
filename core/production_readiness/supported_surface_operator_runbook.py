"""WP-RUNBOOK: operator runbook for SUPPORTED kernel surfaces."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_supported_surface_operator_runbook"
OUT_DIR_REL = Path("out/production_readiness/ws8")


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


def _load(repo_root: Path, rel: str) -> dict[str, Any] | None:
    path = repo_root / rel
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def build_supported_surface_operator_runbook(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    inventory = _load(
        repo_root, "out/production_readiness/ws8/supported_surface_freeze_inventory.v1.json"
    ) or {}

    procedures = [
        {
            "surface": "canonical_json",
            "purpose": "Deterministic JSON serialize/hash/write under policy",
            "commands": [
                "python -c \"from core.canonical.json import canonical_hash; print(canonical_hash({'a':1}))\"",
            ],
            "tests": ["tests/test_canonical_json.py"],
            "notes": "Library call; prefer service facade for path-gated writes.",
        },
        {
            "surface": "run_fast_ci",
            "purpose": "Mandatory local/CI validation entry point",
            "commands": [
                "export PATH=\"$(pwd)/.venv/bin:$PATH\"",
                "python scripts/run_fast_ci.py",
            ],
            "tests": ["tests/test_run_fast_ci.py"],
            "notes": "Advisory readiness gates fail-open; exit 0 required for G1.",
        },
        {
            "surface": "validation_service.v1",
            "purpose": "Schema validation (contracts/ only schema_ref)",
            "commands": [
                "python scripts/runtime/run_validation_service.py --help",
            ],
            "tests": ["tests/test_validation_service.py"],
            "notes": "SUPPORTED service; no production authority grant.",
        },
        {
            "surface": "artifact_and_provenance_service.v0",
            "purpose": "Hash/dumps/write via canonical_json; out/ only",
            "commands": [
                "python scripts/artifact/run_artifact_provenance_service.py --help",
                (
                    "python scripts/artifact/run_artifact_provenance_service.py "
                    "--operation hash --payload '{\"x\":1}'"
                ),
            ],
            "tests": ["tests/test_artifact_provenance_service.py"],
            "notes": "PATH_DENIED outside out/; organized under scripts/artifact/.",
        },
        {
            "surface": "readiness_scorecard_and_decision",
            "purpose": "Freeze gates + binding release decision",
            "commands": [
                "python scripts/readiness/run_freeze_gate_scorecard.py",
                "python scripts/readiness/run_release_decision.py --help",
                "python scripts/readiness/run_candidate_deploy_readiness.py",
                "python scripts/readiness/run_production_activation_authority_gate.py",
            ],
            "tests": [
                "tests/test_freeze_gate_scorecard.py",
                "tests/test_release_decision.py",
            ],
            "notes": "CANDIDATE_APPROVED still deploy-held; activation gate DENIED.",
        },
    ]

    runbook: dict[str, Any] = {
        "schema_version": "supported_surface_operator_runbook.v1",
        "artifact_type": "supported_surface_operator_runbook",
        "work_package": "WP-RUNBOOK_SUPPORTED_SURFACE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "surface_summary": inventory.get("summary"),
        "safety_rules": [
            "Do not set production_activation_authorized true from this runbook",
            "Do not enable ABRAXAS_BOUNDARY_FAIL_CLOSED without operator approval",
            "Prefer scripts/run_* and SUPPORTED services over ad-hoc core writers",
            "Writes must go through sole-writer / artifact service under out/",
        ],
        "procedures": procedures,
        "notes": [
            "Operational guide only; not a deploy authorization.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v8.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "supported_surface_operator_runbook.v1.json",
            runbook,
        )
        md_lines = [
            "# SUPPORTED Surface Operator Runbook",
            "",
            f"Produced: {produced_at}  ",
            f"SHA: `{sha}`  ",
            "",
            "## Safety",
            "",
        ]
        for rule in runbook["safety_rules"]:
            md_lines.append(f"- {rule}")
        md_lines.extend(["", "## Procedures", ""])
        for proc in procedures:
            md_lines.append(f"### {proc['surface']}")
            md_lines.append("")
            md_lines.append(proc["purpose"])
            md_lines.append("")
            md_lines.append("```bash")
            md_lines.extend(proc["commands"])
            md_lines.append("```")
            md_lines.append("")
            if proc.get("tests"):
                md_lines.append("Tests: " + ", ".join(f"`{t}`" for t in proc["tests"]))
                md_lines.append("")
            if proc.get("notes"):
                md_lines.append(f"_{proc['notes']}_")
                md_lines.append("")
        (out_dir / "supported_surface_operator_runbook.v1.md").write_text(
            "\n".join(md_lines) + "\n",
            encoding="utf-8",
        )

    return runbook
