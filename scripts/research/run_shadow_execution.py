from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash, write_canonical_json
from core.governance.authority import locked_authority
from core.pipelines.registry import load_contracts


def main() -> None:
    contracts = load_contracts(Path("contracts/pipelines"))
    contract = next((c for c in contracts if c.pipeline_id == "research_intake"), contracts[0])
    invocation_plan = [{"rune_id": rune, "mode": "shadow"} for rune in sorted(contract.required_runes)]
    execution = {
        "schema_version": "ShadowExecutionRun.v1",
        "pipeline_id": contract.pipeline_id,
        "invocation_plan": invocation_plan,
        "authority": locked_authority(),
        "status": "completed",
    }
    execution["run_id"] = canonical_hash(execution)
    receipt = {
        "schema_version": "ShadowExecutionReceipt.v1",
        "run_id": execution["run_id"],
        "pipeline_id": contract.pipeline_id,
        "authority": locked_authority(),
        "status": "valid",
    }
    write_canonical_json("out/execution/latest.json", execution)
    write_canonical_json("out/execution/receipts.latest.json", receipt)
    print(json.dumps({"status": execution["status"], "pipeline_id": contract.pipeline_id}))


if __name__ == "__main__":
    main()
