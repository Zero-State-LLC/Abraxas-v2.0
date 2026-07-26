from __future__ import annotations

# WP-D batch2: pure builder — publication via sole-writer scripts only.
# Gap G3: conflict population is detection-only; no auto-resolution.
import hashlib
from collections import defaultdict

from core.oracle.conflicts import IntakeConflictPacket
from core.oracle.evidence import SourceEvidencePacket
from core.oracle.intake import OracleIntakeEnvelope
from core.oracle.lineage import IntakeLineageNode, IntakeLineagePacket
from core.oracle.normalization import IntakeNormalizationPacket
from core.oracle.operator_review import OperatorIntakeReviewPacket
from core.oracle.replay import IntakeReplayPacket
from core.oracle.stabilization import IntakeStabilizationPacket


def _detect_intake_conflicts(
    source_payloads: list[dict[str, str]],
) -> list[IntakeConflictPacket]:
    """Detect intake conflicts across source payloads. Does not resolve them."""
    conflicts: list[IntakeConflictPacket] = []

    by_source: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for payload in source_payloads:
        source_id = payload["source_id"]
        raw = payload["payload"]
        raw_hash = OracleIntakeEnvelope.hash_payload(raw)
        normalized = " ".join(raw.lower().split())
        normalized_hash = hashlib.sha256(normalized.encode()).hexdigest()
        by_source[source_id].append((raw_hash, normalized_hash, payload.get("source_type", "")))

    for source_id, entries in sorted(by_source.items()):
        raw_hashes = sorted({e[0] for e in entries})
        norm_hashes = sorted({e[1] for e in entries})
        source_types = sorted({e[2] for e in entries if e[2]})

        if len(entries) > 1 and len(raw_hashes) > 1:
            conflicts.append(
                IntakeConflictPacket(
                    conflict_id=f"conflict:provenance:{source_id[:16]}",
                    conflicting_hashes=raw_hashes,
                    conflict_type="provenance_mismatch",
                    severity="high",
                    resolution_required=True,
                    status="open",
                )
            )
        elif len(entries) > 1 and len(raw_hashes) == 1:
            conflicts.append(
                IntakeConflictPacket(
                    conflict_id=f"conflict:duplicate:{source_id[:16]}",
                    conflicting_hashes=raw_hashes,
                    conflict_type="duplicate_source",
                    severity="low",
                    resolution_required=False,
                    status="open",
                )
            )

        if len(norm_hashes) > 1:
            conflicts.append(
                IntakeConflictPacket(
                    conflict_id=f"conflict:normalization:{source_id[:16]}",
                    conflicting_hashes=norm_hashes,
                    conflict_type="normalization_mismatch",
                    severity="medium",
                    resolution_required=True,
                    status="open",
                )
            )

        if len(source_types) > 1:
            conflicts.append(
                IntakeConflictPacket(
                    conflict_id=f"conflict:lineage:{source_id[:16]}",
                    conflicting_hashes=sorted(source_types),
                    conflict_type="lineage_break",
                    severity="medium",
                    resolution_required=True,
                    status="open",
                )
            )

    conflicts.sort(key=lambda c: c.conflict_id)
    return conflicts


def run_oracle_intake(source_payloads: list[dict[str, str]]) -> dict:
    """Build oracle intake packet. Conflicts are detected, never auto-resolved.

    Multi-payload input is supported only for conflict detection under a single
    ``source_id``. Mixed source IDs fail closed because this builder emits one
    intake packet from the first payload and would otherwise silently drop the
    rest while reporting ``stable``.
    """
    if not source_payloads:
        raise ValueError("source_payloads must not be empty")

    source_ids = {payload["source_id"] for payload in source_payloads}
    if len(source_ids) > 1:
        raise ValueError(
            "run_oracle_intake emits one intake packet; mixed source_ids must be "
            f"split before intake (got {sorted(source_ids)!r})"
        )

    payload = source_payloads[0]
    raw = payload["payload"]
    source_hash = hashlib.sha256(payload["source_id"].encode()).hexdigest()
    raw_hash = OracleIntakeEnvelope.hash_payload(raw)
    normalized = " ".join(raw.lower().split())
    normalized_hash = hashlib.sha256(normalized.encode()).hexdigest()

    conflicts = _detect_intake_conflicts(source_payloads)
    intake_status = "conflict_detected" if conflicts else "normalized"
    # IntakeStabilizationPacket forbids stable when conflict_count > 0
    stabilization_state = "conflicted" if conflicts else "stable"

    intake = OracleIntakeEnvelope(
        intake_id=f"intake:{source_hash[:10]}",
        source_id=payload["source_id"],
        source_type=payload["source_type"],  # type: ignore[arg-type]
        source_hash=source_hash,
        raw_payload_hash=raw_hash,
        normalized_payload_hash=normalized_hash,
        intake_status=intake_status,
    )
    norm = IntakeNormalizationPacket(
        normalization_id=f"norm:{source_hash[:10]}",
        source_hash=source_hash,
        normalized_hash=normalized_hash,
        normalization_steps=["lowercase", "whitespace_collapse"],
        deterministic_normalization_hash=IntakeNormalizationPacket.compute_hash(
            source_hash, normalized_hash, ["lowercase", "whitespace_collapse"]
        ),
    )
    evidence = SourceEvidencePacket(
        evidence_id=f"evidence:{source_hash[:10]}",
        intake_hash=source_hash,
        provenance_chain=[payload["source_id"], payload["source_type"]],
        evidence_type="structural",
        deterministic_evidence_hash=SourceEvidencePacket.compute_hash(
            source_hash, [payload["source_id"], payload["source_type"]], "structural"
        ),
    )
    replay = IntakeReplayPacket(
        replay_id=f"replay:{source_hash[:10]}",
        source_intake_hash=normalized_hash,
        replay_intake_hash=normalized_hash,
        deterministic_match=True,
        mismatched_normalizations=[],
    )
    lineage_nodes = [
        IntakeLineageNode(intake_hash=source_hash, generation=0),
        IntakeLineageNode(
            intake_hash=normalized_hash,
            parent_hash=source_hash,
            generation=1,
            normalization_hash=norm.deterministic_normalization_hash,
        ),
    ]
    lineage = IntakeLineagePacket(
        lineage_id=f"lineage:{source_hash[:10]}",
        lineage_depth=2,
        lineage_nodes=lineage_nodes,
        deterministic_lineage_hash=IntakeLineagePacket.compute_hash(lineage_nodes),
        status="ok",
    )

    stabilization = IntakeStabilizationPacket(
        stabilization_id=f"stabilization:{source_hash[:10]}",
        intake_hash=source_hash,
        replay_match_count=1,
        replay_failure_count=0,
        conflict_count=len(conflicts),
        stabilization_window=3,
        stabilization_state=stabilization_state,
    )

    pending = [c.conflict_id for c in conflicts if c.resolution_required]
    operator_actions = ["review_conflicts", "no_auto_resolve"] if conflicts else ["review_pending"]

    review = OperatorIntakeReviewPacket(
        review_id=f"review:{source_hash[:10]}",
        intake_hash=source_hash,
        pending_conflicts=pending,
        stabilization_state=stabilization.stabilization_state,
        replay_status="matched",
        operator_actions=operator_actions,
    )

    return {
        "intake": intake.model_dump(),
        "normalization": norm.model_dump(),
        "evidence": evidence.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "conflicts": [c.model_dump() for c in conflicts],
        "stabilization": stabilization.model_dump(),
        "review": review.model_dump(),
    }
