from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.aal_viz_ingest_projection_pack import (  # noqa: E402
    build_aal_viz_ingest_projection_pack,
    write_aal_viz_ingest_projection_pack,
)

OUT = Path("out/projections/aal_viz_ingest_projection_pack_001.latest.json")


def main() -> None:
    packet = build_aal_viz_ingest_projection_pack()
    write_aal_viz_ingest_projection_pack(OUT, packet)
    print(packet["authority"])
    print(packet["projection_hash"])


if __name__ == "__main__":
    main()
