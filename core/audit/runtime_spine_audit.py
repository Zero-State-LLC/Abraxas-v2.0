from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .status import BLOCKED, NOT_COMPUTABLE, PASS, WARN, normalize_audit_status


@dataclass(frozen=True)
class AuditArtifactRef:
    path: str
    sha256: str
    status: str | None


@dataclass(frozen=True)
class RuntimeSpineAuditFinding:
    code: str
    severity: str
    message: str
    artifact_path: str


@dataclass(frozen=True)
class RuntimeSpineAuditSummary:
    posture: str
    artifact_count: int
    finding_count: int


@dataclass(frozen=True)
class RuntimeSpineAuditReport:
    artifact_refs: tuple[AuditArtifactRef, ...]
    findings: tuple[RuntimeSpineAuditFinding, ...]
    summary: RuntimeSpineAuditSummary
    chain_hash: str


REQUIRED_ARTIFACTS = (
    "out/audit/canon_authority_stub.latest.json",
    "out/audit/governance_runtime_scaffold.latest.json",
    "out/audit/lane_enforcement.latest.json",
    "out/audit/runtime_spine_skeleton.latest.json",
)


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_runtime_spine_audit_report(base_dir: Path | str = ".", include_fixture_attestation: bool = False) -> RuntimeSpineAuditReport:
    base = Path(base_dir)
    refs: list[AuditArtifactRef] = []
    findings: list[RuntimeSpineAuditFinding] = []

    posture = PASS
    required = list(REQUIRED_ARTIFACTS)
    if include_fixture_attestation:
        required.append("out/audit/canon_attestation_fixture.latest.json")

    for rel_path in sorted(required):
        full_path = base / rel_path
        if not full_path.exists():
            findings.append(RuntimeSpineAuditFinding("ARTIFACT_MISSING", "not_computable", "Required artifact is missing.", rel_path))
            refs.append(AuditArtifactRef(path=rel_path, sha256="NOT_COMPUTABLE", status=None))
            posture = NOT_COMPUTABLE
            continue

        text = full_path.read_text(encoding="utf-8")
        digest = _sha256_text(text)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            findings.append(RuntimeSpineAuditFinding("ARTIFACT_MALFORMED", "not_computable", "Artifact JSON parse failed.", rel_path))
            refs.append(AuditArtifactRef(path=rel_path, sha256=digest, status=None))
            posture = NOT_COMPUTABLE
            continue

        normalized = normalize_audit_status(payload)
        status = normalized["status"]
        refs.append(AuditArtifactRef(path=rel_path, sha256=digest, status=status))
        if status == BLOCKED:
            findings.append(RuntimeSpineAuditFinding("ARTIFACT_BLOCKED", "error", "Artifact reports BLOCKED posture.", rel_path))
            posture = BLOCKED if posture != NOT_COMPUTABLE else posture
        elif status not in {PASS, WARN, NOT_COMPUTABLE}:
            findings.append(RuntimeSpineAuditFinding("ARTIFACT_STATUS_UNKNOWN", "warning", "Artifact status is unknown; treating as WARN.", rel_path))
            if posture == PASS:
                posture = WARN
        elif status == WARN and posture == PASS:
            posture = WARN
        elif status == NOT_COMPUTABLE:
            findings.append(RuntimeSpineAuditFinding("ARTIFACT_NOT_COMPUTABLE", "not_computable", "Artifact reports NOT_COMPUTABLE status.", rel_path))
            posture = NOT_COMPUTABLE

    ordered_refs = tuple(sorted(refs, key=lambda r: r.path))
    ordered_findings = tuple(sorted(findings, key=lambda f: (f.artifact_path, f.code)))
    summary = RuntimeSpineAuditSummary(posture=posture, artifact_count=len(ordered_refs), finding_count=len(ordered_findings))
    chain_input = {
        "artifact_refs": [asdict(ref) for ref in ordered_refs],
        "findings": [asdict(f) for f in ordered_findings],
        "posture": posture,
    }
    chain_hash = _sha256_text(_canonical_json(chain_input))
    return RuntimeSpineAuditReport(artifact_refs=ordered_refs, findings=ordered_findings, summary=summary, chain_hash=chain_hash)


def write_runtime_spine_audit_artifact(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    report = build_runtime_spine_audit_report(base)
    payload = {
        "artifact_refs": [asdict(ref) for ref in report.artifact_refs],
        "findings": [asdict(f) for f in report.findings],
        "summary": asdict(report.summary),
        "chain_hash": report.chain_hash,
        "status": report.summary.posture,
    }
    text = _canonical_json(payload) + "\n"
    output = base / "out/audit/runtime_spine_audit.latest.json"
    output.write_text(text, encoding="utf-8")
    return report.chain_hash
