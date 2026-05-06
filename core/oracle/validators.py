from __future__ import annotations

from core.oracle.conflicts import IntakeConflictPacket
from core.oracle.lineage import IntakeLineagePacket
from core.oracle.replay import IntakeReplayPacket


def validate_intake_replay(intake: dict, replay_packet: IntakeReplayPacket, lineage_packet: IntakeLineagePacket | None = None, conflicts: list[IntakeConflictPacket] | None = None) -> dict[str, object]:
    conflicts = conflicts or []
    gates = [
        {"gate": "intake_replay_gate", "passed": replay_packet.deterministic_match, "reason": "replay mismatch invalidates stabilization"},
        {"gate": "intake_lineage_gate", "passed": lineage_packet is None or lineage_packet.status == "ok", "reason": "lineage mismatch fail closed"},
        {"gate": "oracle_intake_gate", "passed": bool(intake.get("source_hash")), "reason": "provenance present"},
    ]
    severe_open = [c for c in conflicts if c.severity == "severe" and c.status != "resolved"]
    gates.append({"gate": "intake_conflict_gate", "passed": not severe_open, "reason": "unresolved severe conflicts block approval"})
    return {"status": "doctrine_compliant" if all(g["passed"] for g in gates) else "repair_required", "gate_results": gates}
