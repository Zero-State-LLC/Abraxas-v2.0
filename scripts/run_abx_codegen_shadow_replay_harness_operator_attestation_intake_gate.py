from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abx_codegen_shadow_replay_harness_operator_attestation_intake_gate import (  # noqa: E402
    write_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate,
)


def run(repo_root: str | Path = ".", out_root: str | Path | None = None) -> dict:
    return write_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        repo_root, out_root=out_root
    )


if __name__ == "__main__":
    packet = run()
    print(packet["gate_id"])
    print(packet["status"])
    print(packet["recommended_next_lane"])
