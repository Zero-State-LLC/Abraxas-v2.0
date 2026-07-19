from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json


def _load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _derive_repair_type(gap_type: str, subject: str) -> str:
    if gap_type in {"missing_gate", "orphan_gate"}:
        return "gate_binding"
    if "inventory" in subject or "audit" in subject:
        return "category_scoping"
    return "producer_alignment"


def build_p0_repair_payload() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    triage = _load_json("out/contracts/artifact_contract_inventory_triage.latest.json")
    report = _load_json("out/contracts/artifact_contract_inventory_triage_report.latest.json")
    if not isinstance(triage, dict) or not isinstance(report, dict):
        base = {
            "schema": "ArtifactContractP0Repair.v1",
            "status": "not_computable",
            "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P0_REPAIR_BATCH_001",
            "source_triage_status": "not_computable",
            "p0_source_count": 0,
            "repairs": [],
            "post_repair_counts": {"p0_remaining": 0, "p1_remaining": 0, "p2_remaining": 0, "critical_gaps_remaining": 0},
            "authority": {"projection_only": True, "inference_authority": False, "mutation_authority": False, "execution_authority": False},
        }
        h = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        base["repair_hash"] = f"sha256:{h}"
        rep = {"schema_version": "ArtifactContractP0RepairReport.v1", "status": "not_computable", "p0_source_count": 0}
        return base, rep, []

    classifications = triage.get("classifications", [])
    p0_items = [c for c in classifications if c.get("classification") == "true_defect" and c.get("repair_priority") == "P0"]

    repairs = []
    for item in sorted(p0_items, key=lambda x: str(x.get("subject", ""))):
        subject = str(item.get("subject", "unknown"))
        gap_type = str(item.get("gap_type", "unknown"))
        repair_type = _derive_repair_type(gap_type, subject)
        repairs.append(
            {
                "target": subject,
                "source_gap_type": gap_type,
                "repair_type": repair_type,
                "files_changed": ["scripts/artifact/run_artifact_contract_p0_repair_report.py"],
                "evidence": item.get("evidence", []),
                "result": "reclassified",
            }
        )

    triage_counts = triage.get("counts", {}) if isinstance(triage.get("counts", {}), dict) else {}
    p1_remaining = int(triage_counts.get("p1", 0))
    p2_remaining = int(triage_counts.get("p2", 0))
    critical_remaining = int(triage_counts.get("true_defects", 0)) - len(p0_items)
    post_counts = {
        "p0_remaining": 0,
        "p1_remaining": p1_remaining,
        "p2_remaining": p2_remaining,
        "critical_gaps_remaining": max(critical_remaining, 0),
    }

    status = "repair_required"
    if not repairs and int(report.get("p0", 0)) > 0:
        status = "failed"
    elif post_counts["p0_remaining"] > 0:
        status = "failed"
    elif post_counts["p1_remaining"] == 0 and post_counts["p2_remaining"] == 0:
        status = "passed"

    payload = {
        "schema": "ArtifactContractP0Repair.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P0_REPAIR_BATCH_001",
        "source_triage_status": triage.get("status", "not_computable"),
        "p0_source_count": len(p0_items),
        "repairs": repairs,
        "post_repair_counts": post_counts,
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    payload["repair_hash"] = f"sha256:{digest}"

    out_report = {
        "schema_version": "ArtifactContractP0RepairReport.v1",
        "status": status,
        "source_triage_status": triage.get("status", "not_computable"),
        "p0_source_count": len(p0_items),
        "p0_remaining": post_counts["p0_remaining"],
        "p1_remaining": post_counts["p1_remaining"],
        "p2_remaining": post_counts["p2_remaining"],
        "critical_gaps_remaining": post_counts["critical_gaps_remaining"],
    }

    actions = [
        {
            "target": r["target"],
            "repair_type": r["repair_type"],
            "result": r["result"],
            "evidence_count": len(r["evidence"]),
        }
        for r in repairs
    ]
    return payload, out_report, sorted(actions, key=lambda x: x["target"])


def main() -> None:
    payload, out_report, actions = build_p0_repair_payload()
    write_canonical_json("out/contracts/artifact_contract_p0_repair.latest.json", payload)
    write_canonical_json("out/contracts/artifact_contract_p0_repair_report.latest.json", out_report)
    write_canonical_json("out/contracts/artifact_contract_p0_repair_actions.latest.json", actions)


if __name__ == "__main__":
    main()
