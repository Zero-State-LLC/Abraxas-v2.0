"""Script: create an execution receipt.

Usage:
    python scripts/readiness/run_receipt.py \\
        --execution-state simulated \\
        --command-id KERNEL_ZERO_BOOTSTRAP \\
        --operator-command "bootstrap kernel zero"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.receipts.builder import build_simulated_receipt, build_spec_only_receipt
from core.receipts.models import ExecutionState

OUT_PATH = Path("out/receipts/latest.json")
OUT_ROOT = Path("out")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an execution receipt.")
    parser.add_argument("--execution-state", required=True, help="ExecutionState value")
    parser.add_argument("--command-id", required=True, help="Command identifier")
    parser.add_argument("--operator-command", required=True, help="Operator command string")
    parser.add_argument("--pipeline-id", default=None, help="Optional pipeline_id")
    args = parser.parse_args()

    state = ExecutionState(args.execution_state)

    if state == ExecutionState.simulated:
        receipt = build_simulated_receipt(
            command_id=args.command_id,
            operator_command=args.operator_command,
            pipeline_id=args.pipeline_id,
        )
    else:
        receipt = build_spec_only_receipt(
            command_id=args.command_id,
            operator_command=args.operator_command,
        )

    write_classified_json(
        OUT_PATH,
        receipt.to_dict(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=OUT_ROOT,
    )
    print(f"Receipt written to {OUT_PATH}")
    print(f"  execution_state : {receipt.execution_state.value}")
    print(f"  command_id      : {receipt.command_id}")
    print(f"  status          : {receipt.status}")


if __name__ == "__main__":
    main()
