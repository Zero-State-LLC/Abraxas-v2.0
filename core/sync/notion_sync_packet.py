from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from core.canonical.json import canonical_hash

ARTIFACT_TYPE = "NotionSyncPacket.v1"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


REQUIRED_FIELDS: tuple[str, ...] = (
    "notion_page_id",
    "milestone",
    "repo_commit",
    "branch",
    "ci_status",
    "canon_status",
    "artifact_hashes",
)


def _canonical(value: Any) -> dict[str, Any]:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _iso8601_utc(ts: datetime | None = None) -> str:
    now = ts or datetime.now(timezone.utc)
    return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_required_fields(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if value is None:
            missing.append(field)
            continue
        if field == "artifact_hashes":
            if not isinstance(value, dict) or not value:
                missing.append(field)
        elif isinstance(value, str) and not value.strip():
            missing.append(field)
    return sorted(set(missing))


def build_notion_sync_packet(*, payload: dict[str, Any], generated_at: str | None = None) -> dict[str, Any]:
    missing = _validate_required_fields(payload)
    artifact_hashes = payload.get("artifact_hashes", {})
    deterministic_hashes = dict(sorted((str(k), str(v)) for k, v in artifact_hashes.items())) if isinstance(artifact_hashes, dict) else {}

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "notion_page_id": str(payload.get("notion_page_id", NOT_COMPUTABLE)),
        "milestone": str(payload.get("milestone", NOT_COMPUTABLE)),
        "repo_commit": str(payload.get("repo_commit", NOT_COMPUTABLE)),
        "branch": str(payload.get("branch", NOT_COMPUTABLE)),
        "ci_status": str(payload.get("ci_status", NOT_COMPUTABLE)),
        "canon_status": str(payload.get("canon_status", NOT_COMPUTABLE)),
        "artifact_hashes": deterministic_hashes,
        "generated_at": generated_at or _iso8601_utc(),
        "advisory_only": True,
        "projection_only": True,
        "sync_status": "SYNC_READY" if not missing else "NOT_COMPUTABLE",
        "missing_evidence": missing,
        "evidence_only": True,
        "mutation_authority": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "github_writeback": False,
        "notion_writeback": False,
    }
    packet = {**base, "packet_hash": canonical_hash(base)}
    return _canonical(packet)
