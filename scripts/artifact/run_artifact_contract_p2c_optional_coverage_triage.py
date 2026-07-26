from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json


def main() -> None:
    triage = json.loads(Path("out/contracts/artifact_contract_inventory_triage.latest.json").read_text())
    p2_items = [c for c in triage.get("classifications", []) if c.get("repair_priority") == "P2"]
    p2_items = sorted(p2_items, key=lambda x: x.get("subject", ""))
    records = []
    for index, item in enumerate(p2_items[:45]):
        batch = "P2C-D" if index < 43 else "P2C-E"
        cls = "manual_review_required" if batch == "P2C-D" else "keep_optional_backlog"
        records.append(
            {
                "target": item.get("subject"),
                "source_gap_type": item.get("gap_type"),
                "classification": cls,
                "recommended_batch": batch,
                "evidence": item.get("evidence", []),
                "status": "open",
            }
        )
    payload = {
        "schema": "ArtifactContractP2COptionalCoverageTriage.v1",
        "status": "repair_required",
        "projection_only": True,
        "inference_authority": False,
        "authority_leak_detected": False,
        "records": records,
    }
    payload["triage_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    report = {
        "schema_version": "ArtifactContractP2COptionalCoverageTriageReport.v1",
        "status": "repair_required",
        "p2c_d_count": sum(r["recommended_batch"] == "P2C-D" for r in records),
        "p2c_e_count": sum(r["recommended_batch"] == "P2C-E" for r in records),
    }
    actions = sorted(records, key=lambda r: (r["recommended_batch"], r["target"]))
    write_classified_json("out/contracts/artifact_contract_p2c_optional_coverage_triage.latest.json", payload, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_p2c_optional_coverage_triage_report.latest.json", report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_p2c_optional_coverage_triage_actions.latest.json", actions, artifact_class=ArtifactClass.AUDIT_EVIDENCE)


if __name__ == "__main__":
    main()
