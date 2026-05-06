from __future__ import annotations

from core.sandbox.branches import SandboxBranchPacket
from core.sandbox.convergence import SandboxConvergencePacket
from core.sandbox.lineage import SandboxLineagePacket
from core.sandbox.replay import SandboxReplayPacket


def validate_sandbox_replay(
    branch: SandboxBranchPacket,
    replay_packet: SandboxReplayPacket,
    lineage_packet: SandboxLineagePacket | None = None,
    convergence_packet: SandboxConvergencePacket | None = None,
) -> dict[str, object]:
    gates: list[dict[str, object]] = []
    gates.append({"gate": "sandbox_branch_gate", "passed": branch.parent_state_hash != branch.sandbox_state_hash, "reason": "isolated"})
    gates.append({"gate": "sandbox_replay_gate", "passed": replay_packet.deterministic_match and not replay_packet.mismatched_mutations, "reason": "deterministic replay"})
    lineage_ok = lineage_packet is None or lineage_packet.status == "ok"
    gates.append({"gate": "sandbox_lineage_gate", "passed": lineage_ok, "reason": "lineage valid" if lineage_ok else "lineage invalid"})
    if convergence_packet is not None:
        gates.append({"gate": "sandbox_convergence_gate", "passed": convergence_packet.convergence_score >= 0.5, "reason": "convergence threshold"})
    production_taint = any("production" in m.lower() for m in replay_packet.replayed_mutations)
    gates.append({"gate": "sandbox_operator_review_gate", "passed": not production_taint, "reason": "no production mutation attempts"})
    failed = [g for g in gates if not g["passed"]]
    return {"status": "doctrine_compliant" if not failed else "repair_required", "gate_results": gates}
