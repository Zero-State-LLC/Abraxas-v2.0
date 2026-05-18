from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_static_preview_bundle import build_operator_narrative_static_preview_packet, write_operator_narrative_static_preview_bundle


def main() -> int:
    paths = RuntimePaths.from_env()
    paths.previews_dir.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_static_preview_packet(
        export_bundle_path=paths.operator_narrative_export_bundle_latest,
        export_bundle_markdown_path=paths.operator_narrative_export_bundle_latest.with_suffix('.md'),
        governance_audit_path=paths.operator_narrative_export_bundle_governance_audit_latest,
        governance_audit_markdown_path=paths.operator_narrative_export_bundle_governance_audit_latest.with_suffix('.md'),
    )
    out = paths.operator_narrative_static_preview_latest
    write_operator_narrative_static_preview_bundle(out, packet)
    print(f"final_status={packet['final_status']}")
    print(f"preview_posture={packet['preview_posture']}")
    print(f"wrote={out.as_posix()}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
