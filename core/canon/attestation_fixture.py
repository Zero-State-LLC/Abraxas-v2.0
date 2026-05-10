from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from core.governance_runtime.models import ValidationFinding, ValidationReport


ALLOWED_AUTHORITY_MODE = "FIXTURE_ONLY"
FORBIDDEN_AUTHORITY_MODES = {"LIVE_CANON", "CANON_ACTIVE"}
REQUIRED_NOTION_PAGE_IDS = {
    "73460b50-4dfd-4cc3-93e7-906559678624",
    "35c3e8ba-2f5c-81b9-b283-e000933cf25c",
}


@dataclass(frozen=True)
class CanonAttestationSourceRef:
    source_type: str
    source_id: str
    label: str


@dataclass(frozen=True)
class CanonAttestationFixture:
    schema_version: str
    fixture_id: str
    authority_mode: str
    source_refs: tuple[CanonAttestationSourceRef, ...]
    doctrine_hash: str
    repo_execution_hash: str
    attestation_hash: str
    generated_at_policy: str = "STATIC"


@dataclass(frozen=True)
class CanonAttestationFixtureReport:
    fixture_id: str
    status: str
    findings: tuple[ValidationFinding, ...]
    receipt_hash: str
    attestation_hash: str


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _fixture_material(fixture: CanonAttestationFixture) -> dict:
    return {
        "schema_version": fixture.schema_version,
        "fixture_id": fixture.fixture_id,
        "authority_mode": fixture.authority_mode,
        "source_refs": [asdict(ref) for ref in fixture.source_refs],
        "doctrine_hash": fixture.doctrine_hash,
        "repo_execution_hash": fixture.repo_execution_hash,
        "generated_at_policy": fixture.generated_at_policy,
    }


def load_canon_attestation_fixture(path: Path | str) -> CanonAttestationFixture:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    source_refs = tuple(CanonAttestationSourceRef(**ref) for ref in payload["source_refs"])
    return CanonAttestationFixture(
        schema_version=payload["schema_version"],
        fixture_id=payload["fixture_id"],
        authority_mode=payload["authority_mode"],
        source_refs=source_refs,
        doctrine_hash=payload["doctrine_hash"],
        repo_execution_hash=payload["repo_execution_hash"],
        attestation_hash=payload["attestation_hash"],
        generated_at_policy=payload.get("generated_at_policy", "OMITTED"),
    )


def validate_canon_attestation_fixture(fixture: CanonAttestationFixture) -> ValidationReport:
    findings: list[ValidationFinding] = []
    status = "PASS"
    blocked = False

    if fixture.authority_mode in FORBIDDEN_AUTHORITY_MODES:
        findings.append(ValidationFinding(code="AUTHORITY_MODE_BLOCKED", severity="error", message="Live canon authority modes are blocked for fixture attestation."))
        status = "BLOCKED"
        blocked = True
    elif fixture.authority_mode != ALLOWED_AUTHORITY_MODE:
        findings.append(ValidationFinding(code="AUTHORITY_MODE_INVALID", severity="not_computable", message="Fixture authority mode must be FIXTURE_ONLY."))
        if not blocked:
            status = "NOT_COMPUTABLE"

    present_types = {ref.source_type for ref in fixture.source_refs}
    missing_optional = {"NOTION_DATABASE", "OPERATOR_RECEIPT", "REPO_FILE"} - present_types
    if missing_optional:
        findings.append(ValidationFinding(code="OPTIONAL_SOURCE_REF_MISSING", severity="warning", message="Optional source references are missing."))
        if status == "PASS":
            status = "WARN"

    notion_pages = {ref.source_id for ref in fixture.source_refs if ref.source_type == "NOTION_PAGE"}
    if not REQUIRED_NOTION_PAGE_IDS.issubset(notion_pages):
        findings.append(ValidationFinding(code="REQUIRED_NOTION_REF_MISSING", severity="not_computable", message="Required Notion page references are missing."))
        if not blocked:
            status = "NOT_COMPUTABLE"

    if not fixture.doctrine_hash or not fixture.repo_execution_hash or not fixture.attestation_hash:
        findings.append(ValidationFinding(code="ATTESTATION_HASH_FIELDS_MISSING", severity="not_computable", message="Fixture hashes are required for deterministic attestation."))
        if not blocked:
            status = "NOT_COMPUTABLE"

    recomputed = _sha256_text(_canonical_json(_fixture_material(fixture)))
    if fixture.attestation_hash != recomputed:
        findings.append(ValidationFinding(code="ATTESTATION_HASH_MISMATCH", severity="not_computable", message="Fixture attestation hash is not canonical."))
        if not blocked:
            status = "NOT_COMPUTABLE"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "fixture_id": fixture.fixture_id}))
    return ValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)


def build_fixture_attestation_report(fixture: CanonAttestationFixture) -> CanonAttestationFixtureReport:
    validation = validate_canon_attestation_fixture(fixture)
    return CanonAttestationFixtureReport(
        fixture_id=fixture.fixture_id,
        status=validation.status,
        findings=validation.findings,
        receipt_hash=validation.receipt_hash,
        attestation_hash=fixture.attestation_hash,
    )


def write_canon_attestation_fixture_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    fixture_path = base / "fixtures/canon/canon_attestation_fixture.v1.json"
    fixture = load_canon_attestation_fixture(fixture_path)
    report = build_fixture_attestation_report(fixture)
    payload = {
        "fixture_id": report.fixture_id,
        "status": report.status,
        "attestation_hash": report.attestation_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "generated_at_policy": fixture.generated_at_policy,
    }
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/canon_attestation_fixture.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
