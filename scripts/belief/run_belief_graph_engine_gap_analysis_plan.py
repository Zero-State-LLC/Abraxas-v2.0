from __future__ import annotations

from pathlib import Path

from core.belief_graph_engine_gap_analysis_plan import (
    build_belief_graph_engine_gap_analysis_plan,
    write_belief_graph_engine_gap_analysis_plan,
    write_belief_graph_engine_gap_analysis_plan_markdown,
)


def run(
    *,
    repo_root: str | Path = ".",
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
):
    packet = build_belief_graph_engine_gap_analysis_plan(repo_root=repo_root)
    if out_json is not None:
        write_belief_graph_engine_gap_analysis_plan(out_json, packet)
    if out_md is not None:
        write_belief_graph_engine_gap_analysis_plan_markdown(out_md, packet)
    return packet
