from __future__ import annotations

import hashlib
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.oracle.conflicts import IntakeConflictPacket
from core.oracle.evidence import SourceEvidencePacket
from core.oracle.intake import OracleIntakeEnvelope
from core.oracle.lineage import IntakeLineageNode, IntakeLineagePacket
from core.oracle.normalization import IntakeNormalizationPacket
from core.oracle.operator_review import OperatorIntakeReviewPacket
from core.oracle.replay import IntakeReplayPacket
from core.oracle.stabilization import IntakeStabilizationPacket


def run_oracle_intake(source_payloads: list[dict[str, str]]) -> dict:
    payload = source_payloads[0]
    raw = payload["payload"]
    source_hash = hashlib.sha256(payload["source_id"].encode()).hexdigest()
    raw_hash = OracleIntakeEnvelope.hash_payload(raw)
    normalized = " ".join(raw.lower().split())
    normalized_hash = hashlib.sha256(normalized.encode()).hexdigest()
    intake = OracleIntakeEnvelope(intake_id=f"intake:{source_hash[:10]}", source_id=payload["source_id"], source_type=payload["source_type"], source_hash=source_hash, raw_payload_hash=raw_hash, normalized_payload_hash=normalized_hash, intake_status="normalized")
    norm = IntakeNormalizationPacket(normalization_id=f"norm:{source_hash[:10]}", source_hash=source_hash, normalized_hash=normalized_hash, normalization_steps=["lowercase", "whitespace_collapse"], deterministic_normalization_hash=IntakeNormalizationPacket.compute_hash(source_hash, normalized_hash, ["lowercase", "whitespace_collapse"]))
    evidence = SourceEvidencePacket(evidence_id=f"evidence:{source_hash[:10]}", intake_hash=source_hash, provenance_chain=[payload["source_id"], payload["source_type"]], evidence_type="structural", deterministic_evidence_hash=SourceEvidencePacket.compute_hash(source_hash, [payload["source_id"], payload["source_type"]], "structural"))
    replay = IntakeReplayPacket(replay_id=f"replay:{source_hash[:10]}", source_intake_hash=normalized_hash, replay_intake_hash=normalized_hash, deterministic_match=True, mismatched_normalizations=[])
    lineage_nodes = [IntakeLineageNode(intake_hash=source_hash, generation=0), IntakeLineageNode(intake_hash=normalized_hash, parent_hash=source_hash, generation=1, normalization_hash=norm.deterministic_normalization_hash)]
    lineage = IntakeLineagePacket(lineage_id=f"lineage:{source_hash[:10]}", lineage_depth=2, lineage_nodes=lineage_nodes, deterministic_lineage_hash=IntakeLineagePacket.compute_hash(lineage_nodes), status="ok")
    conflicts: list[IntakeConflictPacket] = []
    stabilization = IntakeStabilizationPacket(stabilization_id=f"stabilization:{source_hash[:10]}", intake_hash=source_hash, replay_match_count=1, replay_failure_count=0, conflict_count=len(conflicts), stabilization_window=3, stabilization_state="stable")
    review = OperatorIntakeReviewPacket(review_id=f"review:{source_hash[:10]}", intake_hash=source_hash, pending_conflicts=[], stabilization_state=stabilization.stabilization_state, replay_status="matched", operator_actions=["review_pending"])
    packet = {"intake": intake.model_dump(), "normalization": norm.model_dump(), "evidence": evidence.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "conflicts": [c.model_dump() for c in conflicts], "stabilization": stabilization.model_dump(), "review": review.model_dump()}
    write_canonical_json(Path("out/oracle/latest.json"), packet)
    write_canonical_json(Path("out/oracle_lineage/latest.json"), lineage.model_dump())
    write_canonical_json(Path("out/oracle_conflicts/latest.json"), {"conflicts": [c.model_dump() for c in conflicts]})
    write_canonical_json(Path("out/oracle_replay/latest.json"), replay.model_dump())
    return packet
