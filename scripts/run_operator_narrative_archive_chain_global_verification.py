from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_archive_chain_global_verification import (
    build_operator_narrative_archive_chain_global_verification_packet,
    write_operator_narrative_archive_chain_global_verification,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_narrative_archive_chain_global_verification_latest


def _dirty_files() -> list[str]:
    proc = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=False)
    files = []
    for line in proc.stdout.splitlines():
        if len(line) > 3:
            files.append(line[3:].strip())
    return files


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_archive_chain_global_verification_packet()
    packet["artifact_drift_summary"]["dirty_files_after_verification"] = _dirty_files()
    packet["artifact_drift_summary"]["artifacts_changed_during_verification"] = bool(packet["artifact_drift_summary"]["dirty_files_after_verification"])
    write_operator_narrative_archive_chain_global_verification(OUT_PATH, packet)
    print(f"final_status={packet['final_status']}")
    print(f"verification_posture={packet['verification_posture']}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
