from __future__ import annotations


def validate_active_milestone(doctrine_summary: dict, stabilization_artifacts: dict) -> dict[str, object]:
    stabilized = stabilization_artifacts.get("stabilized_milestones", [])
    if not stabilized:
        return {"status": "not_computable", "reason": "missing stabilization artifacts"}
    active_expected = stabilized[-1]
    if doctrine_summary.get("active_milestone") != active_expected:
        return {"status": "failed", "reason": "stale milestone label"}
    lineage = stabilization_artifacts.get("milestone_lineage", [])
    seen = set()
    for node in lineage:
        mid = node.get("milestone_id")
        if mid in seen:
            return {"status": "failed", "reason": "lineage mismatch"}
        seen.add(mid)
    return {"status": "passed", "reason": "active milestone validated", "active_milestone": active_expected}
