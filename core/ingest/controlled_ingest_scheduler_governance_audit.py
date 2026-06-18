from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry
from core.ingest.scheduler import (
    AUTHORITY,
    TARGET_PATCH_ID,
    build_scheduled_manifest,
    build_scheduler_receipt,
    decide_ingest_windows,
)

SCHEMA_VERSION = "ControlledIngestSchedulerGovernanceAudit.v1"
ARTIFACT_TYPE = SCHEMA_VERSION
PATCH_ID = "PATCH-ABX-AUTO-INGEST-002-GOVERNANCE-AUDIT-001"
AUDIT_ID = "controlled_ingest_scheduler_governance_audit_001"

_REQUIRED_TRUE_KEYS = ("advisory_only", "projection_only", "non_authoritative")
_REQUIRED_FALSE_KEYS = ("forecast_authority", "canon_mutation", "runtime_mutation", "execution_authority")
_REQUIRED_ARTIFACTS = {
    "scheduler_impl": "core/ingest/scheduler.py",
    "scheduler_runner": "Scripts/run_ingest_scheduler.py",
    "decision_contract": "contracts/ingest/ingest_window_decision_set.v1.schema.json",
    "manifest_contract": "contracts/ingest/scheduled_ingest_run_manifest.v1.schema.json",
    "receipt_contract": "contracts/ingest/scheduler_receipt.v1.schema.json",
}
_AUDIT_ARTIFACTS = (
    "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json",
    "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.md",
)


def _sample_adapter_config() -> dict[str, Any]:
    return {
        "adapters": [
            {"adapter_id": "abx_market_feed_v1", "domain": "finance", "enabled": True},
            {"adapter_id": "abx_geo_feed_v1", "domain": "geopolitics", "enabled": True},
        ]
    }


def _sample_policy() -> dict[str, Any]:
    return {
        "schema_version": "IngestWindowPolicy.v1",
        "policy_id": "abx_controlled_ingest_scheduler_v1",
        "timezone": "UTC",
        "global": {
            "min_seconds_between_runs": 300,
            "max_concurrent_adapters": 1,
            "quiet_window_enabled": True,
            "quiet_window": {"start_hour": 2, "end_hour": 5, "cadence_multiplier": 4.0},
        },
        "domain_policies": {
            "finance": {
                "base_cadence_seconds": 900,
                "min_cadence_seconds": 300,
                "max_cadence_seconds": 3600,
                "operator_window_required": False,
            },
            "geopolitics": {
                "base_cadence_seconds": 3600,
                "min_cadence_seconds": 1800,
                "max_cadence_seconds": 21600,
                "operator_window_required": True,
            },
        },
        "volatility_policy": {
            "enabled": True,
            "compression_thresholds": [{"metric": "z_score", "gte": 2.5, "cadence_multiplier": 0.5}],
            "expansion_thresholds": [{"metric": "z_score", "lt": 1.0, "cadence_multiplier": 2.0}],
        },
    }


def _sample_scheduler_state() -> dict[str, Any]:
    return {
        "schema_version": "SchedulerState.v1",
        "scheduler_id": "abx_controlled_ingest_scheduler_v1",
        "last_run_by_adapter": {},
        "last_decision_hash": None,
        "active_operator_windows": [],
        "cooldowns": {},
        "blocked_adapters": [],
    }


def _sample_anomaly_state() -> dict[str, Any]:
    return {
        "schema_version": "ShadowAnomalyState.v1",
        "generated_at": "2026-06-04T00:00:00Z",
        "domain_scores": {
            "finance": {"z_score": 3.0, "source": "fixture"},
            "geopolitics": {"z_score": 0.5, "source": "fixture"},
        },
    }


def _finding(severity: str, category: str, message: str, evidence_refs: list[str]) -> dict[str, Any]:
    refs = sorted(str(ref) for ref in evidence_refs)
    digest = hashlib.sha256(f"{severity}|{category}|{message}|{'|'.join(refs)}".encode("utf-8")).hexdigest()[:16]
    return {
        "finding_id": f"finding.{category.lower()}.{digest}",
        "severity": severity,
        "category": category,
        "message": message,
        "evidence_refs": refs,
    }


def _load_texts(repo_root: Path) -> tuple[dict[str, str], list[dict[str, Any]]]:
    texts: dict[str, str] = {}
    findings: list[dict[str, Any]] = []
    for key, rel_path in sorted(_REQUIRED_ARTIFACTS.items()):
        path = repo_root / rel_path
        try:
            texts[key] = path.read_text(encoding="utf-8")
        except OSError:
            findings.append(_finding("FAIL", "SOURCE", f"required source missing or unreadable: {rel_path}", [rel_path]))
    return texts, findings


def _build_packets(*, repo_root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    root = repo_root or Path(__file__).resolve().parents[2]
    decision_set = decide_ingest_windows(
        adapter_config_set=_sample_adapter_config(),
        window_policy=_sample_policy(),
        scheduler_state=_sample_scheduler_state(),
        anomaly_state=_sample_anomaly_state(),
        now_iso="2026-06-04T03:00:00Z",
    )
    manifest = build_scheduled_manifest(
        decision_set,
        max_concurrent_adapters=1,
        oracle_signal_module_present=(root / "core/oracle_signal.py").exists(),
    )
    receipt = build_scheduler_receipt(decision_set, manifest)
    return decision_set, manifest, receipt


def build_controlled_ingest_scheduler_governance_audit_packet(
    *,
    repo_root: Path | str = Path(__file__).resolve().parents[2],
) -> dict[str, Any]:
    root = Path(repo_root)
    texts, findings = _load_texts(root)

    if findings:
        packet = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": ARTIFACT_TYPE,
            "patch_id": PATCH_ID,
            "audit_id": AUDIT_ID,
            "final_status": "NOT_COMPUTABLE",
            "audit_posture": "NOT_COMPUTABLE",
            "checked_artifacts": deepcopy(_REQUIRED_ARTIFACTS),
            "source_hashes": {
                key: canonical_hash({"text": text}) for key, text in sorted(texts.items())
            },
            "authority_assertions": {},
            "boundary_assertions": {},
            "findings": sorted(findings, key=lambda item: (item["severity"], item["category"], item["finding_id"])),
            "finding_counts": {
                "PASS": 0,
                "FAIL": len(findings),
            },
            "recommended_next_step": "CONTROLLED_INGEST_SCHEDULER_SOURCE_REPAIR_REQUIRED",
            "recommended_next_step_reason": "A required scheduler source or contract surface is missing or unreadable.",
        }
        packet["audit_hash"] = canonical_hash(packet)
        return packet

    decision_set, manifest, receipt = _build_packets(repo_root=root)
    snapshots = {
        "decision_set": deepcopy(decision_set),
        "manifest": deepcopy(manifest),
        "receipt": deepcopy(receipt),
    }

    authority_assertions: dict[str, bool] = {}
    boundary_assertions: dict[str, bool | str] = {}

    for packet_name, packet in snapshots.items():
        for key in _REQUIRED_TRUE_KEYS:
            ok = packet.get(key) is True
            authority_assertions[f"{packet_name}.{key}"] = ok
            if not ok:
                findings.append(
                    _finding("FAIL", "GOVERNANCE", f"{packet_name} must set {key}=true", [f"{packet_name}.{key}"])
                )
        for key in _REQUIRED_FALSE_KEYS:
            ok = packet.get(key) is False
            authority_assertions[f"{packet_name}.{key}"] = ok
            if not ok:
                findings.append(
                    _finding("FAIL", "GOVERNANCE", f"{packet_name} must set {key}=false", [f"{packet_name}.{key}"])
                )

    boundary_assertions["decision_set.authority"] = decision_set.get("authority") == AUTHORITY
    if not boundary_assertions["decision_set.authority"]:
        findings.append(_finding("FAIL", "BOUNDARY", "decision_set authority must remain SHADOW_SCHEDULING_ONLY", ["decision_set.authority"]))

    boundary_assertions["receipt.authority"] = receipt.get("authority") == AUTHORITY
    if not boundary_assertions["receipt.authority"]:
        findings.append(_finding("FAIL", "BOUNDARY", "receipt authority must remain SHADOW_SCHEDULING_ONLY", ["receipt.authority"]))

    handoff = manifest.get("handoff", {})
    boundary_assertions["manifest.handoff.authority"] = handoff.get("authority") == "SHADOW_ONLY"
    if not boundary_assertions["manifest.handoff.authority"]:
        findings.append(_finding("FAIL", "BOUNDARY", "manifest handoff authority must remain SHADOW_ONLY", ["manifest.handoff.authority"]))

    boundary_assertions["manifest.handoff.target_pipeline"] = handoff.get("target_pipeline") == "abx_auto_ingest_v1"
    if not boundary_assertions["manifest.handoff.target_pipeline"]:
        findings.append(_finding("FAIL", "BOUNDARY", "manifest handoff target pipeline must remain abx_auto_ingest_v1", ["manifest.handoff.target_pipeline"]))

    boundary_assertions["manifest.handoff.target_patch"] = str(handoff.get("target_patch", ""))
    if boundary_assertions["manifest.handoff.target_patch"] != TARGET_PATCH_ID:
        findings.append(
            _finding(
                "FAIL",
                "BOUNDARY",
                f"manifest handoff target_patch must be {TARGET_PATCH_ID}",
                ["manifest.handoff.target_patch"],
            )
        )

    decisions = decision_set.get("decisions", [])
    decision_authority_ok = isinstance(decisions, list) and all(
        isinstance(row, dict) and row.get("authority") == AUTHORITY for row in decisions
    )
    boundary_assertions["decision_rows.authority"] = decision_authority_ok
    if not decision_authority_ok:
        findings.append(_finding("FAIL", "BOUNDARY", "every decision row must remain SHADOW_SCHEDULING_ONLY", ["decision_set.decisions.authority"]))

    boundary_assertions["scheduler_id_consistency"] = (
        decision_set.get("scheduler_id") == manifest.get("scheduler_id") == receipt.get("scheduler_id")
    )
    if not boundary_assertions["scheduler_id_consistency"]:
        findings.append(_finding("FAIL", "INTEGRITY", "scheduler_id must match across decision set, manifest, and receipt", ["decision_set.scheduler_id", "manifest.scheduler_id", "receipt.scheduler_id"]))

    registry = build_generated_artifact_registry(root)
    entry_map = {entry.artifact_path: entry for entry in registry.entries}
    for artifact in _AUDIT_ARTIFACTS:
        entry = entry_map.get(artifact)
        key = f"registry.{artifact}"
        ok = entry is not None and entry.determinism_class == "DERIVED_OPTIONAL"
        boundary_assertions[key] = ok
        if not ok:
            findings.append(_finding("FAIL", "REGISTRY", f"{artifact} must be classified as DERIVED_OPTIONAL", [artifact, "core/generated_artifact_registry.py"]))

    if not findings:
        findings.append(_finding("PASS", "GOVERNANCE", "controlled ingest scheduler authority locks and handoff boundaries are preserved", list(_REQUIRED_ARTIFACTS.values())))

    findings = sorted(findings, key=lambda item: ({"FAIL": 0, "PASS": 1}.get(item["severity"], 9), item["category"], item["finding_id"]))
    fail_count = sum(1 for item in findings if item["severity"] == "FAIL")
    final_status = "FAIL" if fail_count else "PASS"
    audit_posture = "FAILED" if fail_count else "CLEAN"
    recommended_next_step = (
        "CONTROLLED_INGEST_SCHEDULER_BOUNDARY_REPAIR_REQUIRED"
        if fail_count
        else "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW"
    )
    recommended_next_step_reason = (
        "A governance boundary or registry invariant is broken and should be repaired before additional scheduler layering."
        if fail_count
        else "The controlled ingest scheduler now has a governed advisory audit surface and is ready for operator review."
    )

    packet = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "patch_id": PATCH_ID,
        "audit_id": AUDIT_ID,
        "final_status": final_status,
        "audit_posture": audit_posture,
        "checked_artifacts": deepcopy(_REQUIRED_ARTIFACTS),
        "source_hashes": {
            key: canonical_hash({"text": text}) for key, text in sorted(texts.items())
        },
        "authority_assertions": authority_assertions,
        "boundary_assertions": boundary_assertions,
        "findings": findings,
        "finding_counts": {
            "PASS": sum(1 for item in findings if item["severity"] == "PASS"),
            "FAIL": fail_count,
        },
        "recommended_next_step": recommended_next_step,
        "recommended_next_step_reason": recommended_next_step_reason,
    }
    packet["audit_hash"] = canonical_hash(packet)
    return packet


def render_controlled_ingest_scheduler_governance_audit_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Controlled Ingest Scheduler Governance Audit",
        "",
        f"- final_status: `{packet['final_status']}`",
        f"- audit_posture: `{packet['audit_posture']}`",
        f"- recommended_next_step: `{packet['recommended_next_step']}`",
        f"- recommended_next_step_reason: {packet['recommended_next_step_reason']}",
        "",
        "## Findings",
        "",
    ]
    for finding in packet["findings"]:
        lines.append(f"- `{finding['severity']}` `{finding['category']}`: {finding['message']}")
    lines.append("")
    return "\n".join(lines)


def write_controlled_ingest_scheduler_governance_audit(path: Path | str, packet: dict[str, Any]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(out_path, packet)
    out_path.with_suffix(".md").write_text(
        render_controlled_ingest_scheduler_governance_audit_markdown(packet),
        encoding="utf-8",
    )
