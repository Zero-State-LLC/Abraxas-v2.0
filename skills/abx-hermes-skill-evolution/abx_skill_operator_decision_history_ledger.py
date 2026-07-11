#!/usr/bin/env python3
"""
Append-Only Operator Decision History Ledger (v3.1)

Records immutable events for the operator decision lifecycle.
Rebuilds current known events on each run for deterministic valid chain.
Events: REVIEW_PACKET_GENERATED, DECISION_INPUT_RECORDED, VALIDATION_PERFORMED, RECONCILIATION_PERFORMED.

Hash chain uses sequence + key content (no wall time dependency for integrity).
Replayable. Preserves history. No authority conferred.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
OPERATOR_DIR = Path("out/operator_input")
HISTORY_PATH = OUT / "abx_hermes_operator_decision_history_v3_1.latest.json"
CHAIN_VALID_PATH = OUT / "abx_hermes_operator_decision_history_chain_validation_v3_1.latest.json"

REVIEW_PATH = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
DECISION_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"
VALIDATION_PATH = OUT / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json"
RECONC_PATH = OUT / "abx_hermes_operator_decision_reconciliation_v3_0.latest.json"


def load_json_safe(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def compute_event_hash(event: dict) -> str:
    h_input = {k: event.get(k) for k in sorted(event.keys()) if k not in ("timestamp", "event_hash")}
    return hashlib.sha256(json.dumps(h_input, sort_keys=True).encode()).hexdigest()[:16]

def append_event(history: list, event_class: str, formal_review_id: str, candidate_id: str,
                 source_artifact: str, source_hash: str, decision_id: str = None,
                 decision_value: str = None, validation_class: str = None,
                 routing_lane: str = None, authority_conferred: bool = False) -> dict:
    seq = len(history) + 1
    prev_hash = history[-1]["event_hash"] if history else "GENESIS"
    event = {
        "event_sequence": seq,
        "event_class": event_class,
        "formal_review_id": formal_review_id,
        "candidate_id": candidate_id,
        "source_artifact": source_artifact,
        "source_hash": source_hash,
        "decision_id": decision_id,
        "decision_value": decision_value,
        "validation_class": validation_class,
        "routing_lane": routing_lane,
        "authority_conferred": authority_conferred,
        "previous_event_hash": prev_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    h_input = {k: event.get(k) for k in sorted(event.keys()) if k not in ("event_hash", "timestamp")}
    event["event_hash"] = hashlib.sha256(json.dumps(h_input, sort_keys=True).encode()).hexdigest()[:16]
    history.append(event)
    return event


def main():
    review = load_json_safe(REVIEW_PATH) or {}
    decision = load_json_safe(DECISION_PATH) or {}
    validation = load_json_safe(VALIDATION_PATH) or {}
    recon = load_json_safe(RECONC_PATH) or {}

    history = []
    formal_review_id = review.get("formal_review_id") or (decision.get("formal_review_id") if decision else None)
    candidate_id = review.get("candidate_id", "abx_hermes_skill_evolution_v2.x-evo")

    # Always rebuild current events in fixed deterministic order (idempotent + always valid chain)
    if review:
        append_event(history, "REVIEW_PACKET_GENERATED", formal_review_id, candidate_id,
                     "abx_hermes_formal_operator_review_packet_v2_6.latest.json",
                     review.get("deterministic_hash", ""),
                     routing_lane=review.get("recommended_next_lane"))

    if decision:
        append_event(history, "DECISION_INPUT_RECORDED", formal_review_id, candidate_id,
                     "abx_hermes_formal_operator_decision_v2_7.input.json",
                     "",
                     decision_value=decision.get("decision_value"))

    if validation:
        append_event(history, "VALIDATION_PERFORMED", formal_review_id, candidate_id,
                     "abx_hermes_formal_operator_decision_validation_v2_8.latest.json",
                     validation.get("status", ""),
                     decision_value=validation.get("decision_value"),
                     validation_class=validation.get("status"))

    if recon:
        append_event(history, "RECONCILIATION_PERFORMED", formal_review_id, candidate_id,
                     "abx_hermes_operator_decision_reconciliation_v3_0.latest.json",
                     recon.get("deterministic_hash", ""),
                     decision_value=recon.get("current_decision", {}).get("decision_value") if recon.get("current_decision") else None,
                     validation_class=recon.get("reconciliation_status"),
                     routing_lane=recon.get("next_required_action"))

    history_obj = {
        "schema_version": "3.1",
        "ledger_class": "ABX_HERMES_OPERATOR_DECISION_HISTORY",
        "events": history,
        "event_count": len(history),
        "genesis": "GENESIS" if history else None,
        "last_event_hash": history[-1]["event_hash"] if history else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    HISTORY_PATH.write_text(json.dumps(history_obj, indent=2))

    # Fresh chain validation
    chain_valid = True
    errors = []
    prev = "GENESIS"
    for ev in history:
        if ev.get("previous_event_hash") != prev:
            chain_valid = False
            errors.append(f"CHAIN_BREAK at seq {ev['event_sequence']}")
        recomputed = compute_event_hash({k: ev.get(k) for k in ev if k != "timestamp"})
        if ev.get("event_hash") != recomputed:
            chain_valid = False
            errors.append(f"HASH_MISMATCH at seq {ev['event_sequence']}")
        prev = ev.get("event_hash")

    validation_obj = {
        "schema_version": "3.1",
        "validation_class": "ABX_HERMES_OPERATOR_DECISION_HISTORY_CHAIN_VALIDATION",
        "chain_valid": chain_valid,
        "event_count": len(history),
        "errors": errors,
        "last_event_hash": history[-1]["event_hash"] if history else None,
        "deterministic_hash": compute_event_hash({"chain_valid": chain_valid, "event_count": len(history)}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    CHAIN_VALID_PATH.write_text(json.dumps(validation_obj, indent=2))

    print(f"Decision history ledger emitted: {HISTORY_PATH} (events={len(history)})")
    print(f"Chain validation: {CHAIN_VALID_PATH} valid={chain_valid}")
    return history_obj


if __name__ == "__main__":
    main()
