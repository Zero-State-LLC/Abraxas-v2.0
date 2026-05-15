"""Opt-in runtime performance profiling helpers for ABRAXAS v2.0."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Iterator, Mapping

from core.canonical.json import write_canonical_json
from core.diagnostics import stable_correlation_id

PATCH_ID = "PATCH-P8-RUNTIME-PERFORMANCE-PROFILING-001"
PROFILE_ENV_FLAG = "ABRAXAS_PROFILE_RUNTIME"

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"", "0", "false", "no", "off"})


def _normalize_path(value: str | Path) -> str:
    if isinstance(value, Path):
        return value.as_posix()
    return str(value)


def runtime_profiling_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Return whether runtime profiling is explicitly enabled."""
    source = os.environ if env is None else env
    raw = source.get(PROFILE_ENV_FLAG)
    if raw is None:
        return False
    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return False


def stable_phase_name(surface: str, phase: str) -> str:
    """Build a stable phase label for runtime profiling."""
    return f"{surface}.{phase}"


def build_profile_correlation_id(
    namespace: str,
    *,
    artifact_path: str | Path | None = None,
    context: Any | None = None,
) -> str:
    """Build a deterministic profiling correlation identifier."""
    return stable_correlation_id(
        f"runtime_profile.{namespace}",
        artifact_path=artifact_path,
        context=context,
    )


@dataclass(slots=True)
class RuntimeProfiler:
    """Collect observational runtime timings and emit a deterministic packet."""

    output_path: str | Path
    enabled: bool = field(default_factory=runtime_profiling_enabled)
    _measured_surfaces: set[str] = field(default_factory=set, init=False)
    _phase_timings: dict[str, dict[str, Any]] = field(default_factory=dict, init=False)
    _artifact_paths: dict[str, str] = field(default_factory=dict, init=False)
    _correlation_ids: dict[str, str] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.output_path = Path(self.output_path)
        self.record_artifact("profile_artifact", self.output_path)

    def record_surface(self, surface: str) -> None:
        if not self.enabled:
            return
        self._measured_surfaces.add(surface)

    def record_artifact(self, name: str, path: str | Path) -> None:
        if not self.enabled:
            return
        self._artifact_paths[name] = _normalize_path(path)

    def record_correlation(
        self,
        name: str,
        correlation_id: str | None = None,
        *,
        namespace: str | None = None,
        artifact_path: str | Path | None = None,
        context: Any | None = None,
    ) -> str | None:
        if not self.enabled:
            return None
        resolved = correlation_id
        if resolved is None:
            if namespace is None:
                raise ValueError("namespace is required when correlation_id is omitted")
            resolved = build_profile_correlation_id(
                namespace,
                artifact_path=artifact_path,
                context=context,
            )
        self._correlation_ids[name] = resolved
        return resolved

    @contextmanager
    def measure(
        self,
        surface: str,
        phase: str,
    ) -> Iterator[None]:
        if not self.enabled:
            yield
            return
        self.record_surface(surface)
        phase_name = stable_phase_name(surface, phase)
        started = perf_counter_ns()
        try:
            yield
        finally:
            self._phase_timings[phase_name] = {
                "duration_ns": max(perf_counter_ns() - started, 0),
                "observational_only": True,
            }

    def build_packet(
        self,
        *,
        final_status: str = "PASS",
        remaining_blockers: list[str] | None = None,
    ) -> dict[str, Any]:
        blockers = [] if remaining_blockers is None else list(remaining_blockers)
        return {
            "patch_id": PATCH_ID,
            "profile_enabled": self.enabled,
            "measured_surfaces": sorted(self._measured_surfaces),
            "phase_timings": {
                phase_name: self._phase_timings[phase_name]
                for phase_name in sorted(self._phase_timings)
            },
            "artifact_paths": {
                key: self._artifact_paths[key] for key in sorted(self._artifact_paths)
            },
            "correlation_ids": {
                key: self._correlation_ids[key] for key in sorted(self._correlation_ids)
            },
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
            "final_status": final_status,
            "remaining_blockers": blockers,
        }

    def write(
        self,
        *,
        final_status: str = "PASS",
        remaining_blockers: list[str] | None = None,
    ) -> Path | None:
        if not self.enabled:
            return None
        write_canonical_json(
            self.output_path,
            self.build_packet(
                final_status=final_status,
                remaining_blockers=remaining_blockers,
            ),
        )
        return self.output_path
