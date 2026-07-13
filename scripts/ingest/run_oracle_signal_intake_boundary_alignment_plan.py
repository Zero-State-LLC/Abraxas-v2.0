from __future__ import annotations

from pathlib import Path

from core.sync.oracle_signal_intake_boundary_alignment_plan import (
    build_oracle_signal_intake_boundary_alignment_plan,
    write_oracle_signal_intake_boundary_alignment_plan,
    write_oracle_signal_intake_boundary_alignment_plan_markdown,
)


def run(
    *,
    repo_root: str | Path = ".",
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
):
    packet = build_oracle_signal_intake_boundary_alignment_plan(repo_root=repo_root)
    if out_json is not None:
        write_oracle_signal_intake_boundary_alignment_plan(out_json, packet)
    if out_md is not None:
        write_oracle_signal_intake_boundary_alignment_plan_markdown(out_md, packet)
    return packet


def main(argv: list[str] | None = None) -> None:
    del argv
    run()


if __name__ == "__main__":
    main()
