from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.global_pipeline_aal_viz_dashboard import (
    write_global_pipeline_aal_viz_dashboard_artifacts,
)


def main() -> int:
    artifacts = write_global_pipeline_aal_viz_dashboard_artifacts()
    print(artifacts["dashboard_packet"]["status"])
    print(artifacts["dashboard_packet"]["dashboard_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
