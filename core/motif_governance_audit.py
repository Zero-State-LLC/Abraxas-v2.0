from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.generated_artifact_registry import build_generated_artifact_registry

PATCH_ID = "PATCH-P38-MOTIF-GOVERNANCE-AUDIT-001"
SCHEMA_VERSION = "MotifGovernanceAudit.v1"
AUDIT_ID = "motif_governance_audit_001"

STATUSES = {"PASS", "WARN", "FAIL", "NOT_COMPUTABLE"}
POSTURES = {"CLEAN", "WARNING", "FAILED", "NOT_COMPUTABLE"}

ALLOWED_MOTIF_CLASSES = {
    "BLOCKER_CLASS",
    "DEGRADATION_VECTOR",
    "CORRIDOR_PRESSURE",
    "CLIMATOLOGY_COUNT",
    "OVERLAY_LINEAGE",
}

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "audit_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "projection_only": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
    "readiness_claims_allowed": False,
    "motif_learning_authority": False,
    "adaptive_ontology_mutation_allowed": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "ui_command_authority": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
}

_DENY_KEYS = [k for k, v in _GOVERNANCE_FLAGS.items() if v is False]
_AFFIRM_KEYS = ["advisory_only", "projection_only", "non_authoritative"]


def _load_json(path: str | Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _src_paths(paths: RuntimePaths) -> dict[str, str]:
    return {
        "pressure_motif_registry": paths.pressure_motif_registry_latest.as_posix(),
        "aal_viz_pressure_motif_overlay": paths.aal_viz_pressure_motif_overlay_latest.as_posix(),
    }


def _finding(severity: str, category: str, message: str, evidence_refs: list[str]) -> dict[str, Any]:
    refs = sorted(str(x) for x in evidence_refs)
    raw = f"{category}|{message.strip()}|{'|'.join(refs)}"
    fid = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return {
        "finding_id": f"finding.{category.lower()}.{fid}",
        "severity": severity,
        "category": category,
        "message": message.strip(),
        "evidence_refs": refs,
    }


def _motif_hash_valid(motif: dict[str, Any]) -> bool:
    clone = {k: v for k, v in motif.items() if k != "motif_hash"}
    return str(motif.get("motif_hash", "")) == canonical_hash(clone)


def build_motif_governance_audit_receipt(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    sources = source_artifact_paths or _src_paths(paths)

    loaded: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}
    findings: list[dict[str, Any]] = []

    for key, path in sorted(sources.items()):
        payload, status = _load_json(path)
        loaded[key] = payload
        source_status[key] = status
        if status != "PRESENT":
            findings.append(_finding("FAIL", "SOURCE", f"required source {key} is {status.lower()}", [path]))

    if source_packets:
        for key, payload in source_packets.items():
            loaded[key] = deepcopy(payload)
            source_status[key] = "PRESENT"

    registry = loaded.get("pressure_motif_registry") or {}
    overlay = loaded.get("aal_viz_pressure_motif_overlay") or {}

    motifs = registry.get("motif_catalog", []) if isinstance(registry.get("motif_catalog", []), list) else None
    if motifs is None:
        findings.append(_finding("FAIL", "MOTIF_INTEGRITY", "motif_catalog missing or not a list", ["pressure_motif_registry.motif_catalog"]))
        motifs = []

    motif_ids = [str(m.get("motif_id", "")) for m in motifs if isinstance(m, dict)]
    if motif_ids != sorted(motif_ids):
        findings.append(_finding("FAIL", "MOTIF_INTEGRITY", "motif_id sequence is not sorted deterministically", ["pressure_motif_registry.motif_catalog.motif_id"]))

    motif_class_counts: dict[str, int] = {}
    reg_classes: set[str] = set()
    for m in motifs:
        if not isinstance(m, dict):
            findings.append(_finding("FAIL", "MOTIF_INTEGRITY", "motif entry is not an object", ["pressure_motif_registry.motif_catalog"]))
            continue
        klass = str(m.get("motif_class", ""))
        reg_classes.add(klass)
        motif_class_counts[klass] = motif_class_counts.get(klass, 0) + 1
        if klass not in ALLOWED_MOTIF_CLASSES:
            findings.append(_finding("FAIL", "MOTIF_INTEGRITY", f"motif class {klass} outside allowed enum", [f"motif:{m.get('motif_id', '')}"]))
        if not _motif_hash_valid(m):
            findings.append(_finding("FAIL", "HASH_INTEGRITY", f"motif hash mismatch for {m.get('motif_id', '')}", [f"motif:{m.get('motif_id', '')}"]))

    if motif_class_counts != (registry.get("motif_class_counts") or {}):
        findings.append(_finding("FAIL", "MOTIF_INTEGRITY", "motif_class_counts does not align with motif_catalog", ["pressure_motif_registry.motif_class_counts"]))

    refs = [str(x) for x in registry.get("motif_evidence_refs", [])]
    if refs != sorted(set(refs)):
        findings.append(_finding("FAIL", "MOTIF_INTEGRITY", "motif_evidence_refs not sorted/deduplicated", ["pressure_motif_registry.motif_evidence_refs"]))

    if not isinstance(registry.get("source_hash_lineage"), dict):
        findings.append(_finding("FAIL", "MOTIF_INTEGRITY", "registry source_hash_lineage missing or not object", ["pressure_motif_registry.source_hash_lineage"]))

    # hash integrity for full packets
    if isinstance(registry, dict) and "registry_hash" in registry:
        clone = deepcopy(registry)
        claimed = str(clone.pop("registry_hash", ""))
        if claimed != canonical_hash(clone):
            findings.append(_finding("FAIL", "HASH_INTEGRITY", "registry_hash mismatch", ["pressure_motif_registry.registry_hash"]))

    if isinstance(overlay, dict) and "overlay_hash" in overlay:
        clone = deepcopy(overlay)
        claimed = str(clone.pop("overlay_hash", ""))
        if claimed != canonical_hash(clone):
            findings.append(_finding("FAIL", "HASH_INTEGRITY", "overlay_hash mismatch", ["aal_viz_pressure_motif_overlay.overlay_hash"]))

    overlay_ids = set()
    overlay_classes = set()
    for section in ("overlay_nodes", "overlay_cards", "overlay_badges"):
        entries = overlay.get(section, [])
        if not isinstance(entries, list):
            findings.append(_finding("FAIL", "OVERLAY_INTEGRITY", f"{section} missing or not list", [f"aal_viz_pressure_motif_overlay.{section}"]))
            continue
        for e in entries:
            if not isinstance(e, dict):
                continue
            mid = str(e.get("motif_id", ""))
            mclass = str(e.get("motif_class", ""))
            if mid:
                overlay_ids.add(mid)
            if mclass:
                overlay_classes.add(mclass)

    unknown_ids = sorted(x for x in overlay_ids if x not in set(motif_ids))
    if unknown_ids:
        findings.append(_finding("FAIL", "OVERLAY_INTEGRITY", "overlay references unknown motif IDs", unknown_ids))

    unknown_classes = sorted(x for x in overlay_classes if x not in reg_classes)
    if unknown_classes:
        findings.append(_finding("FAIL", "OVERLAY_INTEGRITY", "overlay includes motif classes absent from registry", unknown_classes))

    # governance
    for packet_name, packet in (("p36", registry), ("p37", overlay)):
        g = packet.get("governance_flags", {}) if isinstance(packet, dict) else {}
        for key in _DENY_KEYS:
            if bool(g.get(key, False)):
                findings.append(_finding("FAIL", "GOVERNANCE", f"{packet_name} governance flag {key} must be false", [f"{packet_name}.governance_flags.{key}"]))
        for key in _AFFIRM_KEYS:
            if not bool(g.get(key, False)):
                findings.append(_finding("FAIL", "GOVERNANCE", f"{packet_name} governance flag {key} must be true", [f"{packet_name}.governance_flags.{key}"]))

    # registry classification
    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry_map = {e.artifact_path: e for e in reg.entries}
    required_optional = [
        "out/projections/pressure_motif_registry_001.latest.json",
        "out/projections/aal_viz_pressure_motif_overlay_001.latest.json",
    ]
    for p in required_optional:
        e = entry_map.get(p)
        if e is None:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"missing generated artifact registry entry: {p}", [p]))
        elif e.determinism_class not in {"DERIVED_OPTIONAL", "AUDIT_VOLATILE"}:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"unexpected determinism class for {p}: {e.determinism_class}", [p]))

    nc = any(source_status.get(k) != "PRESENT" for k in ("pressure_motif_registry", "aal_viz_pressure_motif_overlay"))
    fail_count = sum(1 for f in findings if f["severity"] == "FAIL")
    warn_count = sum(1 for f in findings if f["severity"] == "WARN")

    if nc:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif fail_count:
        final_status, posture = "FAIL", "FAILED"
    elif warn_count:
        final_status, posture = "WARN", "WARNING"
    else:
        final_status, posture = "PASS", "CLEAN"
        findings.append(_finding("PASS", "SOURCE", "all required motif governance inputs were readable", list(sources.values())))

    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    findings = sorted(findings, key=lambda x: (order.get(str(x["severity"]), 9), str(x["category"]), str(x["finding_id"])))

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": posture,
        "checked_artifacts": sources,
        "findings": findings,
        "finding_counts": {
            "PASS": sum(1 for f in findings if f["severity"] == "PASS"),
            "WARN": warn_count,
            "FAIL": fail_count,
        },
        "motif_integrity_summary": {
            "motif_count": len(motif_ids),
            "registered_motif_classes": sorted(reg_classes),
            "motif_ids_sorted": motif_ids == sorted(motif_ids),
        },
        "overlay_integrity_summary": {
            "overlay_motif_id_count": len(overlay_ids),
            "unknown_overlay_motif_ids": unknown_ids,
            "unknown_overlay_motif_classes": unknown_classes,
        },
        "governance_integrity_summary": {
            "required_deny_flags": sorted(_DENY_KEYS),
            "required_affirm_flags": sorted(_AFFIRM_KEYS),
        },
        "registry_classification_summary": {
            "expected_non_ci_drift_enforced": required_optional,
        },
        "source_hashes": {k: (canonical_hash(v) if isinstance(v, dict) else "NOT_COMPUTABLE") for k, v in sorted(loaded.items())},
        "blocker_summary": sorted(f["message"] for f in findings if f["severity"] == "FAIL"),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "audit_only": True,
            "advisory_only": True,
            "non_authoritative": True,
            "fail_closed": True,
        },
    }
    packet["audit_hash"] = canonical_hash(packet)
    return packet


def build_motif_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P38 Motif Governance Audit Receipt",
        "",
        f"- audit_id: `{packet['audit_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- audit_posture: `{packet['audit_posture']}`",
        f"- findings_fail: `{packet.get('finding_counts', {}).get('FAIL', 0)}`",
        f"- findings_warn: `{packet.get('finding_counts', {}).get('WARN', 0)}`",
        "",
        "## Findings",
    ]
    findings = packet.get("findings", [])
    if findings:
        for f in findings:
            lines.append(f"- `{f['severity']}` `{f['category']}` {f['message']}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_motif_governance_audit_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_motif_governance_audit_markdown(packet), encoding="utf-8")
