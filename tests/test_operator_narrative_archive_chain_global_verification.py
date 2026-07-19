from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_archive_chain_global_verification import (
    PATCH_ID,
    SCHEMA_VERSION,
    VERIFICATION_ID,
    build_operator_narrative_archive_chain_global_verification_packet,
    write_operator_narrative_archive_chain_global_verification,
)


def _p56() -> dict:
    return {
        "final_status": "STABILITY_RECEIPT_DEGRADED",
        "stability_posture": "STABLE_WITH_OBSERVED_BLOCKERS",
        "replay_count": 3,
        "blocker_summary": [],
        "repaired_blocker_guard_summary": {"p51_repaired_blockers_reintroduced": []},
    }


def _runner(results: dict[str, dict]):
    def _run(command: str, _timeout: int) -> dict:
        out = dict(results[command])
        out.setdefault("command", command)
        out.setdefault("duration_ms", 1)
        out.setdefault("exit_code", 0)
        out.setdefault("timed_out", False)
        out.setdefault("could_run", True)
        out.setdefault("stdout_digest", "a" * 64)
        out.setdefault("stderr_digest", "b" * 64)
        out.setdefault("stdout_snippet", "")
        out.setdefault("stderr_snippet", "")
        out.setdefault("passed", out["could_run"] and (not out["timed_out"]) and out["exit_code"] == 0)
        return out

    return _run


def _all_pass() -> dict[str, dict]:
    return {
        "pytest -q": {},
        "pyright": {},
        "ruff check .": {},
        "python scripts/artifact/run_artifact_regeneration.py --full --validation-only": {},
        "python scripts/artifact/run_artifact_regeneration.py --check-drift": {},
    }


def test_pass_and_hash_repeatable(tmp_path: Path) -> None:
    p56 = tmp_path / "p56.json"
    p56.write_text(json.dumps(_p56()), encoding="utf-8")
    a = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=p56,
        command_runner=_runner(_all_pass()),
    )
    b = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=p56,
        command_runner=_runner(_all_pass()),
    )
    assert a["final_status"] == "GLOBAL_VERIFICATION_PASS"
    assert a["verification_hash"] == b["verification_hash"]


def test_failures_by_command(tmp_path: Path) -> None:
    p56 = tmp_path / "p56.json"
    p56.write_text(json.dumps(_p56()), encoding="utf-8")
    for cmd in _all_pass().keys():
        results = _all_pass()
        results[cmd] = {"exit_code": 1, "passed": False}
        pkt = build_operator_narrative_archive_chain_global_verification_packet(
            p56_receipt_json_path=p56,
            command_runner=_runner(results),
        )
        assert pkt["final_status"] == "GLOBAL_VERIFICATION_FAIL"


def test_not_computable_and_p56_guards(tmp_path: Path) -> None:
    pkt = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=tmp_path / "missing.json",
        command_runner=_runner(_all_pass()),
    )
    assert pkt["final_status"] == "NOT_COMPUTABLE"

    p56 = _p56()
    p56["replay_count"] = 2
    path = tmp_path / "p56.json"
    path.write_text(json.dumps(p56), encoding="utf-8")
    pkt = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=path,
        command_runner=_runner(_all_pass()),
    )
    assert pkt["final_status"] == "GLOBAL_VERIFICATION_FAIL"

    p56 = _p56()
    p56["final_status"] = "STABILITY_RECEIPT_ONLY"
    path.write_text(json.dumps(p56), encoding="utf-8")
    pkt = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=path,
        command_runner=_runner(_all_pass()),
    )
    assert pkt["final_status"] == "GLOBAL_VERIFICATION_FAIL"

    p56 = _p56()
    p56["repaired_blocker_guard_summary"] = {"p51_repaired_blockers_reintroduced": ["source_missing:p42_report_json"]}
    path.write_text(json.dumps(p56), encoding="utf-8")
    pkt = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=path,
        command_runner=_runner(_all_pass()),
    )
    assert pkt["final_status"] == "GLOBAL_VERIFICATION_FAIL"


def test_writer_schema_registry_and_bounded_logs(tmp_path: Path) -> None:
    p56 = tmp_path / "p56.json"
    p56.write_text(json.dumps(_p56()), encoding="utf-8")
    res = _all_pass()
    long_text = "x" * 5000
    res["pytest -q"] = {"stdout_snippet": long_text, "stderr_snippet": long_text, "stdout_digest": "c" * 64, "stderr_digest": "d" * 64}
    pkt = build_operator_narrative_archive_chain_global_verification_packet(
        p56_receipt_json_path=p56,
        command_runner=_runner(res),
    )
    out = tmp_path / "p57.json"
    write_operator_narrative_archive_chain_global_verification(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_archive_chain_global_verification.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["verification_id"]["const"] == VERIFICATION_ID

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in registry.entries}
    assert emap["out/audit/operator_narrative_archive_chain_global_verification_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_archive_chain_global_verification_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"


def test_no_shell_true_usage() -> None:
    source = Path("core/operator_narrative_archive_chain_global_verification.py").read_text(encoding="utf-8")
    assert "shell=True" not in source
