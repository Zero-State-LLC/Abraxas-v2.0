"""Script: emit deterministic yggdrasil geometric route replay receipt artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.yggdrasil_geometric_route_replay_receipt import (
    build_yggdrasil_geometric_route_replay_receipt,
    default_output_contract,
    default_replay_effects,
    default_replay_observations,
    default_route_effects,
    default_stability_policy,
    serialize_yggdrasil_geometric_route_replay_receipt,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P46-YGGDRASIL-GEOMETRIC-ROUTE-REPLAY-RECEIPT-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.yggdrasil_geometric_route_replay_receipt_latest

_PAYLOAD: dict = {
    "receipt_id": "yggdrasil_geometric_route_replay_receipt_001",
    "replay_scope": {
        "surface_type": "YGGDRASIL_GEOMETRIC_ROUTE_METADATA",
        "replay_mode": "METADATA_REPLAY",
        "intended_lane": "OBSERVATION_ONLY",
    },
    "source_route_metadata_refs": [
        "YggdrasilGeometricRouteMetadata.v1:route-metadata-001",
    ],
    "source_signal_packet_refs": [],
    "source_metric_registry_refs": [],
    "source_test_vector_pack_refs": [],
    "replay_observations": default_replay_observations(),
    "stability_policy": default_stability_policy(),
    "route_effects": default_route_effects(),
    "replay_effects": default_replay_effects(),
    "output_contract": default_output_contract(),
    "governance_flags": {
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "runtime_mutation": False,
        "forecast_influence": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "activation_approved": False,
        "authorization_granted": False,
    },
    "provenance": {
        "source": "P46_YGGDRASIL_GEOMETRIC_ROUTE_REPLAY_RECEIPT_PLANNING_GATE",
        "evidence_refs": [
            "YggdrasilGeometricRouteMetadata.v1:route-metadata-001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/yggdrasil_geometric_route_replay_receipt.v1.schema.json",
            "contracts/canon/yggdrasil_geometric_route_metadata.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def _build_markdown(packet: dict) -> str:
    scope = packet.get("replay_scope", {})
    observations = packet.get("replay_observations", [])
    lines = [
        "# P46 Yggdrasil Geometric Route Replay Receipt",
        "",
        f"- receipt_id: `{packet.get('receipt_id', '?')}`",
        f"- receipt_type: `{packet.get('receipt_type', '?')}`",
        f"- schema_version: `{packet.get('schema_version', '?')}`",
        f"- canonical_hash: `{packet.get('canonical_hash', '?')}`",
        f"- created_at_utc: `{packet.get('created_at_utc', '?')}`",
        "",
        "## Replay Scope",
        f"- surface_type: `{scope.get('surface_type', '?')}`",
        f"- replay_mode: `{scope.get('replay_mode', '?')}`",
        f"- intended_lane: `{scope.get('intended_lane', '?')}`",
        "",
        f"## Replay Observations ({len(observations)})",
    ]
    for obs in observations:
        lines += [
            f"### {obs.get('observation_id', '?')}",
            f"- type: `{obs.get('observation_type', '?')}`",
            f"- status: `{obs.get('implementation_status', '?')}`",
            f"- description: {obs.get('description', '')}",
            "",
        ]
    lines += [
        "## Governance",
        "- production_activation: `false`",
        "- valid_for_execution: `false`",
        "- advisory_only: `true` (metadata replay gate only)",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "yggdrasil_geometric_route_replay_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "yggdrasil_geometric_route_replay_receipt_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_yggdrasil_geometric_route_replay_receipt(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_yggdrasil_geometric_route_replay_receipt(packet), encoding="utf-8"
    )
    OUT_PATH.with_suffix(".md").write_text(_build_markdown(packet), encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "yggdrasil_geometric_route_replay_receipt_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"receipt_id={packet['receipt_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
