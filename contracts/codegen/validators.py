from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, TypeAlias

from pydantic import ValidationError

from core.canonical.json import canonical_hash

from contracts.codegen.models import (
    AuthorityLocks,
    CodeDropEnvelope,
    CodegenTaskPacket,
    MetaGateSeal,
    PatchContract,
    ShadowReplayFixture,
    StrictCodegenModel,
)

CodegenModel: TypeAlias = (
    PatchContract
    | CodeDropEnvelope
    | MetaGateSeal
    | CodegenTaskPacket
    | ShadowReplayFixture
)

CODEGEN_SCHEMA_NAMES: tuple[str, ...] = (
    "PatchContract",
    "CodeDropEnvelope",
    "MetaGateSeal",
    "CodegenTaskPacket",
    "ShadowReplayFixture",
)

_MODEL_BY_SCHEMA_VERSION: dict[str, type[StrictCodegenModel]] = {
    "PatchContract.v1": PatchContract,
    "CodeDropEnvelope.v1": CodeDropEnvelope,
    "MetaGateSeal.v1": MetaGateSeal,
    "CodegenTaskPacket.v1": CodegenTaskPacket,
    "ShadowReplayFixture.v1": ShadowReplayFixture,
}


def _schema_root() -> Path:
    return Path(__file__).resolve().parent / "schemas"


def load_codegen_schema(schema_name: str) -> dict[str, Any]:
    if schema_name not in CODEGEN_SCHEMA_NAMES:
        raise ValueError(f"unknown codegen schema: {schema_name}")
    schema_path = _schema_root() / f"{schema_name}.json"
    value = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"schema is not an object: {schema_path}")
    return value


def validate_authority_locks(value: Mapping[str, Any]) -> AuthorityLocks:
    locks = AuthorityLocks.model_validate(dict(value))
    for name, lock_value in locks.model_dump().items():
        if name == "advisory_only":
            if lock_value is not True:
                raise ValueError("advisory_only must remain true")
            continue
        if lock_value is not False:
            raise ValueError(f"authority lock must remain false: {name}")
    return locks


def canonical_hash_without_field(
    value: Mapping[str, Any],
    *,
    hash_field: str = "canonical_hash",
) -> str:
    payload = dict(value)
    payload.pop(hash_field, None)
    return canonical_hash(payload)


def validate_canonical_hash_field(
    value: Mapping[str, Any],
    *,
    hash_field: str = "canonical_hash",
) -> str:
    observed = value.get(hash_field)
    if not isinstance(observed, str):
        raise ValueError(f"missing canonical hash field: {hash_field}")
    expected = canonical_hash_without_field(value, hash_field=hash_field)
    if observed != expected:
        raise ValueError(f"canonical hash mismatch: expected {expected}")
    return observed


def validate_codegen_model(value: Mapping[str, Any]) -> CodegenModel:
    schema_version = value.get("schema_version")
    if not isinstance(schema_version, str):
        raise ValueError("missing schema_version")
    model_type = _MODEL_BY_SCHEMA_VERSION.get(schema_version)
    if model_type is None:
        raise ValueError(f"unsupported schema_version: {schema_version}")
    try:
        model = model_type.model_validate(dict(value))
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc

    model_dump = model.model_dump()
    locks = model_dump.get("authority_locks")
    if isinstance(locks, Mapping):
        validate_authority_locks(locks)
    return model

