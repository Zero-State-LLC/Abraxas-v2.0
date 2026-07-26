"""Application runtime context — settings + injected ports (not a god object)."""

from __future__ import annotations

from dataclasses import dataclass

from core.ports.clock import Clock, SystemClock
from core.ports.provider import DeniedProvider, ProviderPort
from core.ports.storage import ArtifactStore, FilesystemArtifactStore
from core.settings import RuntimeSettings, load_runtime_settings


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    settings: RuntimeSettings
    clock: Clock
    storage: ArtifactStore
    provider: ProviderPort

    @classmethod
    def build(
        cls,
        settings: RuntimeSettings | None = None,
        *,
        clock: Clock | None = None,
        storage: ArtifactStore | None = None,
        provider: ProviderPort | None = None,
    ) -> RuntimeContext:
        resolved = settings or load_runtime_settings()
        resolved_clock = clock or SystemClock()
        resolved_storage = storage or FilesystemArtifactStore(
            resolved.repo_root,
            resolved.resolved_out_dir(),
        )
        resolved_provider = provider or DeniedProvider()
        return cls(
            settings=resolved,
            clock=resolved_clock,
            storage=resolved_storage,
            provider=resolved_provider,
        )
