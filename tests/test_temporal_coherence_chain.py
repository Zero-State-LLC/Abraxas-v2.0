from __future__ import annotations

import json
from pathlib import Path

from scripts import run_temporal_coherence_chain


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def test_run_chain_deterministic_stage_ordering(monkeypatch) -> None:
    called: list[str] = []

    def _runner(name: str):
        def _run(_args: list[str]) -> None:
            called.append(name)

        return _run

    monkeypatch.setattr(run_temporal_coherence_chain, "_STAGE_DEFS", (
        ("a", _runner("a"), Path("out/projections/a.json"), "status"),
        ("b", _runner("b"), Path("out/projections/b.json"), "status"),
    ))
    monkeypatch.setattr(run_temporal_coherence_chain, "_load_json", lambda _path: {"status": "ADVISORY_ONLY"})

    receipt = run_temporal_coherence_chain.run_chain()
    assert called == ["a", "b"]
    assert [s["stage_name"] for s in receipt["stages"]] == ["a", "b"]


def test_missing_upstream_artifact_fail_closed_receipt(monkeypatch) -> None:
    monkeypatch.setattr(run_temporal_coherence_chain, "_STAGE_DEFS", (
        ("a", lambda _args: None, Path("missing.json"), "status"),
        ("b", lambda _args: None, Path("b.json"), "status"),
    ))
    monkeypatch.setattr(run_temporal_coherence_chain, "_load_json", lambda _path: None)

    receipt = run_temporal_coherence_chain.run_chain()
    assert receipt["final_chain_status"] == "BLOCKED"
    assert receipt["stages"][1]["observed_status"] == "SKIPPED_DUE_TO_UPSTREAM"


def test_p27_not_computable_causes_p28_fail_closed(monkeypatch) -> None:
    payloads = {
        "temporal_resonance_coherence": {"final_status": "NOT_COMPUTABLE"},
    }

    monkeypatch.setattr(run_temporal_coherence_chain, "_STAGE_DEFS", (
        ("cross_run_topology_fusion", lambda _args: None, Path("x.json"), "status"),
        ("temporal_stability_pressure", lambda _args: None, Path("x.json"), "status"),
        ("temporal_state_diff", lambda _args: None, Path("x.json"), "status"),
        ("temporal_topology_cartography", lambda _args: None, Path("x.json"), "status"),
        ("temporal_resonance_coherence", lambda _args: None, Path("p27.json"), "final_status"),
        ("coherence_field_operator_surface", lambda _args: None, Path("p28.json"), "coherence_field_operator_surface_status"),
    ))

    def _load(path: Path):
        if path.as_posix() == "p27.json":
            return payloads["temporal_resonance_coherence"]
        return {"status": "ADVISORY_ONLY"}

    monkeypatch.setattr(run_temporal_coherence_chain, "_load_json", _load)
    receipt = run_temporal_coherence_chain.run_chain()
    assert receipt["final_chain_status"] == "BLOCKED"
    assert receipt["stages"][5]["completed"] is False


def test_success_chain_emits_receipt_with_governance_flags(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_temporal_coherence_chain, "CHAIN_JSON_PATH", Path("out/audit/temporal_coherence_chain_001.latest.json"))
    monkeypatch.setattr(run_temporal_coherence_chain, "CHAIN_MD_PATH", Path("out/audit/temporal_coherence_chain_001.latest.md"))

    monkeypatch.setattr(run_temporal_coherence_chain, "_STAGE_DEFS", (
        ("a", lambda _args: None, Path("a.json"), "status"),
    ))
    monkeypatch.setattr(run_temporal_coherence_chain, "_load_json", lambda _path: {"status": "ADVISORY_ONLY"})
    run_temporal_coherence_chain.main()

    receipt = json.loads(Path("out/audit/temporal_coherence_chain_001.latest.json").read_text(encoding="utf-8"))
    assert receipt["final_chain_status"] == "ADVISORY_ONLY"
    assert receipt["governance_flags"]["no_authority_escalation"] is True
    assert Path("out/audit/temporal_coherence_chain_001.latest.md").read_text(encoding="utf-8").endswith("\n")


def test_stable_receipt_shape_across_repeated_runs(monkeypatch) -> None:
    monkeypatch.setattr(run_temporal_coherence_chain, "_STAGE_DEFS", (
        ("a", lambda _args: None, Path("a.json"), "status"),
    ))
    monkeypatch.setattr(run_temporal_coherence_chain, "_load_json", lambda _path: {"status": "ADVISORY_ONLY"})

    first = run_temporal_coherence_chain.run_chain()
    second = run_temporal_coherence_chain.run_chain()
    assert sorted(first.keys()) == sorted(second.keys())
    assert first["stages"][0].keys() == second["stages"][0].keys()


def test_no_shell_true_usage() -> None:
    source = Path("scripts/run_temporal_coherence_chain.py").read_text(encoding="utf-8")
    assert "shell=True" not in source
