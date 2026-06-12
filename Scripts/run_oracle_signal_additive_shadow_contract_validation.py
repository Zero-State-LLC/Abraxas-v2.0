"""Run Oracle Signal additive shadow contract validation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.oracle_signal_additive_shadow_contract_validation import (  # noqa: E402
    write_oracle_signal_additive_shadow_contract_validation,
)


def run(repo_root: str | Path = ".", out_root: str | Path | None = None) -> dict[str, object]:
    return write_oracle_signal_additive_shadow_contract_validation(repo_root, out_root=out_root)


if __name__ == "__main__":
    packet = run()
    print(packet["status"])
    print(packet["validation_id"])
