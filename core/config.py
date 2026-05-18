"""Config and path helpers for ABRAXAS v2.0."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_TRUE_VALUES = frozenset({"1", "true", "yes"})
_FALSE_VALUES = frozenset({"", "0", "false", "no", "off"})


def parse_env_bool(name: str, *, default: bool) -> bool:
    """Parse a boolean environment variable with explicit accepted values."""
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(f"{name} must be one of: 1, true, yes, 0, false, no, off")


def parse_env_path(name: str, *, default: Path) -> Path:
    """Parse a path environment variable, rejecting blank overrides."""
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip()
    if not normalized:
        raise ValueError(f"{name} must not be blank")
    return Path(normalized)


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    """Centralized operational paths derived from stable defaults and env overrides."""

    contracts_dir: Path
    out_dir: Path

    @classmethod
    def from_env(cls) -> RuntimePaths:
        return cls(
            contracts_dir=parse_env_path("CONTRACTS_DIR", default=Path("contracts")),
            out_dir=parse_env_path("OUT_DIR", default=Path("out")),
        )

    @property
    def pipelines_contracts_dir(self) -> Path:
        return self.contracts_dir / "pipelines"

    @property
    def audit_dir(self) -> Path:
        return self.out_dir / "audit"

    @property
    def runtime_performance_profile_latest(self) -> Path:
        return self.audit_dir / "runtime_performance_profile_001.latest.json"

    @property
    def runtime_benchmark_latest(self) -> Path:
        return self.audit_dir / "runtime_benchmark_001.latest.json"

    @property
    def stabilization_release_readiness_latest(self) -> Path:
        return self.audit_dir / "stabilization_release_readiness_001.latest.json"

    @property
    def governance_freeze_baseline_latest(self) -> Path:
        return self.audit_dir / "governance_freeze_baseline_001.latest.json"

    @property
    def operator_runtime_console_latest(self) -> Path:
        return self.audit_dir / "operator_runtime_console_001.latest.json"

    @property
    def operator_action_queue_latest(self) -> Path:
        return self.audit_dir / "operator_action_queue_001.latest.json"

    @property
    def incremental_replay_latest(self) -> Path:
        return self.audit_dir / "incremental_replay_001.latest.json"

    @property
    def contracts_output_dir(self) -> Path:
        return self.out_dir / "contracts"

    @property
    def state_dir(self) -> Path:
        return self.out_dir / "state"

    @property
    def registry_latest(self) -> Path:
        return self.out_dir / "registry" / "latest.json"

    @property
    def validation_latest(self) -> Path:
        return self.out_dir / "validation" / "latest.json"

    @property
    def projection_aal_viz_latest(self) -> Path:
        return self.out_dir / "projections" / "aal_viz.latest.json"

    @property
    def aal_viz_runtime_projection_latest(self) -> Path:
        return self.out_dir / "projections" / "aal_viz_runtime_projection_001.latest.json"

    @property
    def live_projection_refresh_latest(self) -> Path:
        return self.out_dir / "projections" / "live_projection_refresh_001.latest.json"

    @property
    def temporal_snapshot_spine_latest(self) -> Path:
        return self.out_dir / "projections" / "temporal_snapshot_spine_001.latest.json"

    @property
    def projection_bus_latest(self) -> Path:
        return self.out_dir / "projections" / "projection_bus_001.latest.json"

    @property
    def projection_chronoscope_latest(self) -> Path:
        return self.out_dir / "projections" / "projection_chronoscope_001.latest.json"

    @property
    def aal_viz_graph_render_packet_latest(self) -> Path:
        return self.out_dir / "projections" / "aal_viz_graph_render_packet_001.latest.json"

    @property
    def read_only_transport_latest(self) -> Path:
        return self.out_dir / "projections" / "read_only_transport_001.latest.json"

    @property
    def temporal_state_diff_latest(self) -> Path:
        return self.out_dir / "projections" / "temporal_state_diff_001.latest.json"

    @property
    def multi_run_convergence_latest(self) -> Path:
        return self.out_dir / "projections" / "multi_run_convergence_001.latest.json"

    @property
    def cross_run_topology_fusion_latest(self) -> Path:
        return self.out_dir / "projections" / "cross_run_topology_fusion_001.latest.json"

    @property
    def temporal_topology_cartography_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "temporal_topology_cartography_001.latest.json"
        )

    @property
    def temporal_regime_transition_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "temporal_regime_transition_001.latest.json"
        )

    @property
    def temporal_stability_pressure_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "temporal_stability_pressure_001.latest.json"
        )

    @property
    def temporal_persistence_memory_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "temporal_persistence_memory_001.latest.json"
        )

    @property
    def temporal_resonance_coherence_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "temporal_resonance_coherence_001.latest.json"
        )

    @property
    def coherence_field_operator_surface_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "coherence_field_operator_surface_001.latest.json"
        )

    @property
    def operator_attention_weather_latest(self) -> Path:
        return (
            self.out_dir
            / "projections"
            / "operator_attention_weather_001.latest.json"
        )

    @property
    def execution_latest(self) -> Path:
        return self.out_dir / "execution" / "latest.json"

    @property
    def replay_latest(self) -> Path:
        return self.out_dir / "replay" / "latest.json"

    @property
    def telemetry_latest(self) -> Path:
        return self.out_dir / "telemetry" / "latest.json"

    @property
    def topology_latest(self) -> Path:
        return self.out_dir / "topology" / "latest.json"

    @property
    def state_runtime_latest(self) -> Path:
        return self.state_dir / "runtime.latest.json"


def api_public_readonly_enabled() -> bool:
    """Return whether the public readonly API surface is explicitly enabled."""
    return parse_env_bool("ABRAXAS_API_PUBLIC_READONLY", default=False)
