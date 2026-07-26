from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

SUBSYSTEMS = [
    ("external_action_proposals", "external_action_proposal_summary", ["external_action_proposal_gate"]),
    ("proposal_sandbox_routing", "proposal_sandbox_routing_summary", ["proposal_sandbox_route_gate"]),
    ("proposal_sandbox_evaluation", "proposal_sandbox_evaluation_summary", ["proposal_sandbox_evaluation_gate"]),
    ("proposal_decision_bridge", "proposal_decision_bridge_summary", ["proposal_decision_bridge_gate"]),
    ("human_decision_ledger", "human_decision_ledger_summary", ["human_decision_ledger_gate"]),
    ("human_decision_continuity", "human_decision_continuity_summary", ["human_decision_continuity_chain_gate"]),
]


def _find_tests(prefix: str) -> list[str]:
    return sorted(str(p) for p in Path("tests").glob(f"test_{prefix}*.py"))


def _contains_any(files: list[str], patterns: list[str]) -> bool:
    text = "\n".join(Path(f).read_text() for f in files)
    return any(pattern in text for pattern in patterns)


def main() -> None:
    validation = json.loads(Path("out/validation/latest.json").read_text())
    projection = json.loads(Path("out/projections/aal_viz.latest.json").read_text())
    val_text = json.dumps(validation, sort_keys=True)

    inventory = []
    gaps = []

    for subsystem, summary_name, gates in sorted(SUBSYSTEMS):
        tests = _find_tests(subsystem)
        direct_count = len(tests)
        indirect_count = len(_find_tests("doctrine_")) + len(_find_tests("aal_viz_projection"))

        direct_text_files = tests
        indirect_files = sorted(
            str(p) for p in Path("tests").glob("test_*.py") if "proposal" in p.name or "human_decision" in p.name or "doctrine" in p.name or "aal_viz" in p.name
        )
        replay_present = _contains_any(direct_text_files + indirect_files, ["replay", "mismatch"])
        fail_closed_present = _contains_any(direct_text_files + indirect_files, ["failed", "forbidden", "blocked", "not_computable"])
        authority_present = _contains_any(direct_text_files + indirect_files, ["authority", "projection_only", "inference_authority", "execute", "deploy"])
        invariant_present = summary_name in projection and projection.get("projection_only") is True and projection.get("inference_authority") is False

        item_gaps: list[str] = []
        if not fail_closed_present:
            item_gaps.append("missing_fail_closed_coverage")
        if not replay_present:
            item_gaps.append("missing_replay_coverage")
        if not invariant_present:
            item_gaps.append("missing_invariant_coverage")
        if not authority_present:
            item_gaps.append("missing_authority_leak_coverage")
        if any(g not in val_text for g in gates):
            item_gaps.append("missing_doctrine_gate_surface")

        status = "passed"
        if {
            "missing_fail_closed_coverage",
            "missing_replay_coverage",
            "missing_invariant_coverage",
            "missing_authority_leak_coverage",
        }.intersection(item_gaps):
            status = "failed"
        elif item_gaps or direct_count < 1:
            status = "repair_required"

        inventory.append(
            {
                "subsystem": subsystem,
                "runtime_surface": f"core/{subsystem}/runtime.py",
                "validator_surface": f"core/{subsystem}/validators.py",
                "replay_surface": f"out/{subsystem}_replay/latest.json",
                "lineage_surface": f"out/{subsystem}_lineage/latest.json",
                "diagnostics_surface": f"out/{subsystem}_diagnostics/latest.json",
                "doctrine_gate_names": gates,
                "projection_summary_name": summary_name,
                "associated_tests": tests,
                "direct_test_count": direct_count,
                "indirect_test_count": indirect_count,
                "invariant_test_present": invariant_present,
                "replay_test_present": replay_present,
                "fail_closed_test_present": fail_closed_present,
                "authority_leak_test_present": authority_present,
                "coverage_status": status,
                "gaps": item_gaps,
            }
        )
        if item_gaps:
            gaps.append({"subsystem": subsystem, "gaps": item_gaps})

    overall = "passed"
    if any(i["coverage_status"] == "failed" for i in inventory):
        overall = "failed"
    elif gaps:
        overall = "repair_required"

    report = {
        "schema_version": "RuntimeTestCoverageCorrelationReport.v1",
        "status": overall,
        "inventory_count": len(inventory),
        "gap_count": len(gaps),
        "projection_only": projection.get("projection_only"),
        "inference_authority": projection.get("inference_authority"),
        "authority_leak_detected": projection.get("inference_authority") is not False,
    }

    out_root = Path("out")
    write_classified_json(
        "out/contracts/runtime_test_coverage_correlation.latest.json",
        inventory,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=out_root,
    )
    write_classified_json(
        "out/contracts/runtime_test_coverage_correlation_report.latest.json",
        report,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=out_root,
    )
    write_classified_json(
        "out/contracts/runtime_test_coverage_correlation_gaps.latest.json",
        gaps,
        artifact_class=ArtifactClass.BUILD_EVIDENCE,
        out_root=out_root,
    )


if __name__ == "__main__":
    main()
