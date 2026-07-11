#!/usr/bin/env python3
"""
Formal Operator Decision Ledger (v2.9)
Consumes validated operator decision + review packet.
Emits a traceable decision ledger for promotion eligibility surfaces.
Advisory / SHADOW only. Never mutates active skill or grants authority.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("out/audit")
OPERATOR_DIR = Path("out/operator_input")
DECISION_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"
VALIDATION_PATH = OUT / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json"
REVIEW_PATH = OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json"

def main():
    decision = json.loads(DECISION_PATH.read_text()) if DECISION_PATH.exists() else {}
    validation = json.loads(VALIDATION_PATH.read_text()) if VALIDATION_PATH.exists() else {}
    review = json.loads(REVIEW_PATH.read_text()) if REVIEW_PATH.exists() else {}

    ledger = {
        "schema_version": "2.9",
        "ledger_class": "ABX_HERMES_FORMAL_OPERATOR_DECISION_LEDGER",
        "formal_review_id": decision.get("formal_review_id") or review.get("formal_review_id"),
        "decision_value": decision.get("decision_value"),
        "operator_id": decision.get("operator", {}).get("operator_id"),
        "validation_status": validation.get("status"),
        "validation_errors": validation.get("errors", []),
        "operator_decision_present": bool(decision.get("decision_value")),
        "operator_decision_validated": validation.get("status") == "VALIDATED",
        "review_packet_binding": {
            "review_id_match": decision.get("formal_review_id") == review.get("formal_review_id"),
            "packet_hash_match": decision.get("review_packet_hash") == review.get("deterministic_hash"),
        },
        "authority": {
            "advisory_only": True,
            "promotion_authorized": False,
            "production_activation_allowed": False,
            "active_skill_replacement_allowed": False,
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    out_path = OUT / "abx_hermes_formal_operator_decision_ledger_v2_9.latest.json"
    out_path.write_text(json.dumps(ledger, indent=2))

    print(f"Decision ledger emitted: {out_path}")
    print(f"Decision value: {ledger['decision_value']}")
    print(f"Validation status: {ledger['validation_status']}")
    return ledger

if __name__ == "__main__":
    main()
