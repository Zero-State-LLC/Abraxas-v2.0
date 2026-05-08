from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def _keep_type(target: str, source_gap_type: str) -> str:
    if source_gap_type == "missing_test":
        return "optional_test_surface_kept"
    if source_gap_type == "orphan_summary":
        return "optional_observability_kept"
    if source_gap_type in {"missing_producer", "missing_replay"}:
        return "optional_contract_surface_kept"
    if "artifact_contract" in target:
        return "noncritical_audit_surface_kept"
    return "optional_backlog_preserved"


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    d_triage = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")
    d_report = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json")
    d2_report = _load("out/contracts/artifact_contract_p2c_d2_deferred_conversion_report.latest.json")

    d3_items = [
        item
        for item in d_triage.get("items", [])
        if item.get("classification") == "convert_to_keep_optional" and item.get("recommended_batch") == "P2C-D3"
    ]
    d3_items = sorted(d3_items, key=lambda x: x["target"])

    keeps = []
    for item in d3_items:
        target = str(item["target"])
        source_gap_type = str(item.get("source_gap_type", "unknown"))
        keeps.append(
            {
                "target": target,
                "source_gap_type": source_gap_type,
                "keep_type": _keep_type(target, source_gap_type),
                "reason": "preserved in optional backlog without semantic mutation",
                "evidence": item.get("evidence", []),
                "allowed_future_batch": "P2C-D5",
                "result": "kept",
                "status": "closed",
            }
        )

    unresolved = [k for k in keeps if k["result"] in {"unresolved", "not_computable"}]
    downstream = {
        "D4": int(d_report.get("convert_to_archive_candidate", 0)),
        "D5": int(d_report.get("requires_operator_decision", 0)),
    }

    invariants_ok = (
        d_triage.get("invariants", {}).get("projection_only") is True
        and d_triage.get("invariants", {}).get("inference_authority") is False
        and d_triage.get("invariants", {}).get("authority_leak_detected") is False
    )

    status = "repair_required"
    if unresolved or not invariants_ok:
        status = "failed"
    elif all(v == 0 for v in downstream.values()) and all(k["result"] == "kept" for k in keeps):
        status = "passed"

    payload = {
        "schema": "ArtifactContractP2CD3KeepOptional.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D3_KEEP_OPTIONAL_BATCH_014",
        "source_d3_count": len(d3_items),
        "keeps": keeps,
        "downstream_preserved": downstream,
        "cleared_queues_preserved": {
            "P1A": 0,
            "P1C": 0,
            "P2A": 0,
            "P2C-A": 0,
            "P2C-B": 0,
            "P2C-D1": 5,
            "P2C-D2": int(d2_report.get("deferred_count", 0)),
        },
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    payload["keep_hash"] = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    report = {
        "schema_version": "ArtifactContractP2CD3KeepOptionalReport.v1",
        "status": status,
        "source_d3_count": len(d3_items),
        "kept_count": sum(k["result"] == "kept" for k in keeps),
        "partially_kept_count": sum(k["result"] == "partially_kept" for k in keeps),
        "unresolved_count": len(unresolved),
        "d4_preserved": downstream["D4"],
        "d5_preserved": downstream["D5"],
        "authority_invariants_ok": invariants_ok,
    }

    actions = [
        {
            "target": row["target"],
            "keep_type": row["keep_type"],
            "result": row["result"],
            "status": row["status"],
        }
        for row in keeps
    ]
    return payload, report, sorted(actions, key=lambda x: x["target"])


def main() -> None:
    payload, report, actions = build()
    write_canonical_json("out/contracts/artifact_contract_p2c_d3_keep_optional.latest.json", payload)
    write_canonical_json("out/contracts/artifact_contract_p2c_d3_keep_optional_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_p2c_d3_keep_optional_actions.latest.json", actions)


if __name__ == "__main__":
    main()
