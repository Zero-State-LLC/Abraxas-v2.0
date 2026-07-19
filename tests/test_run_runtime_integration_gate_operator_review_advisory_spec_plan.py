"""Tests for scripts/runtime/run_runtime_integration_gate_operator_review_advisory_spec_plan.py.

Candidate: 03ab393fa9b10805
Class: TEST
"""

from pathlib import Path

from scripts.runtime import run_runtime_integration_gate_operator_review_advisory_spec_plan as runner

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runner_writes_real_advisory_packet_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "runtime_integration_gate_operator_review_advisory_spec_plan.json"
    out_md = tmp_path / "runtime_integration_gate_operator_review_advisory_spec_plan.md"

    packet = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert out_json.exists()
    assert out_md.exists()
    assert packet["plan_status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY"
    assert packet["recommended_next_lane"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN"
    assert packet["operator_review_required"] is True
    assert packet["operator_attestation_present"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_runtime_wiring"] is False
    assert packet["codegen_implementation_allowed"] is False
    assert "CODEGEN_IMPLEMENTATION" in packet["blocked_patch_classes"]
    assert "MANDATORY_PRE_DISPATCH_WIRING" in packet["blocked_patch_classes"]
    assert out_md.read_text(encoding="utf-8").startswith(
        "# Runtime Integration Gate Operator Review Advisory Spec Plan 001\n"
    )


def test_runner_outputs_are_stable(tmp_path: Path) -> None:
    out_json = tmp_path / "runtime_integration_gate_operator_review_advisory_spec_plan.json"
    out_md = tmp_path / "runtime_integration_gate_operator_review_advisory_spec_plan.md"

    first = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = runner.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_main_prints_packet_summary(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        runner,
        "run",
        lambda: {
            "plan_id": "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_001",
            "plan_status": "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY",
            "recommended_next_lane": "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN",
        },
    )
    assert runner.main() == 0
    out = capsys.readouterr().out
    assert "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_001" in out
    assert "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY" in out
    assert "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN" in out
