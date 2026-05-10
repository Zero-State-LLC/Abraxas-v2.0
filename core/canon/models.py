from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CanonSource(str, Enum):
    NOTION_PAGE = "NOTION_PAGE"
    NOTION_DATABASE = "NOTION_DATABASE"
    REPO_FILE = "REPO_FILE"
    OPERATOR_RECEIPT = "OPERATOR_RECEIPT"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"


@dataclass(frozen=True)
class CanonDoctrineRef:
    source_type: CanonSource
    source_id: str
    label: str


@dataclass(frozen=True)
class CanonAttestation:
    doctrine_hash: str
    repo_execution_hash: str
    sync_posture: str


@dataclass(frozen=True)
class CanonDriftFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class CanonSyncPacket:
    canon_ref: CanonDoctrineRef
    repo_ref: CanonDoctrineRef
    attestation: CanonAttestation
    status: str
