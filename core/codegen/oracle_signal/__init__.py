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
from core.codegen.oracle_signal.holler_oracle_ingest_wiring import (
    build_holler_oracle_ingest_wiring,
)
from core.codegen.oracle_signal.holler_oracle_measurement_readiness import (
    build_holler_oracle_measurement_readiness,
)
from core.codegen.oracle_signal.holler_oracle_shadow_dryrun import (
    build_holler_oracle_shadow_dryrun,
)
from core.codegen.oracle_signal.holler_oracle_shadow_measurement import (
    build_holler_oracle_shadow_measurement,
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
from core.codegen.oracle_signal.oracle_ingest_wiring_builder import (
    build_oracle_ingest_wiring,
    build_oracle_ingest_wiring_receipt,
)
from core.codegen.oracle_signal.oracle_measurement_readiness_assessor import (
    build_oracle_measurement_readiness,
    build_oracle_measurement_readiness_receipt,
)
from core.codegen.oracle_signal.oracle_operator_decision_intake import (
    build_oracle_operator_decision_intake,
)
from core.codegen.oracle_signal.oracle_shadow_dryrun_executor import (
    build_oracle_shadow_dryrun,
    build_oracle_shadow_dryrun_receipt,
)
from core.codegen.oracle_signal.oracle_shadow_measurement_executor import (
    build_oracle_shadow_measurement,
    build_oracle_shadow_measurement_receipt,
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
    "build_holler_oracle_ingest_wiring",
    "build_holler_oracle_measurement_readiness",
    "build_holler_oracle_shadow_dryrun",
    "build_holler_oracle_shadow_measurement",
    "build_oracle_adversarial_fixture",
    "build_oracle_calibration_report",
    "build_oracle_holler_intake",
    "build_oracle_ingest_wiring",
    "build_oracle_ingest_wiring_receipt",
    "build_oracle_measurement_readiness",
    "build_oracle_measurement_readiness_receipt",
    "build_oracle_operator_decision_intake",
    "build_oracle_schema_registry",
    "build_oracle_schema_validation_fixture_set",
    "build_oracle_schema_validation_receipt",
    "build_oracle_signal_envelope",
    "build_oracle_signal_layer_completion_receipt",
    "build_oracle_shadow_dryrun",
    "build_oracle_shadow_dryrun_receipt",
    "build_oracle_shadow_measurement",
    "build_oracle_shadow_measurement_receipt",
    "build_shadow_replay_harness_stub",
    "SCHEMA_BY_PACKET_KEY",
    "validate_holler_oracle_batch_evolution",
    "validate_oracle_packet",
    "validate_oracle_schema_packets",
]
