from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from .authority_router import authority_gate
from .models import RuntimeDecision, RuntimeInvocation


from core.audit.status import build_audit_status_envelope
def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def route_runtime_invocation(invocation: RuntimeInvocation) -> RuntimeDecision:
    invocation_text = json.dumps(asdict(invocation), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    invocation_hash = _hash_text(invocation_text)
    posture, reason = authority_gate(invocation)
    decision_payload = {
        "invocation_hash": invocation_hash,
        "posture": posture.value,
        "reason": reason,
        "route": asdict(invocation.route),
    }
    decision_hash = _hash_text(json.dumps(decision_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return RuntimeDecision(posture=posture, decision_hash=decision_hash, reason=reason)



def build_runtime_spine_audit_payload(invocation: RuntimeInvocation) -> dict:
    decision = route_runtime_invocation(invocation)
    envelope = build_audit_status_envelope(
        artifact_id="runtime_spine_skeleton",
        artifact_type="runtime_spine",
        status=decision.posture.value,
        findings=[],
        source_artifacts=[],
        artifact_hash=decision.decision_hash,
        generated_at_policy="INPUT_DERIVED",
    )
    return {"invocation": asdict(invocation), "decision": {"posture": decision.posture.value, "decision_hash": decision.decision_hash, "reason": decision.reason}, "status": decision.posture.value, "posture": decision.posture.value, "runtime_posture": decision.posture.value, "audit_envelope": envelope}
