"""Advisory ConflictReport builder for RUNE.PIPELINE.CONFLICT_SCAN.

Detection and classification only. Never auto-resolves conflicts.
execution_authority is always False. Operator disposition required
for any resolution (see Conflict Resolution Logic Analysis).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Sequence
import hashlib
import json

ConflictType = Literal[
    "provenance_mismatch",
    "normalization_mismatch",
    "replay_mismatch",
    "lineage_break",
    "duplicate_source",
    "authority_violation",
    "dependency_conflict",
    "schema_mismatch",
    "unknown",
]
Severity = Literal["low", "medium", "high", "severe"]
ScanStatus = Literal["PASS", "CONFLICTS_DETECTED", "NOT_COMPUTABLE"]


@dataclass(frozen=True)
class ConflictFinding:
    finding_id: str
    conflict_type: ConflictType
    severity: Severity
    subject_ids: tuple[str, ...]
    detail: str
    resolution_required: bool = True


@dataclass
class ConflictReport:
    """ConflictReport.v1 — advisory output of CONFLICT_SCAN."""

    schema_version: str = "ConflictReport.v1"
    report_id: str = ""
    pipeline_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    producer_system: str = "GROK"
    execution_authority: bool = False
    net_catalog_delta: int = 0
    scan_status: ScanStatus = "PASS"
    findings: List[Dict[str, Any]] = field(default_factory=list)
    conflict_count: int = 0
    blocking_conflict_detected: bool = False
    resolution_required: bool = False
    recommended_next: str = "CONTINUE"
    source_receipts: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    provenance_hash: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    authority_locks: Dict[str, bool] = field(
        default_factory=lambda: {
            "execution_authority": False,
            "auto_resolve": False,
            "canon_mutation": False,
            "runtime_mutation": False,
            "forecast_routing": False,
        }
    )

    def finalize(self) -> "ConflictReport":
        payload = {
            "schema_version": self.schema_version,
            "pipeline_id": self.pipeline_id,
            "producer_system": self.producer_system,
            "execution_authority": self.execution_authority,
            "net_catalog_delta": self.net_catalog_delta,
            "scan_status": self.scan_status,
            "findings": self.findings,
            "conflict_count": self.conflict_count,
            "blocking_conflict_detected": self.blocking_conflict_detected,
            "resolution_required": self.resolution_required,
            "recommended_next": self.recommended_next,
            "source_receipts": sorted(self.source_receipts),
            "notes": self.notes,
            "authority_locks": self.authority_locks,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.provenance_hash = hashlib.sha256(raw).hexdigest()
        if not self.report_id:
            self.report_id = f"conflict-report:{self.provenance_hash[:12]}"
        self.provenance = {
            "generator": "ConflictReport.v1-advisory-0.1",
            "producer_system": self.producer_system,
            "registers": {"classification": "OBSERVED"},
            "loop_dynamics": {
                "assessment_complete": True,
                "retrocausal_risk": "NONE",
            },
            "hash": self.provenance_hash,
        }
        return self

    def to_dict(self) -> dict:
        return asdict(self)


def _severity_rank(s: Severity) -> int:
    return {"low": 1, "medium": 2, "high": 3, "severe": 4}.get(s, 0)


def detect_hash_conflicts(
    items: Sequence[Dict[str, Any]],
    *,
    id_key: str = "id",
    hash_key: str = "hash",
) -> List[ConflictFinding]:
    """Detect duplicate IDs with mismatched hashes (provenance/normalization class)."""
    by_id: Dict[str, List[str]] = {}
    for item in items:
        iid = str(item.get(id_key, ""))
        h = str(item.get(hash_key, ""))
        if not iid:
            continue
        by_id.setdefault(iid, []).append(h)

    findings: List[ConflictFinding] = []
    for iid, hashes in sorted(by_id.items()):
        unique = sorted(set(hashes))
        if len(hashes) > 1 and len(unique) > 1:
            findings.append(
                ConflictFinding(
                    finding_id=f"hash-mismatch:{iid}",
                    conflict_type="provenance_mismatch",
                    severity="high",
                    subject_ids=(iid,),
                    detail=f"ID {iid!r} has divergent hashes: {unique}",
                    resolution_required=True,
                )
            )
        elif len(hashes) > 1 and len(unique) == 1:
            findings.append(
                ConflictFinding(
                    finding_id=f"duplicate-source:{iid}",
                    conflict_type="duplicate_source",
                    severity="low",
                    subject_ids=(iid,),
                    detail=f"ID {iid!r} appears {len(hashes)} times with identical hash",
                    resolution_required=False,
                )
            )
    return findings


def detect_dependency_conflicts(
    required: Sequence[str],
    available: Sequence[str],
) -> List[ConflictFinding]:
    """Detect required dependencies missing from available set."""
    avail = set(available)
    missing = sorted(set(required) - avail)
    findings: List[ConflictFinding] = []
    for dep in missing:
        findings.append(
            ConflictFinding(
                finding_id=f"missing-dep:{dep}",
                conflict_type="dependency_conflict",
                severity="high",
                subject_ids=(dep,),
                detail=f"Required dependency {dep!r} not present in available set",
                resolution_required=True,
            )
        )
    return findings


def build_conflict_report(
    *,
    pipeline_id: str = "universal_ingest",
    items: Optional[Sequence[Dict[str, Any]]] = None,
    required_dependencies: Optional[Sequence[str]] = None,
    available_dependencies: Optional[Sequence[str]] = None,
    extra_findings: Optional[Sequence[ConflictFinding]] = None,
    source_receipts: Optional[List[str]] = None,
    notes: Optional[str] = None,
    producer_system: str = "GROK",
) -> ConflictReport:
    """Build an advisory ConflictReport.v1.

    Performs detection only. Does not resolve, merge, or select winners.
    Severe/high findings set resolution_required and recommended_next to
    OPERATOR_REVIEW.
    """
    findings: List[ConflictFinding] = []

    if items is not None:
        findings.extend(detect_hash_conflicts(items))

    if required_dependencies is not None:
        findings.extend(
            detect_dependency_conflicts(
                required_dependencies,
                available_dependencies or [],
            )
        )

    if extra_findings:
        findings.extend(list(extra_findings))

    findings_sorted = sorted(findings, key=lambda f: (f.finding_id, f.conflict_type))
    max_sev = max((_severity_rank(f.severity) for f in findings_sorted), default=0)
    blocking = any(
        f.severity in ("high", "severe") and f.resolution_required for f in findings_sorted
    )
    needs_resolution = any(f.resolution_required for f in findings_sorted)

    if not findings_sorted:
        status: ScanStatus = "PASS"
        next_action = "CONTINUE"
    elif blocking:
        status = "CONFLICTS_DETECTED"
        next_action = "OPERATOR_REVIEW"
    else:
        status = "CONFLICTS_DETECTED"
        next_action = "OPERATOR_REVIEW" if needs_resolution else "CONTINUE"

    report = ConflictReport(
        pipeline_id=pipeline_id,
        producer_system=producer_system,
        scan_status=status,
        findings=[
            {
                "finding_id": f.finding_id,
                "conflict_type": f.conflict_type,
                "severity": f.severity,
                "subject_ids": list(f.subject_ids),
                "detail": f.detail,
                "resolution_required": f.resolution_required,
            }
            for f in findings_sorted
        ],
        conflict_count=len(findings_sorted),
        blocking_conflict_detected=blocking,
        resolution_required=needs_resolution,
        recommended_next=next_action,
        source_receipts=source_receipts or [],
        notes=notes,
    )
    return report.finalize()


def emit_conflict_scan_packet(
    *,
    pipeline_id: str = "universal_ingest",
    items: Optional[Sequence[Dict[str, Any]]] = None,
    required_dependencies: Optional[Sequence[str]] = None,
    available_dependencies: Optional[Sequence[str]] = None,
    source_receipts: Optional[List[str]] = None,
    notes: Optional[str] = None,
    producer_system: str = "GROK",
) -> Dict[str, Any]:
    """Convenience emitter returning a dict suitable as conflict_scan_packet."""
    return build_conflict_report(
        pipeline_id=pipeline_id,
        items=items,
        required_dependencies=required_dependencies,
        available_dependencies=available_dependencies,
        source_receipts=source_receipts,
        notes=notes,
        producer_system=producer_system,
    ).to_dict()
