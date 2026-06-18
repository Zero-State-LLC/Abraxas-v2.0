from __future__ import annotations

import json
from pathlib import Path

from core.governance.authority import Authority
from core.yggdrasil.rune_route_binding_matrix import (
    build_coupling_map,
    build_rune_route_binding_matrix,
    write_coupling_map,
    write_coupling_map_markdown,
    write_rune_route_binding_matrix,
    write_rune_route_binding_matrix_markdown,
)
from scripts import run_yggdrasil_rune_route_binding_matrix


def test_binding_matrix_is_deterministic() -> None:
    first = build_rune_route_binding_matrix()
    second = build_rune_route_binding_matrix()
    assert first == second


def test_binding_rows_sorted_and_not_computable() -> None:
    packet = build_rune_route_binding_matrix()
    rows = packet["bindings"]
    pairs = [(row["pipeline_id"], row["rune_id"]) for row in rows]
    assert pairs == sorted(pairs)
    assert all(row["status"] == "NOT_COMPUTABLE" for row in rows)
    assert all(row["pipeline_requires_rune"] is True for row in rows)


def test_authority_flags_remain_locked_in_all_binding_rows() -> None:
    packet = build_rune_route_binding_matrix()
    for row in packet["bindings"]:
        Authority.model_validate(row["authority"]["rune"]).assert_locked()
        Authority.model_validate(row["authority"]["pipeline"]).assert_locked()
        Authority.model_validate(row["authority"]["route"]).assert_locked()


def test_coupling_map_sorted_and_contains_unbound_runes() -> None:
    packet = build_coupling_map()
    assert list(packet["rune_to_pipelines"]) == sorted(packet["rune_to_pipelines"])
    assert list(packet["pipeline_to_route"]) == sorted(packet["pipeline_to_route"])
    assert packet["unbound_runes"] == sorted(packet["unbound_runes"])
    assert "RUNE.PIPELINE.OPERATOR_REVIEW" not in packet["unbound_runes"]
    assert "RUNE.PIPELINE.POSITIVE_PROOF" not in packet["unbound_runes"]
    assert "RUNE.PIPELINE.STABILIZATION_DECIDE" not in packet["unbound_runes"]
    assert packet["unbound_runes"] == []


def test_seal_and_final_status_are_locked_false() -> None:
    matrix = build_rune_route_binding_matrix()
    coupling = build_coupling_map()
    for packet in (matrix, coupling):
        assert packet["FORECAST_ROUTING"] is False
        assert packet["CANON_MUTATION"] is False
        assert packet["RUNTIME_MUTATION"] is False
        assert packet["EXECUTION_AUTHORITY"] is False
        assert packet["PRIVATE_RUNTIME_ROUTES_ALLOWED"] is False
        assert packet["final_status"] == "BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY"


def test_writers_emit_single_newline(tmp_path: Path) -> None:
    matrix_path = tmp_path / "matrix.latest.json"
    coupling_path = tmp_path / "coupling.latest.json"
    matrix_md_path = tmp_path / "matrix.latest.md"
    coupling_md_path = tmp_path / "coupling.latest.md"
    write_rune_route_binding_matrix(matrix_path, build_rune_route_binding_matrix())
    write_coupling_map(coupling_path, build_coupling_map())
    write_rune_route_binding_matrix_markdown(
        matrix_md_path,
        build_rune_route_binding_matrix(),
    )
    write_coupling_map_markdown(coupling_md_path, build_coupling_map())
    matrix_text = matrix_path.read_text(encoding="utf-8")
    coupling_text = coupling_path.read_text(encoding="utf-8")
    matrix_md_text = matrix_md_path.read_text(encoding="utf-8")
    coupling_md_text = coupling_md_path.read_text(encoding="utf-8")
    assert matrix_text.endswith("\n") and not matrix_text.endswith("\n\n")
    assert coupling_text.endswith("\n") and not coupling_text.endswith("\n\n")
    assert matrix_md_text.endswith("\n") and not matrix_md_text.endswith("\n\n")
    assert coupling_md_text.endswith("\n") and not coupling_md_text.endswith("\n\n")
    assert "BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY" in matrix_md_text
    assert "BINDING_SURFACE_FORMALIZED_ADVISORY_ONLY" in coupling_md_text


def test_runner_writes_expected_outputs(tmp_path: Path) -> None:
    matrix_path = tmp_path / "out" / "audit" / "yggdrasil_rune_route_binding_matrix_001.latest.json"
    coupling_path = tmp_path / "out" / "audit" / "yggdrasil_coupling_map_001.latest.json"
    matrix_md_path = matrix_path.with_suffix(".md")
    coupling_md_path = coupling_path.with_suffix(".md")
    run_yggdrasil_rune_route_binding_matrix.run(
        matrix_out_path=matrix_path,
        coupling_out_path=coupling_path,
        matrix_md_out_path=matrix_md_path,
        coupling_md_out_path=coupling_md_path,
    )
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    coupling = json.loads(coupling_path.read_text(encoding="utf-8"))
    assert matrix["schema_version"] == "YggdrasilRuneRouteBindingMatrix.v1"
    assert coupling["schema_version"] == "YggdrasilCouplingMap.v1"
    assert matrix_md_path.read_text(encoding="utf-8").startswith(
        "# Yggdrasil Rune Route Binding Matrix 001\n"
    )
    assert coupling_md_path.read_text(encoding="utf-8").startswith(
        "# Yggdrasil Coupling Map 001\n"
    )


def test_schema_files_define_expected_locks() -> None:
    matrix_schema = json.loads(
        Path("contracts/yggdrasil/rune_route_binding_matrix.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    coupling_schema = json.loads(
        Path("contracts/yggdrasil/coupling_map.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for schema in (matrix_schema, coupling_schema):
        assert schema["properties"]["FORECAST_ROUTING"]["const"] is False
        assert schema["properties"]["CANON_MUTATION"]["const"] is False
        assert schema["properties"]["RUNTIME_MUTATION"]["const"] is False
        assert schema["properties"]["EXECUTION_AUTHORITY"]["const"] is False
        assert schema["properties"]["PRIVATE_RUNTIME_ROUTES_ALLOWED"]["const"] is False
