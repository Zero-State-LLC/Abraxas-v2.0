from __future__ import annotations

import json
from pathlib import Path

from core.research_fold_drop_spec_builder import (
    build_research_fold_drop_spec_builder,
    write_research_fold_drop_spec_builder,
)
from scripts import run_research_fold_drop_spec_builder

# A well-formed P94 PASS packet (minimal fields required by the builder).
_VALID_P94_PACKET: dict[str, object] = {
    "artifact_type": "ResearchFoldCanonAlignmentPlan.v1",
    "status": "PASS",
    "canon_alignment_status": "ALIGNED",
    "authority_locks": {
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "forecast_influence": False,
        "forecast_weight_allowed": False,
        "shadow_to_forecast_leakage": False,
        "scheduler_mutation": False,
        "autonomous_execution": False,
        "operator_bypass": False,
        "hidden_intent_claim_authority": False,
    },
}

_EXPECTED_DROP_006_SPEC_IDS = {
    "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_SPEC",
    "DROP006B_ACTIVE_INFERENCE_INTENTIONAL_PLANNING_SPEC",
    "DROP006C_ISOTONIC_SURVIVAL_CALIBRATION_SPEC",
}

_EXPECTED_DROP_007_SPEC_IDS = {
    "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_SPEC",
    "DROP007B_ALGORITHMIC_COORDINATION_THRESHOLD_SPEC",
    "DROP007C_PROACTIVE_INTENT_RECOMMENDATION_SPEC",
}

_AUTHORITY_LOCK_FIELDS = {
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "forecast_influence",
    "forecast_weight_allowed",
    "shadow_to_forecast_leakage",
    "scheduler_mutation",
    "autonomous_execution",
    "operator_bypass",
    "hidden_intent_claim_authority",
}


def test_deterministic_repeated_output() -> None:
    first = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    second = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_p94_missing_returns_not_computable() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=None)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p94_packet_missing" in packet["not_computable_reasons"]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["generated_drop_specs"] == []


def test_p94_failed_status_returns_not_computable() -> None:
    bad_p94 = {**_VALID_P94_PACKET, "status": "NOT_COMPUTABLE"}
    packet = build_research_fold_drop_spec_builder(p94_packet=bad_p94)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p94_status_not_pass" in r for r in packet["not_computable_reasons"])


def test_p94_malformed_non_dict_returns_not_computable() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet="not_a_dict")  # type: ignore[arg-type]
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p94_packet_malformed" in r for r in packet["not_computable_reasons"])
    assert packet["generated_drop_specs"] == []


def test_p94_wrong_artifact_type_returns_not_computable() -> None:
    bad_p94 = {**_VALID_P94_PACKET, "artifact_type": "SomeOtherArtifact.v1"}
    packet = build_research_fold_drop_spec_builder(p94_packet=bad_p94)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p94_artifact_type_mismatch" in r for r in packet["not_computable_reasons"])


def test_p94_not_aligned_returns_not_computable() -> None:
    bad_p94 = {**_VALID_P94_PACKET, "canon_alignment_status": "NOT_ALIGNED"}
    packet = build_research_fold_drop_spec_builder(p94_packet=bad_p94)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p94_canon_alignment_not_aligned" in r for r in packet["not_computable_reasons"])


def test_p94_authority_drift_returns_not_computable() -> None:
    drifted_locks = {**_VALID_P94_PACKET["authority_locks"], "production_activation": True}  # type: ignore[arg-type]
    bad_p94 = {**_VALID_P94_PACKET, "authority_locks": drifted_locks}
    packet = build_research_fold_drop_spec_builder(p94_packet=bad_p94)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any("p94_authority_drift_detected" in r for r in packet["not_computable_reasons"])


def test_authority_locks_always_false() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    assert set(packet["authority_locks"].keys()) == _AUTHORITY_LOCK_FIELDS
    assert all(value is False for value in packet["authority_locks"].values())


def test_authority_locks_false_on_not_computable() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=None)
    assert set(packet["authority_locks"].keys()) == _AUTHORITY_LOCK_FIELDS
    assert all(value is False for value in packet["authority_locks"].values())


def test_drop_006_specs_included_and_advisory_only() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    drop_006_specs = [s for s in packet["generated_drop_specs"] if s["drop_id"] == "DROP006"]
    observed_ids = {s["spec_id"] for s in drop_006_specs}
    assert observed_ids == _EXPECTED_DROP_006_SPEC_IDS
    for spec in drop_006_specs:
        assert spec["spec_mode"] == "ADVISORY_SPEC_ONLY"
        assert spec["executable"] is False


def test_drop_007_specs_included_and_advisory_only() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    drop_007_specs = [s for s in packet["generated_drop_specs"] if s["drop_id"] == "DROP007"]
    observed_ids = {s["spec_id"] for s in drop_007_specs}
    assert observed_ids == _EXPECTED_DROP_007_SPEC_IDS
    for spec in drop_007_specs:
        assert spec["spec_mode"] == "ADVISORY_SPEC_ONLY"
        assert spec["executable"] is False


def test_no_executable_modules_generated() -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    for spec in packet["generated_drop_specs"]:
        assert spec["executable"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True


def test_recommended_next_lane_p96_only_on_pass() -> None:
    pass_packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    assert pass_packet["status"] == "PASS"
    assert pass_packet["recommended_next_lane"] == "P96_RESEARCH_FOLD_VALIDATION_PLAN"

    blocked_packet = build_research_fold_drop_spec_builder(p94_packet=None)
    assert blocked_packet["status"] == "NOT_COMPUTABLE"
    assert blocked_packet["recommended_next_lane"] != "P96_RESEARCH_FOLD_VALIDATION_PLAN"


def test_schema_locks_authority_fields_false() -> None:
    schema = json.loads(
        Path("contracts/canon/research_fold_drop_spec_builder.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for field in _AUTHORITY_LOCK_FIELDS:
        assert schema["properties"]["authority_locks"]["properties"][field]["const"] is False


def test_schema_locks_executable_false() -> None:
    schema = json.loads(
        Path("contracts/canon/research_fold_drop_spec_builder.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["properties"]["generated_drop_specs"]["items"]["properties"]["executable"]["const"] is False
    assert (
        schema["properties"]["generated_drop_specs"]["items"]["properties"]["spec_mode"]["const"]
        == "ADVISORY_SPEC_ONLY"
    )


def test_runner_writes_deterministically(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_fold_drop_spec_builder" / "latest.json"
    first = run_research_fold_drop_spec_builder.run(
        p94_packet=_VALID_P94_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    first_text = out_path.read_text(encoding="utf-8")

    second = run_research_fold_drop_spec_builder.run(
        p94_packet=_VALID_P94_PACKET,
        repo_root=tmp_path,
        out_path=out_path,
    )
    second_text = out_path.read_text(encoding="utf-8")

    assert first["packet_hash"] == second["packet_hash"]
    assert first_text == second_text


def test_writer_final_newline(tmp_path: Path) -> None:
    packet = build_research_fold_drop_spec_builder(p94_packet=_VALID_P94_PACKET)
    out_path = tmp_path / "research_fold_drop_spec_builder_test.json"
    write_research_fold_drop_spec_builder(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")


# ---------------------------------------------------------------------------
# CLI / path-loading tests
# ---------------------------------------------------------------------------

from scripts.run_research_fold_drop_spec_builder import (  # noqa: E402
    _load_p94_packet,
)


def test_load_p94_packet_missing_returns_none(tmp_path: Path) -> None:
    assert _load_p94_packet(tmp_path / "nonexistent.json") is None


def test_load_p94_packet_malformed_json_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert _load_p94_packet(bad) is None


def test_load_p94_packet_non_dict_returns_none(tmp_path: Path) -> None:
    arr = tmp_path / "arr.json"
    arr.write_text("[1, 2, 3]", encoding="utf-8")
    assert _load_p94_packet(arr) is None


def test_load_p94_packet_valid_returns_dict(tmp_path: Path) -> None:
    p = tmp_path / "p94.json"
    p.write_text(json.dumps(_VALID_P94_PACKET), encoding="utf-8")
    loaded = _load_p94_packet(p)
    assert isinstance(loaded, dict)
    assert loaded["artifact_type"] == "ResearchFoldCanonAlignmentPlan.v1"


def test_main_missing_p94_path_produces_not_computable(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "research_fold_drop_spec_builder" / "latest.json"
    absent = tmp_path / "absent_p94.json"
    packet = run_research_fold_drop_spec_builder.run(
        p94_packet=_load_p94_packet(absent),
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "p94_packet_missing" in packet["not_computable_reasons"]


def test_main_valid_p94_file_produces_pass(tmp_path: Path) -> None:
    p94_file = tmp_path / "p94.json"
    p94_file.write_text(json.dumps(_VALID_P94_PACKET), encoding="utf-8")
    out_path = tmp_path / "out" / "research_fold_drop_spec_builder" / "latest.json"
    packet = run_research_fold_drop_spec_builder.run(
        p94_packet=_load_p94_packet(p94_file),
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert packet["status"] == "PASS"
    assert packet["recommended_next_lane"] == "P96_RESEARCH_FOLD_VALIDATION_PLAN"


def test_main_malformed_p94_file_produces_not_computable(tmp_path: Path) -> None:
    bad = tmp_path / "bad_p94.json"
    bad.write_text("{broken", encoding="utf-8")
    out_path = tmp_path / "out" / "research_fold_drop_spec_builder" / "latest.json"
    packet = run_research_fold_drop_spec_builder.run(
        p94_packet=_load_p94_packet(bad),
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert packet["status"] == "NOT_COMPUTABLE"


def test_p94_default_path_constant() -> None:
    from scripts.run_research_fold_drop_spec_builder import P94_DEFAULT_PATH

    assert str(P94_DEFAULT_PATH) == "out/research_fold_canon_alignment_plan/latest.json"


def test_parse_args_default_p94_path() -> None:
    from scripts.run_research_fold_drop_spec_builder import _parse_args

    args = _parse_args([])
    assert args.p94_path == "out/research_fold_canon_alignment_plan/latest.json"


def test_parse_args_custom_p94_path(tmp_path: Path) -> None:
    from scripts.run_research_fold_drop_spec_builder import _parse_args

    custom = str(tmp_path / "my_p94.json")
    args = _parse_args(["--p94-path", custom])
    assert args.p94_path == custom
