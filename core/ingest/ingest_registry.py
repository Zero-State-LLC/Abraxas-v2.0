from __future__ import annotations

from pathlib import Path

from core.ingest.ingest_adapter import (
    AuditArtifactIngestAdapter,
    FilesystemIngestAdapter,
    IngestAdapter,
    IngestAdapterDescriptor,
    JsonIngestAdapter,
)
from core.ingest.ingest_packet import IngestPacket


class IngestRegistry:
    def __init__(self, adapters: tuple[IngestAdapter, ...] | None = None) -> None:
        self._adapters: dict[str, IngestAdapter] = {}
        self._ordered_adapter_ids: list[str] = []
        for adapter in adapters or (
            AuditArtifactIngestAdapter(),
            JsonIngestAdapter(),
            FilesystemIngestAdapter(),
        ):
            self.register(adapter)

    def register(self, adapter: IngestAdapter) -> None:
        adapter_id = adapter.descriptor.adapter_id
        if adapter_id in self._adapters:
            raise ValueError(f"duplicate ingest adapter: {adapter_id}")
        self._adapters[adapter_id] = adapter
        self._ordered_adapter_ids.append(adapter_id)

    def get(self, adapter_id: str) -> IngestAdapter:
        try:
            return self._adapters[adapter_id]
        except KeyError as exc:
            raise KeyError(f"unknown ingest adapter: {adapter_id}") from exc

    def list_descriptors(self) -> tuple[IngestAdapterDescriptor, ...]:
        return tuple(self._adapters[adapter_id].descriptor for adapter_id in self._ordered_adapter_ids)

    def resolve(self, repository_root: Path | str, source_path: Path | str) -> IngestAdapter:
        root = Path(repository_root).resolve()
        candidate = Path(source_path)
        resolved = (
            candidate.resolve()
            if candidate.is_absolute()
            else (root / candidate).resolve()
        )
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("ingest only supports local repository sources") from exc
        if not resolved.is_file():
            raise ValueError("ingest source must be an existing file")
        for adapter_id in self._ordered_adapter_ids:
            adapter = self._adapters[adapter_id]
            if adapter.supports(root, resolved):
                return adapter
        raise ValueError("no ingest adapter available for source")

    def ingest(self, repository_root: Path | str, source_path: Path | str) -> IngestPacket:
        return self.resolve(repository_root, source_path).ingest(repository_root, source_path)


def build_default_ingest_registry() -> IngestRegistry:
    return IngestRegistry()


DEFAULT_INGEST_REGISTRY = build_default_ingest_registry()
