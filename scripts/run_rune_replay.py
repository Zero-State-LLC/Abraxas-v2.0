from __future__ import annotations

from core.canonical.json import write_canonical_json


def main() -> None:
    name = __file__.split('/')[-1].replace('.py','')
    write_canonical_json(f"out/{name}/latest.json", {"schema_version": "MilestoneContinuityStub.v1", "script": name, "status": "ok"})
    print(f"{name} complete")


if __name__ == "__main__":
    main()
