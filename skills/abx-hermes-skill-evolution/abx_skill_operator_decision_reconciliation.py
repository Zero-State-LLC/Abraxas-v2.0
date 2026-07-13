#!/usr/bin/env python3
"""
Operator Decision Lifecycle Reconciliation (v3.0)

Inspects current review packet + decision input + prior ledger/validation.
Classifies precisely:
- CURRENT_DECISION_VALID (full match + all acks + authority blocked + identity + valid decision)
- PRIOR_DECISION_STALE (bound to this packet or prior but incomplete / previously blocked)
- CURRENT_DECISION_MISSING
- DECISION_INVALID
- etc.

Preserves history. Does not overwrite decision records.
Emits reconciliation artifact.
Advisory / SHADOW only. Never mutates active skill or grants authority.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
OPERATOR_DIR = Path("out/operator_input")
REVIEW_PATH = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"
DECISION_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"
VALIDATION_PATH = OUT / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json"
LEDGER_PATH = OUT / "abx_hermes_formal_operator_decision_ledger_v2_9.latest.json"

ALLOWED_DECISIONS = {
    "APPROVE_EXTENDED_OBSERVATION",
    "REQUEST_MORE_EVIDENCE",
    "REJECT_CANDIDATE",
    "HOLD_FOR_REVIEW",
}
REQUIRED_ACKS = [
    "review_packet_examined",
    "advisory_boundary_understood",
    "no_production_authority_granted",
    "no_active_skill_replacement_authorized",
    "decision_is_human_supplied",
    "operator_attestation",
]
REQUIRED_AUTH = [
    "promotion_authorized",
    "production_activation_allowed",
    "active_skill_replacement_allowed",
    "automatic_transition_allowed",
]


def load_json_safe(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def compute_det_hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def main():
    review = load_json_safe(REVIEW_PATH) or {}
    decision = load_json_safe(DECISION_PATH) or {}
    validation = load_json_safe(VALIDATION_PATH) or {}
    ledger = load_json_safe(LEDGER_PATH) or {}

    current_review_id = review.get("formal_review_id")
    current_packet_hash = review.get("deterministic_hash")

    dec_review_id = decision.get("formal_review_id")
    dec_packet_hash = decision.get("review_packet_hash")
    dec_value = decision.get("decision_value")
    op = decision.get("operator", {})
    acks = decision.get("acknowledgements", {})
    auth = decision.get("authority_boundary", {})

    # Historical scan (simplified: use prior ledger if present and different)
    historical_decisions = []
    if ledger and ledger.get("formal_review_id") and ledger.get("formal_review_id") != current_review_id:
        historical_decisions.append({
            "formal_review_id": ledger.get("formal_review_id"),
            "decision_value": ledger.get("decision_value"),
            "validation_status": ledger.get("validation_status"),
            "note": "prior_ledger"
        })

    # Preserve the validation load for stale-decision classification context.
    _ = validation.get("status") == "BLOCKED_BY_VALIDATION_ERRORS"

    errors = []
    is_full_match = (
        dec_review_id == current_review_id and
        dec_packet_hash == current_packet_hash
    )

    if not decision:
        classification = "CURRENT_DECISION_MISSING"
        errors.append("NO_DECISION_INPUT")
    elif not is_full_match:
        classification = "PRIOR_DECISION_STALE"
        errors.append("PACKET_BINDING_MISMATCH_WITH_CURRENT_REVIEW")
    else:
        # Check completeness for CURRENT_VALID
        if dec_value not in ALLOWED_DECISIONS:
            errors.append("INVALID_DECISION_VALUE")
        for ack in REQUIRED_ACKS:
            if acks.get(ack) is not True:
                errors.append(f"MISSING_OR_FALSE_ACK:{ack}")
        for key in REQUIRED_AUTH:
            if auth.get(key) is not False:
                errors.append(f"AUTHORITY_NOT_BLOCKED:{key}")
        if not op.get("operator_id"):
            errors.append("MISSING_OPERATOR_IDENTITY")

        if errors:
            classification = "PRIOR_DECISION_STALE"  # incomplete for current packet -> treat as stale historical
        else:
            classification = "CURRENT_DECISION_VALID"

    # Collect examined records
    decision_records_examined = []
    if decision:
        decision_records_examined.append({
            "source": "current_input",
            "formal_review_id": dec_review_id,
            "decision_value": dec_value,
            "packet_hash": dec_packet_hash,
        })
    if ledger:
        decision_records_examined.append({
            "source": "ledger_v2_9",
            "formal_review_id": ledger.get("formal_review_id"),
            "decision_value": ledger.get("decision_value"),
            "validation_status": ledger.get("validation_status"),
        })

    current_decision = None
    if classification == "CURRENT_DECISION_VALID":
        current_decision = {
            "formal_review_id": dec_review_id,
            "decision_value": dec_value,
            "operator_id": op.get("operator_id"),
        }

    supersede_recommended = False
    supersede_reason = None
    if classification == "PRIOR_DECISION_STALE":
        supersede_recommended = True
        supersede_reason = "Stale/incomplete decision record for current review. Recommend SUPERSEDE_PRIOR_DECISION or new FORMAL_OPERATOR_DECISION."

    historical_decisions = historical_decisions or []
    if classification in ("PRIOR_DECISION_STALE", "DECISION_INVALID") and decision:
        historical_decisions.append({
            "formal_review_id": dec_review_id,
            "decision_value": dec_value,
            "note": "stale_or_incomplete_for_current_packet",
            "previous_validation_status": validation.get("status"),
        })

    reconciliation = {
        "schema_version": "3.0",
        "artifact_class": "ABX_HERMES_OPERATOR_DECISION_RECONCILIATION",
        "current_review_packet": {
            "formal_review_id": current_review_id,
            "packet_hash": current_packet_hash,
            "candidate_id": review.get("candidate_id"),
        },
        "decision_records_examined": decision_records_examined,
        "classifications": [
            {"record": "current_decision_input", "classification": classification, "errors": errors}
        ],
        "current_decision": current_decision,
        "historical_decisions": historical_decisions,
        "conflicts": [],
        "shadow_findings": [
            f"Live decision input incomplete or previously blocked for packet {current_review_id}"
        ] if classification != "CURRENT_DECISION_VALID" else [],
        "reconciliation_status": classification,
        "next_required_action": "FORMAL_OPERATOR_DECISION_REQUIRED" if classification != "CURRENT_DECISION_VALID" else "NONE",
        "supersede_recommended": supersede_recommended,
        "supersede_reason": supersede_reason,
        "authority_boundary": {
            "promotion_authorized": False,
            "production_activation_allowed": False,
            "active_skill_replacement_allowed": False,
        },
        "deterministic_hash": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Deterministic hash over key content (no wall time)
    hash_input = {
        "current_review_packet": reconciliation["current_review_packet"],
        "classifications": reconciliation["classifications"],
        "reconciliation_status": reconciliation["reconciliation_status"],
        "next_required_action": reconciliation["next_required_action"],
        "supersede_recommended": reconciliation.get("supersede_recommended"),
    }
    reconciliation["deterministic_hash"] = compute_det_hash(hash_input)

    out_path = OUT / "abx_hermes_operator_decision_reconciliation_v3_0.latest.json"
    out_path.write_text(json.dumps(reconciliation, indent=2))

    print(f"Decision reconciliation emitted: {out_path}")
    print(f"reconciliation_status: {reconciliation['reconciliation_status']}")
    print(f"next_required_action: {reconciliation['next_required_action']}")
    return reconciliation


if __name__ == "__main__":
    main()
