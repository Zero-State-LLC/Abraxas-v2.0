"""Artifact & Provenance Service v0 (WP-J).

Thin facade over SUPPORTED core.canonical.json.
Path policy: write operations may only target paths under out/ (no traversal).
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import (
    CanonicalWriteError,
    canonical_dumps,
    canonical_hash,
    prepare_canonical_artifact,
    write_canonical_artifact,
    write_canonical_json,
    write_canonical_json_if_changed,
)

SERVICE_ID = "artifact_and_provenance_service"
SERVICE_VERSION = "0.1.0"
REQUEST_SCHEMA_VERSION = "ArtifactProvenanceServiceRequest.v1"
ALLOWED_OPS = frozenset({"hash", "dumps", "write", "write_if_changed"})


def _error(
    *,
    error_class: str,
    message: str,
    execution_id: str,
    retryable: bool = False,
    operator_action_required: bool = True,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": "ERROR",
        "error_class": error_class,
        "message": message,
        "retryable": retryable,
        "operator_action_required": operator_action_required,
        "execution_id": execution_id,
        "service_id": SERVICE_ID,
        "service_version": SERVICE_VERSION,
        "evidence": evidence or [],
    }


def _resolve_out_path(repo_root: Path, rel: str) -> Path | None:
    ref = rel.replace("\\", "/").lstrip("./")
    if ".." in ref.split("/"):
        return None
    if not ref.startswith("out/"):
        return None
    path = (repo_root / ref).resolve()
    try:
        path.relative_to((repo_root / "out").resolve())
    except ValueError:
        return None
    return path


def execute(
    request: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Execute hash/dumps/write against canonical_json with fail-closed path policy."""
    repo_root = Path(repo_root or Path.cwd()).resolve()
    execution_id = str(request.get("execution_id") or uuid.uuid4())

    try:
        if not isinstance(request, dict):
            return _error(
                error_class="REQUEST_INVALID",
                message="Request must be a JSON object.",
                execution_id=execution_id,
            )
        if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
            return _error(
                error_class="REQUEST_INVALID",
                message=f"schema_version must be {REQUEST_SCHEMA_VERSION}.",
                execution_id=execution_id,
            )
        if request.get("service_id") != SERVICE_ID:
            return _error(
                error_class="REQUEST_INVALID",
                message=f"service_id must be {SERVICE_ID}.",
                execution_id=execution_id,
            )
        operation = request.get("operation")
        if operation not in ALLOWED_OPS:
            return _error(
                error_class="REQUEST_INVALID",
                message=f"operation must be one of {sorted(ALLOWED_OPS)}.",
                execution_id=execution_id,
            )
        if "payload" not in request:
            return _error(
                error_class="PAYLOAD_MISSING",
                message="payload is required.",
                execution_id=execution_id,
            )
        payload = request["payload"]

        if operation == "hash":
            return {
                "status": "OK",
                "service_id": SERVICE_ID,
                "service_version": SERVICE_VERSION,
                "execution_id": execution_id,
                "operation": operation,
                "result": {"canonical_hash": canonical_hash(payload)},
                "provenance": {
                    "implementation": "core.canonical.json",
                    "path_policy": "out/_only_no_traversal",
                },
            }

        if operation == "dumps":
            return {
                "status": "OK",
                "service_id": SERVICE_ID,
                "service_version": SERVICE_VERSION,
                "execution_id": execution_id,
                "operation": operation,
                "result": {
                    "canonical_json": canonical_dumps(payload),
                    "canonical_hash": canonical_hash(payload),
                },
                "provenance": {
                    "implementation": "core.canonical.json",
                    "path_policy": "out/_only_no_traversal",
                },
            }

        # write / write_if_changed
        path_rel = request.get("path")
        if not isinstance(path_rel, str) or not path_rel.strip():
            return _error(
                error_class="PATH_DENIED",
                message="path is required for write operations and must be under out/.",
                execution_id=execution_id,
            )
        target = _resolve_out_path(repo_root, path_rel)
        if target is None:
            return _error(
                error_class="PATH_DENIED",
                message="path must resolve under out/ without traversal.",
                execution_id=execution_id,
                evidence=[str(path_rel)],
            )

        artifact_class_raw = request.get("artifact_class") or "AUDIT_EVIDENCE"
        try:
            artifact_class = ArtifactClass(str(artifact_class_raw))
        except ValueError:
            return _error(
                error_class="REQUEST_INVALID",
                message=f"unknown artifact_class: {artifact_class_raw!r}",
                execution_id=execution_id,
            )

        try:
            if isinstance(payload, dict):
                stamped = prepare_canonical_artifact(payload, artifact_class)
                written = write_canonical_artifact(
                    target,
                    stamped,
                    artifact_class=artifact_class,
                    out_root=repo_root / "out",
                    if_changed=(operation == "write_if_changed"),
                )
                if operation == "write" and not written:
                    # Force publish semantics for explicit write.
                    write_canonical_artifact(
                        target,
                        stamped,
                        artifact_class=artifact_class,
                        out_root=repo_root / "out",
                        if_changed=False,
                    )
                    written = True
                stored_hash = stamped["canonical_hash"]
            else:
                # Non-object payloads remain on legacy writer (migration residual).
                if operation == "write":
                    write_canonical_json(target, payload)
                    written = True
                else:
                    written = write_canonical_json_if_changed(target, payload)
                stored_hash = canonical_hash(payload)
        except (OSError, CanonicalWriteError) as exc:
            return _error(
                error_class="WRITE_FAILED",
                message=f"Write failed: {exc}",
                execution_id=execution_id,
                evidence=[str(path_rel)],
            )

        rel_out = str(target.relative_to(repo_root)).replace("\\", "/")
        result: dict[str, Any] = {
            "path": rel_out,
            "written": written,
            "canonical_hash": stored_hash,
        }
        if isinstance(payload, dict):
            result["artifact_class"] = artifact_class.value
        return {
            "status": "OK",
            "service_id": SERVICE_ID,
            "service_version": SERVICE_VERSION,
            "execution_id": execution_id,
            "operation": operation,
            "result": result,
            "provenance": {
                "implementation": "core.canonical.json",
                "path_policy": "out/_only_no_traversal",
            },
        }
    except Exception as exc:  # noqa: BLE001
        return _error(
            error_class="INTERNAL_ERROR",
            message=f"Unexpected artifact service error: {exc}",
            execution_id=execution_id,
        )
