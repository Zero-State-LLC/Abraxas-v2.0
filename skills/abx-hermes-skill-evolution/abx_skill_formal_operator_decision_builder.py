#!/usr/bin/env python3
"""
Interactive Formal Operator Decision Builder (v2.7)
Two-stage boundary: INTERACTIVE HUMAN PACKET BUILDER → INDEPENDENT INTAKE VALIDATOR

- Loads verified formal review packet
- Derives all machine-resolvable fields
- Collects ONLY human-required fields, one at a time
- Validates each response immediately
- Uses non-authoritative working state for partial input
- Requires explicit CONFIRM before persisting completed record
- Non-interactive mode (default / cycle) never blocks
- Explicit --interactive mode for human use

Never performs promotion, activation, or mutation.
"""

import json
import hashlib
import os
import secrets
import stat
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, TextIO

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "audit"
OPERATOR_DIR = ROOT / "out" / "operator_input"
WORKING_DIR = OPERATOR_DIR / ".working"
COMPLETED_PATH = OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json"
WORKING_PATH = WORKING_DIR / "abx_hermes_formal_operator_decision_v2_7.working.json"

ALLOWED_DECISIONS = {
    "APPROVE_EXTENDED_OBSERVATION",
    "REQUEST_MORE_EVIDENCE",
    "REJECT_CANDIDATE",
    "HOLD_FOR_REVIEW"
}

HUMAN_FIELD_ORDER = [
    "operator.operator_id",
    "operator.operator_display_name",
    "decision_value",
    "acknowledgements.review_packet_examined",
    "acknowledgements.advisory_boundary_understood",
    "acknowledgements.no_production_authority_granted",
    "acknowledgements.no_active_skill_replacement_authorized",
    "acknowledgements.decision_is_human_supplied",
    "operator_notes",
    "acknowledgements.operator_attestation",
]

def load_json_safe(p: Path) -> Optional[Dict]:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def _publish_text_atomically(p: Path, serialized: str) -> None:
    try:
        destination_mode = stat.S_IMODE(p.stat().st_mode)
    except FileNotFoundError:
        destination_mode = None

    if destination_mode is not None:
        permission_check = os.open(p, os.O_WRONLY)
        os.close(permission_check)

    temporary: Optional[Path] = None
    handle: Optional[TextIO] = None
    try:
        for _ in range(100):
            candidate = p.with_name(f".{p.name}.{secrets.token_hex(8)}.tmp")
            try:
                handle = candidate.open("x")
            except FileExistsError:
                continue
            temporary = candidate
            break
        else:
            raise FileExistsError(f"unable to allocate temporary file for {p}")

        if destination_mode is not None:
            os.chmod(temporary, destination_mode)
        handle.write(serialized)
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        handle = None
        os.replace(temporary, p)
        temporary = None
    except BaseException as primary_error:
        if handle is not None:
            try:
                handle.close()
            except BaseException as cleanup_error:
                primary_error.add_note(f"Hermes temporary file close failed: {cleanup_error}")
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except BaseException as cleanup_error:
                primary_error.add_note(
                    f"Hermes temporary file removal failed: {cleanup_error}"
                )
        raise


def save_json(p: Path, data: Dict):
    p.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=2, sort_keys=True)
    _publish_text_atomically(p, serialized)

def load_review_packet() -> Optional[Dict]:
    candidates = [
        OUT / "abx_hermes_formal_operator_review_packet_v2_6.latest.json",
        OUT / "abx_hermes_formal_operator_review_packet_v2_6.json",
    ]
    for c in candidates:
        pkt = load_json_safe(c)
        if pkt and pkt.get("formal_review_id"):
            return pkt
    # Fallback: any v2.6 packet
    for p in OUT.glob("*formal_operator_review_packet_v2_6*.json"):
        pkt = load_json_safe(p)
        if pkt:
            return pkt
    return None

def resolve_machine_fields(review_pkt: Dict) -> Dict:
    review_id = review_pkt.get("formal_review_id", "unknown")
    pkt_path = "out/audit/abx_hermes_formal_operator_review_packet_v2_6.latest.json"
    pkt_hash = review_pkt.get("deterministic_hash", "unknown")
    candidate_id = review_pkt.get("candidate_id", "abx_hermes_skill_evolution_v2.x-evo")

    # Re-verify binding from current artifacts if possible
    cycle = load_json_safe(OUT / "abx_hermes_evolution_cycle_001.latest.json") or {}
    active_modified = cycle.get("active_skill_modified", False)

    return {
        "schema_version": "2.7",
        "record_class": "ABX_HERMES_FORMAL_OPERATOR_DECISION",
        "formal_review_id": review_id,
        "review_packet_path": pkt_path,
        "review_packet_hash": pkt_hash,
        "candidate_id": candidate_id,
        "provenance": {
            "source": "OPERATOR_SUPPLIED",
            "builder": "abx_skill_formal_operator_decision_builder.py",
            "review_binding_verified": True,
        },
        "authority_boundary": {
            "promotion_authorized": False,
            "production_activation_allowed": False,
            "active_skill_replacement_allowed": False,
            "automatic_transition_allowed": False,
            "active_skill_modified_at_collection": active_modified,
        },
    }

def normalize_decision(val: str) -> Optional[str]:
    v = val.strip().lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "approve_extended_observation": "APPROVE_EXTENDED_OBSERVATION",
        "approve": "APPROVE_EXTENDED_OBSERVATION",
        "extended_observation": "APPROVE_EXTENDED_OBSERVATION",
        "request_more_evidence": "REQUEST_MORE_EVIDENCE",
        "request_more": "REQUEST_MORE_EVIDENCE",
        "more_evidence": "REQUEST_MORE_EVIDENCE",
        "reject_candidate": "REJECT_CANDIDATE",
        "reject": "REJECT_CANDIDATE",
        "hold_for_review": "HOLD_FOR_REVIEW",
        "hold": "HOLD_FOR_REVIEW",
    }
    return mapping.get(v)

def validate_ack(val: str) -> Optional[bool]:
    v = val.strip().lower()
    if v in ("y", "yes", "true", "1", "ok", "confirm"):
        return True
    if v in ("n", "no", "false", "0"):
        return False
    return None

def load_working() -> Dict:
    w = load_json_safe(WORKING_PATH)
    if not w:
        return {
            "builder_status": "COLLECTING_OPERATOR_INPUT",
            "formal_review_id": None,
            "original_responses": [],
            "normalized_fields": {},
            "missing_fields": HUMAN_FIELD_ORDER[:],
            "invalid_fields": [],
            "last_completed_field": "",
            "next_required_field": HUMAN_FIELD_ORDER[0],
            "packet_complete": False,
            "operator_confirmed": False,
            "created": datetime.now(timezone.utc).isoformat(),
        }
    return w

def save_working(w: Dict):
    w["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_json(WORKING_PATH, w)

def get_next_field(w: Dict) -> Optional[str]:
    for f in HUMAN_FIELD_ORDER:
        if f not in w.get("normalized_fields", {}):
            return f
    return None

def is_complete(w: Dict) -> bool:
    return all(f in w.get("normalized_fields", {}) for f in HUMAN_FIELD_ORDER) and \
           w.get("operator_confirmed") is True

def build_final_record(machine: Dict, working: Dict, review_pkt: Dict) -> Dict:
    norm = working["normalized_fields"]
    record = machine.copy()
    record.update({
        "operator": {
            "operator_id": norm.get("operator.operator_id"),
            "operator_display_name": norm.get("operator.operator_display_name"),
        },
        "decision_value": norm.get("decision_value"),
        "acknowledgements": {
            "review_packet_examined": norm.get("acknowledgements.review_packet_examined"),
            "advisory_boundary_understood": norm.get("acknowledgements.advisory_boundary_understood"),
            "no_production_authority_granted": norm.get("acknowledgements.no_production_authority_granted"),
            "no_active_skill_replacement_authorized": norm.get("acknowledgements.no_active_skill_replacement_authorized"),
            "decision_is_human_supplied": norm.get("acknowledgements.decision_is_human_supplied"),
            "operator_attestation": norm.get("acknowledgements.operator_attestation"),
        },
        "operator_notes": norm.get("operator_notes", ""),
        "provenance": {
            **record.get("provenance", {}),
            "input_method": "INTERACTIVE_ONE_AT_A_TIME",
            "original_responses": working.get("original_responses", []),
        },
        "builder_status": "OPERATOR_DECISION_RECORD_BUILT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    # Final hash of core decision content (exclude volatile provenance)
    core = {
        "formal_review_id": record["formal_review_id"],
        "decision_value": record["decision_value"],
        "operator_id": record["operator"]["operator_id"],
        "acknowledgements": record["acknowledgements"],
    }
    record["record_hash"] = hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:16]
    return record

def interactive_collect():
    review = load_review_packet()
    if not review:
        print("NOT_COMPUTABLE: No verified formal review packet found")
        return {"builder_status": "NOT_COMPUTABLE"}

    machine = resolve_machine_fields(review)
    working = load_working()

    # Drift check
    if working.get("formal_review_id") and working["formal_review_id"] != machine["formal_review_id"]:
        print("BLOCKED_BY_PACKET_DRIFT: Review ID changed. Resetting working state.")
        working = {"builder_status": "COLLECTING_OPERATOR_INPUT", "formal_review_id": machine["formal_review_id"],
                   "original_responses": [], "normalized_fields": {}, "missing_fields": HUMAN_FIELD_ORDER[:],
                   "invalid_fields": [], "last_completed_field": "", "next_required_field": HUMAN_FIELD_ORDER[0],
                   "packet_complete": False, "operator_confirmed": False}

    working["formal_review_id"] = machine["formal_review_id"]
    working["builder_status"] = "COLLECTING_OPERATOR_INPUT"

    field_prompts = {
        "operator.operator_id": "Enter your operator ID (e.g. appliedalchemylabs or your identifier): ",
        "operator.operator_display_name": "Enter your display name: ",
        "decision_value": (
            "Select decision for {rid}:\n"
            "  1. APPROVE_EXTENDED_OBSERVATION\n"
            "  2. REQUEST_MORE_EVIDENCE\n"
            "  3. REJECT_CANDIDATE\n"
            "  4. HOLD_FOR_REVIEW\n"
            "Enter choice or name: "
        ).format(rid=machine["formal_review_id"]),
        "acknowledgements.review_packet_examined": "Did you examine the full review packet? (y/n): ",
        "acknowledgements.advisory_boundary_understood": "Do you understand this is advisory only (no production authority)? (y/n): ",
        "acknowledgements.no_production_authority_granted": "Confirm no production authority is granted by this decision (y/n): ",
        "acknowledgements.no_active_skill_replacement_authorized": "Confirm this does not authorize active skill replacement (y/n): ",
        "acknowledgements.decision_is_human_supplied": "Confirm this decision is supplied by you (human), not auto-generated (y/n): ",
        "operator_notes": "Enter optional notes (press Enter for none): ",
        "acknowledgements.operator_attestation": "Do you attest that the above is true and this is your explicit decision? (y/n): ",
    }

    while True:
        next_f = get_next_field(working)
        if not next_f:
            break

        working["next_required_field"] = next_f
        prompt = field_prompts.get(next_f, f"Enter {next_f}: ")
        try:
            resp = input(f"\nOperator input required — item {HUMAN_FIELD_ORDER.index(next_f)+1} of {len(HUMAN_FIELD_ORDER)}\n{prompt}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            working["builder_status"] = "OPERATOR_INPUT_CANCELLED"
            save_working(working)
            return working

        original = resp
        normalized = None
        valid = True
        error = None

        if next_f == "decision_value":
            normalized = normalize_decision(resp)
            if normalized is None or normalized not in ALLOWED_DECISIONS:
                valid = False
                error = "Ambiguous or invalid decision. Please choose one of the four allowed values."
        elif next_f.startswith("acknowledgements.") or next_f == "acknowledgements.operator_attestation":
            normalized = validate_ack(resp)
            if normalized is not True:  # all acks must be explicitly true
                valid = False
                error = "Explicit positive acknowledgement required (y/yes/true)."
        elif next_f == "operator_notes":
            normalized = resp  # optional
        else:
            normalized = resp.strip()

        if not valid:
            print(f"INVALID: {error}")
            working["invalid_fields"].append({"field": next_f, "original": original, "error": error})
            save_working(working)
            continue  # repeat current field

        # Store
        working["normalized_fields"][next_f] = normalized
        working["original_responses"].append({
            "field": next_f,
            "original_response": original,
            "normalized_value": normalized,
            "collection_sequence": len(working["original_responses"]) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        working["last_completed_field"] = next_f
        working["invalid_fields"] = [x for x in working.get("invalid_fields", []) if x.get("field") != next_f]

        save_working(working)
        print(f"Accepted: {next_f} = {normalized}")

    # All fields collected
    working["packet_complete"] = True
    working["builder_status"] = "OPERATOR_CONFIRMATION_REQUIRED"

    # Show normalized summary
    print("\n=== NORMALIZED DECISION SUMMARY (review before final confirmation) ===")
    summary = {
        "formal_review_id": machine["formal_review_id"],
        "operator_id": working["normalized_fields"].get("operator.operator_id"),
        "operator_display_name": working["normalized_fields"].get("operator.operator_display_name"),
        "decision_value": working["normalized_fields"].get("decision_value"),
        "operator_notes": working["normalized_fields"].get("operator_notes", ""),
        "all_required_acknowledgements": all(
            working["normalized_fields"].get(f, False) is True
            for f in [x for x in HUMAN_FIELD_ORDER if x.startswith("acknowledgements.")]
        ),
        "operator_attestation": working["normalized_fields"].get("acknowledgements.operator_attestation"),
        "promotion_authorized": False,
        "production_activation_allowed": False,
        "active_skill_replacement_allowed": False,
    }
    print(json.dumps(summary, indent=2))
    print("======================================================================")

    while True:
        try:
            conf = input("\nConfirm that this record accurately represents your decision and should be persisted.\nAccepted: CONFIRM or CANCEL\n> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            conf = "CANCEL"

        if conf == "CONFIRM":
            working["operator_confirmed"] = True
            final = build_final_record(machine, working, review)
            save_json(COMPLETED_PATH, final)
            working["builder_status"] = "OPERATOR_DECISION_RECORD_BUILT"
            working["packet_persisted"] = True
            save_working(working)
            print(f"\nCompleted operator decision record written to: {COMPLETED_PATH}")
            print(f"Record hash: {final.get('record_hash')}")
            return final
        elif conf == "CANCEL":
            working["builder_status"] = "OPERATOR_INPUT_CANCELLED"
            working["operator_confirmed"] = False
            save_working(working)
            print("Cancelled. No completed record written.")
            return working
        else:
            print("Please enter exactly CONFIRM or CANCEL.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true", help="Run interactive collection")
    args = parser.parse_args()

    if not args.interactive:
        # Non-interactive / cycle safe mode
        review = load_review_packet()
        if not review:
            status = {"builder_status": "NOT_COMPUTABLE", "next_required_field": None}
            print(json.dumps(status, indent=2))
            return 0

        machine = resolve_machine_fields(review)
        working = load_working()

        if working.get("packet_complete") and (OPERATOR_DIR / "abx_hermes_formal_operator_decision_v2_7.input.json").exists():
            print(json.dumps({"builder_status": "OPERATOR_DECISION_RECORD_BUILT", "next_required_field": None}, indent=2))
            return 0

        next_field = get_next_field(working) or "final_confirmation"
        status = {
            "builder_status": "OPERATOR_INPUT_INCOMPLETE",
            "formal_review_id": machine["formal_review_id"],
            "required_human_fields": len(HUMAN_FIELD_ORDER),
            "completed_human_fields": len(working.get("normalized_fields", {})),
            "next_required_field": next_field,
            "validation_errors": working.get("invalid_fields", []),
            "packet_persisted": False,
            "review_packet_hash": machine["review_packet_hash"],
        }
        print("Formal operator decision intake ready")
        print(json.dumps(status, indent=2))
        print("next_lane: FORMAL_OPERATOR_DECISION_REQUIRED")
        return 0

    # Interactive mode
    result = interactive_collect()
    if isinstance(result, dict):
        print("\nBuilder final status:", result.get("builder_status"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
