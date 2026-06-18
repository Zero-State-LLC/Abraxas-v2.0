from __future__ import annotations

from typing import Any, Mapping


def compute_shadow_metrics(
    signal_packet: Mapping[str, Any],
    registry_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    signal_id = str(signal_packet.get("item_id", "NOT_COMPUTABLE"))
    operator_id = str(registry_packet.get("item_id", "default-registry")) if registry_packet else "default-registry"
    return {
        "schema_version": "GeometricIntelligenceRuntime.v1",
        "status": "SHADOW_METRICS_COMPUTED",
        "signal_id": signal_id,
        "registry_id": operator_id,
        "metrics": [{"operator_id": operator_id, "status": "OBSERVED"}],
        "advisory_only": True,
        "execution_authority": False,
    }
