"""Deterministic architecture/adapter registry."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from core.alembic.adapters import DEFAULT_ADAPTERS
from core.alembic.models import AdapterHealth, ArchitectureDescriptor
from core.alembic.util import det_timestamp, make_id, to_canonical_dict
from core.canonical.json import canonical_hash


class ArchitectureRegistry:
    def __init__(self, adapters: Iterable[object] | None = None) -> None:
        self._adapters: dict[str, object] = {}
        self._descriptors: dict[str, ArchitectureDescriptor] = {}
        self._adapter_owners: dict[str, str] = {}
        for adapter in adapters if adapters is not None else DEFAULT_ADAPTERS:
            self.register(adapter)

    def register(self, adapter: object) -> None:
        descriptor = adapter.descriptor()  # type: ignore[attr-defined]
        if not isinstance(descriptor, ArchitectureDescriptor):
            raise TypeError("adapter.descriptor() must return ArchitectureDescriptor")
        arch_id = descriptor.architecture_id
        adapter_id = descriptor.adapter_id
        if arch_id in self._descriptors:
            raise ValueError(f"duplicate architecture_id: {arch_id}")
        if adapter_id in self._adapter_owners:
            raise ValueError(f"duplicate adapter ownership: {adapter_id}")
        self._descriptors[arch_id] = descriptor
        self._adapters[arch_id] = adapter
        self._adapter_owners[adapter_id] = arch_id

    def get(self, architecture_id: str) -> ArchitectureDescriptor:
        return self._descriptors[architecture_id]

    def get_adapter(self, architecture_id: str) -> object:
        return self._adapters[architecture_id]

    def list_descriptors(self) -> tuple[ArchitectureDescriptor, ...]:
        return tuple(self._descriptors[key] for key in sorted(self._descriptors))

    def list_adapters(self) -> tuple[object, ...]:
        return tuple(self._adapters[key] for key in sorted(self._adapters))

    def health(self) -> tuple[AdapterHealth, ...]:
        rows: list[AdapterHealth] = []
        for architecture_id in sorted(self._adapters):
            adapter = self._adapters[architecture_id]
            rows.append(adapter.health())  # type: ignore[attr-defined]
        return tuple(rows)

    def snapshot(self) -> dict[str, Any]:
        descriptors = [to_canonical_dict(item) for item in self.list_descriptors()]
        health = [to_canonical_dict(item) for item in self.health()]
        payload = {
            "schema_version": "ArchitectureRegistrySnapshot.v1",
            "registry_id": make_id("registry", len(descriptors)),
            "architectures": descriptors,
            "health": health,
            "count": len(descriptors),
            "timestamp": det_timestamp(canonical_hash({"architectures": descriptors})),
            "content_hash": "",
            "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
        }
        payload["content_hash"] = canonical_hash(payload)
        return payload

    def validation_receipt(self) -> dict[str, Any]:
        errors: list[str] = []
        seen_arch: set[str] = set()
        seen_adapter: set[str] = set()
        for descriptor in self.list_descriptors():
            if descriptor.architecture_id in seen_arch:
                errors.append(f"duplicate architecture_id: {descriptor.architecture_id}")
            if descriptor.adapter_id in seen_adapter:
                errors.append(f"duplicate adapter_id: {descriptor.adapter_id}")
            seen_arch.add(descriptor.architecture_id)
            seen_adapter.add(descriptor.adapter_id)
            try:
                ArchitectureDescriptor.model_validate(descriptor.model_dump())
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{descriptor.architecture_id}: {exc}")
        status = "PASS" if not errors else "FAIL"
        payload = {
            "schema_version": "ArchitectureRegistryValidationReceipt.v1",
            "receipt_id": make_id("registry_validation", status, len(errors)),
            "status": status,
            "errors": errors,
            "architecture_count": len(self._descriptors),
            "timestamp": det_timestamp(status + str(errors)),
            "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
        }
        payload["content_hash"] = canonical_hash(payload)
        return payload


def load_registry_from_json(path: str | Path) -> ArchitectureRegistry:
    """Load descriptor overrides for validation; adapters remain code-owned."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    registry = ArchitectureRegistry()
    declared = {item["architecture_id"] for item in payload.get("architectures", [])}
    known = {item.architecture_id for item in registry.list_descriptors()}
    missing = sorted(declared - known)
    if missing:
        raise ValueError(f"registry JSON references unknown architectures: {missing}")
    return registry


def default_registry() -> ArchitectureRegistry:
    return ArchitectureRegistry()
