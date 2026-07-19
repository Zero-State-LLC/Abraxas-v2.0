"""WP-I: release decision + supported surface freeze inventory.

Default fail-closed decision is RELEASE_HELD unless caller supplies another
allowed code. Never implies production activation.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_release_decision"
OUT_DIR_REL = Path("out/production_readiness/ws8")

ALLOWED_CODES = frozenset(
    {
        "RELEASE_HELD",
        "OPERATOR_REVIEW_REQUIRED",
        "NOT_COMPUTABLE",
        "CANDIDATE_APPROVED",
    }
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


def _load(repo_root: Path, rel: str) -> dict[str, Any] | None:
    path = repo_root / rel
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def build_supported_surface_freeze_inventory(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Inventory SUPPORTED interfaces/services as the freeze surface map."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    registry = _load(
        repo_root, "out/production_readiness/ws1/interface_registry_snapshot.v1.json"
    )
    services = _load(repo_root, "out/production_readiness/ws3/service_registry.v1.json")

    supported_interfaces = [
        {
            "contract_id": e.get("contract_id"),
            "path": e.get("path"),
            "tests": e.get("tests") or [],
            "ownership": e.get("ownership"),
        }
        for e in (registry or {}).get("entries", [])
        if e.get("stability_class") == "SUPPORTED"
    ]
    supported_services = [
        {
            "service_id": s.get("service_id"),
            "version": s.get("version"),
            "tests": s.get("tests") or [],
        }
        for s in (services or {}).get("services", [])
        if s.get("stability_class") == "SUPPORTED" and s.get("status") == "IMPLEMENTED"
    ]

    inventory: dict[str, Any] = {
        "schema_version": "supported_surface_freeze_inventory.v1",
        "artifact_type": "supported_surface_freeze_inventory",
        "work_package": "WP-I_SURFACE_FREEZE_INVENTORY",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "supported_interfaces": supported_interfaces,
        "supported_services": supported_services,
        "summary": {
            "supported_interface_count": len(supported_interfaces),
            "supported_service_count": len(supported_services),
        },
        "frozen_claim": (
            "Inventory only. Freezing experimental routes is advisory documentation; "
            "this artifact does not rewrite runtime policy or authorize production."
        ),
        "notes": [
            "Bounded kernel surface for candidate discussion.",
            "Does not disable ADVISORY/EXPERIMENTAL code paths automatically.",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "supported_surface_freeze_inventory.v1.json",
            inventory,
        )
    return inventory


def build_release_decision(
    repo_root: Path,
    *,
    decision_code: str,
    operator_id_or_role: str,
    notes: str,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Emit release decision. Defaults toward hold; activation always false unless
    CANDIDATE_APPROVED (still not production activation).
    """
    repo_root = Path(repo_root).resolve()
    if decision_code not in ALLOWED_CODES:
        raise ValueError(f"decision_code must be one of {sorted(ALLOWED_CODES)}")
    if not operator_id_or_role.strip():
        raise ValueError("operator_id_or_role required")
    if not notes.strip():
        raise ValueError("notes required")

    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    scorecard = _load(repo_root, "out/production_readiness/ws8/freeze_gate_scorecard.v1.json")
    summary = (scorecard or {}).get("summary") or {}
    all_pass = bool(summary.get("all_pass"))

    # Guard: never emit CANDIDATE_APPROVED if scorecard not all_pass
    effective = decision_code
    if decision_code == "CANDIDATE_APPROVED" and not all_pass:
        effective = "RELEASE_HELD"
        notes = (
            notes
            + " | AUTO_DOWNGRADE: CANDIDATE_APPROVED requested but freeze scorecard "
            "not all_pass; forced RELEASE_HELD."
        )

    production_activation_authorized = False
    readiness_state = "NOT_READY"
    if effective == "CANDIDATE_APPROVED":
        # Bounded candidate documentation only — still not production live.
        readiness_state = "CANDIDATE_HELD_FOR_OPERATOR_DEPLOY"
        production_activation_authorized = False

    inventory = build_supported_surface_freeze_inventory(
        repo_root, produced_at=produced_at, write=write
    )

    decision: dict[str, Any] = {
        "schema_version": "release_decision.v1",
        "artifact_type": "release_decision",
        "work_package": (
            "WP-I_PLUS_CANDIDATE_APPROVED"
            if effective == "CANDIDATE_APPROVED"
            else "WP-I_RELEASE_DECISION"
        ),
        "decision_id": "RELEASE_DECISION_PRODUCTION_CANDIDATE_001",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "decision_code": effective,
        "operator_id_or_role": operator_id_or_role,
        "decided_at": produced_at,
        "production_activation_authorized": production_activation_authorized,
        "readiness_state": readiness_state,
        "deploy_held": effective == "CANDIDATE_APPROVED",
        "scorecard_ref": "out/production_readiness/ws8/freeze_gate_scorecard.v1.json",
        "scorecard_summary": summary,
        "surface_inventory_ref": (
            "out/production_readiness/ws8/supported_surface_freeze_inventory.v1.json"
        ),
        "surface_summary": inventory.get("summary"),
        "notes": notes,
        "constraints": [
            "Does not authorize production activation or live deploy",
            "CANDIDATE_APPROVED is still operator-deploy held (deploy_held=true)",
            "Fail-closed sole-writer/boundary remain off unless separately approved",
            "Neon Genie remains non-control-plane",
            "Do not market as production ready",
        ],
        "linked_artifacts": [
            "out/production_readiness/ws8/freeze_gate_scorecard.v1.json",
            "out/production_readiness/ws8/supported_surface_freeze_inventory.v1.json",
            "out/production_readiness/ws1/sole_writer_residual_acceptance.v1.json",
            "out/production_readiness/ws8/threat_model_operator_decision_record.v0.json",
            "out/production_readiness/CONTINUATION_PLAN.v7.md",
            "out/production_readiness/CONTINUATION_PLAN.v6.md",
            "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "release_decision.v1.json", decision)

    return decision
