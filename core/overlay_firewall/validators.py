from __future__ import annotations
from core.overlay_firewall.readiness import FORBIDDEN_FIREWALL_STATUS


def validate_overlay_firewall(
    firewall: dict,
    eligibility: dict,
    replay: dict,
    diagnostics: list[dict],
    lineage: dict,
) -> dict[str, object]:
    failures: list[str] = []
    if firewall.get("firewall_status") in FORBIDDEN_FIREWALL_STATUS:
        failures.append("forbidden firewall status appears")
    if not replay.get("deterministic_match", False):
        failures.append("replay mismatch exists")
    if any(
        d.get("severity") == "critical" and not d.get("resolved", False)
        for d in diagnostics
    ):
        failures.append("critical diagnostics unresolved")
    if not eligibility.get("rollback_ready", False):
        failures.append("rollback unsafe")
    if eligibility.get("readiness_score", 0) < 0.65:
        failures.append("readiness below threshold")
    if not eligibility.get("governance_safe", False):
        failures.append("governance unsafe")
    if not eligibility.get("containment_safe", False):
        failures.append("containment critical")
    if not eligibility.get("continuity_safe", False):
        failures.append("continuity broken")
    if firewall.get("authority", {}).get("runtime_mutation_allowed", False):
        failures.append("authority mutation appears")
    if lineage.get("lineage_cycle_detected", False):
        failures.append("lineage cycle exists")
    if any(d.get("code") == "auto_approval_attempted" for d in diagnostics):
        failures.append("automatic approval attempted")
    return {"status": "failed" if failures else "passed", "failures": failures}
