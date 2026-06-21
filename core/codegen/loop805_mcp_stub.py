from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID
from core.codegen.spine_mcp_projection import SPINE_TOOLS


LOOP_805_MCP_STUB_SCHEMA_VERSION = "AbxLoop805McpExposureStub.v1"


def build_loop805_mcp_exposure_stub(
    *,
    timestamp: str,
    tool_contracts: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    contracts = [_normalize_contract(contract) for contract in tool_contracts]
    base: dict[str, Any] = {
        "schema_version": LOOP_805_MCP_STUB_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "stub_id": "ABX_LOOP_805_MCP_EXPOSURE_STUB",
        "stub_status": "MCP_EXPOSURE_STUB_READY_READ_ONLY_NOT_LIVE",
        "timestamp": timestamp,
        "tool_contracts": contracts,
        "operator_gate": {
            "required": True,
            "attestation_required": True,
            "approval_template": (
                "I approve review of the Loop 805 MCP exposure stub as read-only "
                "planning evidence. I do not authorize live MCP exposure."
            ),
            "brier_score": 0.09,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_runtime_activation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def default_loop805_mcp_tool_contracts() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "tool_name": tool_name,
            "mode": "READ_ONLY_STUB",
            "live_exposure": False,
            "request_schema": {
                "type": "object",
                "required": ["intent", "evidence_paths"],
                "additionalProperties": False,
            },
            "response_schema": {
                "type": "object",
                "required": [
                    "provenance",
                    "token_telemetry",
                    "authority_locks",
                    "canonical_hash",
                ],
                "additionalProperties": True,
            },
            "brier_score": 0.1,
        }
        for tool_name in SPINE_TOOLS
    )


def _normalize_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    tool_name = str(contract.get("tool_name", ""))
    if tool_name not in SPINE_TOOLS:
        raise ValueError(f"unsupported Loop 805 MCP tool: {tool_name}")
    normalized = dict(contract)
    normalized["live_exposure"] = False
    normalized["valid_for_execution"] = False
    normalized["valid_for_runtime_activation"] = False
    return normalized
