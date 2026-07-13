#!/usr/bin/env python3
"""
Independent Formal Operator Decision Intake Validator (v2.8)
Consumes the completed operator decision record from the builder.
Performs strict independent validation (no trust of builder output).
Emits validation receipt. Never mutates active skill. Advisory only.

States: VALIDATED | BLOCKED_BY_* | NOT_COMPUTABLE
"""

import json
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
OPERATOR_DIR = Path("out/operator_input")
COMPLETED_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"
REVIEW_PACKET_PATH = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"

ALLOWED_DECISIONS = {
    "APPROVE_EXTENDED_OBSERVATION",
    "REQUEST_MORE_EVIDENCE",
    "REJECT_CANDIDATE",
    "HOLD_FOR_REVIEW"
}

REQUIRED_ACKS = [
    "review_packet_examined",
    "advisory_boundary_understood",
    "no_production_authority_granted",
    "no_active_skill_replacement_authorized",
    "decision_is_human_supplied",
    "operator_attestation"
]

def load_json_safe(p: Path):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def main():
    decision = load_json_safe(COMPLETED_PATH)
    review = load_json_safe(REVIEW_PACKET_PATH)

    if not decision or not review:
        status = "NOT_COMPUTABLE"
        print(f"Decision validator: {status} (missing decision record or review packet)")
        result = {
            "validation_class": "ABX_HERMES_FORMAL_OPERATOR_DECISION_VALIDATOR",
            "status": status,
            "formal_review_id": decision.get("formal_review_id") if decision else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        (OUT / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json").write_text(json.dumps(result, indent=2))
        return result

    errors = []
    review_id = decision.get("formal_review_id")
    if review_id != review.get("formal_review_id"):
        errors.append("REVIEW_ID_MISMATCH")

    if decision.get("review_packet_hash") != review.get("deterministic_hash"):
        errors.append("PACKET_HASH_MISMATCH")

    if decision.get("decision_value") not in ALLOWED_DECISIONS:
        errors.append("INVALID_DECISION_VALUE")

    acks = decision.get("acknowledgements", {})
    for ack in REQUIRED_ACKS:
        if acks.get(ack) is not True:
            errors.append(f"MISSING_OR_FALSE_ACK:{ack}")

    auth = decision.get("authority_boundary", {})
    for key in ["promotion_authorized", "production_activation_allowed", "active_skill_replacement_allowed", "automatic_transition_allowed"]:
        if auth.get(key) is not False:
            errors.append(f"AUTHORITY_NOT_BLOCKED:{key}")

    # Check operator fields present
    op = decision.get("operator", {})
    if not op.get("operator_id") or not op.get("operator_display_name"):
        errors.append("MISSING_OPERATOR_IDENTITY")

    if errors:
        status = "BLOCKED_BY_VALIDATION_ERRORS"
    else:
        status = "VALIDATED"

    result = {
        "validation_class": "ABX_HERMES_FORMAL_OPERATOR_DECISION_VALIDATOR_V2_8",
        "status": status,
        "formal_review_id": review_id,
        "decision_value": decision.get("decision_value"),
        "operator_id": op.get("operator_id"),
        "errors": errors,
        "binding_verified": len(errors) == 0 and not any("MISMATCH" in e for e in errors),
        "all_acks_true": all(acks.get(a) is True for a in REQUIRED_ACKS),
        "authority_all_blocked": all(auth.get(k) is False for k in ["promotion_authorized", "production_activation_allowed", "active_skill_replacement_allowed", "automatic_transition_allowed"]),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    out_path = OUT / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json"
    out_path.write_text(json.dumps(result, indent=2))

    print(f"Decision validator: {status}")
    if errors:
        print("Errors:", errors)
    print(f"Validation artifact: {out_path}")
    return result

if __name__ == "__main__":
    main()
