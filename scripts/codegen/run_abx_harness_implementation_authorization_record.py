from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.abx_harness_implementation_authorization_record import (  # noqa: E402
    write_abx_harness_implementation_authorization_record,
)


def run(source_root: str | Path = ".", out_root: str | Path | None = None) -> dict:
    return write_abx_harness_implementation_authorization_record(
        source_root, out_root=out_root
    )


if __name__ == "__main__":
    packet = run()
    print(packet["record_id"])
    print(packet["status"])
