#!/usr/bin/env python3
"""Compatibility CLI for Oracle Signal Layer advisory receipt emission."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.codegen.loop805_observability import (  # noqa: E402
    build_oracle_full_live_endpoint_env_intake_observability_hook,
    build_oracle_full_live_runtime_execution_attempt_observability_hook,
    build_oracle_full_live_runtime_preflight_observability_hook,
    build_oracle_persistent_execution_secret_vault_plan_observability_hook,
    build_oracle_persistent_sandbox_secret_store_stub_observability_hook,
    build_oracle_sandbox_probe_gate_proposal_observability_hook,
)
from core.codegen.oracle_signal import (  # noqa: E402
    build_holler_oracle_full_live_runtime_preflight,
    build_oracle_full_live_endpoint_env_intake,
    build_oracle_full_live_endpoint_env_intake_receipt,
    build_oracle_full_live_runtime_execution_attempt,
    build_oracle_full_live_runtime_execution_attempt_receipt,
    build_oracle_full_live_runtime_preflight,
    build_oracle_full_live_runtime_preflight_receipt,
    build_oracle_persistent_execution_secret_vault_plan,
    build_oracle_persistent_execution_secret_vault_plan_receipt,
    build_oracle_persistent_sandbox_secret_store_stub,
    build_oracle_persistent_sandbox_secret_store_stub_receipt,
    build_oracle_sandbox_probe_gate_proposal,
    build_oracle_sandbox_probe_gate_proposal_receipt,
    validate_oracle_schema_packets,
)
from tests.codegen.test_oracle_signal_layer_completion import (  # noqa: E402
    MERGE_SHA,
    TIMESTAMP,
    _build_packets,
)
from core.codegen.oracle_signal.holler_oracle_schema_validator import (  # noqa: E402
    validate_holler_oracle_batch_evolution,
)
from core.codegen.oracle_signal.oracle_schema_validator import (  # noqa: E402
    build_oracle_schema_validation_receipt,
)


_REDACTED_VALUE_FIELD_MARKERS = (
    "api_key",
    "credential",
    "endpoint_url",
    "token",
)


def _endpoint_environment() -> dict[str, str | None]:
    return {
        "ORACLE_SIGNAL_ENDPOINT_URL": os.environ.get("ORACLE_SIGNAL_ENDPOINT_URL"),
        "HOLLERSPORTS_BATCH_ENDPOINT_URL": os.environ.get(
            "HOLLERSPORTS_BATCH_ENDPOINT_URL"
        ),
    }


def _redact_receipt_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = str(key).lower()
            if (
                isinstance(item, str)
                and any(
                    marker in normalized_key
                    for marker in _REDACTED_VALUE_FIELD_MARKERS
                )
            ):
                redacted[str(key)] = "<redacted>"
            else:
                redacted[str(key)] = _redact_receipt_payload(item)
        return redacted
    if isinstance(value, list):
        return [_redact_receipt_payload(item) for item in value]
    return value


def _write_json(path: str | None, packet: Mapping[str, Any]) -> None:
    if not path:
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(_redact_receipt_payload(packet), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {output}")  # codeql[py/clear-text-logging-sensitive-data]


def _validation_receipt(packets: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    validation_results = validate_oracle_schema_packets(
        packets=packets,
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_validation = validate_holler_oracle_batch_evolution(
        holler_intake=packets["oracle_holler_intake"],
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    return build_oracle_schema_validation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        validation_results={
            **validation_results,
            "holler_oracle_batch_evolution": holler_validation,
        },
    )


def _with_runtime_packets(base: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    packets = dict(base)
    env = _endpoint_environment()
    preflight = build_oracle_full_live_runtime_preflight(
        timestamp=TIMESTAMP,
        oracle_full_live_runtime_command=packets["full_live_runtime_command"],
        oracle_full_live_runtime_command_receipt=packets[
            "full_live_runtime_command_receipt"
        ],
        endpoint_environment=env,
    )
    holler_preflight = build_holler_oracle_full_live_runtime_preflight(
        timestamp=TIMESTAMP,
        holler_intake=packets["holler"],
        oracle_full_live_runtime_preflight=preflight,
    )
    preflight_hook = build_oracle_full_live_runtime_preflight_observability_hook(
        timestamp=TIMESTAMP,
        full_live_runtime_preflight_receipt_hash="e" * 64,
        full_live_runtime_preflight_schema_path=(
            "contracts/canon/oracle/oracle_full_live_runtime_preflight.v1.schema.json"
        ),
        preflight_status=preflight["preflight_status"],
    )
    preflight_receipt = build_oracle_full_live_runtime_preflight_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_full_live_runtime_preflight=preflight,
        holler_oracle_full_live_runtime_preflight=holler_preflight,
        observability_hook=preflight_hook,
    )
    endpoint_intake = build_oracle_full_live_endpoint_env_intake(
        timestamp=TIMESTAMP,
        oracle_full_live_runtime_preflight_receipt=preflight_receipt,
    )
    endpoint_intake_hook = (
        build_oracle_full_live_endpoint_env_intake_observability_hook(
            timestamp=TIMESTAMP,
            endpoint_env_intake_receipt_hash="f" * 64,
            endpoint_env_intake_schema_path=(
                "contracts/canon/oracle/"
                "oracle_full_live_endpoint_env_intake.v1.schema.json"
            ),
        )
    )
    endpoint_intake_receipt = build_oracle_full_live_endpoint_env_intake_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_full_live_endpoint_env_intake=endpoint_intake,
        observability_hook=endpoint_intake_hook,
    )
    execution_attempt = build_oracle_full_live_runtime_execution_attempt(
        timestamp=TIMESTAMP,
        oracle_full_live_runtime_command=packets["full_live_runtime_command"],
        oracle_full_live_runtime_command_receipt=packets[
            "full_live_runtime_command_receipt"
        ],
        oracle_full_live_runtime_preflight=preflight,
        endpoint_environment=env,
    )
    execution_hook = build_oracle_full_live_runtime_execution_attempt_observability_hook(
        timestamp=TIMESTAMP,
        runtime_execution_attempt_receipt_hash="0" * 64,
        runtime_execution_attempt_schema_path=(
            "contracts/canon/oracle/oracle_full_live_runtime_execution.v1.schema.json"
        ),
        attempt_status=execution_attempt["attempt_status"],
        external_call_count=execution_attempt["execution_summary"][
            "external_call_count"
        ],
    )
    execution_receipt = build_oracle_full_live_runtime_execution_attempt_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_full_live_runtime_execution_attempt=execution_attempt,
        observability_hook=execution_hook,
    )
    packets.update(
        {
            "full_live_runtime_preflight": preflight,
            "full_live_runtime_preflight_receipt": preflight_receipt,
            "full_live_endpoint_env_intake": endpoint_intake,
            "full_live_endpoint_env_intake_receipt": endpoint_intake_receipt,
            "full_live_runtime_execution_attempt": execution_attempt,
            "full_live_runtime_execution_attempt_receipt": execution_receipt,
        }
    )
    return packets


def _with_persistent_packets(base: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    packets = _with_runtime_packets(base)
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp=TIMESTAMP,
        oracle_full_live_endpoint_env_intake_receipt=packets[
            "full_live_endpoint_env_intake_receipt"
        ],
        oracle_full_live_runtime_preflight_receipt=packets[
            "full_live_runtime_preflight_receipt"
        ],
        oracle_full_live_runtime_execution_attempt_receipt=packets[
            "full_live_runtime_execution_attempt_receipt"
        ],
    )
    plan_hook = build_oracle_persistent_execution_secret_vault_plan_observability_hook(
        timestamp=TIMESTAMP,
        persistent_execution_secret_vault_plan_receipt_hash="7" * 64,
        persistent_execution_secret_vault_plan_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_execution_secret_vault_plan.v1.schema.json"
        ),
    )
    plan_receipt = build_oracle_persistent_execution_secret_vault_plan_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_execution_secret_vault_plan=plan,
        observability_hook=plan_hook,
    )
    stub = build_oracle_persistent_sandbox_secret_store_stub(
        timestamp=TIMESTAMP,
        oracle_persistent_execution_secret_vault_plan_receipt=plan_receipt,
    )
    stub_hook = build_oracle_persistent_sandbox_secret_store_stub_observability_hook(
        timestamp=TIMESTAMP,
        persistent_sandbox_secret_store_stub_receipt_hash="8" * 64,
        persistent_sandbox_secret_store_stub_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_sandbox_secret_store_stub.v1.schema.json"
        ),
    )
    stub_receipt = build_oracle_persistent_sandbox_secret_store_stub_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_sandbox_secret_store_stub=stub,
        observability_hook=stub_hook,
    )
    proposal = build_oracle_sandbox_probe_gate_proposal(
        timestamp=TIMESTAMP,
        oracle_persistent_sandbox_secret_store_stub_receipt=stub_receipt,
    )
    proposal_hook = build_oracle_sandbox_probe_gate_proposal_observability_hook(
        timestamp=TIMESTAMP,
        sandbox_probe_gate_proposal_receipt_hash="9" * 64,
        sandbox_probe_gate_proposal_schema_path=(
            "contracts/canon/oracle/oracle_sandbox_probe_gate_proposal.v1.schema.json"
        ),
    )
    proposal_receipt = build_oracle_sandbox_probe_gate_proposal_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_sandbox_probe_gate_proposal=proposal,
        observability_hook=proposal_hook,
    )
    packets.update(
        {
            "oracle_persistent_execution_secret_vault_plan": plan,
            "oracle_persistent_execution_secret_vault_plan_receipt": plan_receipt,
            "oracle_persistent_sandbox_secret_store_stub": stub,
            "oracle_persistent_sandbox_secret_store_stub_receipt": stub_receipt,
            "oracle_sandbox_probe_gate_proposal": proposal,
            "oracle_sandbox_probe_gate_proposal_receipt": proposal_receipt,
        }
    )
    return packets


BASE_PACKET_KEYS = [
    "envelope",
    "holler",
    "calibration",
    "adversarial",
    "registry",
    "wiring",
    "dryrun",
    "readiness",
    "shadow_measurement",
    "measurement_proposal",
    "authorization_proposal",
    "decision_review_candidate",
    "authorization_decision_record",
    "live_wiring_preparation",
    "production_activation_ready",
    "full_live_execution",
    "full_live_run_control",
    "full_live_runtime_command",
]

PACKET_KEY_ALIASES = {
    "envelope": "oracle_signal_envelope",
    "holler": "oracle_holler_intake",
    "calibration": "oracle_calibration_report",
    "adversarial": "oracle_adversarial_fixture",
    "registry": "oracle_schema_registry",
    "wiring": "oracle_ingest_wiring",
    "dryrun": "oracle_shadow_dryrun",
    "readiness": "oracle_measurement_readiness",
    "shadow_measurement": "oracle_shadow_measurement",
    "measurement_proposal": "oracle_measurement_proposal",
    "authorization_proposal": "oracle_measurement_authorization_proposal",
    "decision_review_candidate": (
        "oracle_measurement_authorization_decision_review_candidate"
    ),
    "authorization_decision_record": "oracle_authorization_decision_record",
    "live_wiring_preparation": "oracle_live_wiring_preparation",
    "production_activation_ready": "oracle_production_activation_ready",
    "full_live_execution": "oracle_full_live_execution",
    "full_live_run_control": "oracle_full_live_run_control",
    "full_live_runtime_command": "oracle_full_live_runtime_command",
    "full_live_runtime_preflight": "oracle_full_live_runtime_preflight",
    "full_live_endpoint_env_intake": "oracle_full_live_endpoint_env_intake",
    "full_live_runtime_execution_attempt": "oracle_full_live_runtime_execution",
    "oracle_persistent_execution_secret_vault_plan": (
        "oracle_persistent_execution_secret_vault_plan"
    ),
    "oracle_persistent_sandbox_secret_store_stub": (
        "oracle_persistent_sandbox_secret_store_stub"
    ),
    "oracle_sandbox_probe_gate_proposal": "oracle_sandbox_probe_gate_proposal",
}


def _schema_packets(
    packets: Mapping[str, Mapping[str, Any]],
    keys: list[str],
) -> dict[str, Mapping[str, Any]]:
    return {PACKET_KEY_ALIASES[key]: packets[key] for key in keys}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-oracle-schemas", action="store_true")
    flag_destinations = {
        "emit-oracle-persistent-execution-secret-vault-plan": (
            "emit_oracle_persistent_execution_vault_plan"
        ),
        "emit-oracle-persistent-sandbox-secret-store-stub": (
            "emit_oracle_persistent_sandbox_store_stub"
        ),
    }
    for flag in (
        "emit-oracle-validation",
        "emit-oracle-shadow-dryrun",
        "emit-oracle-measurement-readiness",
        "emit-oracle-shadow-measurement",
        "emit-oracle-measurement-proposal",
        "emit-oracle-measurement-authorization-proposal",
        "emit-oracle-measurement-authorization-decision-review-candidate",
        "emit-oracle-layer-complete",
        "emit-oracle-live-wiring-preparation",
        "emit-oracle-production-activation-ready",
        "emit-oracle-full-live",
        "emit-oracle-full-live-run-control",
        "emit-oracle-full-live-runtime-command",
        "emit-oracle-full-live-runtime-preflight",
        "emit-oracle-full-live-endpoint-env-intake",
        "emit-oracle-full-live-runtime-execution",
        "emit-oracle-persistent-execution-secret-vault-plan",
        "emit-oracle-persistent-sandbox-secret-store-stub",
        "emit-oracle-sandbox-probe-gate-proposal",
    ):
        flag_kwargs = {"action": "store_true"}
        if flag in flag_destinations:
            flag_kwargs["dest"] = flag_destinations[flag]
        parser.add_argument(f"--{flag}", **flag_kwargs)
    option_destinations = {
        "oracle-persistent-execution-secret-vault-plan-out": (
            "oracle_persistent_execution_vault_plan_out"
        ),
        "oracle-persistent-sandbox-secret-store-stub-out": (
            "oracle_persistent_sandbox_store_stub_out"
        ),
    }
    for option in (
        "oracle-validation-out",
        "oracle-shadow-dryrun-out",
        "oracle-measurement-readiness-out",
        "oracle-shadow-measurement-out",
        "oracle-measurement-proposal-out",
        "oracle-measurement-authorization-proposal-out",
        "oracle-measurement-authorization-decision-review-candidate-out",
        "oracle-completion-out",
        "oracle-live-wiring-preparation-out",
        "oracle-production-activation-ready-out",
        "oracle-full-live-out",
        "oracle-full-live-run-control-out",
        "oracle-full-live-runtime-command-out",
        "oracle-full-live-runtime-preflight-out",
        "oracle-full-live-endpoint-env-intake-out",
        "oracle-full-live-runtime-execution-out",
        "oracle-persistent-execution-secret-vault-plan-out",
        "oracle-persistent-sandbox-secret-store-stub-out",
        "oracle-sandbox-probe-gate-proposal-out",
    ):
        option_kwargs = {}
        if option in option_destinations:
            option_kwargs["dest"] = option_destinations[option]
        parser.add_argument(f"--{option}", **option_kwargs)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    base = _build_packets()
    runtime = _with_runtime_packets(base)
    persistent = _with_persistent_packets(base)

    outputs = [
        (args.emit_oracle_validation, args.oracle_validation_out, base["validation_receipt"]),
        (args.emit_oracle_shadow_dryrun, args.oracle_shadow_dryrun_out, base["dryrun_receipt"]),
        (
            args.emit_oracle_measurement_readiness,
            args.oracle_measurement_readiness_out,
            base["readiness_receipt"],
        ),
        (
            args.emit_oracle_shadow_measurement,
            args.oracle_shadow_measurement_out,
            base["shadow_measurement_receipt"],
        ),
        (
            args.emit_oracle_measurement_proposal,
            args.oracle_measurement_proposal_out,
            base["measurement_proposal_receipt"],
        ),
        (
            args.emit_oracle_measurement_authorization_proposal,
            args.oracle_measurement_authorization_proposal_out,
            base["authorization_receipt"],
        ),
        (
            args.emit_oracle_measurement_authorization_decision_review_candidate,
            args.oracle_measurement_authorization_decision_review_candidate_out,
            base["decision_review_receipt"],
        ),
        (args.emit_oracle_layer_complete, args.oracle_completion_out, base["receipt"]),
        (
            args.emit_oracle_live_wiring_preparation,
            args.oracle_live_wiring_preparation_out,
            base["live_wiring_receipt"],
        ),
        (
            args.emit_oracle_production_activation_ready,
            args.oracle_production_activation_ready_out,
            base["production_activation_receipt"],
        ),
        (args.emit_oracle_full_live, args.oracle_full_live_out, base["full_live_receipt"]),
        (
            args.emit_oracle_full_live_run_control,
            args.oracle_full_live_run_control_out,
            base["full_live_run_control_receipt"],
        ),
        (
            args.emit_oracle_full_live_runtime_command,
            args.oracle_full_live_runtime_command_out,
            base["full_live_runtime_command_receipt"],
        ),
        (
            args.emit_oracle_full_live_runtime_preflight,
            args.oracle_full_live_runtime_preflight_out,
            runtime["full_live_runtime_preflight_receipt"],
        ),
        (
            args.emit_oracle_full_live_endpoint_env_intake,
            args.oracle_full_live_endpoint_env_intake_out,
            runtime["full_live_endpoint_env_intake_receipt"],
        ),
        (
            args.emit_oracle_full_live_runtime_execution,
            args.oracle_full_live_runtime_execution_out,
            runtime["full_live_runtime_execution_attempt_receipt"],
        ),
        (
            args.emit_oracle_persistent_execution_vault_plan,
            args.oracle_persistent_execution_vault_plan_out,
            persistent["oracle_persistent_execution_secret_vault_plan_receipt"],
        ),
        (
            args.emit_oracle_persistent_sandbox_store_stub,
            args.oracle_persistent_sandbox_store_stub_out,
            persistent["oracle_persistent_sandbox_secret_store_stub_receipt"],
        ),
        (
            args.emit_oracle_sandbox_probe_gate_proposal,
            args.oracle_sandbox_probe_gate_proposal_out,
            persistent["oracle_sandbox_probe_gate_proposal_receipt"],
        ),
    ]
    for enabled, path, packet in outputs:
        if enabled:
            _write_json(path, packet)

    if args.oracle_validation_out and (
        args.validate_oracle_schemas
        or args.emit_oracle_validation
        or args.emit_oracle_full_live_runtime_preflight
        or args.emit_oracle_full_live_runtime_execution
        or args.emit_oracle_persistent_execution_vault_plan
        or args.emit_oracle_persistent_sandbox_store_stub
        or args.emit_oracle_sandbox_probe_gate_proposal
    ):
        if args.emit_oracle_persistent_execution_vault_plan:
            keys = BASE_PACKET_KEYS + [
                "full_live_runtime_preflight",
                "full_live_endpoint_env_intake",
                "full_live_runtime_execution_attempt",
                "oracle_persistent_execution_secret_vault_plan",
            ]
            validation = _validation_receipt(_schema_packets(persistent, keys))
        elif args.emit_oracle_persistent_sandbox_store_stub:
            keys = BASE_PACKET_KEYS + [
                "full_live_runtime_preflight",
                "full_live_endpoint_env_intake",
                "full_live_runtime_execution_attempt",
                "oracle_persistent_execution_secret_vault_plan",
                "oracle_persistent_sandbox_secret_store_stub",
            ]
            validation = _validation_receipt(_schema_packets(persistent, keys))
        elif args.emit_oracle_sandbox_probe_gate_proposal or args.emit_oracle_full_live_runtime_execution:
            keys = BASE_PACKET_KEYS + [
                "full_live_runtime_preflight",
                "full_live_endpoint_env_intake",
                "full_live_runtime_execution_attempt",
                "oracle_persistent_execution_secret_vault_plan",
                "oracle_persistent_sandbox_secret_store_stub",
                "oracle_sandbox_probe_gate_proposal",
            ]
            validation = _validation_receipt(_schema_packets(persistent, keys))
        elif args.emit_oracle_full_live_runtime_preflight:
            keys = BASE_PACKET_KEYS + [
                "full_live_runtime_preflight",
                "full_live_endpoint_env_intake",
            ]
            validation = _validation_receipt(_schema_packets(runtime, keys))
        else:
            validation = base["validation_receipt"]
        _write_json(args.oracle_validation_out, validation)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
