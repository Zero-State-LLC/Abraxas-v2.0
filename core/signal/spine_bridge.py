"""Bridge FamiliarIngestionReceipt → advisory spine touchpoint (SHADOW).

Does not call Oracle runtime, mutate queues, or grant authority.
Produces seeds suitable for AbraxasClient.analyze input_payload / documentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
)

SCHEMA_VERSION = "FamiliarSpineTouchpoint.v0"
DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}


def _finalize(body: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(body)
    sealed.pop("touchpoint_hash", None)
    sealed["touchpoint_hash"] = canonical_hash(sealed)
    return sealed


def build_familiar_spine_touchpoint(
    receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    """Map a familiar ingestion receipt to a spine touchpoint packet."""
    if receipt is None:
        return _finalize(
            {
                "schema_version": SCHEMA_VERSION,
                "touchpoint_id": "fst_no_receipt",
                "route": "ABSTAIN_NO_INPUT",
                "receipt_id": "",
                "pack_id": "",
                "pack_hash": "",
                "reason": "no_receipt",
                "input_payload_seed": {},
                "oracle_candidate_seed": {},
                "register_counts": {},
                "commercial_claims_blocked": True,
                "evidence_density": 0.1,
                "advisory_only": True,
                "lane": "SHADOW",
                "authority": dict(DEFAULT_AUTHORITY),
            }
        )

    status = str(receipt.get("status") or "")
    receipt_id = str(receipt.get("receipt_id") or "")
    pack_id = str(receipt.get("pack_id") or "")
    pack_hash = str(receipt.get("pack_hash") or "")

    if status == "NO_INPUT":
        route = "ABSTAIN_NO_INPUT"
        reason = "familiar_ingestion_no_input"
    elif status == "REJECTED_INVALID_PACK":
        route = "ABSTAIN_INVALID"
        reason = "familiar_ingestion_rejected_invalid_pack"
    elif status != "INGESTED_SHADOW":
        route = "ABSTAIN_NOT_INGESTED"
        reason = f"unexpected_receipt_status:{status}"
    else:
        route = "ORACLE_SHADOW_CANDIDATE"
        reason = "familiar_ingestion_shadow_ready"

    topic = str(receipt.get("topic") or "")
    observed = int(receipt.get("observed_claim_count") or 0)
    density = float(receipt.get("evidence_density") or 0.1)
    counts = receipt.get("register_counts") or {}
    summaries = receipt.get("source_summaries") or []

    input_seed: dict[str, Any] = {}
    oracle_seed: dict[str, Any] = {}
    if route == "ORACLE_SHADOW_CANDIDATE":
        input_seed = {
            "kind": "evidence_pack_shadow",
            "pipeline_id": "familiar_ingestion",
            "pack_id": pack_id,
            "pack_hash": pack_hash,
            "topic": topic,
            "intent": receipt.get("intent"),
            "register_counts": counts,
            "observed_claim_count": observed,
            "source_count": receipt.get("source_count"),
            "commercial_claims_blocked": receipt.get("commercial_claims_blocked"),
            "evidence_density": density,
            "source_summaries": summaries,
            "advisory_only": True,
        }
        # Compact text payload for oracle intake builders (single source_id)
        payload_text = (
            f"EvidencePack.v0 pack_id={pack_id} topic={topic} "
            f"OBSERVED={observed} density={density} "
            f"commercial_blocked={receipt.get('commercial_claims_blocked')}"
        )
        oracle_seed = {
            "source_id": f"familiar:{pack_id or pack_hash[:16]}",
            "source_type": "evidence_pack",
            "payload": payload_text,
            "advisory_only": True,
            "forecast_authority": False,
        }

    touchpoint_id = f"fst_{(pack_hash or receipt_id or 'empty')[:16]}"
    return _finalize(
        {
            "schema_version": SCHEMA_VERSION,
            "touchpoint_id": touchpoint_id,
            "route": route,
            "receipt_id": receipt_id,
            "pack_id": pack_id,
            "pack_hash": pack_hash,
            "reason": reason,
            "input_payload_seed": input_seed,
            "oracle_candidate_seed": oracle_seed,
            "register_counts": counts,
            "commercial_claims_blocked": bool(
                receipt.get("commercial_claims_blocked", True)
            ),
            "evidence_density": density,
            "advisory_only": True,
            "lane": "SHADOW",
            "authority": dict(DEFAULT_AUTHORITY),
            "blockers": list(receipt.get("blockers") or []),
            "validation_errors": list(receipt.get("validation_errors") or []),
        }
    )


def build_touchpoint_from_pack_path(
    path: str | Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Pack path → familiar receipt → spine touchpoint (pure)."""
    receipt = build_familiar_ingestion_receipt_from_path(path, repo_root=repo_root)
    return build_familiar_spine_touchpoint(receipt)


def build_ai_os_kernel_status(repo_root: Path) -> dict[str, Any]:
    """Machine-readable AI OS kernel posture (does not flip production readiness)."""
    root = Path(repo_root).resolve()
    surfaces = {
        "evidence_pack_schema": (
            root / "contracts/signal/evidence_pack.v0.schema.json"
        ).is_file(),
        "evidence_pack_core": (root / "core/signal/evidence_pack.py").is_file(),
        "familiar_ingestion_schema": (
            root / "contracts/ingest/familiar_ingestion_receipt.v0.schema.json"
        ).is_file(),
        "familiar_ingestion_core": (
            root / "core/ingest/familiar_ingestion_receipt.py"
        ).is_file(),
        "spine_touchpoint_schema": (
            root / "contracts/signal/familiar_spine_touchpoint.v0.schema.json"
        ).is_file(),
        "spine_bridge_core": (root / "core/signal/spine_bridge.py").is_file(),
        "oracle_belief_bridge_schema": (
            root / "contracts/signal/familiar_oracle_belief_bridge.v0.schema.json"
        ).is_file(),
        "oracle_belief_bridge_core": (
            root / "core/signal/familiar_oracle_belief_bridge.py"
        ).is_file(),
        "operator_review_schema": (
            root / "contracts/signal/familiar_operator_review_packet.v0.schema.json"
        ).is_file(),
        "operator_review_core": (
            root / "core/signal/familiar_operator_review.py"
        ).is_file(),
        "operator_review_queue_dry_run_core": (
            root / "core/signal/familiar_operator_review.py"
        ).is_file(),
        "alembic_residual_inventory_core": (
            root / "core/alembic/residual_inventory.py"
        ).is_file(),
        "forager_skill": (
            root / "skills/abx-familiar-signal-forager/SKILL.md"
        ).is_file(),
        "neon_genie_skill": (root / "skills/abx-neon-genie/SKILL.md").is_file(),
        "master_loop_skill": (
            root / "skills/abraxas-master-loop-workflow/SKILL.md"
        ).is_file(),
        "os_unification_doc": (
            root / "docs/architecture/ABRAXAS_HERMES_OS_UNIFICATION_001.md"
        ).is_file(),
        "realization_backlog": (
            root / "docs/architecture/ABRAXAS_AI_OS_REALIZATION_BACKLOG_001.md"
        ).is_file(),
        "fixture_pack": (
            root
            / "skills/abx-familiar-signal-forager/fixtures"
            / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
        ).is_file(),
        "forensics_core": (root / "core/forensics/pipeline.py").is_file(),
    }
    required = [
        "evidence_pack_schema",
        "evidence_pack_core",
        "familiar_ingestion_schema",
        "familiar_ingestion_core",
        "spine_bridge_core",
        "forager_skill",
    ]
    ready = all(surfaces[k] for k in required)
    missing = [k for k in required if not surfaces[k]]

    # Kernel ACTIVE_SHADOW when Slice A–C core files present; production still denied
    kernel_state = "ACTIVE_SHADOW" if ready else "PARTIAL"
    if missing:
        kernel_state = "PARTIAL"

    payload = {
        "schema_version": "AiOsKernelStatus.v0",
        "ai_os_kernel": kernel_state,
        "external_production_authorized": False,
        "activation_default": "LOCAL_DEV",
        "lane": "SHADOW",
        "syscall": {
            "name": "signal_forage",
            "pack_schema": "EvidencePack.v0",
            "ingest_receipt": "FamiliarIngestionReceipt.v0",
            "spine_touchpoint": "FamiliarSpineTouchpoint.v0",
            "oracle_belief_bridge": "FamiliarOracleBeliefBridge.v0",
            "path": (
                "forage → EvidencePack → familiar_ingestion receipt "
                "→ spine touchpoint → oracle/belief SHADOW bridge "
                "→ operator-review disposition seed "
                "→ operator-review-dry-run queue projection "
                "(advisory; no runtime mutation / no queue write) "
                "→ forensics disposition (ops gate DENIED)"
            ),
            "operator_review": "FamiliarOperatorReviewPacket.v0",
            "operator_review_queue_dry_run": "FamiliarOperatorReviewQueueDryRun.v0",
        },
        "surfaces": surfaces,
        "missing_required": missing,
        "commands": {
            "validate_pack": "python -m abraxas forage validate --pack PATH",
            "ingest_pack": "python -m abraxas forage ingest --pack PATH",
            "spine_touch": "python -m abraxas forage spine-touch --pack PATH",
            "oracle_belief_bridge": (
                "python -m abraxas forage oracle-belief-bridge --pack PATH"
            ),
            "operator_review": (
                "python -m abraxas forage operator-review --pack PATH"
            ),
            "operator_review_dry_run": (
                "python -m abraxas forage operator-review-dry-run --pack PATH"
            ),
            "alembic_residuals": "python -m abraxas os alembic-residuals",
            "os_status": "python -m abraxas os status",
            "forensics_run": "python -m abraxas os forensics run --pack PATH",
        },
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
    }
    payload["status_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "status_hash"}
    )
    return payload
