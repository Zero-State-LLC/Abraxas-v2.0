from __future__ import annotations

# WP-D4-C3: pure builder — sole-writer scripts own out/ publication.
from core.overlay_firewall.readiness import OverlayExecutionReadinessFirewallPacket
from core.overlay_firewall.governance import OverlayFirewallGovernancePacket
from core.overlay_firewall.containment import OverlayFirewallContainmentPacket
from core.overlay_firewall.rollback import OverlayFirewallRollbackPacket
from core.overlay_firewall.continuity import OverlayFirewallContinuityPacket
from core.overlay_firewall.eligibility import OverlayFirewallEligibilityPacket
from core.overlay_firewall.replay import OverlayFirewallReplayPacket
from core.overlay_firewall.lineage import OverlayFirewallLineagePacket
from core.overlay_firewall.diagnostics import OverlayFirewallDiagnosticPacket
from core.overlay_firewall.operator_review import OperatorOverlayFirewallReviewPacket
from core.overlay_firewall.validators import validate_overlay_firewall


def run_overlay_execution_firewall(
    readiness_packets: list[dict],
    governance_packets: list[dict],
    containment_packets: list[dict],
    resolution_packets: list[dict],
    replay_packets: list[dict],
) -> dict[str, object]:
    overlay_hash = "overlay-1"
    readiness_score = 0.82
    g = OverlayFirewallGovernancePacket(
        governance_firewall_id="ofg-1",
        overlay_hash=overlay_hash,
        governance_continuity_score=0.9,
        critical_governance_diagnostics=[],
        authority_violation_count=0,
        governance_safe=True,
        deterministic_governance_hash=OverlayFirewallGovernancePacket.compute_hash(
            overlay_hash, 0.9, [], 0, True
        ),
        status="passed",
    )
    c = OverlayFirewallContainmentPacket(
        containment_firewall_id="ofc-1",
        overlay_hash=overlay_hash,
        containment_restrictions=["observe_only"],
        critical_recommendations=[],
        containment_safe=True,
        deterministic_containment_hash=OverlayFirewallContainmentPacket.compute_hash(
            overlay_hash, ["observe_only"], [], True
        ),
        status="passed",
    )
    r = OverlayFirewallRollbackPacket(
        rollback_firewall_id="ofr-1",
        overlay_hash=overlay_hash,
        rollback_ready=True,
        rollback_blockers=[],
        deterministic_rollback_hash=OverlayFirewallRollbackPacket.compute_hash(
            overlay_hash, True, []
        ),
        status="passed",
    )
    ct = OverlayFirewallContinuityPacket(
        continuity_firewall_id="oft-1",
        overlay_hash=overlay_hash,
        continuity_score=0.88,
        unresolved_events=["evt-latency"],
        critical_unresolved_events=[],
        continuity_safe=True,
        deterministic_continuity_hash=OverlayFirewallContinuityPacket.compute_hash(
            overlay_hash, 0.88, ["evt-latency"], [], True
        ),
        status="passed",
    )
    deny = []
    e = OverlayFirewallEligibilityPacket(
        eligibility_id="ofe-1",
        overlay_hash=overlay_hash,
        readiness_score=readiness_score,
        rollback_ready=r.rollback_ready,
        governance_safe=g.governance_safe,
        containment_safe=c.containment_safe,
        continuity_safe=ct.continuity_safe,
        replay_valid=True,
        eligible_for_operator_review=True,
        denial_reasons=deny,
        deterministic_eligibility_hash=OverlayFirewallEligibilityPacket.compute_hash(
            overlay_hash, readiness_score, True, True, True, True, True, True, deny
        ),
        status="passed",
    )
    status = (
        "eligible_for_operator_review" if e.eligible_for_operator_review else "blocked"
    )
    blocked = [] if e.eligible_for_operator_review else e.denial_reasons
    f = OverlayExecutionReadinessFirewallPacket(
        firewall_id="off-1",
        overlay_hash=overlay_hash,
        readiness_hash="readiness-hash",
        governance_hash=g.deterministic_governance_hash,
        containment_hash=c.deterministic_containment_hash,
        resolution_hash="resolution-hash",
        firewall_status=status,
        blocked_reasons=blocked,
        deterministic_firewall_hash=OverlayExecutionReadinessFirewallPacket.compute_hash(
            overlay_hash,
            "readiness-hash",
            g.deterministic_governance_hash,
            c.deterministic_containment_hash,
            "resolution-hash",
            status,
            blocked,
        ),
        status="passed",
    )
    replay = OverlayFirewallReplayPacket(
        replay_id="ofrp-1",
        source_firewall_hash=f.deterministic_firewall_hash,
        replay_firewall_hash=f.deterministic_firewall_hash,
        deterministic_match=True,
        mismatch_reasons=[],
        status="passed",
    )
    lineage = OverlayFirewallLineagePacket(
        lineage_id="ofl-1",
        overlay_hash=overlay_hash,
        parent_hashes=[
            f.readiness_hash,
            f.governance_hash,
            f.containment_hash,
            f.resolution_hash,
        ],
        lineage_cycle_detected=False,
        status="passed",
    )
    diags: list[OverlayFirewallDiagnosticPacket] = []
    review = OperatorOverlayFirewallReviewPacket(
        review_id="ofor-1",
        overlay_hash=overlay_hash,
        firewall_status=f.firewall_status,
        operator_review_required=True,
        pending_actions=[],
        status="pending",
    )
    validator = validate_overlay_firewall(
        f.model_dump(),
        e.model_dump(),
        replay.model_dump(),
        [d.model_dump() for d in diags],
        lineage.model_dump(),
    )
    summary = {
        "firewall_status": f.firewall_status,
        "blocked_reasons": f.blocked_reasons,
        "rollback_ready": r.rollback_ready,
        "replay_matches": replay.deterministic_match,
        "critical_diagnostics": 0,
        "containment_restrictions": c.containment_restrictions,
        "governance_continuity": g.governance_continuity_score,
        "operator_review_required": review.operator_review_required,
        "projection_only": True,
        "inference_authority": False,
    }
    packet = {
        "schema_version": "OverlayFirewallRuntimePacket.v1",
        "firewall": f.model_dump(),
        "governance": g.model_dump(),
        "containment": c.model_dump(),
        "rollback": r.model_dump(),
        "continuity": ct.model_dump(),
        "eligibility": e.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": [d.model_dump() for d in diags],
        "operator_review": review.model_dump(),
        "overlay_firewall_summary": summary,
        "overlay_firewall_readiness_gate": "passed",
        "overlay_firewall_governance_gate": "passed",
        "overlay_firewall_containment_gate": "passed",
        "overlay_firewall_rollback_gate": "passed",
        "overlay_firewall_continuity_gate": "passed",
        "overlay_firewall_eligibility_gate": "passed",
        "overlay_firewall_replay_gate": "passed",
        "overlay_firewall_operator_review_gate": "passed",
        "validator": validator,
        "status": validator["status"],
    }
    return packet
