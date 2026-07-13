from __future__ import annotations

from pathlib import Path

from core.temporal_continuity_p80_authorization_record_regeneration_receipt import (
    DEFAULT_OUT_PATH,
    build_temporal_continuity_p80_authorization_record_regeneration_receipt,
    write_temporal_continuity_p80_authorization_record_regeneration_receipt,
)


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    packet = build_temporal_continuity_p80_authorization_record_regeneration_receipt(
        repo_root=repo_root
    )
    write_temporal_continuity_p80_authorization_record_regeneration_receipt(
        out_path or DEFAULT_OUT_PATH,
        packet,
    )
    return packet


def main(argv: list[str] | None = None) -> None:
    del argv
    run()


if __name__ == "__main__":
    main()
