"""Oracle Signal Layer advisory canon-extension builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
This package is an advisory extension only. It does not mutate canon,
runtime, scheduler, queue, MCP, GitHub, or Notion authority.
"""

from __future__ import annotations

from core.codegen.oracle_signal.holler_oracle_ingest_stub import (
    build_holler_oracle_ingest_stub,
    build_shadow_replay_harness_stub,
)
from core.codegen.oracle_signal.holler_oracle_schema_validator import (
    validate_holler_oracle_batch_evolution,
)
from core.codegen.oracle_signal.oracle_signal_intake_builder import (
    ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
    build_oracle_adversarial_fixture,
    build_oracle_calibration_report,
    build_oracle_holler_intake,
    build_oracle_schema_registry,
    build_oracle_signal_envelope,
    build_oracle_signal_layer_completion_receipt,
)
from core.codegen.oracle_signal.oracle_schema_validator import (
    SCHEMA_BY_PACKET_KEY,
    build_oracle_schema_validation_fixture_set,
    build_oracle_schema_validation_receipt,
    validate_oracle_packet,
    validate_oracle_schema_packets,
)

__all__ = [
    "ORACLE_CANON_EXTENSION_SCHEMA_PATHS",
    "build_holler_oracle_ingest_stub",
    "build_oracle_adversarial_fixture",
    "build_oracle_calibration_report",
    "build_oracle_holler_intake",
    "build_oracle_schema_registry",
    "build_oracle_schema_validation_fixture_set",
    "build_oracle_schema_validation_receipt",
    "build_oracle_signal_envelope",
    "build_oracle_signal_layer_completion_receipt",
    "build_shadow_replay_harness_stub",
    "SCHEMA_BY_PACKET_KEY",
    "validate_holler_oracle_batch_evolution",
    "validate_oracle_packet",
    "validate_oracle_schema_packets",
]
