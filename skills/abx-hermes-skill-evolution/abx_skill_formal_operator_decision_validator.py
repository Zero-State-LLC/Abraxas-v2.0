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

from core.canonical.json import write_canonical_json

from abx_skill_stabilization_evolution_contracts import (
    STABILIZATION_OPERATOR_DECISIONS,
)

OUT = Path("out/audit")
OPERATOR_DIR = Path("out/operator_input")
COMPLETED_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"
REVIEW_PACKET_PATH = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"

ALLOWED_DECISIONS = {
    "APPROVE_EXTENDED_OBSERVATION",
    "REQUEST_MORE_EVIDENCE",
    "REJECT_CANDIDATE",
    "HOLD_FOR_REVIEW"
} | STABILIZATION_OPERATOR_DECISIONS

REQUIRED_ACKS = [
    "review_packet_examined",
    "advisory_boundary_understood",
    "no_production_authority_granted",
    "no_active_skill_replacement_authorized",
    "decision_is_human_supplied",
    "operator_attestation"
]

def reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def load_input(path, name, errors, bindings):
    import hashlib
    bindings[name] = None
    try:
        raw = path.read_bytes()
    except OSError:
        errors.append(f"UNREADABLE_INPUT:{name}")
        return None
    bindings[name] = hashlib.sha256(raw).hexdigest()
    try:
        value = json.loads(raw, parse_constant=reject_constant)
        # Also reject overflowed JSON exponents (e.g. 1e999) anywhere nested.
        json.dumps(value, allow_nan=False)
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError):
        errors.append(f"INVALID_JSON:{name}")
        return None


def load_json_safe(p: Path):
    return load_input(p, "input", [], {})


def validate_shapes(decision, review, errors):
    for name, obj in [("decision", decision), ("review", review)]:
        if not isinstance(obj, dict):
            errors.append(f"INVALID_OBJECT:{name}")
            continue
        keys = ("formal_review_id", "deterministic_hash") if name == "review" else (
            "formal_review_id", "review_packet_hash", "decision_value", "timestamp", "confirmed_review_sha256")
        for key in keys:
            if not isinstance(obj.get(key), str) or not obj[key]:
                errors.append(f"INVALID_STRING:{name}.{key}")
    if not isinstance(decision, dict):
        return
    for key in ("provenance", "acknowledgements", "authority_boundary", "operator"):
        nested = decision.get(key)
        if not isinstance(nested, dict):
            errors.append(f"INVALID_OBJECT:decision.{key}")
        elif key in ("operator", "provenance"):
            fields = ("operator_id", "operator_display_name") if key == "operator" else ("source", "input_method")
            for field in fields:
                if not isinstance(nested.get(field), str) or not nested[field]:
                    errors.append(f"INVALID_STRING:decision.{key}.{field}")


def main():
    errors = []
    bindings = {}
    decision = load_input(COMPLETED_PATH, "decision", errors, bindings)
    review = load_input(REVIEW_PACKET_PATH, "review", errors, bindings)
    validate_shapes(decision, review, errors)
    if errors:
        result = {
            "validation_class": "ABX_HERMES_FORMAL_OPERATOR_DECISION_VALIDATOR_V2_8",
            "status": "BLOCKED_BY_VALIDATION_ERRORS",
            "errors": errors,
            "binding_verified": False,
            "input_sha256": bindings,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        write_canonical_json(OUT / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json", result)
        print("Decision validator: BLOCKED_BY_VALIDATION_ERRORS", errors)
        return result
    assert isinstance(decision, dict) and isinstance(review, dict)
    provenance = decision.get("provenance", {})
    if (provenance.get("source") != "OPERATOR_SUPPLIED" or
            provenance.get("input_method") != "INTERACTIVE_ONE_AT_A_TIME"):
        errors.append("HUMAN_INPUT_REQUIRED")
    try:
        collected = datetime.fromisoformat(decision.get("timestamp", ""))
        age = (datetime.now(timezone.utc) - collected).total_seconds()
        if not 0 <= age <= 86400:
            errors.append("STALE_OR_FUTURE_DECISION")
    except (ValueError, TypeError):
        errors.append("INVALID_CONFIRMATION_TIMESTAMP")
    import hashlib
    review_sha256 = hashlib.sha256(json.dumps(review, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    if decision.get("confirmed_review_sha256") != review_sha256:
        errors.append("IMMUTABLE_REVIEW_BINDING_MISMATCH")
    if decision.get("operator_confirmed") is not True:
        errors.append("EXPLICIT_CONFIRMATION_REQUIRED")
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
        "input_sha256": bindings,
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
    write_canonical_json(out_path, result)

    print(f"Decision validator: {status}")
    if errors:
        print("Errors:", errors)
    print(f"Validation artifact: {out_path}")
    return result

if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] == "VALIDATED" else 1)
