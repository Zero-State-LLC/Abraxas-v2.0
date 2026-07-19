from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text())


def _deferral_type(target: str, source_gap_type: str) -> str:
    if source_gap_type == "missing_test":
        return "optional_test_surface_deferred"
    if source_gap_type == "orphan_summary":
        return "optional_observability_deferred"
    if "artifact_contract" in target:
        return "noncritical_audit_surface_deferred"
    if source_gap_type in {"missing_producer", "missing_replay"}:
        return "optional_contract_surface_deferred"
    return "downstream_governance_backlog"


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    d_triage = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")
    d_report = _load("out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json")
    d1_report = _load("out/contracts/artifact_contract_p2c_d1_minimal_implementation_report.latest.json")

    d2_items = [
        item
        for item in d_triage.get("items", [])
        if item.get("classification") == "convert_to_deferred" and item.get("recommended_batch") == "P2C-D2"
    ]
    d2_items = sorted(d2_items, key=lambda x: x["target"])

    conversions = []
    for item in d2_items:
        target = str(item["target"])
        source_gap_type = str(item.get("source_gap_type", "unknown"))
        conversions.append(
            {
                "target": target,
                "source_gap_type": source_gap_type,
                "deferral_type": _deferral_type(target, source_gap_type),
                "reason": "converted to documented deferral queue without semantic mutation",
                "evidence": item.get("evidence", []),
                "allowed_future_batch": "P2C-D3",
                "result": "deferred",
                "status": "closed",
            }
        )

    unresolved = [c for c in conversions if c["result"] in {"unresolved", "not_computable"}]

    downstream = {
        "D3": int(d_report.get("convert_to_keep_optional", 0)),
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
    elif all(v == 0 for v in downstream.values()) and all(c["result"] == "deferred" for c in conversions):
        status = "passed"

    payload = {
        "schema": "ArtifactContractP2CD2DeferredConversion.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D2_DEFERRED_CONVERSION_BATCH_013",
        "source_d2_count": len(d2_items),
        "conversions": conversions,
        "downstream_preserved": downstream,
        "cleared_queues_preserved": {
            "P1A": 0,
            "P1C": 0,
            "P2A": 0,
            "P2C-A": 0,
            "P2C-B": 0,
            "P2C-D1": int(d1_report.get("implemented_count", 0)),
        },
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    payload["conversion_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    report = {
        "schema_version": "ArtifactContractP2CD2DeferredConversionReport.v1",
        "status": status,
        "source_d2_count": len(d2_items),
        "deferred_count": sum(c["result"] == "deferred" for c in conversions),
        "partially_deferred_count": sum(c["result"] == "partially_deferred" for c in conversions),
        "unresolved_count": len(unresolved),
        "d3_preserved": downstream["D3"],
        "d4_preserved": downstream["D4"],
        "d5_preserved": downstream["D5"],
        "authority_invariants_ok": invariants_ok,
    }

    actions = [
        {
            "target": row["target"],
            "deferral_type": row["deferral_type"],
            "result": row["result"],
            "status": row["status"],
        }
        for row in conversions
    ]
    return payload, report, sorted(actions, key=lambda x: x["target"])


def main() -> None:
    payload, report, actions = build()
    write_canonical_json("out/contracts/artifact_contract_p2c_d2_deferred_conversion.latest.json", payload)
    write_canonical_json("out/contracts/artifact_contract_p2c_d2_deferred_conversion_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_p2c_d2_deferred_conversion_actions.latest.json", actions)


if __name__ == "__main__":
    main()
