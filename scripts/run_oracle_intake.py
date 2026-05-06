from __future__ import annotations

from core.oracle.runtime import run_oracle_intake


def main() -> None:
    source_payloads = [{"source_id": "fixture:001", "source_type": "document", "payload": "Deterministic Oracle Intake Evidence"}]
    run_oracle_intake(source_payloads)
    print("oracle intake artifacts emitted")


if __name__ == "__main__":
    main()
