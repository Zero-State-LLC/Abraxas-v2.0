from __future__ import annotations

import hashlib
import json
import mimetypes
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from core.belief_graph.claim_object import ClaimObject, ClaimStatus
from core.belief_graph.evidence_object import EvidenceObject
from core.belief_graph.signal_graph import SignalGraphRelationship
from core.belief_graph.theory_object import TheoryObject
from core.canonical.json import canonical_hash
from core.ingest.ingest_packet import FINAL_STATUS, IngestPacket
from core.ingest.source_record import SourcePayload, SourceRecord

_ALLOWED_STATUSES = {"OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"}


class IngestAdapterDescriptor(BaseModel):
    schema_version: Literal["IngestAdapter.v1"] = "IngestAdapter.v1"
    adapter_id: Literal["filesystem_adapter", "json_adapter", "audit_artifact_adapter"]
    description: str = Field(min_length=1)
    source_kinds: tuple[Literal["filesystem", "json", "audit_artifact"], ...]
    supported_extensions: tuple[str, ...] = Field(default_factory=tuple)
    produces: tuple[
        Literal["EvidenceObject", "ClaimObject", "TheoryObject"],
        Literal["EvidenceObject", "ClaimObject", "TheoryObject"],
        Literal["EvidenceObject", "ClaimObject", "TheoryObject"],
    ] = ("EvidenceObject", "ClaimObject", "TheoryObject")
    local_only: Literal[True] = True
    advisory_only: Literal[True] = True
    web_ingest_enabled: Literal[False] = False
    FORECAST_ROUTING: Literal[False] = False
    CANON_MUTATION: Literal[False] = False
    RUNTIME_MUTATION: Literal[False] = False
    EXECUTION_AUTHORITY: Literal[False] = False
    TRUTH_ASSIGNMENT: Literal[False] = False
    FINAL_STATUS: Literal["GLOBAL_INGEST_SPINE_ADVISORY_ONLY"] = FINAL_STATUS

    model_config = {"frozen": True}

    @field_validator("description")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description required")
        return value


class IngestAdapter(ABC):
    descriptor: IngestAdapterDescriptor
    source_type: Literal["filesystem", "json", "audit_artifact"]

    def ingest(self, repository_root: Path | str, source_path: Path | str) -> IngestPacket:
        root = Path(repository_root).resolve()
        path = self._resolve_local_path(root, source_path)
        source_record = self._build_source_record(root, path)
        return self._build_packet(source_record)

    def supports(self, repository_root: Path | str, source_path: Path | str) -> bool:
        root = Path(repository_root).resolve()
        try:
            path = self._resolve_local_path(root, source_path)
        except ValueError:
            return False
        return self._supports_resolved_path(root, path)

    @abstractmethod
    def _supports_resolved_path(self, repository_root: Path, source_path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _read_payload(self, source_path: Path) -> SourcePayload:
        raise NotImplementedError

    def _build_source_record(self, repository_root: Path, source_path: Path) -> SourceRecord:
        raw_bytes = source_path.read_bytes()
        relative_path = source_path.relative_to(repository_root).as_posix()
        digest = hashlib.sha256(raw_bytes).hexdigest()
        payload = self._read_payload(source_path)
        content_type = mimetypes.guess_type(source_path.name)[0] or "application/octet-stream"
        return SourceRecord(
            adapter_id=self.descriptor.adapter_id,
            source_uri=relative_path,
            source_type=self.source_type,
            observed_at=f"deterministic:{relative_path}:{digest[:16]}",
            content_type=content_type,
            sha256=digest,
            size_bytes=len(raw_bytes),
            metadata={
                "path": relative_path,
                "suffix": source_path.suffix,
                "repository_root": repository_root.as_posix(),
            },
            payload=payload,
        )

    def _build_packet(self, source_record: SourceRecord) -> IngestPacket:
        evidence = self._build_evidence(source_record)
        claim = self._build_claim(source_record, evidence)
        theory = self._build_theory(source_record, claim, evidence)
        relationships = (
            SignalGraphRelationship(
                source_ref=claim.id,
                source_type="claim",
                target_ref=evidence.hash,
                target_type="evidence",
                relationship="supported_by",
            ),
            SignalGraphRelationship(
                source_ref=theory.id,
                source_type="theory",
                target_ref=claim.id,
                target_type="claim",
                relationship="organizes",
            ),
            SignalGraphRelationship(
                source_ref=theory.id,
                source_type="theory",
                target_ref=evidence.hash,
                target_type="evidence",
                relationship="grounded_by",
            ),
        )
        return IngestPacket(
            adapter_id=self.descriptor.adapter_id,
            source_record=source_record,
            evidence=(evidence,),
            claims=(claim,),
            theories=(theory,),
            relationships=relationships,
            provenance={
                "adapter": self.descriptor.model_dump(mode="json"),
                "source_uri": source_record.source_uri,
            },
        )

    def _build_evidence(self, source_record: SourceRecord) -> EvidenceObject:
        return EvidenceObject(
            source=source_record.source_uri,
            provenance={
                "adapter_id": self.descriptor.adapter_id,
                "source_type": source_record.source_type,
                "content_type": source_record.content_type,
                "size_bytes": source_record.size_bytes,
            },
            timestamp=source_record.observed_at,
            evidence_type=source_record.source_type.upper(),
            hash=source_record.sha256,
        )

    def _build_claim(self, source_record: SourceRecord, evidence: EvidenceObject) -> ClaimObject:
        status = self._claim_status(source_record)
        return ClaimObject(
            id=self._claim_id(source_record),
            statement=self._claim_statement(source_record),
            provenance={
                "adapter_id": self.descriptor.adapter_id,
                "source_uri": source_record.source_uri,
                "advisory_only": True,
            },
            evidence_refs=(evidence.hash,),
            confidence=self._claim_confidence(source_record, status),
            status=status,
        )

    def _build_theory(
        self,
        source_record: SourceRecord,
        claim: ClaimObject,
        evidence: EvidenceObject,
    ) -> TheoryObject:
        return TheoryObject(
            id=self._theory_id(source_record),
            supporting_claims=(claim.id,),
            conflicting_claims=(),
            evidence_refs=(evidence.hash,),
        )

    def _claim_status(self, source_record: SourceRecord) -> ClaimStatus:
        payload = source_record.payload
        if isinstance(payload, dict):
            raw_status = payload.get("status")
            if isinstance(raw_status, str) and raw_status in _ALLOWED_STATUSES:
                return raw_status  # pyright: ignore[reportReturnType]
            raw_validation_status = payload.get("validation_status")
            if raw_validation_status == "NOT_COMPUTABLE":
                return "NOT_COMPUTABLE"
        return "OBSERVED"

    def _claim_confidence(
        self,
        source_record: SourceRecord,
        status: ClaimStatus,
    ) -> float | Literal["NOT_COMPUTABLE"]:
        if status == "NOT_COMPUTABLE":
            return "NOT_COMPUTABLE"
        payload = source_record.payload
        if isinstance(payload, dict):
            raw_confidence = payload.get("confidence")
            if isinstance(raw_confidence, (int, float)) and 0.0 <= raw_confidence <= 1.0:
                return float(raw_confidence)
        return 0.0

    def _claim_statement(self, source_record: SourceRecord) -> str:
        payload = source_record.payload
        if isinstance(payload, dict):
            for key in ("statement", "summary", "title"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        return f"{self.source_type.replace('_', ' ')} source observed at {source_record.source_uri}."

    def _claim_id(self, source_record: SourceRecord) -> str:
        return f"claim-{canonical_hash({'adapter': self.descriptor.adapter_id, 'sha256': source_record.sha256})[:24]}"

    def _theory_id(self, source_record: SourceRecord) -> str:
        return f"theory-{canonical_hash({'adapter': self.descriptor.adapter_id, 'source_uri': source_record.source_uri})[:24]}"

    def _resolve_local_path(self, repository_root: Path, source_path: Path | str) -> Path:
        candidate = Path(source_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (repository_root / candidate).resolve()
        try:
            resolved.relative_to(repository_root)
        except ValueError as exc:
            raise ValueError("ingest only supports local repository sources") from exc
        if not resolved.is_file():
            raise ValueError("ingest source must be an existing file")
        return resolved


class FilesystemIngestAdapter(IngestAdapter):
    descriptor = IngestAdapterDescriptor(
        adapter_id="filesystem_adapter",
        description="Read local repository files as advisory filesystem observations.",
        source_kinds=("filesystem",),
        supported_extensions=("*",),
    )
    source_type = "filesystem"

    def _supports_resolved_path(self, repository_root: Path, source_path: Path) -> bool:
        return source_path.is_file()

    def _read_payload(self, source_path: Path) -> SourcePayload:
        raw_bytes = source_path.read_bytes()
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return f"<binary:{len(raw_bytes)} bytes>"


class JsonIngestAdapter(IngestAdapter):
    descriptor = IngestAdapterDescriptor(
        adapter_id="json_adapter",
        description="Read local repository JSON sources into advisory ingest packets.",
        source_kinds=("json",),
        supported_extensions=(".json",),
    )
    source_type = "json"

    def _supports_resolved_path(self, repository_root: Path, source_path: Path) -> bool:
        return source_path.suffix.lower() == ".json"

    def _read_payload(self, source_path: Path) -> SourcePayload:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        if isinstance(payload, (dict, list, str)):
            return payload
        raise ValueError("json adapter requires object, array, or string payloads")


class AuditArtifactIngestAdapter(JsonIngestAdapter):
    descriptor = IngestAdapterDescriptor(
        adapter_id="audit_artifact_adapter",
        description="Read local audit artifacts into advisory ingest packets without authority.",
        source_kinds=("audit_artifact",),
        supported_extensions=(".json",),
    )
    source_type = "audit_artifact"

    def _supports_resolved_path(self, repository_root: Path, source_path: Path) -> bool:
        if source_path.suffix.lower() != ".json":
            return False
        relative_path = source_path.relative_to(repository_root)
        return relative_path.parts[:2] == ("out", "audit")

    def _claim_status(self, source_record: SourceRecord) -> ClaimStatus:
        status = super()._claim_status(source_record)
        if status != "OBSERVED":
            return status
        return "INFERRED"
