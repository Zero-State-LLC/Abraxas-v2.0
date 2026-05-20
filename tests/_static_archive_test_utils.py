from __future__ import annotations

from pathlib import Path
from shutil import copy2


def copy_upstream_package_artifacts(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = tmp_path / "out"
    (out_dir / "package").mkdir(parents=True)
    (out_dir / "audit").mkdir(parents=True)
    copy2(
        repo_root / "out/package/operator_narrative_static_archive_package_001.latest.json",
        out_dir / "package/operator_narrative_static_archive_package_001.latest.json",
    )
    for name in (
        "operator_narrative_static_archive_package_governance_audit_001.latest.json",
        "operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
        "operator_narrative_static_archive_package_stability_receipt_001.latest.json",
        "operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
    ):
        copy2(repo_root / f"out/audit/{name}", out_dir / f"audit/{name}")


def write_p71_doc(tmp_path: Path) -> None:
    p71 = tmp_path / "docs/plans/P71_planning_gate_static_archive_package_completion_seal.md"
    p71.parent.mkdir(parents=True, exist_ok=True)
    p71.write_text("P71_PLAN_READY\nP71_COMPLETION_SEAL_PLANNING_REQUIRED\n", encoding="utf-8")
