from __future__ import annotations

import json
from pathlib import Path

from core.runtime.topology_replay import replay_execution_graph


def main() -> None:
    runtime_run = json.loads(Path("out/yggdrasil/runtime.latest.json").read_text(encoding="utf-8"))
    packet = replay_execution_graph(runtime_run)
    print(packet["status"])


if __name__ == "__main__":
    main()
