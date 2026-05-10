from __future__ import annotations

from pathlib import Path
from dataclasses import asdict
from typing import Any, Mapping

from .ledger import *
from .ledger import _canonical_json, _sha256_text
from .validator import validate_replay_temporal_diff


def derive_replay_temporal_diff(base: Mapping[str, Any], candidate: Mapping[str, Any]) -> ReplayTemporalDiff:
    b, c = dict(base), dict(candidate)
    findings = []
    status = "NO_DIVERGENCE"
    if not b.get("replay_id") or not c.get("replay_id"):
        findings.append(ReplayDivergenceFinding("f-missing", "MISSING_INPUT", "NOT_COMPUTABLE", "missing", "missing", "Missing base/candidate refs."))
        status = "BLOCKED_BY_INPUTS"
    else:
        if b.get("replay_hash") != c.get("replay_hash"):
            findings.append(ReplayDivergenceFinding("f-hash", "HASH_MISMATCH", "WARN", str(b.get("replay_hash")), str(c.get("replay_hash")), "Replay hash mismatch.")); status = "DIVERGENCE_DETECTED"
        if b.get("replay_status") != c.get("replay_status"):
            findings.append(ReplayDivergenceFinding("f-status", "STATUS_CHANGE", "WARN", str(b.get("replay_status")), str(c.get("replay_status")), "Replay status changed.")); status = "DIVERGENCE_DETECTED"
        if b.get("rollback_plan_hash") != c.get("rollback_plan_hash"):
            findings.append(ReplayDivergenceFinding("f-rb", "ROLLBACK_CHANGE", "WARN", str(b.get("rollback_plan_hash")), str(c.get("rollback_plan_hash")), "Rollback plan hash changed.")); status = "ROLLBACK_DIVERGENCE"
        if b.get("authorization_hash") != c.get("authorization_hash"):
            findings.append(ReplayDivergenceFinding("f-auth", "AUTHORIZATION_CHANGE", "WARN", str(b.get("authorization_hash")), str(c.get("authorization_hash")), "Authorization hash changed.")); status = "AUTHORIZATION_DIVERGENCE"
        if b.get("nondeterminism_detected") or c.get("nondeterminism_detected"):
            findings.append(ReplayDivergenceFinding("f-nd", "NONDETERMINISM", "BLOCKED", str(b.get("nondeterminism_detected")), str(c.get("nondeterminism_detected")), "Nondeterminism detected.")); status = "NONDETERMINISM_DETECTED"

    score = compute_temporal_stability_score((b, c))
    return build_replay_temporal_diff("diff-1", str(b.get("replay_id", "")), str(b.get("replay_hash", "")), str(c.get("replay_id", "")), str(c.get("replay_hash", "")), (ReplayDiffInputRef("REPLAY_EXECUTION", str(b.get("replay_id", "")), str(b.get("replay_hash", ""))), ReplayDiffInputRef("REPLAY_EXECUTION", str(c.get("replay_id", "")), str(c.get("replay_hash", "")))), tuple(findings), score, status, "FORECAST", None)


def write_replay_ledger_temporal_diff_contract_audit(base_dir: Path | str = ".") -> str:
    b={"replay_id":"r1","replay_hash":"h1","replay_status":"REPLAY_READY","rollback_plan_hash":"rb1","authorization_hash":"a1","nondeterminism_detected":False}
    c={"replay_id":"r2","replay_hash":"h1","replay_status":"REPLAY_READY","rollback_plan_hash":"rb1","authorization_hash":"a1","nondeterminism_detected":False}
    d=derive_replay_temporal_diff(b,c)
    report=validate_replay_temporal_diff(d)
    payload={"status":report.status,"diff_hash":d.diff_hash,"receipt_hash":report.receipt_hash,"findings":[asdict(f) for f in report.findings],"schema_version":d.schema_version}
    text=_canonical_json(payload)+"\n"
    out=Path(base_dir)/"out/audit/replay_ledger_temporal_diff_contract.latest.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(text,encoding="utf-8")
    return _sha256_text(text)
