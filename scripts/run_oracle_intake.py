from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.oracle.runtime import run_oracle_intake


def main() -> None:
    source_payloads = [
        {
            "source_id": "fixture:001",
            "source_type": "document",
            "payload": "Deterministic Oracle Intake Evidence",
        }
    ]
    packet = run_oracle_intake(source_payloads)
    write_canonical_json(Path("out/oracle/latest.json"), packet)
    write_canonical_json(Path("out/oracle_lineage/latest.json"), packet["lineage"])
    write_canonical_json(
        Path("out/oracle_conflicts/latest.json"),
        {"conflicts": packet["conflicts"]},
    )
    write_canonical_json(Path("out/oracle_replay/latest.json"), packet["replay"])
    print("oracle intake artifacts emitted")


if __name__ == "__main__":
    main()
