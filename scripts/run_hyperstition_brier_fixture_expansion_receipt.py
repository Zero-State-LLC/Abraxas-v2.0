from __future__ import annotations

from pathlib import Path

from core.canonical.json import normalize_numbers
from core.hyperstition_brier_fixture_expansion import (
    DEFAULT_OUT_PATH,
    build_hyperstition_brier_fixture_expansion_receipt,
    write_hyperstition_brier_fixture_expansion_receipt,
)


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    packet = normalize_numbers(
        build_hyperstition_brier_fixture_expansion_receipt(repo_root=repo_root)
    )
    write_hyperstition_brier_fixture_expansion_receipt(
        Path(out_path) if out_path is not None else DEFAULT_OUT_PATH,
        packet,
    )
    return packet
