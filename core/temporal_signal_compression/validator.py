from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalClimateSignalCompressionLedger, TemporalCompressionValidationFinding, TemporalCompressionValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_signal_compression_ledger(ledger: TemporalClimateSignalCompressionLedger | Mapping[str, Any]) -> TemporalCompressionValidationReport:
    ledger_entry = ledger if isinstance(ledger, TemporalClimateSignalCompressionLedger) else TemporalClimateSignalCompressionLedger(**dict(ledger))
    findings=[]
    status="PASS"
    if (not ledger_entry.projection_only) or ledger_entry.ledger_authoritative or ledger_entry.execution_allowed or ledger_entry.mutation_allowed or ledger_entry.rollback_allowed or ledger_entry.promotion_allowed or ledger_entry.routing_change_allowed or ledger_entry.timeline_collapse_allowed or ledger_entry.canonical_selection_allowed or ledger_entry.replay_normalization_allowed or ledger_entry.adapter_activation_allowed or ledger_entry.auto_transition_allowed:
        findings.append(TemporalCompressionValidationFinding("FLAGS_FORBIDDEN","error","ledger flags must enforce projection-only, non-authoritative, non-executing, non-mutating, non-routing, non-collapsing, non-selecting, non-normalizing, non-activating."))
        status="BLOCKED"
    if any((not c.lineage_preserved) or c.replay_normalization_allowed or c.canonical_selection_allowed for c in ledger_entry.compression_clusters):
        findings.append(TemporalCompressionValidationFinding("CLUSTER_PRESERVATION_REQUIRED","error","clusters must preserve lineage and forbid normalization/canonical selection."))
        status="BLOCKED"
    if any((not m.lineage_preserved) or m.replay_normalization_allowed for m in ledger_entry.compression_motifs):
        findings.append(TemporalCompressionValidationFinding("MOTIF_PRESERVATION_REQUIRED","error","motifs must preserve lineage and forbid replay normalization."))
        status="BLOCKED"
    if any(o.action_authorization_allowed for o in ledger_entry.observations):
        findings.append(TemporalCompressionValidationFinding("OBSERVATION_AUTH_FORBIDDEN","error","observations cannot authorize action."))
        status="BLOCKED"
    if any(r.execution_allowed or r.mutation_allowed or r.routing_change_allowed or r.replay_normalization_allowed or r.canonical_selection_allowed for r in ledger_entry.recommendations):
        findings.append(TemporalCompressionValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN","error","recommendations cannot execute/mutate/route/normalize/select."))
        status="BLOCKED"
    if ledger_entry.ledger_status == "COMPRESSED_PRESSURE" and not any(c.cluster_type == "PRESSURE_CLUSTER" for c in ledger_entry.compression_clusters) and not any(o.observation_type == "PRESSURE_ESCALATION" for o in ledger_entry.observations):
        findings.append(TemporalCompressionValidationFinding("PRESSURE_CONSTRAINT","error","COMPRESSED_PRESSURE requires pressure clusters/observations."))
        status="BLOCKED"
    if ledger_entry.ledger_status == "COMPRESSED_REGIME_RISK" and not any(c.cluster_type == "REGIME_CLUSTER" for c in ledger_entry.compression_clusters) and not any(o.observation_type == "REGIME_DESTABILIZATION" for o in ledger_entry.observations):
        findings.append(TemporalCompressionValidationFinding("REGIME_CONSTRAINT","error","COMPRESSED_REGIME_RISK requires regime clusters/observations."))
        status="BLOCKED"
    if ledger_entry.ledger_status == "COMPRESSED_FRACTURE_RISK" and not any(c.cluster_type == "FRACTURE_CLUSTER" for c in ledger_entry.compression_clusters) and not any(o.observation_type == "FRACTURE_DENSITY" for o in ledger_entry.observations):
        findings.append(TemporalCompressionValidationFinding("FRACTURE_CONSTRAINT","error","COMPRESSED_FRACTURE_RISK requires fracture clusters/observations."))
        status="BLOCKED"
    if ledger_entry.ledger_status == "COMPRESSED_NONDETERMINISM" and not any(c.cluster_type == "NONDETERMINISM_CLUSTER" for c in ledger_entry.compression_clusters) and not any(o.observation_type == "NONDETERMINISM_ESCALATION" for o in ledger_entry.observations):
        findings.append(TemporalCompressionValidationFinding("NONDET_CONSTRAINT","error","COMPRESSED_NONDETERMINISM requires nondeterminism clusters/observations."))
        status="BLOCKED"
    if ledger_entry.ledger_status == "SIGNAL_OVERLOAD" and not any(b.overloaded for b in ledger_entry.pressure_bands):
        findings.append(TemporalCompressionValidationFinding("OVERLOAD_CONSTRAINT","error","SIGNAL_OVERLOAD requires overloaded pressure band."))
        status="BLOCKED"
    if ledger_entry.ledger_status == "BLOCKED_HISTORY_VISIBLE" and not any(c.cluster_type == "BLOCKED_HISTORY_CLUSTER" for c in ledger_entry.compression_clusters):
        findings.append(TemporalCompressionValidationFinding("BLOCKED_CONSTRAINT","error","BLOCKED_HISTORY_VISIBLE requires blocked-history cluster."))
        status="BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"ledger_id":ledger_entry.ledger_id}))
    return TemporalCompressionValidationReport(status, tuple(findings), receipt_hash)
