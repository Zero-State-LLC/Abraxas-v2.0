from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash, write_canonical_json

ARTIFACT_TYPE = "static_archive_package_index_pointer_receipt"
SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageIndexPointerReceipt.v1"
PATCH_ID = "PATCH-P69-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-INDEX-POINTER-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_index_pointer_receipt_001"
DETERMINISTIC_GENERATED_AT = "1970-01-01T00:00:00Z"
EXPECTED_ORDER = ["P64", "P65", "P66", "P67", "P68"]

FORBIDDEN_TOKENS = ("release", "distribution", "readiness")


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    try:
        txt = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "MISSING", ""
    except OSError:
        return None, "CORRUPT", ""
    try:
        data = json.loads(txt)
    except json.JSONDecodeError:
        return None, "CORRUPT", txt
    return (data if isinstance(data, dict) else None), ("PRESENT" if isinstance(data, dict) else "CORRUPT"), txt


def build_operator_narrative_static_archive_package_index_pointer_receipt_packet(*,
    p64_json_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.json",
    p65_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
    p66_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
    p67_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
    p68_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
    upstream_packets: dict[str, dict[str, Any]] | None = None,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    refs = {
        "P64": root / Path(p64_json_path),
        "P65": root / Path(p65_json_path),
        "P66": root / Path(p66_json_path),
        "P67": root / Path(p67_json_path),
        "P68": root / Path(p68_json_path),
    }
    loaded: dict[str, dict[str, Any] | None] = {}
    raw: dict[str, str] = {}
    source_state: dict[str, str] = {}
    blockers: list[str] = []

    for sid, path in refs.items():
        if upstream_packets is not None:
            if sid in upstream_packets:
                obj = deepcopy(upstream_packets[sid])
                loaded[sid], raw[sid], source_state[sid] = obj, canonical_dumps(obj), "PRESENT"
            else:
                loaded[sid], raw[sid], source_state[sid] = None, "", "MISSING"
        else:
            obj, state, txt = _read_json(path)
            loaded[sid], raw[sid], source_state[sid] = obj, txt, state

    if any(source_state[sid] != "PRESENT" or loaded[sid] is None for sid in EXPECTED_ORDER):
        blockers.extend([f"{sid} missing/corrupt" for sid in EXPECTED_ORDER if source_state[sid] != "PRESENT" or loaded[sid] is None])

    ordered_pointers: list[dict[str, Any]] = []
    for sid in EXPECTED_ORDER:
        pkt = loaded.get(sid) or {}
        src_txt = raw.get(sid, "")
        status = str(pkt.get("final_status", "NOT_COMPUTABLE"))
        posture = str(pkt.get("closure_posture", pkt.get("stability_posture", pkt.get("audit_posture", "NOT_COMPUTABLE"))))
        if not src_txt or "final_status" not in pkt:
            blockers.append(f"{sid} required hash/status fields absent")
        if sid in {"P67", "P68"} and "posture" not in " ".join(pkt.keys()).lower() and sid == "P68" and "closure_posture" not in pkt:
            blockers.append(f"{sid} required posture fields absent")
        ordered_pointers.append({
            "surface_id": sid,
            "artifact_role": "static_archive_package",
            "artifact_path": refs[sid].as_posix(),
            "artifact_hash": hashlib.sha256(src_txt.encode("utf-8")).hexdigest() if src_txt else "NOT_COMPUTABLE",
            "status": status,
            "posture": posture,
            "governance_role": "read_only_reference",
        })

    pointer_order = [p["surface_id"] for p in ordered_pointers]
    if pointer_order != EXPECTED_ORDER:
        blockers.append("pointer order drift")
    if len({p["surface_id"] for p in ordered_pointers}) != len(ordered_pointers):
        blockers.append("duplicate surface_id")
    if len({p["artifact_path"] for p in ordered_pointers}) != len(ordered_pointers):
        blockers.append("duplicate artifact_path")

    p68 = loaded.get("P68") or {}
    if p68.get("final_status") != "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED":
        blockers.append("P68 closure state not preserved")
    if p68.get("closure_posture") != "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSED_WITH_OBSERVED_BLOCKERS":
        blockers.append("P68 closure posture not preserved")

    p64_b = ((loaded.get("P64") or {}).get("blocker_preservation_summary") or {})
    p67_b = ((loaded.get("P67") or {}).get("blocker_preservation_summary") or {})
    p68_b = ((loaded.get("P68") or {}).get("blocker_preservation_summary") or {})
    if p64_b != p67_b or p67_b != p68_b:
        blockers.append("blocker preservation mismatch")

    governance_flags = {
        "receipt_only": True, "read_only": True, "non_authoritative": True, "deterministic": True,
        "advisory_only": True, "pointer_only": True, "compact_reference_only": True,
        "package_creation": False, "package_mutation": False, "payload_duplication": False,
        "distribution": False, "publishing": False, "release_readiness": False,
        "command_authority": False, "action_authority": False, "execution_authority": False,
        "runtime_mutation": False, "forecast_influence": False, "canon_promotion": False,
    }
    for k, v in governance_flags.items():
        if k in {"receipt_only", "read_only", "non_authoritative", "deterministic", "advisory_only", "pointer_only", "compact_reference_only"}:
            if v is not True:
                blockers.append(f"governance invariant false: {k}")
        elif v is not False:
            blockers.append(f"forbidden capability flag true: {k}")

    upstream_blob = "\n".join(raw.values()).lower()
    if any((f"{token} readiness" in upstream_blob or f"{token} ready" in upstream_blob) for token in FORBIDDEN_TOKENS):
        blockers.append("release/distribution/readiness semantics detected")

    fail_upstream = any((loaded.get(s) or {}).get("final_status", "").endswith("_FAIL") for s in ["P65", "P66", "P67", "P68"])
    degraded = bool((p68_b or {}).get("observed_degraded_roles")) or int((p68_b or {}).get("observed_blocker_count", 0) or 0) > 0

    if any(source_state[sid] != "PRESENT" or loaded[sid] is None for sid in EXPECTED_ORDER):
        final_status = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_NOT_COMPUTABLE"
        index_posture = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_NOT_COMPUTABLE"
    elif blockers or fail_upstream:
        final_status = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_FAIL"
        index_posture = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_UNSTABLE"
    elif degraded:
        final_status = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_DEGRADED"
        index_posture = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_STABLE_WITH_OBSERVED_BLOCKERS"
    else:
        final_status = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_PASS"
        index_posture = "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_STABLE"

    packet = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "final_status": final_status,
        "index_posture": index_posture,
        "pointer_count": len(ordered_pointers),
        "ordered_surface_ids": pointer_order,
        "ordered_pointers": ordered_pointers,
        "blocker_preservation_summary": deepcopy(p68_b),
        "p68_closure_state_preserved": p68.get("final_status") == "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED",
        "p68_closure_posture_preserved": p68.get("closure_posture") == "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSED_WITH_OBSERVED_BLOCKERS",
        "governance_flags": governance_flags,
        "broken_surface_ledger": sorted(set(blockers)),
        "provenance": {"deterministic": True, "read_only": True, "non_authoritative": True, "pointer_only": True, "source_linked": True},
    }
    packet["index_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_index_pointer_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P69 Static Archive Package Index Pointer Receipt", "",
        f"- final_status: `{packet.get('final_status','')}`",
        f"- index_posture: `{packet.get('index_posture','')}`",
        f"- index_hash: `{packet.get('index_hash','')}`",
        f"- pointer_count: `{packet.get('pointer_count', 0)}`", "",
        "## Ordered Surface IDs",
    ]
    lines.extend([f"- `{s}`" for s in packet.get("ordered_surface_ids", [])])
    lines.extend(["", "## Referenced Artifact Paths"])
    lines.extend([f"- `{p.get('surface_id')}` -> `{p.get('artifact_path')}`" for p in packet.get("ordered_pointers", [])])
    lines.extend(["", "## Blocker Preservation State", f"- `{packet.get('blocker_preservation_summary', {})}`", "", "## Governance Denial Flags"])
    for k, v in (packet.get("governance_flags") or {}).items():
        if v is False:
            lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Broken Surface Ledger"])
    ledger = packet.get("broken_surface_ledger", [])
    lines.extend([f"- `{x}`" for x in ledger] if ledger else ["- none"])
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_index_pointer_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_index_pointer_receipt_markdown(packet), encoding="utf-8")
