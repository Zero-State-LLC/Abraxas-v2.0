from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from typing import Any, Mapping, Sequence

from .models import ReplayLedgerEntry, ReplayLineageRef, ReplayLedger, ReplayDiffInputRef, ReplayDivergenceFinding, ReplayTemporalStabilityScore, ReplayTemporalDiff

LEDGER_SCHEMA = "ReplayLedger.v1"
DIFF_SCHEMA = "ReplayTemporalDiff.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_replay_ledger_json(ledger: ReplayLedger | Mapping[str, Any]) -> str:
    payload = asdict(ledger) if isinstance(ledger, ReplayLedger) else dict(ledger)
    payload.pop("ledger_hash", None)
    return _canonical_json(payload)


def replay_ledger_hash(ledger: ReplayLedger | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_replay_ledger_json(ledger))


def canonical_replay_temporal_diff_json(diff: ReplayTemporalDiff | Mapping[str, Any]) -> str:
    payload = asdict(diff) if isinstance(diff, ReplayTemporalDiff) else dict(diff)
    payload.pop("diff_hash", None)
    return _canonical_json(payload)


def replay_temporal_diff_hash(diff: ReplayTemporalDiff | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_replay_temporal_diff_json(diff))


def compute_temporal_stability_score(entries: Sequence[Mapping[str, Any]]) -> ReplayTemporalStabilityScore:
    run_count = len(entries)
    if run_count < 2:
        return ReplayTemporalStabilityScore("score-1", run_count, run_count, 0, 1.0 if run_count else 0.0, "INSUFFICIENT_HISTORY", False)
    stable = 1
    div = 0
    for i in range(1, run_count):
        same = entries[i].get("replay_hash") == entries[i-1].get("replay_hash") and entries[i].get("replay_status") == entries[i-1].get("replay_status")
        if same:
            stable += 1
        else:
            div += 1
    ratio = stable / run_count
    posture = "STABLE" if ratio >= 0.95 else ("MIXED" if ratio >= 0.70 else "UNSTABLE")
    return ReplayTemporalStabilityScore("score-1", run_count, stable, div, round(ratio, 10), posture, False)


def build_replay_ledger(ledger_id: str, entries: tuple[ReplayLedgerEntry, ...], lineage_refs: tuple[ReplayLineageRef, ...], ledger_status: str, ledger_policy: str, created_by_lane: str, authority_ref: dict | None) -> ReplayLedger:
    draft = ReplayLedger(LEDGER_SCHEMA, ledger_id, entries, lineage_refs, ledger_status, ledger_policy, created_by_lane, authority_ref, False, False, False, "PENDING")
    return replace(draft, ledger_hash=replay_ledger_hash(draft))


def build_replay_temporal_diff(diff_id: str, base_replay_id: str, base_replay_hash: str, candidate_replay_id: str, candidate_replay_hash: str, input_refs: tuple[ReplayDiffInputRef, ...], divergence_findings: tuple[ReplayDivergenceFinding, ...], stability_score: ReplayTemporalStabilityScore, diff_status: str, created_by_lane: str, authority_ref: dict | None) -> ReplayTemporalDiff:
    draft = ReplayTemporalDiff(DIFF_SCHEMA, diff_id, base_replay_id, base_replay_hash, candidate_replay_id, candidate_replay_hash, input_refs, divergence_findings, stability_score, diff_status, created_by_lane, authority_ref, False, False, False, "PENDING")
    return replace(draft, diff_hash=replay_temporal_diff_hash(draft))
