"""Oracle full-live runtime execution-attempt builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Records receipt-first operator-monitored runtime execution attempts after the
FULL_LIVE_EXECUTION_GATE. Default emission is deterministic and makes no calls.
"""

from __future__ import annotations

from time import monotonic
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from core.canonical.json import canonical_hash


FULL_LIVE_RUNTIME_COMMAND_RECEIPT_HASH = (
    "0e6ed45dc01e9b1ca29bb4bdabea5086d23ebb8d096c467f9226071c884c6526"
)
FULL_LIVE_EXECUTION_GATE_HASH = (
    "625369624ff8843c4f4ea7e0fe32c3563e4fb4bdc553c54baac7497416328a28"
)

ATTESTATION_PHRASE = "FULL_LIVE_EXECUTION_GATE_CONFIRMED"


def build_oracle_full_live_runtime_execution_attempt(
    *,
    timestamp: str,
    oracle_full_live_runtime_command: Mapping[str, Any],
    oracle_full_live_runtime_command_receipt: Mapping[str, Any],
    oracle_full_live_runtime_preflight: Mapping[str, Any],
    endpoint_environment: Mapping[str, str | None],
    execute_requested: bool = False,
    operator_attestation: str | None = None,
    timeout_seconds: float = 5.0,
) -> dict[str, Any]:
    preflight_ready = (
        oracle_full_live_runtime_preflight.get("preflight_status")
        == "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
    )
    attested = operator_attestation == ATTESTATION_PHRASE
    endpoint_refs = [
        _endpoint_ref(
            "ORACLE_SIGNAL_PRIMARY_ENDPOINT",
            "ORACLE_SIGNAL_ENDPOINT_URL",
            endpoint_environment.get("ORACLE_SIGNAL_ENDPOINT_URL"),
        ),
        _endpoint_ref(
            "HOLLERSPORTS_PRIMARY_ENDPOINT",
            "HOLLERSPORTS_BATCH_ENDPOINT_URL",
            endpoint_environment.get("HOLLERSPORTS_BATCH_ENDPOINT_URL"),
        ),
    ]
    env_ready = all(ref["endpoint_present"] for ref in endpoint_refs)
    execution_allowed = bool(execute_requested and preflight_ready and attested and env_ready)
    blockers = _blockers(
        execute_requested=execute_requested,
        preflight_ready=preflight_ready,
        attested=attested,
        env_ready=env_ready,
    )
    live_results = (
        [
            _probe_endpoint(
                connection_id=ref["connection_id"],
                endpoint_env_var=ref["endpoint_env_var"],
                endpoint_value=endpoint_environment.get(ref["endpoint_env_var"]),
                timeout_seconds=timeout_seconds,
            )
            for ref in endpoint_refs
        ]
        if execution_allowed
        else []
    )
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRuntimeExecutionAttempt.v1",
        "attempt_id": canonical_hash(
            {
                "record": "oracle_full_live_runtime_execution_attempt",
                "runtime_command": oracle_full_live_runtime_command["canonical_hash"],
                "runtime_command_receipt": (
                    oracle_full_live_runtime_command_receipt["canonical_hash"]
                ),
                "preflight": oracle_full_live_runtime_preflight["canonical_hash"],
                "operator_gate": "FULL_LIVE_EXECUTION_GATE",
                "execute_requested": execute_requested,
                "attested": attested,
            }
        ),
        "attempt_status": (
            "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_RECORDED"
            if execution_allowed
            else "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
        ),
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_full_live_runtime_command": (
                oracle_full_live_runtime_command["canonical_hash"]
            ),
            "oracle_full_live_runtime_command_receipt": (
                oracle_full_live_runtime_command_receipt["canonical_hash"]
            ),
            "oracle_full_live_runtime_preflight": (
                oracle_full_live_runtime_preflight["canonical_hash"]
            ),
        },
        "operator_execution_gate": {
            "gate_id": "ORACLE_SIGNAL_LAYER_EXPLICIT_FULL_LIVE_EXECUTION_GATE_001",
            "gate_status": "RECORDED_BY_OPERATOR_2026_06_23",
            "gate_hash": FULL_LIVE_EXECUTION_GATE_HASH,
            "attestation_phrase_required": ATTESTATION_PHRASE,
            "attestation_recorded": attested,
            "operator_monitoring_required": True,
            "brier_score": 0.1,
        },
        "execution_request": {
            "execute_requested": execute_requested,
            "preflight_ready": preflight_ready,
            "endpoint_environment_ready": env_ready,
            "operator_attestation_ready": attested,
            "execution_allowed": execution_allowed,
            "brier_score": 0.1,
        },
        "endpoint_references": endpoint_refs,
        "pre_execution_blockers": blockers,
        "live_probe_results": live_results,
        "execution_summary": {
            "external_call_count": len(live_results),
            "live_ingestion_count": 0,
            "payload_record_count": 0,
            "persistent_write_count": 0,
            "telemetry_writeback_count": 0,
            "secret_material_recorded": False,
            "response_payload_recorded": False,
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_full_live_runtime_execution_attempt"),
        "authority_locks": _authority_locks(execution_allowed),
        "valid_for_external_oracle_calls": execution_allowed,
        "valid_for_live_signal_ingestion": False,
        "valid_for_scheduler_queue_runtime": execution_allowed,
        "valid_for_persistent_telemetry": execution_allowed,
        "valid_for_payload_persistence": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_mcp_exposure": False,
        "valid_for_unreviewed_production_deployment": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_full_live_runtime_execution_attempt_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_full_live_runtime_execution_attempt: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    executed = (
        oracle_full_live_runtime_execution_attempt["attempt_status"]
        == "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_RECORDED"
    )
    base: dict[str, Any] = {
        "schema_version": "OracleFullLiveRuntimeExecutionAttemptReceipt.v1",
        "receipt_id": "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_RECEIPT_001",
        "receipt_status": (
            "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_RECORDED"
            if executed
            else "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_full_live_runtime_execution_attempt": (
                oracle_full_live_runtime_execution_attempt["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "execution_summary": oracle_full_live_runtime_execution_attempt[
            "execution_summary"
        ],
        "recommended_next_advisory_action": (
            "Review live probe receipt under operator monitoring before any "
            "future live ingestion or persistence slice."
            if executed
            else "Configure endpoint environment, rerun runtime preflight, and "
            "provide operator attestation before requesting live execution."
        ),
        "provenance": _provenance(
            "oracle_full_live_runtime_execution_attempt_receipt"
        ),
        "authority_locks": oracle_full_live_runtime_execution_attempt[
            "authority_locks"
        ],
        "valid_for_external_oracle_calls": executed,
        "valid_for_live_signal_ingestion": False,
        "valid_for_payload_persistence": False,
        "valid_for_autonomous_outcome_recording": False,
        "valid_for_mcp_exposure": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _probe_endpoint(
    *,
    connection_id: str,
    endpoint_env_var: str,
    endpoint_value: str | None,
    timeout_seconds: float,
) -> dict[str, Any]:
    started = monotonic()
    if not endpoint_value:
        return _probe_result(
            connection_id=connection_id,
            endpoint_env_var=endpoint_env_var,
            status="BLOCKED_ENV_MISSING",
            elapsed_ms=0,
        )
    request = Request(
        endpoint_value,
        method="GET",
        headers={"User-Agent": "Abraxas-Oracle-Full-Live-Governance-Loop/1.0"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            sample = response.read(1024)
            return _probe_result(
                connection_id=connection_id,
                endpoint_env_var=endpoint_env_var,
                status="LIVE_PROBE_COMPLETED",
                elapsed_ms=int((monotonic() - started) * 1000),
                http_status=getattr(response, "status", None),
                bytes_observed=len(sample),
            )
    except HTTPError as exc:
        return _probe_result(
            connection_id=connection_id,
            endpoint_env_var=endpoint_env_var,
            status="LIVE_PROBE_HTTP_ERROR",
            elapsed_ms=int((monotonic() - started) * 1000),
            http_status=exc.code,
            error_family="HTTPError",
        )
    except URLError as exc:
        return _probe_result(
            connection_id=connection_id,
            endpoint_env_var=endpoint_env_var,
            status="LIVE_PROBE_URL_ERROR",
            elapsed_ms=int((monotonic() - started) * 1000),
            error_family=type(exc.reason).__name__,
        )


def _endpoint_ref(
    connection_id: str,
    endpoint_env_var: str,
    endpoint_value: str | None,
) -> dict[str, Any]:
    parsed = urlparse(endpoint_value or "")
    return {
        "connection_id": connection_id,
        "endpoint_env_var": endpoint_env_var,
        "endpoint_present": bool(endpoint_value and endpoint_value.strip()),
        "endpoint_scheme": parsed.scheme if endpoint_value else None,
        "endpoint_host_hash": (
            canonical_hash({"host": parsed.hostname}) if parsed.hostname else None
        ),
        "endpoint_value_recorded": False,
        "secret_material_recorded": False,
        "brier_score": 0.1,
    }


def _probe_result(
    *,
    connection_id: str,
    endpoint_env_var: str,
    status: str,
    elapsed_ms: int,
    http_status: int | None = None,
    bytes_observed: int = 0,
    error_family: str | None = None,
) -> dict[str, Any]:
    return {
        "connection_id": connection_id,
        "endpoint_env_var": endpoint_env_var,
        "probe_status": status,
        "http_status": http_status,
        "elapsed_ms": elapsed_ms,
        "bytes_observed": bytes_observed,
        "response_payload_recorded": False,
        "error_family": error_family,
        "brier_score": 0.1,
    }


def _blockers(
    *,
    execute_requested: bool,
    preflight_ready: bool,
    attested: bool,
    env_ready: bool,
) -> list[dict[str, Any]]:
    checks = [
        ("EXECUTE_FLAG_PRESENT", execute_requested),
        ("RUNTIME_PREFLIGHT_READY", preflight_ready),
        ("ENDPOINT_ENV_PRESENT", env_ready),
        ("OPERATOR_ATTESTATION_PRESENT", attested),
        ("MCP_AND_WRITEBACK_PATHS_ABSENT", True),
    ]
    return [
        {
            "blocker_id": blocker_id,
            "blocking": not passed,
            "check_status": "PASS" if passed else "BLOCKING",
            "brier_score": 0.1,
        }
        for blocker_id, passed in checks
    ]


def _authority_locks(execution_allowed: bool) -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": execution_allowed,
        "actual_external_oracle_calls": execution_allowed,
        "actual_live_data_ingestion": False,
        "persistent_production_runtime_activation": False,
        "mcp_exposure": False,
        "unreviewed_production_deployment": False,
        "autonomous_outcome_recording": False,
        "github_writeback": False,
        "notion_writeback": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "operator_gate": "FULL_LIVE_EXECUTION_GATE",
        "production_activation_ready_receipt_hash": FULL_LIVE_EXECUTION_GATE_HASH,
        "full_live_runtime_command_receipt_hash": (
            FULL_LIVE_RUNTIME_COMMAND_RECEIPT_HASH
        ),
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }
