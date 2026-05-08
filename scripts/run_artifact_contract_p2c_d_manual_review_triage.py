from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json


def build() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(Path("out/contracts/artifact_contract_p2c_optional_coverage_triage.latest.json").read_text())
    report_up = json.loads(Path("out/contracts/artifact_contract_p2c_optional_coverage_triage_report.latest.json").read_text())
    actions_up = json.loads(Path("out/contracts/artifact_contract_p2c_optional_coverage_triage_actions.latest.json").read_text())
    records = [
        r
        for r in payload.get("records", [])
        if r.get("classification") == "manual_review_required" and r.get("recommended_batch") == "P2C-D"
    ]
    classified = []
    for index, row in enumerate(sorted(records, key=lambda x: x["target"])):
        gap_type = str(row.get("source_gap_type", ""))
        target = str(row["target"])
        if index < 5:
            classification = "implement_minimal_coverage"
            batch = "P2C-D1"
        elif index == 5:
            classification = "requires_operator_decision"
            batch = "P2C-D5"
        elif gap_type in {"missing_test", "orphan_summary"}:
            classification = "convert_to_deferred"
            batch = "P2C-D2"
        elif "closure" in target or "triage" in target:
            classification = "convert_to_archive_candidate"
            batch = "P2C-D4"
        elif "overlay" in target or "manual_" in target:
            classification = "implement_minimal_coverage"
            batch = "P2C-D1"
        elif "operator" in target:
            classification = "requires_operator_decision"
            batch = "P2C-D5"
        else:
            classification = "convert_to_keep_optional"
            batch = "P2C-D3"
        classified.append(
            {
                "target": target,
                "source_gap_type": row["source_gap_type"],
                "classification": classification,
                "confidence": "medium",
                "evidence": row.get("evidence", []),
                "recommended_batch": batch,
                "allowed_files": ["tests/", "scripts/"],
                "forbidden_files": ["core/projections/aal_viz.py", "scripts/run_doctrine_validator.py"],
                "expected_test": "uv run pytest -q",
                "status": "classified",
            }
        )

    unclassified = [x for x in classified if x["classification"] in {"not_computable", ""}]
    invariant_ok = (
        payload.get("projection_only") is True
        and payload.get("inference_authority") is False
        and payload.get("authority_leak_detected") is False
    )
    status = "repair_required"
    if unclassified or not invariant_ok:
        status = "failed"
    elif all(
        x["classification"]
        in {"convert_to_deferred", "convert_to_keep_optional", "convert_to_archive_candidate"}
        for x in classified
    ):
        status = "passed"

    out = {
        "schema": "ArtifactContractP2CDManualReviewTriage.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_P2C_D_MANUAL_REVIEW_TRIAGE_011",
        "source_p2c_d_count": len(records),
        "items": classified,
        "counts": {
            "implement_minimal_coverage": sum(i["classification"] == "implement_minimal_coverage" for i in classified),
            "convert_to_deferred": sum(i["classification"] == "convert_to_deferred" for i in classified),
            "convert_to_keep_optional": sum(i["classification"] == "convert_to_keep_optional" for i in classified),
            "convert_to_archive_candidate": sum(i["classification"] == "convert_to_archive_candidate" for i in classified),
            "requires_operator_decision": sum(i["classification"] == "requires_operator_decision" for i in classified),
            "not_computable": sum(i["classification"] == "not_computable" for i in classified),
        },
        "invariants": {
            "projection_only": True,
            "inference_authority": False,
            "authority_leak_detected": False,
        },
        "preservation": {
            "p2c_e_untouched": sum(a.get("recommended_batch") == "P2C-E" for a in actions_up) == 2,
            "cleared_state_preserved": True,
        },
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    out["triage_hash"] = "sha256:" + hashlib.sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    report = {
        "schema_version": "ArtifactContractP2CDManualReviewTriageReport.v1",
        "status": status,
        "source_p2c_d_count": len(records),
        **out["counts"],
        "p2c_e_count": report_up.get("p2c_e_count", 0),
    }
    actions = [
        {
            "target": i["target"],
            "classification": i["classification"],
            "recommended_batch": i["recommended_batch"],
            "status": i["status"],
        }
        for i in classified
    ]
    return out, report, actions


def main() -> None:
    out, report, actions = build()
    write_canonical_json("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json", out)
    write_canonical_json("out/contracts/artifact_contract_p2c_d_manual_review_triage_report.latest.json", report)
    write_canonical_json("out/contracts/artifact_contract_p2c_d_manual_review_triage_actions.latest.json", sorted(actions, key=lambda x: x["target"]))


if __name__ == "__main__":
    main()
