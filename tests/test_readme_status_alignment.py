from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_states_governed_symbolic_intelligence() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Governed Symbolic Intelligence" in readme
    assert "Evidence before authority" in readme
    assert "Governance before autonomy" in readme


def test_readme_states_advisory_posture_and_core_subsystems() -> None:
    """The RDI-era README must keep naming core subsystems and their
    advisory / operator-gated posture (Codegen Spine detail moved to
    ARCHITECTURE.md / PLANS.md in the #1107 rewrite)."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Belief Graph" in readme
    assert "SHADOW" in readme
    assert "advisory" in readme
    assert "hygiene-only" in readme or "operator-gated" in readme


def test_status_holds_production_activation_denied() -> None:
    """STATUS is the operational source of truth for activation posture."""
    status = (REPO_ROOT / "STATUS.md").read_text(encoding="utf-8")
    assert "Production activation" in status
    assert "DENIED" in status
    assert "Do not claim production ready" in status


def test_readme_does_not_claim_production_ready() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    lowered = readme.lower()
    assert "production ready" not in lowered
    assert "production-ready" not in lowered
