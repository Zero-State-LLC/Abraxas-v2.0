from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_static_preview_governance_audit import (
    build_operator_narrative_static_preview_governance_audit_packet,
    write_operator_narrative_static_preview_governance_audit,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    paths.audit_dir.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_static_preview_governance_audit_packet(
        preview_path=paths.operator_narrative_static_preview_latest,
        preview_markdown_path=paths.operator_narrative_static_preview_latest.with_suffix(".md"),
    )
    out = paths.operator_narrative_static_preview_governance_audit_latest
    write_operator_narrative_static_preview_governance_audit(out, packet)
    print(f"final_status={packet['final_status']}")
    print(f"audit_posture={packet['audit_posture']}")
    print(f"wrote={out.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
