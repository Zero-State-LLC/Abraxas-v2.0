"""Validation Service v1 — WS3 service facade (WP-B / WP-K).

Validates a JSON payload against a repo-relative JSON Schema under contracts/.
Does not write to out/ (side_effects: none). Deterministic for identical inputs
when schema files are fixed.

Stability: SUPPORTED (WP-K) — schema_ref restricted to contracts/; fail-closed
path traversal; machine-readable errors; contract tests in
tests/test_validation_service.py.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from core.canonical.json import canonical_hash

SERVICE_ID = "validation_service"
SERVICE_VERSION = "1.0.0"
REQUEST_SCHEMA_VERSION = "ValidationServiceRequest.v1"


def _error_response(
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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _resolve_schema_path(repo_root: Path, schema_ref: str) -> Path | None:
    # Fail closed: only allow schemas under contracts/
    ref = schema_ref.replace("\\", "/").lstrip("./")
    if ".." in ref.split("/"):
        return None
    if not ref.startswith("contracts/"):
        return None
    path = (repo_root / ref).resolve()
    try:
        path.relative_to((repo_root / "contracts").resolve())
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


def validate(
    request: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Validate request.payload against request.schema_ref.

    Returns ValidationServiceResponse.v1 (OK or ERROR). Never raises for
    expected validation failures; unexpected exceptions become INTERNAL_ERROR.
    """
    repo_root = Path(repo_root or Path.cwd()).resolve()
    execution_id = str(request.get("execution_id") or uuid.uuid4())

    try:
        if not isinstance(request, dict):
            return _error_response(
                error_class="REQUEST_INVALID",
                message="Request must be a JSON object.",
                execution_id=execution_id,
            )

        if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
            return _error_response(
                error_class="REQUEST_INVALID",
                message=f"schema_version must be {REQUEST_SCHEMA_VERSION}.",
                execution_id=execution_id,
            )

        if request.get("service_id") != SERVICE_ID:
            return _error_response(
                error_class="REQUEST_INVALID",
                message=f"service_id must be {SERVICE_ID}.",
                execution_id=execution_id,
            )

        schema_ref = request.get("schema_ref")
        if not isinstance(schema_ref, str) or not schema_ref.strip():
            return _error_response(
                error_class="SCHEMA_REF_INVALID",
                message="schema_ref is required and must be a non-empty string.",
                execution_id=execution_id,
            )

        if "payload" not in request:
            return _error_response(
                error_class="REQUEST_INVALID",
                message="payload is required.",
                execution_id=execution_id,
            )

        schema_path = _resolve_schema_path(repo_root, schema_ref)
        if schema_path is None:
            return _error_response(
                error_class="SCHEMA_REF_INVALID",
                message=(
                    "schema_ref must resolve to an existing file under contracts/ "
                    "(path traversal denied)."
                ),
                execution_id=execution_id,
                evidence=[schema_ref],
            )

        try:
            schema_text = schema_path.read_text(encoding="utf-8")
            schema = json.loads(schema_text)
        except (OSError, json.JSONDecodeError) as exc:
            return _error_response(
                error_class="SCHEMA_LOAD_FAILED",
                message=f"Failed to load schema: {exc}",
                execution_id=execution_id,
                evidence=[schema_ref],
            )

        payload = request["payload"]
        schema_sha = _sha256_text(schema_text)
        payload_sha = canonical_hash(payload)

        validator = Draft202012Validator(schema)
        errors: list[dict[str, str]] = []
        for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path)):
            path = "/" + "/".join(str(p) for p in err.absolute_path)
            errors.append(
                {
                    "message": err.message,
                    "path": path if path != "/" else "",
                    "validator": err.validator,
                }
            )

        valid = len(errors) == 0
        return {
            "status": "OK",
            "service_id": SERVICE_ID,
            "service_version": SERVICE_VERSION,
            "execution_id": execution_id,
            "schema_ref": schema_ref.replace("\\", "/"),
            "valid": valid,
            "errors": errors,
            "provenance": {
                "schema_sha256": schema_sha,
                "payload_sha256": payload_sha,
                "validator": "jsonschema",
            },
        }
    except Exception as exc:  # noqa: BLE001 — service boundary fail-closed
        return _error_response(
            error_class="INTERNAL_ERROR",
            message=f"Unexpected validation service error: {exc}",
            execution_id=execution_id,
            retryable=False,
            operator_action_required=True,
        )
