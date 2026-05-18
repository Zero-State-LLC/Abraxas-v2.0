from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.generated_artifact_registry import build_generated_artifact_registry

PATCH_ID = "PATCH-P41-FUSION-GOVERNANCE-AUDIT-001"
SCHEMA_VERSION = "FusionGovernanceAudit.v1"
AUDIT_ID = "fusion_governance_audit_001"

_ALLOWED_STATUSES = {"PASS", "WARN", "FAIL", "NOT_COMPUTABLE"}
_ALLOWED_POSTURES = {"CLEAN", "WARNING", "FAILED", "NOT_COMPUTABLE"}

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "audit_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "inference_authority": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "adaptive_behavior_allowed": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "ui_command_authority": False,
    "psychological_claims_allowed": False,
    "speculative_causation_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
}

_DENY_KEYS = [
    "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed",
    "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed",
    "canon_mutation_allowed", "runtime_mutation_allowed", "ui_command_authority", "adaptive_behavior_allowed",
    "psychological_claims_allowed", "speculative_causation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control",
]
_AFFIRM_KEYS = ["advisory_only", "projection_only", "fusion_overlay_only", "render_consumer_only", "non_authoritative"]


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
        "aal_viz_operator_climate_overlay": paths.aal_viz_operator_climate_overlay_latest.as_posix(),
        "aal_viz_pressure_motif_overlay": paths.aal_viz_pressure_motif_overlay_latest.as_posix(),
        "operator_load_seasonality": paths.operator_load_seasonality_latest.as_posix(),
        "aal_viz_climate_motif_fusion_overlay": paths.aal_viz_climate_motif_fusion_overlay_latest.as_posix(),
    }


def _finding(severity: str, category: str, message: str, evidence_refs: list[str]) -> dict[str, Any]:
    refs = sorted(str(r) for r in evidence_refs)
    fid = hashlib.sha256(f"{category}|{message.strip()}|{'|'.join(refs)}".encode("utf-8")).hexdigest()[:16]
    return {
        "finding_id": f"finding.{category.lower()}.{fid}",
        "severity": severity,
        "category": category,
        "message": message.strip(),
        "evidence_refs": refs,
    }


def _check_sorted(items: Any, key: str) -> bool:
    if not isinstance(items, list):
        return False
    ids = [str(x.get(key, "")) for x in items if isinstance(x, dict)]
    return ids == sorted(ids)


def _check_prefix(items: Any, key: str, prefix: str) -> bool:
    if not isinstance(items, list):
        return False
    return all(isinstance(x, dict) and str(x.get(key, "")).startswith(prefix) for x in items)


def _check_no_dupes(items: Any, key: str) -> bool:
    if not isinstance(items, list):
        return False
    ids = [str(x.get(key, "")) for x in items if isinstance(x, dict)]
    return len(ids) == len(set(ids))


def build_fusion_governance_audit_receipt(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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

    p40 = loaded.get("aal_viz_climate_motif_fusion_overlay") or {}

    # Namespace + collision checks
    collections = [
        ("render_layers", "layer_id"),
        ("overlay_nodes", "node_id"),
        ("overlay_cards", "card_id"),
        ("overlay_badges", "badge_id"),
        ("overlay_edges", "edge_id"),
    ]
    for section, key in collections:
        entries = p40.get(section, [])
        if not isinstance(entries, list):
            findings.append(_finding("FAIL", "NAMESPACE", f"{section} missing or not list", [f"p40.{section}"]))
            continue
        if not _check_no_dupes(entries, key):
            findings.append(_finding("FAIL", "NAMESPACE", f"duplicate {key} values in {section}", [f"p40.{section}.{key}"]))
        if not _check_sorted(entries, key):
            findings.append(_finding("FAIL", "PRIMITIVE_ORDERING", f"{section} not sorted by {key}", [f"p40.{section}.{key}"]))

    if not _check_prefix(p40.get("render_layers", []), "layer_id", "climate.") and not all(str(x.get("layer_id", "")).startswith(("climate.", "motif.", "seasonality.")) for x in p40.get("render_layers", []) if isinstance(x, dict)):
        findings.append(_finding("FAIL", "NAMESPACE", "render_layers must use climate./motif./seasonality. prefixes", ["p40.render_layers.layer_id"]))

    if not all(str(x.get("node_id", "")).startswith(("climate.", "motif.", "seasonality.")) for x in p40.get("overlay_nodes", []) if isinstance(x, dict)):
        findings.append(_finding("FAIL", "NAMESPACE", "overlay_nodes must use climate./motif./seasonality. prefixes", ["p40.overlay_nodes.node_id"]))

    if not all(str(x.get("edge_id", "")).startswith(("climate.", "motif.", "fusion.edge.")) for x in p40.get("overlay_edges", []) if isinstance(x, dict)):
        findings.append(_finding("FAIL", "NAMESPACE", "overlay_edges must use climate./motif./fusion.edge. prefixes", ["p40.overlay_edges.edge_id"]))

    node_ids = {str(x.get("node_id", "")) for x in p40.get("overlay_nodes", []) if isinstance(x, dict)}
    for edge in p40.get("overlay_edges", []) if isinstance(p40.get("overlay_edges", []), list) else []:
        if not isinstance(edge, dict):
            continue
        for ref_key in ("source_node_id", "target_node_id"):
            ref = str(edge.get(ref_key, ""))
            if not ref:
                findings.append(_finding("FAIL", "EDGE_INTEGRITY", f"edge missing {ref_key}", ["p40.overlay_edges"]))
                continue
            if ref not in node_ids and not ref.startswith(("node.evidence.", "lineage.")):
                findings.append(_finding("FAIL", "EDGE_INTEGRITY", f"edge reference {ref_key} unresolved: {ref}", ["p40.overlay_edges"]))
            if any(tok in ref.lower() for tok in ("command", "mutat", "execute", "action")):
                findings.append(_finding("FAIL", "EDGE_INTEGRITY", f"edge reference {ref_key} targets forbidden command/mutation namespace", ["p40.overlay_edges"]))

    lineage = p40.get("source_hash_lineage", {})
    for required in ("p35_overlay_hash", "p37_overlay_hash", "p39_seasonality_hash"):
        if not isinstance(lineage, dict) or str(lineage.get(required, "")).strip() in {"", "NOT_COMPUTABLE"}:
            findings.append(_finding("FAIL", "LINEAGE", f"missing required lineage ref {required}", ["p40.source_hash_lineage"]))

    for required in ("aal_viz_operator_climate_overlay", "aal_viz_pressure_motif_overlay", "operator_load_seasonality", "aal_viz_climate_motif_fusion_overlay"):
        if required not in p40.get("source_hashes", {}):
            findings.append(_finding("FAIL", "LINEAGE", f"missing source_hashes entry {required}", ["p40.source_hashes"]))

    if isinstance(p40, dict) and "fusion_hash" in p40:
        clone = deepcopy(p40)
        claimed = str(clone.pop("fusion_hash", ""))
        recomputed = canonical_hash(clone)
        if claimed != recomputed:
            findings.append(_finding("FAIL", "HASH_INTEGRITY", "fusion_hash mismatch", ["p40.fusion_hash"]))
    else:
        findings.append(_finding("WARN", "HASH_INTEGRITY", "fusion_hash missing; unable to fully verify hash integrity", ["p40.fusion_hash"]))

    g = p40.get("governance_flags", {}) if isinstance(p40, dict) else {}
    for key in _DENY_KEYS:
        if bool(g.get(key, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance flag {key} must be false", [f"p40.governance_flags.{key}"]))
    for key in _AFFIRM_KEYS:
        if not bool(g.get(key, False)):
            findings.append(_finding("FAIL", "GOVERNANCE", f"governance flag {key} must be true", [f"p40.governance_flags.{key}"]))

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry_map = {e.artifact_path: e for e in reg.entries}
    required_optional = [
        "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json",
        "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.md",
    ]
    for p in required_optional:
        e = entry_map.get(p)
        if e is None:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"missing generated artifact registry entry: {p}", [p]))
        elif e.determinism_class not in {"DERIVED_OPTIONAL", "AUDIT_VOLATILE", "RUNTIME_VOLATILE"}:
            findings.append(_finding("FAIL", "REGISTRY_CLASSIFICATION", f"unexpected determinism class for {p}: {e.determinism_class}", [p]))

    nc = any(source_status.get(k) != "PRESENT" for k in sources)
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
        findings.append(_finding("PASS", "SOURCE", "all required fusion governance inputs were readable", list(sources.values())))

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
        "primitive_integrity_summary": {"collections_checked": [name for name, _ in collections]},
        "lineage_integrity_summary": {"required_lineage_keys": ["p35_overlay_hash", "p37_overlay_hash", "p39_seasonality_hash"]},
        "governance_integrity_summary": {"required_deny_flags": sorted(_DENY_KEYS), "required_affirm_flags": sorted(_AFFIRM_KEYS)},
        "registry_classification_summary": {"expected_non_ci_drift_enforced": required_optional},
        "namespace_integrity_summary": {"required_prefixes": ["climate.", "motif.", "seasonality.", "fusion.edge."]},
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
    if packet["final_status"] not in _ALLOWED_STATUSES or packet["audit_posture"] not in _ALLOWED_POSTURES:
        raise ValueError("invalid audit status/posture")
    packet["audit_hash"] = canonical_hash(packet)
    return packet


def build_fusion_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P41 Fusion Governance Audit Receipt",
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


def write_fusion_governance_audit_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_fusion_governance_audit_markdown(packet), encoding="utf-8")
