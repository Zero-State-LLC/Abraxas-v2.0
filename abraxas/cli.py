"""Supported Abraxas CLI: analyze / validate / replay / status / os / forage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from abraxas.client import AbraxasClient
from core.alembic.residual_inventory import build_alembic_residual_inventory
from core.audit.fast_ci_receipt import (
    build_fast_ci_receipt,
    write_fast_ci_receipt,
)
from core.audit.main_cleanliness_receipt import (
    build_main_cleanliness_receipt,
    write_main_cleanliness_receipt,
)
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_canonical_artifact
from core.engineering.branch_hygiene_inventory import build_branch_hygiene_inventory
from core.forensics.aal_viz_projection import (
    build_aal_viz_forensic_projection_from_pack_path,
)
from core.forensics.level99_seed import (
    build_forensic_level99_seed_from_pack_path,
)
from core.forensics.ops_route import (
    build_memetic_ops_route_intent_from_pack_path,
)
from core.forensics.pipeline import run_forensics_from_pack_path
from core.governance.activation_policy import ActivationLane
from core.holler.outcome_binding_dry_run import build_holler_outcome_binding_dry_run
from core.holler.ticket_operator_packet import build_ticket_operator_packet
from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
    write_familiar_ingestion_receipt,
)
from core.memetic.brier_ledger_dry_run import build_memetic_brier_ledger_dry_run
from core.memetic.futurecast_operator_packet import build_futurecast_operator_packet
from core.noctis.operator_review_dry_run import (
    build_noctis_review_dry_run_from_narrative,
)
from core.settings import load_runtime_settings
from core.signal.evidence_pack import validate_path
from core.signal.familiar_operator_review import (
    build_operator_review_from_pack_path,
    build_operator_review_queue_dry_run_from_pack_path,
)
from core.signal.familiar_oracle_belief_bridge import build_bridge_from_pack_path
from core.signal.operation_trace_adapter import (
    receipt_to_operation_trace,
    write_operation_trace,
)
from core.signal.spine_bridge import (
    build_ai_os_kernel_status,
    build_touchpoint_from_pack_path,
)
from core.slice_g_operator_handoff import (
    DEFAULT_FIXTURE as SLICE_G_DEFAULT_FIXTURE,
)
from core.slice_g_operator_handoff import (
    DEFAULT_MD_PATH as SLICE_G_DEFAULT_MD_PATH,
)
from core.slice_g_operator_handoff import (
    DEFAULT_OUT_PATH as SLICE_G_DEFAULT_OUT_PATH,
)
from core.slice_g_operator_handoff import (
    build_slice_g_operator_handoff_review,
    write_slice_g_operator_handoff_review,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def _cmd_analyze(args: argparse.Namespace) -> int:
    settings = load_runtime_settings(
        repo_root=REPO_ROOT,
        default_activation_lane=args.lane,
    )
    client = AbraxasClient(settings=settings)
    input_payload: dict[str, Any] = {}
    if args.input is not None:
        loaded = _load_json(args.input)
        if not isinstance(loaded, dict):
            _print(
                {
                    "status": "ERROR",
                    "error_class": "INPUT_INVALID",
                    "message": "--input must be a JSON object",
                }
            )
            return 2
        input_payload = loaded

    alembic_task = _load_json(args.alembic_task) if args.alembic_task else None
    oracle_candidate = (
        _load_json(args.oracle_candidate) if args.oracle_candidate else None
    )
    result = client.analyze(
        run_id=args.run_id,
        input_payload=input_payload,
        schema_ref=args.schema_ref,
        alembic_task=alembic_task if isinstance(alembic_task, dict) else None,
        oracle_candidate=(
            oracle_candidate if isinstance(oracle_candidate, dict) else None
        ),
        enable_alembic=not args.no_alembic,
        alembic_mode=args.alembic_mode,
        activation_lane=args.lane,
    )
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        out_root = args.out.resolve()
        write_canonical_artifact(
            args.out / "advisory_spine_result.json",
            result,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=out_root,
        )
        if isinstance(result.get("alembic"), dict):
            write_canonical_artifact(
                args.out / "alembic.json",
                result["alembic"],
                artifact_class=ArtifactClass.AUDIT_EVIDENCE,
                out_root=out_root,
            )
    _print(
        {
            "ok": result.get("status") == "OK",
            "status": result.get("status"),
            "run_id": result.get("run_id"),
            "result_hash": result.get("result_hash"),
            "alembic_invoked": bool(
                (result.get("advisory_result") or {}).get("alembic_invoked")
            ),
            "error_class": result.get("error_class"),
        }
    )
    if result.get("status") == "OK":
        return 0
    if result.get("status") == "OPERATOR_GATE":
        return 3
    return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    client = AbraxasClient(settings=load_runtime_settings(repo_root=REPO_ROOT))
    payload = _load_json(args.payload)
    result = client.validate(
        schema_ref=args.schema_ref,
        payload=payload,
        execution_id=args.execution_id,
    )
    _print(
        {
            "ok": result.get("status") == "OK" and result.get("valid") is True,
            "status": result.get("status"),
            "valid": result.get("valid"),
            "error_class": result.get("error_class"),
            "errors": result.get("errors"),
        }
    )
    if result.get("status") == "OK" and result.get("valid") is True:
        return 0
    return 1


def _cmd_replay(args: argparse.Namespace) -> int:
    settings = load_runtime_settings(
        repo_root=REPO_ROOT,
        default_activation_lane=args.lane,
    )
    client = AbraxasClient(settings=settings)
    receipt = _load_json(args.receipt)
    if not isinstance(receipt, dict):
        _print(
            {
                "status": "ERROR",
                "error_class": "REPLAY_INPUT_INVALID",
                "message": "--receipt must be a JSON object",
            }
        )
        return 2
    result = client.replay(receipt, run_id=args.run_id)
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out / "replay_result.json",
            result,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.resolve(),
        )
    _print(
        {
            "ok": result.get("status") == "OK",
            "status": result.get("status"),
            "run_id": result.get("run_id"),
            "result_hash": result.get("result_hash"),
            "error_class": result.get("error_class"),
        }
    )
    return 0 if result.get("status") == "OK" else 1


def _cmd_status(_args: argparse.Namespace) -> int:
    settings = load_runtime_settings(repo_root=REPO_ROOT)
    client = AbraxasClient(settings=settings)
    snapshot = client.status()
    _print(
        {
            "ok": True,
            "candidate_status": snapshot["candidate_status"],
            "external_production_authorized": snapshot[
                "external_production_authorized"
            ],
            "repository_sha": snapshot["repository_sha"],
            "supported_interfaces": snapshot["supported_interfaces"],
            "supported_spine": snapshot["supported_spine"],
            "settings": snapshot.get("settings"),
            "canonical_hash": snapshot["canonical_hash"],
        }
    )
    return 0


def _cmd_os_status(_args: argparse.Namespace) -> int:
    payload = build_ai_os_kernel_status(REPO_ROOT)
    _print({"ok": payload.get("ai_os_kernel") == "ACTIVE_SHADOW", **payload})
    return 0 if payload.get("ai_os_kernel") == "ACTIVE_SHADOW" else 1


def _cmd_os_forensics_run(args: argparse.Namespace) -> int:
    """Run memetic forensics spine on EvidencePack (SHADOW; ops gate always DENIED)."""
    try:
        run = run_forensics_from_pack_path(args.pack, repo_root=REPO_ROOT)
    except Exception as exc:  # noqa: BLE001 — CLI hard-failure boundary
        _print(
            {
                "ok": False,
                "error_class": type(exc).__name__,
                "message": str(exc),
                "advisory_only": True,
                "ops_gate_status": "DENIED",
                "lane": "SHADOW",
            }
        )
        return 1

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            run,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.parent,
        )

    disposition = run.get("disposition") or {}
    disposition_value = str(disposition.get("disposition") or "")
    ops_gate = run.get("ops_gate") or {}
    ops_gate_status = str(ops_gate.get("gate_status") or "DENIED")

    _print(
        {
            "ok": run.get("ok"),
            "pack_id": run.get("pack_id"),
            "pack_path": run.get("pack_path"),
            "disposition": disposition_value,
            "ops_gate_status": ops_gate_status,
            "bridge_status": run.get("bridge_status"),
            "advisory_only": True,
            "lane": run.get("lane"),
            "authority": run.get("authority"),
            "canonical_hash": run.get("canonical_hash"),
            "wrote": str(args.out) if args.out is not None else None,
        }
    )

    if disposition_value == "READY":
        return 0
    if disposition_value in {"HOLD", "NOT_COMPUTABLE"}:
        return 2
    return 1


def _cmd_os_forensics_status(_args: argparse.Namespace) -> int:
    """Report forensics engine posture (SHADOW; no prior-run disk dependency)."""
    _print(
        {
            "ok": True,
            "forensics_engine": "SLICE_C",
            "ops_gate_default": "DENIED",
            "commands": {
                "run": "python -m abraxas os forensics run --pack PATH",
                "project": "python -m abraxas os forensics project --pack PATH",
                "route": "python -m abraxas os forensics route --pack PATH",
                "seed_level99": (
                    "python -m abraxas os forensics seed-level99 --pack PATH"
                ),
            },
            "advisory_only": True,
        }
    )
    return 0


def _cmd_os_forensics_seed_level99(args: argparse.Namespace) -> int:
    """Seed Level99 content packet from forensic READY (SHADOW; gate DENIED)."""
    try:
        seed = build_forensic_level99_seed_from_pack_path(
            args.pack, repo_root=REPO_ROOT
        )
    except Exception as exc:  # noqa: BLE001 — CLI hard-failure boundary
        _print(
            {
                "ok": False,
                "error_class": type(exc).__name__,
                "message": str(exc),
                "advisory_only": True,
                "ops_gate_status": "DENIED",
                "execution_authorized": False,
                "lane": "SHADOW",
            }
        )
        return 1

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            seed,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.parent,
        )

    disposition_value = str(seed.get("disposition") or "")
    pkt = seed.get("content_packet") or {}
    _print(
        {
            "ok": seed.get("seed_status") == "SEEDED",
            "schema_version": seed.get("schema_version"),
            "seed_status": seed.get("seed_status"),
            "pack_id": seed.get("pack_id"),
            "disposition": disposition_value,
            "route_intent": seed.get("route_intent"),
            "ops_gate_status": "DENIED",
            "execution_authorized": False,
            "publish_authorized": False,
            "content_id": pkt.get("content_id") if isinstance(pkt, dict) else None,
            "level99_route": pkt.get("route") if isinstance(pkt, dict) else None,
            "auto_publish_blocked": (
                pkt.get("auto_publish_blocked") if isinstance(pkt, dict) else None
            ),
            "advisory_only": True,
            "lane": "SHADOW",
            "canonical_hash": seed.get("canonical_hash"),
            "wrote": str(args.out) if args.out is not None else None,
        }
    )

    if seed.get("seed_status") == "SEEDED":
        return 0
    if disposition_value in {"HOLD", "NOT_COMPUTABLE"}:
        return 2
    return 1


def _cmd_os_forensics_route(args: argparse.Namespace) -> int:
    """Route intent for Level 99 / Neon seed (SHADOW; gate always DENIED)."""
    try:
        intent = build_memetic_ops_route_intent_from_pack_path(
            args.pack,
            repo_root=REPO_ROOT,
            prefer_neon=bool(getattr(args, "prefer_neon", False)),
        )
    except Exception as exc:  # noqa: BLE001 — CLI hard-failure boundary
        _print(
            {
                "ok": False,
                "error_class": type(exc).__name__,
                "message": str(exc),
                "advisory_only": True,
                "ops_gate_status": "DENIED",
                "execution_authorized": False,
                "lane": "SHADOW",
            }
        )
        return 1

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            intent,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.parent,
        )

    disposition_value = str(intent.get("disposition") or "")
    _print(
        {
            "ok": disposition_value in {"READY", "HOLD", "NOT_COMPUTABLE"},
            "schema_version": intent.get("schema_version"),
            "pack_id": intent.get("pack_id"),
            "disposition": disposition_value,
            "route_intent": intent.get("route_intent"),
            "route_status": intent.get("route_status"),
            "target_pipeline": intent.get("target_pipeline"),
            "ops_gate_status": "DENIED",
            "execution_authorized": False,
            "publish_authorized": False,
            "advisory_only": True,
            "lane": "SHADOW",
            "canonical_hash": intent.get("canonical_hash"),
            "wrote": str(args.out) if args.out is not None else None,
        }
    )

    if disposition_value == "READY":
        return 0
    if disposition_value in {"HOLD", "NOT_COMPUTABLE"}:
        return 2
    return 1


def _cmd_os_forensics_project(args: argparse.Namespace) -> int:
    """Project ForensicRun → AALVizForensicProjection.v0 (SHADOW; gate DENIED)."""
    try:
        proj = build_aal_viz_forensic_projection_from_pack_path(
            args.pack, repo_root=REPO_ROOT
        )
    except Exception as exc:  # noqa: BLE001 — CLI hard-failure boundary
        _print(
            {
                "ok": False,
                "error_class": type(exc).__name__,
                "message": str(exc),
                "advisory_only": True,
                "projection_only": True,
                "ops_gate_status": "DENIED",
                "lane": "SHADOW",
            }
        )
        return 1

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            proj,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.parent,
        )

    disposition_value = str(proj.get("disposition") or "")
    graph = proj.get("graph_summary") or {}
    _print(
        {
            "ok": disposition_value in {"READY", "HOLD", "NOT_COMPUTABLE"},
            "schema_version": proj.get("schema_version"),
            "pack_id": proj.get("pack_id"),
            "disposition": disposition_value,
            "ops_gate_status": "DENIED",
            "simulation": proj.get("simulation"),
            "projection_only": True,
            "advisory_only": True,
            "lane": "SHADOW",
            "node_count": graph.get("node_count"),
            "edge_count": graph.get("edge_count"),
            "canonical_hash": proj.get("canonical_hash"),
            "wrote": str(args.out) if args.out is not None else None,
        }
    )

    if disposition_value == "READY":
        return 0
    if disposition_value in {"HOLD", "NOT_COMPUTABLE"}:
        return 2
    return 1


def _cmd_forage_validate(args: argparse.Namespace) -> int:
    report = validate_path(args.pack, repo_root=REPO_ROOT)
    _print(report)
    return 0 if report.get("ok") else 2


def _cmd_forage_ingest(args: argparse.Namespace) -> int:
    receipt = build_familiar_ingestion_receipt_from_path(args.pack, repo_root=REPO_ROOT)
    out_path = args.out
    if out_path is None and not args.print_only:
        stem = Path(args.pack).stem.replace(".v0", "")
        out_path = (
            REPO_ROOT
            / "out"
            / "ingest"
            / "familiar_ingestion"
            / f"{stem}_receipt.v0.json"
        )
    if not args.print_only and out_path is not None:
        write_familiar_ingestion_receipt(
            Path(out_path),
            receipt,
            out_root=REPO_ROOT / "out",
        )

    # Slice D closed loop: emit OperationTrace for skill-evolution / learning
    trace = receipt_to_operation_trace(
        receipt,
        source_artifact=str(out_path) if out_path else "cli:abraxas forage ingest",
    )
    trace_path = write_operation_trace(trace, out_dir=REPO_ROOT / "out" / "audit")

    _print(
        {
            "ok": receipt.get("status") == "INGESTED_SHADOW",
            "status": receipt.get("status"),
            "receipt_id": receipt.get("receipt_id"),
            "pack_id": receipt.get("pack_id"),
            "receipt_hash": receipt.get("receipt_hash"),
            "wrote": str(out_path) if out_path and not args.print_only else None,
            "operation_trace": str(trace_path),
            "commercial_claims_blocked": receipt.get("commercial_claims_blocked"),
            "evidence_density": receipt.get("evidence_density"),
            "lane": receipt.get("lane"),
            "authority": receipt.get("authority"),
        }
    )
    return 0 if receipt.get("status") == "INGESTED_SHADOW" else 2


def _cmd_forage_spine_touch(args: argparse.Namespace) -> int:
    touchpoint = build_touchpoint_from_pack_path(args.pack, repo_root=REPO_ROOT)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            touchpoint,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    _print(
        {
            "ok": touchpoint.get("route") == "ORACLE_SHADOW_CANDIDATE",
            "route": touchpoint.get("route"),
            "touchpoint_id": touchpoint.get("touchpoint_id"),
            "pack_id": touchpoint.get("pack_id"),
            "reason": touchpoint.get("reason"),
            "touchpoint_hash": touchpoint.get("touchpoint_hash"),
            "input_payload_seed": touchpoint.get("input_payload_seed"),
            "oracle_candidate_seed": touchpoint.get("oracle_candidate_seed"),
            "authority": touchpoint.get("authority"),
            "advisory_only": True,
        }
    )
    return 0 if touchpoint.get("route") == "ORACLE_SHADOW_CANDIDATE" else 2


def _cmd_forage_oracle_belief_bridge(args: argparse.Namespace) -> int:
    """Emit FamiliarOracleBeliefBridge.v0 from pack (SHADOW; no Oracle/Belief mutation)."""
    bridge = build_bridge_from_pack_path(args.pack, repo_root=REPO_ROOT)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            bridge,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    _print(
        {
            "ok": bridge.get("status") == "BRIDGED_SHADOW",
            "status": bridge.get("status"),
            "route": bridge.get("route"),
            "bridge_id": bridge.get("bridge_id"),
            "pack_id": bridge.get("pack_id"),
            "touchpoint_id": bridge.get("touchpoint_id"),
            "reason": bridge.get("reason"),
            "bridge_hash": bridge.get("bridge_hash"),
            "oracle_shadow_intake": bridge.get("oracle_shadow_intake"),
            "belief_seed_count": len(bridge.get("belief_candidate_seeds") or []),
            "authority": bridge.get("authority"),
            "advisory_only": True,
            "wrote": str(args.out) if args.out is not None else None,
        }
    )
    return 0 if bridge.get("status") == "BRIDGED_SHADOW" else 2


def _cmd_forage_operator_review(args: argparse.Namespace) -> int:
    """Emit FamiliarOperatorReviewPacket.v0 from pack (SHADOW; no queue write)."""
    review = build_operator_review_from_pack_path(args.pack, repo_root=REPO_ROOT)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            review,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    _print(
        {
            "ok": review.get("disposition") == "READY_FOR_REVIEW",
            "disposition": review.get("disposition"),
            "recommended_action": review.get("recommended_action"),
            "review_id": review.get("review_id"),
            "bridge_id": review.get("bridge_id"),
            "pack_id": review.get("pack_id"),
            "summary": review.get("summary"),
            "belief_seed_count": review.get("belief_seed_count"),
            "review_queue_hint": review.get("review_queue_hint"),
            "authority": review.get("authority"),
            "advisory_only": True,
            "wrote": str(args.out) if args.out is not None else None,
        }
    )
    return 0 if review.get("disposition") == "READY_FOR_REVIEW" else 2


def _cmd_forage_operator_review_dry_run(args: argparse.Namespace) -> int:
    """Map pack → review seed → OperatorReviewQueueItem/Run dry-run (no queue write)."""
    dry = build_operator_review_queue_dry_run_from_pack_path(
        args.pack, repo_root=REPO_ROOT
    )
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            dry,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    item = dry.get("queue_item") or {}
    run = dry.get("queue_run") or {}
    _print(
        {
            "ok": dry.get("queue_write_performed") is False
            and dry.get("dry_run") is True,
            "schema_version": dry.get("schema_version"),
            "dry_run": True,
            "queue_write_performed": dry.get("queue_write_performed"),
            "disposition": dry.get("disposition"),
            "recommended_action": dry.get("recommended_action"),
            "review_id": dry.get("review_id"),
            "queue_item_id": item.get("queue_item_id"),
            "queue_item_state": item.get("state"),
            "queue_item_priority": item.get("priority"),
            "queue_run_id": run.get("run_id"),
            "recommended_next_state": run.get("recommended_next_state"),
            "target_queue_path": dry.get("target_queue_path"),
            "authority": dry.get("authority"),
            "advisory_only": True,
            "wrote": str(args.out) if args.out is not None else None,
        }
    )
    # Exit 0 for successful dry-run projection; disposition may still be ABSTAIN.
    return 0


def _cmd_os_alembic_residuals(_args: argparse.Namespace) -> int:
    """Track C residual inventory for Alembic spine (stubs stay stubbed)."""
    inv = build_alembic_residual_inventory()
    _print(
        {
            "ok": inv.get("spine_status")
            == "ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS",
            "spine_status": inv.get("spine_status"),
            "inventory_id": inv.get("inventory_id"),
            "counts": inv.get("counts"),
            "unstub_policy": inv.get("unstub_policy"),
            "integration_rule": inv.get("integration_rule"),
            "live_rune_policy": inv.get("live_rune_policy"),
            "backend_unstub_policy": inv.get("backend_unstub_policy"),
            "pipeline_inventory_policy": inv.get("pipeline_inventory_policy"),
            "residuals": inv.get("residuals"),
            "authority": inv.get("authority"),
            "advisory_only": True,
        }
    )
    return 0


def _cmd_os_main_audit(args: argparse.Namespace) -> int:
    """Emit main cleanliness + fast-ci receipts for Notion main-scope audit."""
    cleanliness = build_main_cleanliness_receipt(repo_root=REPO_ROOT)
    fast = build_fast_ci_receipt(
        repo_root=REPO_ROOT,
        commit_sha=cleanliness.get("commit_sha"),
        origin_main_sha=cleanliness.get("origin_main_sha"),
        execute_smoke=bool(getattr(args, "execute_smoke", False)),
    )
    if getattr(args, "write", False):
        clean_path = REPO_ROOT / "out" / "audit" / "main_cleanliness.latest.json"
        fast_path = REPO_ROOT / "out" / "audit" / "fast_ci.latest.json"
        write_main_cleanliness_receipt(clean_path, cleanliness)
        write_fast_ci_receipt(fast_path, fast)
        wrote = {"main_cleanliness": str(clean_path), "fast_ci": str(fast_path)}
    else:
        wrote = None
    _print(
        {
            "ok": cleanliness.get("status") == "PASS"
            and fast.get("status") in {"PASS", "NOT_COMPUTABLE"},
            "main_cleanliness": {
                "schema_version": cleanliness.get("schema_version"),
                "status": cleanliness.get("status"),
                "commit_sha": cleanliness.get("commit_sha"),
                "origin_main_sha": cleanliness.get("origin_main_sha"),
                "ahead": cleanliness.get("ahead"),
                "behind": cleanliness.get("behind"),
                "worktree_clean": cleanliness.get("worktree_clean"),
                "blockers": cleanliness.get("blockers"),
                "canonical_hash": cleanliness.get("canonical_hash"),
            },
            "fast_ci": {
                "schema_version": fast.get("schema_version"),
                "status": fast.get("status"),
                "mode": fast.get("mode"),
                "pass_count": fast.get("pass_count"),
                "fail_count": fast.get("fail_count"),
                "authoritative_full_ci_command": fast.get(
                    "authoritative_full_ci_command"
                ),
                "canonical_hash": fast.get("canonical_hash"),
            },
            "wrote": wrote,
            "authority": cleanliness.get("authority"),
            "advisory_only": True,
        }
    )
    if cleanliness.get("status") == "FAIL" or fast.get("status") == "FAIL":
        return 1
    if cleanliness.get("status") == "NOT_COMPUTABLE" or fast.get(
        "status"
    ) == "NOT_COMPUTABLE":
        return 2
    return 0


def _cmd_os_memetic_brier_dry_run(args: argparse.Namespace) -> int:
    """Project memetic futurecast packet → Brier ledger shape (no ledger write)."""
    packet = build_futurecast_operator_packet(
        forecast_id=str(args.forecast_id or ""),
        topic=str(args.topic or ""),
        selected_horizon=str(args.horizon or ""),
        probability=args.probability,
        register=str(args.register or "INFERRED"),
        evidence_density=args.evidence_density,
        outcome_value=args.outcome,
        claim_text=str(args.claim or ""),
    )
    dry = build_memetic_brier_ledger_dry_run(packet)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            dry,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    entry = dry.get("projected_ledger_entry") or {}
    _print(
        {
            "ok": dry.get("ledger_write_performed") is False
            and dry.get("dry_run") is True,
            "schema_version": dry.get("schema_version"),
            "dry_run": True,
            "ledger_write_performed": dry.get("ledger_write_performed"),
            "projection_status": dry.get("projection_status"),
            "packet_id": dry.get("packet_id"),
            "forecast_id": dry.get("forecast_id"),
            "bridge_status": dry.get("bridge_status"),
            "brier_score": entry.get("brier_score"),
            "ledger_entry_id": entry.get("ledger_entry_id"),
            "target_ledger_path": dry.get("target_ledger_path"),
            "authority": dry.get("authority"),
            "advisory_only": True,
            "wrote": str(args.out) if args.out is not None else None,
        }
    )
    if dry.get("projection_status") == "PROJECTED":
        return 0
    if dry.get("projection_status") == "SEEDED_AWAITING_OUTCOME":
        return 2
    return 1


def _cmd_os_holler_outcome_dry_run(args: argparse.Namespace) -> int:
    """Project holler ticket → outcome binding shape (no binding write)."""
    packet = build_ticket_operator_packet(
        ticket_id=str(args.ticket_id or ""),
        sport=str(args.sport or "UNKNOWN"),
        event_ref=str(args.event_ref or ""),
        market_class=str(args.market_class or "UNKNOWN"),
        probability=args.probability,
        register=str(args.register or "INFERRED"),
        expected_outcome=str(args.expected_outcome or ""),
        observed_outcome=args.observed_outcome,
    )
    dry = build_holler_outcome_binding_dry_run(packet)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            dry,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    projected = dry.get("projected_binding") or {}
    _print(
        {
            "ok": dry.get("binding_write_performed") is False
            and dry.get("dry_run") is True,
            "schema_version": dry.get("schema_version"),
            "dry_run": True,
            "binding_write_performed": dry.get("binding_write_performed"),
            "projection_status": dry.get("projection_status"),
            "ticket_id": dry.get("ticket_id"),
            "packet_id": dry.get("packet_id"),
            "binding_id": projected.get("binding_id"),
            "binding_status": projected.get("binding_status"),
            "target_binding_path": dry.get("target_binding_path"),
            "authority": dry.get("authority"),
            "advisory_only": True,
            "wrote": str(args.out) if args.out is not None else None,
        }
    )
    if dry.get("projection_status") == "MATCHED":
        return 0
    if dry.get("projection_status") == "UNRESOLVED":
        return 2
    return 1


def _cmd_os_noctis_review_dry_run(args: argparse.Namespace) -> int:
    """Project noctis dream narrative → operator review queue shape (no write)."""
    dry = build_noctis_review_dry_run_from_narrative(
        str(args.narrative or ""),
        mode=str(args.mode or "SYSTEM_DREAM"),
        privacy_tier=str(args.privacy_tier or "PUBLIC_SYNTHETIC"),
        dream_id=args.dream_id,
        source=str(args.source or "SYSTEM"),
        seed=str(args.seed or "0"),
    )
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_canonical_artifact(
            args.out,
            dry,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=(args.out.parent if args.out_root is None else args.out_root),
        )
    item = dry.get("queue_item") or {}
    seed = dry.get("continuity_seed") or {}
    _print(
        {
            "ok": dry.get("queue_write_performed") is False
            and dry.get("dry_run") is True,
            "schema_version": dry.get("schema_version"),
            "dry_run": True,
            "queue_write_performed": dry.get("queue_write_performed"),
            "memory_write_performed": dry.get("memory_write_performed"),
            "readiness": dry.get("readiness"),
            "dream_id": dry.get("dream_id"),
            "queue_item_id": item.get("queue_item_id"),
            "queue_item_state": item.get("state"),
            "queue_item_priority": item.get("priority"),
            "continuity_seed_status": seed.get("status"),
            "target_queue_path": dry.get("target_queue_path"),
            "authority": dry.get("authority"),
            "advisory_only": True,
            "wrote": str(args.out) if args.out is not None else None,
        }
    )
    if dry.get("readiness") == "SHADOW_OPERATOR_REVIEW":
        return 0
    if dry.get("readiness") == "NOT_COMPUTABLE":
        return 2
    return 1


def _cmd_os_branch_hygiene(_args: argparse.Namespace) -> int:
    """Advisory remote-branch classification (never deletes)."""
    inv = build_branch_hygiene_inventory(repo_root=REPO_ROOT)
    _print(
        {
            "ok": inv.get("delete_authorized") is False,
            "inventory_id": inv.get("inventory_id"),
            "total_heads": inv.get("total_heads"),
            "class_counts": inv.get("class_counts"),
            "prefix_counts": inv.get("prefix_counts"),
            "candidates_sample": inv.get("candidates_sample"),
            "open_pr_heads": inv.get("open_pr_heads"),
            "delete_authorized": False,
            "policy_doc": inv.get("policy_doc"),
            "authority": inv.get("authority"),
            "advisory_only": True,
            "note": inv.get("note"),
        }
    )
    return 0


def _cmd_os_evolution_volume(_args: argparse.Namespace) -> int:
    """Light SHADOW surface for Hermes signal volume in the evolution ledger.
    Shows task_class keyed volumes (e.g. signal_forage, hyperagent_forager).
    Advisory only.
    """
    audit = REPO_ROOT / "out" / "audit"
    volumes: dict[str, dict] = {}
    for p in sorted(audit.glob("os_signal_*.latest.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
        try:
            data = json.loads(p.read_text())
            tc = data.get("task_class", "unknown")
            skill = data.get("skill_id", "unknown")
            key = f"{skill}:{tc}" if tc else skill
            if key not in volumes:
                volumes[key] = {"runs": 0, "observed": 0, "last": None}
            volumes[key]["runs"] += 1
            prov = data.get("provenance", {})
            volumes[key]["observed"] += prov.get("observed_count", 0)
            volumes[key]["last"] = data.get("timestamp") or str(p)
        except (OSError, json.JSONDecodeError, TypeError):
            continue

    # Also try the bridge ledger snapshot if present
    ledger_path = audit / "hermes_signal_evolution_ledger_snapshot.json"
    if ledger_path.exists():
        try:
            snap = json.loads(ledger_path.read_text())
            for k, v in snap.get("ledger", {}).items():
                if k not in volumes:
                    volumes[k] = {
                        "runs": v.get("runs", 0),
                        "observed": v.get("observed", 0),
                        "last": v.get("last_updated"),
                    }
        except (OSError, json.JSONDecodeError, TypeError):
            pass

    payload = {
        "boundary": "ADVISORY_ONLY | SHADOW | EVOLUTION_VOLUME",
        "lane": "SHADOW",
        "authority": {"execution_authority": False},
        "volumes_by_task_class": volumes,
        "note": "Hermes (and plural) forager volumes visible to evolution cycle. No promotion.",
    }
    _print(payload)
    return 0


def _cmd_os_evolution_review(args: argparse.Namespace) -> int:
    """Slice G SHADOW operator handoff review for volume-derived patch candidates."""
    fixture = args.fixture or Path(SLICE_G_DEFAULT_FIXTURE)
    if args.write:
        payload = write_slice_g_operator_handoff_review(
            repo_root=REPO_ROOT,
            fixture_path=fixture,
            out_path=args.out,
            md_path=args.md,
        )
    else:
        payload = build_slice_g_operator_handoff_review(
            repo_root=REPO_ROOT,
            fixture_path=fixture,
        )
    _print(payload)
    return 0 if payload.get("status") == "SLICE_G_OPERATOR_HANDOFF_READY_ADVISORY_ONLY" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="abraxas",
        description="Abraxas supported product CLI (Governance V3 / advisory spine)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Run advisory golden-path analysis")
    analyze.add_argument("--run-id", default="abraxas-cli-analyze")
    analyze.add_argument("--input", type=Path, default=None)
    analyze.add_argument("--alembic-task", type=Path, default=None)
    analyze.add_argument("--oracle-candidate", type=Path, default=None)
    analyze.add_argument("--schema-ref", default=None)
    analyze.add_argument("--no-alembic", action="store_true")
    analyze.add_argument(
        "--alembic-mode", choices=["advisory", "shadow"], default="advisory"
    )
    analyze.add_argument(
        "--lane",
        choices=[lane.value for lane in ActivationLane],
        default=ActivationLane.LOCAL_DEV.value,
    )
    analyze.add_argument("--out", type=Path, default=None)
    analyze.set_defaults(func=_cmd_analyze)

    validate = sub.add_parser(
        "validate", help="Validate payload against contracts/ schema"
    )
    validate.add_argument("--schema-ref", required=True)
    validate.add_argument("--payload", type=Path, required=True)
    validate.add_argument("--execution-id", default="abraxas-cli-validate")
    validate.set_defaults(func=_cmd_validate)

    replay = sub.add_parser("replay", help="Replay advisory/Alembic receipt")
    replay.add_argument("--receipt", type=Path, required=True)
    replay.add_argument("--run-id", default=None)
    replay.add_argument(
        "--lane",
        choices=[lane.value for lane in ActivationLane],
        default=ActivationLane.LOCAL_DEV.value,
    )
    replay.add_argument("--out", type=Path, default=None)
    replay.set_defaults(func=_cmd_replay)

    status = sub.add_parser("status", help="Print bounded current-state snapshot")
    status.set_defaults(func=_cmd_status)

    # --- AI OS kernel commands ---
    os_parser = sub.add_parser("os", help="AI OS kernel control plane")
    os_sub = os_parser.add_subparsers(dest="os_command", required=True)

    os_status = os_sub.add_parser("status", help="AI OS kernel posture (SHADOW)")
    os_status.set_defaults(func=_cmd_os_status)

    ev_vol = os_sub.add_parser("evolution-volume", help="Light SHADOW view of Hermes/plural forager volume by task_class (advisory)")
    ev_vol.set_defaults(func=_cmd_os_evolution_volume)

    ev_review = os_sub.add_parser(
        "evolution-review",
        help="Slice G SHADOW operator handoff review for volume-derived patch candidates",
    )
    ev_review.add_argument(
        "--fixture",
        type=Path,
        default=Path(SLICE_G_DEFAULT_FIXTURE),
        help="Volume trace fixture JSON array",
    )
    ev_review.add_argument(
        "--write",
        action="store_true",
        help="Write the deterministic JSON and markdown review receipts under out/",
    )
    ev_review.add_argument(
        "--out",
        type=Path,
        default=Path(SLICE_G_DEFAULT_OUT_PATH),
    )
    ev_review.add_argument(
        "--md",
        type=Path,
        default=Path(SLICE_G_DEFAULT_MD_PATH),
    )
    ev_review.set_defaults(func=_cmd_os_evolution_review)

    alembic_res = os_sub.add_parser(
        "alembic-residuals",
        help="Track C Alembic residual inventory (stubs stay stubbed; advisory)",
    )
    alembic_res.set_defaults(func=_cmd_os_alembic_residuals)

    main_audit = os_sub.add_parser(
        "main-audit",
        help=(
            "Main-scope cleanliness + fast-ci receipts for Notion engineering-quality "
            "audit (advisory; no Notion writeback)"
        ),
    )
    main_audit.add_argument(
        "--execute-smoke",
        action="store_true",
        help="Run bounded smoke checks when building fast_ci receipt",
    )
    main_audit.add_argument(
        "--write",
        action="store_true",
        help="Write out/audit/main_cleanliness.latest.json and fast_ci.latest.json",
    )
    main_audit.set_defaults(func=_cmd_os_main_audit)

    memetic_brier = os_sub.add_parser(
        "memetic-brier-dry-run",
        help=(
            "Project memetic futurecast → BrierLedgerEntry.v1 shape "
            "(SHADOW dry-run; never writes out/brier)"
        ),
    )
    memetic_brier.add_argument("--forecast-id", default="")
    memetic_brier.add_argument("--topic", default="")
    memetic_brier.add_argument("--horizon", default="30d")
    memetic_brier.add_argument("--probability", type=float, default=None)
    memetic_brier.add_argument("--outcome", type=float, default=None)
    memetic_brier.add_argument("--register", default="INFERRED")
    memetic_brier.add_argument("--evidence-density", type=float, default=0.5)
    memetic_brier.add_argument("--claim", default="")
    memetic_brier.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not the live ledger path)",
    )
    memetic_brier.add_argument("--out-root", type=Path, default=None)
    memetic_brier.set_defaults(func=_cmd_os_memetic_brier_dry_run)

    holler_out = os_sub.add_parser(
        "holler-outcome-dry-run",
        help=(
            "Project holler ticket → ForecastOutcomeBindingPacket.v1 shape "
            "(FORECAST_GATED dry-run; never writes bindings / no live odds)"
        ),
    )
    holler_out.add_argument("--ticket-id", default="")
    holler_out.add_argument("--sport", default="UNKNOWN")
    holler_out.add_argument("--event-ref", default="")
    holler_out.add_argument("--market-class", default="UNKNOWN")
    holler_out.add_argument("--probability", type=float, default=None)
    holler_out.add_argument("--register", default="INFERRED")
    holler_out.add_argument("--expected-outcome", default="")
    holler_out.add_argument("--observed-outcome", default=None)
    holler_out.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not the live binding path)",
    )
    holler_out.add_argument("--out-root", type=Path, default=None)
    holler_out.set_defaults(func=_cmd_os_holler_outcome_dry_run)

    noctis_review = os_sub.add_parser(
        "noctis-review-dry-run",
        help=(
            "Project noctis dream → OperatorReviewQueueItem.v1 shape + continuity seed "
            "(SHADOW; never writes queue or durable memory)"
        ),
    )
    noctis_review.add_argument("--narrative", required=True)
    noctis_review.add_argument("--dream-id", default=None)
    noctis_review.add_argument("--mode", default="SYSTEM_DREAM")
    noctis_review.add_argument("--privacy-tier", default="PUBLIC_SYNTHETIC")
    noctis_review.add_argument("--source", default="SYSTEM")
    noctis_review.add_argument("--seed", default="0")
    noctis_review.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not the live queue path)",
    )
    noctis_review.add_argument("--out-root", type=Path, default=None)
    noctis_review.set_defaults(func=_cmd_os_noctis_review_dry_run)

    branch_hyg = os_sub.add_parser(
        "branch-hygiene",
        help="Classify remote branches (advisory inventory; never deletes)",
    )
    branch_hyg.set_defaults(func=_cmd_os_branch_hygiene)

    forensics = os_sub.add_parser(
        "forensics",
        help="Memetic forensics spine (SHADOW; ops gate always DENIED)",
    )
    forensics_sub = forensics.add_subparsers(dest="forensics_command", required=True)
    f_run = forensics_sub.add_parser(
        "run",
        help="Run forensics on EvidencePack path → disposition + denied ops gate",
    )
    f_run.add_argument("--pack", type=Path, required=True)
    f_run.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not production activation)",
    )
    f_run.set_defaults(func=_cmd_os_forensics_run)
    f_status = forensics_sub.add_parser(
        "status",
        help="Forensics engine posture (SLICE_C; ops_gate_default DENIED)",
    )
    f_status.set_defaults(func=_cmd_os_forensics_status)
    f_project = forensics_sub.add_parser(
        "project",
        help="AAL-Viz forensic projection from EvidencePack (SHADOW; DENIED)",
    )
    f_project.add_argument("--pack", type=Path, required=True)
    f_project.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not production activation)",
    )
    f_project.set_defaults(func=_cmd_os_forensics_project)
    f_route = forensics_sub.add_parser(
        "route",
        help="Ops route intent (Level99/Neon seed only; gate DENIED; no execution)",
    )
    f_route.add_argument("--pack", type=Path, required=True)
    f_route.add_argument(
        "--prefer-neon",
        action="store_true",
        help="Prefer neon_genie_ideation seed target when READY",
    )
    f_route.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not production activation)",
    )
    f_route.set_defaults(func=_cmd_os_forensics_route)
    f_seed = forensics_sub.add_parser(
        "seed-level99",
        help="Seed Level99 content packet from forensic READY (SHADOW; no publish)",
    )
    f_seed.add_argument("--pack", type=Path, required=True)
    f_seed.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not production activation)",
    )
    f_seed.set_defaults(func=_cmd_os_forensics_seed_level99)

    forage = sub.add_parser("forage", help="Signal forage / EvidencePack OS syscall")
    forage_sub = forage.add_subparsers(dest="forage_command", required=True)

    f_validate = forage_sub.add_parser(
        "validate", help="Validate EvidencePack.v0 JSON"
    )
    f_validate.add_argument("--pack", type=Path, required=True)
    f_validate.set_defaults(func=_cmd_forage_validate)

    f_ingest = forage_sub.add_parser(
        "ingest", help="Emit FamiliarIngestionReceipt.v0 (SHADOW)"
    )
    f_ingest.add_argument("--pack", type=Path, required=True)
    f_ingest.add_argument("--out", type=Path, default=None)
    f_ingest.add_argument(
        "--print-only",
        action="store_true",
        help="Do not write receipt files",
    )
    f_ingest.set_defaults(func=_cmd_forage_ingest)

    f_spine = forage_sub.add_parser(
        "spine-touch",
        help="Build advisory spine touchpoint seeds from pack (no Oracle run)",
    )
    f_spine.add_argument("--pack", type=Path, required=True)
    f_spine.add_argument("--out", type=Path, default=None)
    f_spine.add_argument("--out-root", type=Path, default=None)
    f_spine.set_defaults(func=_cmd_forage_spine_touch)

    f_bridge = forage_sub.add_parser(
        "oracle-belief-bridge",
        help=(
            "Bridge pack → oracle shadow intake + belief candidate seeds "
            "(SHADOW; no Oracle runtime / BeliefGraph mutation)"
        ),
    )
    f_bridge.add_argument("--pack", type=Path, required=True)
    f_bridge.add_argument("--out", type=Path, default=None)
    f_bridge.add_argument("--out-root", type=Path, default=None)
    f_bridge.set_defaults(func=_cmd_forage_oracle_belief_bridge)

    f_review = forage_sub.add_parser(
        "operator-review",
        help=(
            "Emit FamiliarOperatorReviewPacket.v0 disposition seed from pack "
            "(SHADOW; no queue write / attestation)"
        ),
    )
    f_review.add_argument("--pack", type=Path, required=True)
    f_review.add_argument("--out", type=Path, default=None)
    f_review.add_argument("--out-root", type=Path, default=None)
    f_review.set_defaults(func=_cmd_forage_operator_review)

    f_review_dry = forage_sub.add_parser(
        "operator-review-dry-run",
        help=(
            "Map pack → FamiliarOperatorReviewPacket → OperatorReviewQueueItem.v1 "
            "/ Run.v1 shape (SHADOW dry-run; never writes out/operator_review_queue)"
        ),
    )
    f_review_dry.add_argument("--pack", type=Path, required=True)
    f_review_dry.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional audit artifact path (not the live queue path)",
    )
    f_review_dry.add_argument("--out-root", type=Path, default=None)
    f_review_dry.set_defaults(func=_cmd_forage_operator_review_dry_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
