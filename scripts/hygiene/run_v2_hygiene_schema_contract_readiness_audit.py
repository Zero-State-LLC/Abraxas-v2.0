from __future__ import annotations

from pathlib import Path
from typing import Any

from core.sync.v2_hygiene_schema_contract_readiness_audit import (
    write_v2_hygiene_schema_contract_readiness_audit,
)

OUT_JSON = Path("out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")


def run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    return write_v2_hygiene_schema_contract_readiness_audit(
        repo_root,
        out_root=out_root,
    )


def main() -> None:
    packet = run()
    print(f"wrote {OUT_JSON}")
    print(f"status={packet['status']}")
    print(f"audit_hash={packet['audit_hash']}")


if __name__ == "__main__":
    main()
