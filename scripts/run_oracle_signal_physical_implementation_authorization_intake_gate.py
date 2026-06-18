from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.oracle_signal_physical_implementation_authorization_intake_gate import (  # noqa: E402
    write_oracle_signal_physical_implementation_authorization_intake_gate,
)


def run(source_root: str | Path = ".", out_root: str | Path | None = None) -> dict:
    return write_oracle_signal_physical_implementation_authorization_intake_gate(
        source_root, out_root=out_root
    )


if __name__ == "__main__":
    packet = run()
    print(packet["gate_id"])
    print(packet["status"])
