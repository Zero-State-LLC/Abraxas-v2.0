"""Explicit ports for clock, storage, and provider adapters."""

from core.ports.clock import Clock, FixedClock, SystemClock
from core.ports.provider import (
    DeniedProvider,
    FixtureProvider,
    ProviderDeniedError,
    ProviderError,
    ProviderPort,
    gated_invoke,
)
from core.ports.storage import ArtifactStore, FilesystemArtifactStore

__all__ = [
    "ArtifactStore",
    "Clock",
    "DeniedProvider",
    "FilesystemArtifactStore",
    "FixedClock",
    "FixtureProvider",
    "ProviderDeniedError",
    "ProviderError",
    "ProviderPort",
    "SystemClock",
    "gated_invoke",
]
