from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def _archive_type(target: str, source_gap_type: str) -> str:
    if "closure" in target:
        return "noncritical_closure_surface_candidate"
    if "report" in target:
        return "superseded_report_surface_candidate"
    if source_gap_type in {"missing_test", "orphan_summary"}:
        return "optional_archive_candidate"
    if source_gap_type in {"missing_producer", "missing_replay"}:
        return "redundant_audit_surface_candidate"
    return "downstream_archive_review_candidate"


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    d_triage = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")
    d_report = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json")
    d3_report = _load("out/contracts/artifact_contract_p2c_d3_keep_optional_report.latest.json")

    d4_items = [
        item
        for item in d_triage.get("items", [])
        if item.get("classification") == "convert_to_archive_candidate" and item.get("recommended_batch") == "P2C-D4"
    ]
    d4_items = sorted(d4_items, key=lambda x: x["target"])

    records = []
    for item in d4_items:
        target = str(item["target"])
        source_gap_type = str(item.get("source_gap_type", "unknown"))
        records.append(
            {
                "target": target,
                "source_gap_type": source_gap_type,
                "archive_candidate_type": _archive_type(target, source_gap_type),
                "reason": "recorded as archive candidate with no artifact deletion and no semantic mutation",
                "evidence": item.get("evidence", []),
                "allowed_future_batch": "P2C-D5",
                "result": "archive_candidate_recorded",
                "status": "recorded",
            }
        )

    unresolved = [r for r in records if r["result"] in {"unresolved", "not_computable"}]
    downstream_d5 = int(d_report.get("requires_operator_decision", 0))
    invariants_ok = (
        d_triage.get("invariants", {}).get("projection_only") is True
        and d_triage.get("invariants", {}).get("inference_authority") is False
        and d_triage.get("invariants", {}).get("authority_leak_detected") is False
    )

    status = "repair_required"
    if unresolved or not invariants_ok:
        status = "failed"
    elif downstream_d5 == 0 and all(r["result"] == "archive_candidate_recorded" for r in records):
        status = "passed"

    payload = {
        "schema": "ArtifactContractP2CD4ArchiveCandidate.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D4_ARCHIVE_CANDIDATE_BATCH_015",
        "source_d4_count": len(d4_items),
        "records": records,
        "downstream_preserved": {"D5": downstream_d5},
        "cleared_queues_preserved": {
            "P1A": 0,
            "P1C": 0,
            "P2A": 0,
            "P2C-A": 0,
            "P2C-B": 0,
            "P2C-D1": 5,
            "P2C-D2": 30,
            "P2C-D3": int(d3_report.get("kept_count", 0)),
        },
        "files_deleted": [],
        "artifacts_deleted": [],
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    payload["archive_hash"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    report = {
        "schema_version": "ArtifactContractP2CD4ArchiveCandidateReport.v1",
        "status": status,
        "source_d4_count": len(d4_items),
        "archive_candidate_recorded_count": sum(r["result"] == "archive_candidate_recorded" for r in records),
        "partially_recorded_count": sum(r["result"] == "partially_recorded" for r in records),
        "unresolved_count": len(unresolved),
        "d5_preserved": downstream_d5,
        "authority_invariants_ok": invariants_ok,
        "files_deleted": 0,
        "artifacts_deleted": 0,
    }

    actions = [
        {
            "target": row["target"],
            "archive_candidate_type": row["archive_candidate_type"],
            "result": row["result"],
            "status": row["status"],
        }
        for row in records
    ]
    return payload, report, sorted(actions, key=lambda x: x["target"])


def main() -> None:
    payload, report, actions = build()
    write_classified_json("out/contracts/artifact_contract_p2c_d4_archive_candidate.latest.json", payload, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_p2c_d4_archive_candidate_report.latest.json", report, artifact_class=ArtifactClass.AUDIT_EVIDENCE)
    write_classified_json("out/contracts/artifact_contract_p2c_d4_archive_candidate_actions.latest.json", actions, artifact_class=ArtifactClass.AUDIT_EVIDENCE)


if __name__ == "__main__":
    main()
