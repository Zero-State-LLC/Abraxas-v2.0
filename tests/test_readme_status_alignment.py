from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

STABILIZATION_INTAKE_ROW = (
    "| v2.0 hygiene Phase 1 stabilization operator attestation intake gate | "
    "`out/operator_review/"
    "v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json` | "
    "`ATTESTATION_INTAKE_VALIDATED_FOR_FUTURE_DECISION_RECORD_GATE` |"
)

STALE_STABILIZATION_INTAKE_ROW = (
    "| v2.0 hygiene Phase 1 stabilization operator attestation intake gate | "
    "`out/operator_review/"
    "v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json` | "
    "`NOT_COMPUTABLE` |"
)


def test_readme_stabilization_intake_status_matches_validated_artifact() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert STABILIZATION_INTAKE_ROW in readme
    assert STALE_STABILIZATION_INTAKE_ROW not in readme


def test_readme_lists_stabilization_creation_terminal_hold() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    creation_rows = (
        "v2.0 hygiene Phase 1 stabilization decision-record gate",
        "v2.0 hygiene Phase 1 stabilization decision-record planning receipt",
        "v2.0 hygiene Phase 1 stabilization decision-record creation gate",
        "v2.0 hygiene Phase 1 stabilization decision-record creation plan",
        "v2.0 hygiene Phase 1 stabilization decision-record creation authorization gate",
        (
            "v2.0 hygiene Phase 1 stabilization decision-record creation "
            "authorization chain compression audit"
        ),
    )
    for row_label in creation_rows:
        assert readme.count(row_label) >= 2
    assert (
        "v2.0 hygiene Phase 1 stabilization decision-record creation authorization "
        "chain compression audit"
    ) in readme
    assert (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_AUTHORIZATION_"
        "CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
    ) in readme
