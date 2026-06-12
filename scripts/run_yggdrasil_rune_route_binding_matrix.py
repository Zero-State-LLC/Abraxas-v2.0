from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.yggdrasil.rune_route_binding_matrix import (  # noqa: E402
    build_coupling_map,
    build_rune_route_binding_matrix,
    write_coupling_map,
    write_coupling_map_markdown,
    write_rune_route_binding_matrix,
    write_rune_route_binding_matrix_markdown,
)

OUT_MATRIX = Path("out/audit/yggdrasil_rune_route_binding_matrix_001.latest.json")
OUT_COUPLING = Path("out/audit/yggdrasil_coupling_map_001.latest.json")
OUT_MATRIX_MD = OUT_MATRIX.with_suffix(".md")
OUT_COUPLING_MD = OUT_COUPLING.with_suffix(".md")


def run(
    *,
    repo_root: str | Path = ROOT,
    matrix_out_path: str | Path | None = None,
    coupling_out_path: str | Path | None = None,
    matrix_md_out_path: str | Path | None = None,
    coupling_md_out_path: str | Path | None = None,
) -> dict[str, dict[str, object]]:
    root = Path(repo_root)
    matrix = build_rune_route_binding_matrix(repo_root=root)
    coupling = build_coupling_map(repo_root=root)

    resolved_matrix_out = Path(matrix_out_path) if matrix_out_path is not None else root / OUT_MATRIX
    resolved_coupling_out = (
        Path(coupling_out_path) if coupling_out_path is not None else root / OUT_COUPLING
    )
    resolved_matrix_md_out = (
        Path(matrix_md_out_path) if matrix_md_out_path is not None else root / OUT_MATRIX_MD
    )
    resolved_coupling_md_out = (
        Path(coupling_md_out_path) if coupling_md_out_path is not None else root / OUT_COUPLING_MD
    )
    write_rune_route_binding_matrix(resolved_matrix_out, matrix)
    write_coupling_map(resolved_coupling_out, coupling)
    write_rune_route_binding_matrix_markdown(resolved_matrix_md_out, matrix)
    write_coupling_map_markdown(resolved_coupling_md_out, coupling)
    return {"binding_matrix": matrix, "coupling_map": coupling}


def main() -> int:
    packet = run()
    print(packet["binding_matrix"]["binding_count"])
    print(packet["coupling_map"]["final_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
