from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abraxas_spec_stack_belief_graph_schema_audit import (  # noqa: E402
    write_abraxas_spec_stack_belief_graph_schema_audit,
)
from core.abraxas_spec_stack_binding_schema_audit import (  # noqa: E402
    write_abraxas_spec_stack_binding_schema_audit,
)
from core.abraxas_spec_stack_codegen_spine_schema_audit import (  # noqa: E402
    write_abraxas_spec_stack_codegen_spine_schema_audit,
)
from core.abraxas_spec_stack_ingest_schema_audit import (  # noqa: E402
    write_abraxas_spec_stack_ingest_schema_audit,
)
from core.abraxas_spec_stack_schema_audit_receipt import (  # noqa: E402
    write_abraxas_spec_stack_schema_audit_receipt,
)
from core.abraxas_spec_stack_situation_runtime_schema_audit import (  # noqa: E402
    write_abraxas_spec_stack_situation_runtime_schema_audit,
)


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict:
    write_abraxas_spec_stack_belief_graph_schema_audit(repo_root, out_root=out_root)
    write_abraxas_spec_stack_codegen_spine_schema_audit(repo_root, out_root=out_root)
    write_abraxas_spec_stack_ingest_schema_audit(repo_root, out_root=out_root)
    write_abraxas_spec_stack_binding_schema_audit(repo_root, out_root=out_root)
    write_abraxas_spec_stack_situation_runtime_schema_audit(repo_root, out_root=out_root)
    return write_abraxas_spec_stack_schema_audit_receipt(repo_root, out_root=out_root)


def main() -> int:
    receipt = run()
    for audit in receipt["domain_audits"]:
        print(f"{audit['domain']}: {audit['status']}")
    print(receipt["receipt_id"])
    print(receipt["status"])
    print(receipt["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
