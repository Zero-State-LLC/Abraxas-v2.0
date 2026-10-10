"""Independent activation evidence for INTERNAL_CANARY (reference implementation).

The candidate may report measurements; it cannot grant itself PASS. Canary
activation therefore needs an ``ActivationEvidence.v1`` record produced outside
the candidate by a trusted issuer (signed CI, a ratchet gate such as pawl, or an
operator receipt) and signed with that issuer's Ed25519 key.

Trust model:
- The trust store (issuer ids, kinds, public keys, required checks) is
  deployment configuration loaded from outside the candidate's code. Only the
  issuer holds its private key, so verifying never lets the candidate forge.
- Evidence binds the exact candidate revision (git SHA), the configuration
  digest, the required checks and their results, the issuer, and a validity
  window. The expected revision and digest come from the deployment, not from
  the evidence.
- Anything absent, malformed, unsigned, untrusted, self-asserted, mismatched,
  stale or failed blocks activation. A missing ``cryptography`` package makes
  evidence UNVERIFIABLE (fail closed).
"""

from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from core.canonical.json import canonical_dumps

EVIDENCE_SCHEMA_VERSION = "ActivationEvidence.v1"
TRUST_STORE_SCHEMA_VERSION = "ActivationEvidenceTrustStore.v1"
MAX_VALIDITY = timedelta(days=7)
CLOCK_SKEW = timedelta(minutes=5)

IssuerKind = Literal["signed_ci", "ratchet_gate", "operator_receipt"]
CheckResult = Literal["PASS", "FAIL"]


class EvidenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    ABSENT = "ABSENT"
    MALFORMED = "MALFORMED"
    UNVERIFIABLE = "UNVERIFIABLE"
    UNTRUSTED_ISSUER = "UNTRUSTED_ISSUER"
    SELF_ASSERTED = "SELF_ASSERTED"
    MISMATCHED = "MISMATCHED"
    STALE = "STALE"
    FAILED = "FAILED"


class EvidenceIssuer(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer_id: str = Field(min_length=1)
    kind: IssuerKind


class ActivationEvidencePayload(BaseModel):
    """What the issuer attests. The signature covers its canonical JSON."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["ActivationEvidence.v1"]
    lane: Literal["INTERNAL_CANARY"]
    candidate_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    config_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    checks: dict[str, CheckResult]
    issuer: EvidenceIssuer
    issued_at: datetime
    expires_at: datetime

    @field_validator("issued_at", "expires_at")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamps must carry a timezone")
        return value

    def signing_bytes(self) -> bytes:
        return canonical_dumps(self.model_dump(mode="json")).encode("utf-8")


class SignedActivationEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    payload: ActivationEvidencePayload
    key_id: str = Field(min_length=1)
    signature: str = Field(min_length=1)  # base64 Ed25519 signature


class TrustedIssuer(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer_id: str = Field(min_length=1)
    kind: IssuerKind
    key_id: str = Field(min_length=1)
    public_key: str = Field(min_length=1)  # base64 raw 32-byte Ed25519 key


class TrustStore(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["ActivationEvidenceTrustStore.v1"]
    required_checks: tuple[str, ...] = Field(min_length=1)
    issuers: tuple[TrustedIssuer, ...] = Field(min_length=1)

    def issuer_for(self, key_id: str) -> TrustedIssuer | None:
        return next((i for i in self.issuers if i.key_id == key_id), None)


class EvidenceVerification(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: EvidenceStatus
    reasons: tuple[str, ...] = ()
    issuer_id: str | None = None
    candidate_revision: str | None = None

    @property
    def verified(self) -> bool:
        return self.status is EvidenceStatus.VERIFIED


def load_trust_store(path: Path) -> TrustStore:
    return TrustStore.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _result(status: EvidenceStatus, *reasons: str, **fields: Any) -> EvidenceVerification:
    return EvidenceVerification(status=status, reasons=tuple(reasons), **fields)


def _signature_valid(public_key_b64: str, signature_b64: str, message: bytes) -> bool | None:
    """True/False for a checked signature; None when it cannot be checked."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        return None
    try:
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64, validate=True))
        signature = base64.b64decode(signature_b64, validate=True)
    except (binascii.Error, ValueError):
        return False
    try:
        key.verify(signature, message)
    except InvalidSignature:
        return False
    return True


def verify_activation_evidence(
    evidence: Mapping[str, Any] | None,
    *,
    trust_store: TrustStore | None,
    expected_revision: str | None,
    expected_config_digest: str | None,
    now: datetime,
    candidate_identity: str | None = None,
    required_checks: Sequence[str] | None = None,
) -> EvidenceVerification:
    """Verify evidence for INTERNAL_CANARY; anything but VERIFIED blocks activation."""
    if evidence is None:
        return _result(EvidenceStatus.ABSENT, "no_activation_evidence")
    if trust_store is None:
        return _result(EvidenceStatus.UNVERIFIABLE, "no_trust_store_configured")
    if not expected_revision or not expected_config_digest:
        return _result(EvidenceStatus.UNVERIFIABLE, "deployment_did_not_declare_revision_or_config")

    try:
        signed = SignedActivationEvidence.model_validate(dict(evidence))
    except ValidationError as exc:
        return _result(EvidenceStatus.MALFORMED, f"invalid_evidence:{exc.error_count()}_errors")
    payload = signed.payload
    fields = {"issuer_id": payload.issuer.issuer_id, "candidate_revision": payload.candidate_revision}

    trusted = trust_store.issuer_for(signed.key_id)
    if trusted is None:
        return _result(EvidenceStatus.UNTRUSTED_ISSUER, "unknown_key_id", **fields)
    if (trusted.issuer_id, trusted.kind) != (payload.issuer.issuer_id, payload.issuer.kind):
        return _result(EvidenceStatus.UNTRUSTED_ISSUER, "issuer_does_not_match_key", **fields)
    if candidate_identity is not None and payload.issuer.issuer_id == candidate_identity:
        return _result(EvidenceStatus.SELF_ASSERTED, "candidate_cannot_issue_its_own_evidence", **fields)

    checked = _signature_valid(trusted.public_key, signed.signature, payload.signing_bytes())
    if checked is None:
        return _result(EvidenceStatus.UNVERIFIABLE, "ed25519_support_unavailable", **fields)
    if not checked:
        return _result(EvidenceStatus.UNVERIFIABLE, "signature_invalid", **fields)

    mismatches = []
    if payload.candidate_revision != expected_revision:
        mismatches.append("candidate_revision")
    if payload.config_digest != expected_config_digest:
        mismatches.append("config_digest")
    required = tuple(required_checks) if required_checks is not None else trust_store.required_checks
    missing = sorted(set(required) - set(payload.checks))
    if missing:
        mismatches.append("missing_checks:" + ",".join(missing))
    if mismatches:
        return _result(EvidenceStatus.MISMATCHED, *mismatches, **fields)

    if payload.expires_at - payload.issued_at > MAX_VALIDITY:
        return _result(EvidenceStatus.STALE, "validity_window_too_long", **fields)
    if payload.issued_at > now + CLOCK_SKEW:
        return _result(EvidenceStatus.STALE, "issued_in_the_future", **fields)
    if now >= payload.expires_at:
        return _result(EvidenceStatus.STALE, "expired", **fields)

    failed = sorted(name for name in required if payload.checks[name] != "PASS")
    if failed:
        return _result(EvidenceStatus.FAILED, "failed_checks:" + ",".join(failed), **fields)

    return _result(EvidenceStatus.VERIFIED, "independent_evidence_verified", **fields)


def verify_evidence_files(
    evidence_path: Path | None,
    trust_store_path: Path | None,
    *,
    expected_revision: str | None,
    expected_config_digest: str | None,
    now: datetime,
    candidate_identity: str | None = None,
) -> EvidenceVerification:
    """Load deployment-supplied evidence and trust store files, then verify."""
    if evidence_path is None or not evidence_path.is_file():
        return _result(EvidenceStatus.ABSENT, "no_activation_evidence")
    if trust_store_path is None or not trust_store_path.is_file():
        return _result(EvidenceStatus.UNVERIFIABLE, "no_trust_store_configured")
    try:
        trust_store = load_trust_store(trust_store_path)
    except (ValueError, ValidationError):
        return _result(EvidenceStatus.UNVERIFIABLE, "trust_store_invalid")
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except ValueError:
        return _result(EvidenceStatus.MALFORMED, "evidence_not_json")
    if not isinstance(evidence, dict):
        return _result(EvidenceStatus.MALFORMED, "evidence_not_object")
    return verify_activation_evidence(
        evidence,
        trust_store=trust_store,
        expected_revision=expected_revision,
        expected_config_digest=expected_config_digest,
        now=now,
        candidate_identity=candidate_identity,
    )
