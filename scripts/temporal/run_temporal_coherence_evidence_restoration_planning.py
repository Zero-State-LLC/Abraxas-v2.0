from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_coherence_evidence_restoration_planning import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_temporal_coherence_evidence_restoration_planning,
    write_temporal_coherence_evidence_restoration_planning,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path = DEFAULT_OUT_PATH,
) -> dict[str, object]:
    packet = build_temporal_coherence_evidence_restoration_planning(
        repo_root=repo_root
    )
    write_temporal_coherence_evidence_restoration_planning(
        Path(repo_root) / out_path,
        packet,
    )
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
