from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.receipts.builder import build_receipt_markdown, build_spec_only_receipt

PREP_SCHEMA_VERSION = "GlobalPipelineRepoExecutionPrepPacket.v1"
PREP_JSON_PATH = Path("out/operator_review/global_pipeline_repo_execution_prep_001.latest.json")
PREP_MD_PATH = Path("out/operator_review/global_pipeline_repo_execution_prep_001.latest.md")
RECEIPT_JSON_PATH = Path("out/execution_receipts/global_pipeline_repo_prep.latest.json")
RECEIPT_MD_PATH = Path("out/execution_receipts/global_pipeline_repo_prep.latest.md")

QUEUE_PATH = Path("out/operator_review_queue/latest.json")
PROJECTION_PATH = Path("out/projections/global_pipeline_aal_viz_projection_packet_001.latest.json")
SYNC_RECEIPT_PATH = Path("out/sync/operator_review_queue_canon_sync_receipt_candidate_001.latest.json")
EXECUTION_RECEIPT_STANDARD_PATH = Path("out/execution_receipts/latest.json")

MISSING_DEPENDENCY_PATHS = (
    "out/global_pipeline_registry/latest.json",
    "out/global_pipeline_doctrine_validation/latest.json",
    "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json",
    "out/global_pipeline_aal_viz/dashboard_packet.latest.json",
    "out/global_pipeline_aal_viz/view_state.latest.json",
)

DASHBOARD_PATH = Path("out/global_pipeline_aal_viz/dashboard_packet.latest.json")
VIEW_STATE_PATH = Path("out/global_pipeline_aal_viz/view_state.latest.json")
DOCTRINE_REVIEW_PATH = Path("out/global_pipeline_doctrine_validation/operator_review_packet.latest.json")


def _read_json(root: Path, rel_path: Path) -> dict[str, Any]:
    import json

    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _phase(phase_id: str, title: str, status: str, repo_paths: list[str], notes: str) -> dict[str, Any]:
    return {
        "phase_id": phase_id,
        "title": title,
        "status": status,
        "repo_paths": repo_paths,
        "notes": notes,
    }


def build_global_pipeline_repo_execution_prep_packet(
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, Any]:
    base = Path(root)
    source_base = Path(source_root) if source_root is not None else base
    queue = _read_json(source_base, QUEUE_PATH)
    projection = _read_json(source_base, PROJECTION_PATH)
    sync_receipt = _read_json(source_base, SYNC_RECEIPT_PATH)
    receipt_standard = _read_json(source_base, EXECUTION_RECEIPT_STANDARD_PATH)

    missing_dependencies = [
        path for path in MISSING_DEPENDENCY_PATHS if not (source_base / path).exists()
    ]
    dashboard_packet = (
        _read_json(source_base, DASHBOARD_PATH) if not missing_dependencies else None
    )
    doctrine_review = (
        _read_json(source_base, DOCTRINE_REVIEW_PATH)
        if "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json"
        not in missing_dependencies
        else None
    )
    operator_review_hold = bool(
        dashboard_packet
        and doctrine_review
        and (
            dashboard_packet.get("recommended_next_state") == "review"
            or doctrine_review.get("state") in {"repair_required", "held", "rejected"}
        )
    )
    readiness_ready = (not missing_dependencies) and (not operator_review_hold)

    phases = [
        _phase(
            "phase_01_receipt_standard",
            "Repo execution receipt standard",
            "ready",
            [
                "core/receipts/models.py",
                "core/receipts/builder.py",
                "core/receipts/validator.py",
                "Scripts/run_repo_execution_receipt.py",
                "contracts/receipts/repo_execution_receipt.v1.schema.json",
                "out/execution_receipts/latest.json",
            ],
            "The governed receipt standard is implemented and can record spec-only, simulated, local, CI, and committed execution states.",
        ),
        _phase(
            "phase_02_operator_review_queue",
            "Operator review queue staging",
            "ready",
            [
                "core/global_operator_review_queue.py",
                "Scripts/run_global_operator_review_queue.py",
                "out/operator_review_queue/latest.json",
                "out/sync/operator_review_queue_canon_sync_receipt_candidate_001.latest.json",
            ],
            "Current queue remains advisory-only and shows two P2 items with no authority leakage.",
        ),
        _phase(
            "phase_03_projection_surface",
            "Global pipeline projection surface",
            "ready",
            [
                "out/projections/global_pipeline_aal_viz_projection_packet_001.latest.json",
            ],
            "The global pipeline AAL-Viz projection packet exists and remains projection-only.",
        ),
        _phase(
            "phase_04_missing_global_pipeline_spine",
            "Missing global pipeline spine dependencies",
            "blocked" if missing_dependencies else "ready",
            list(missing_dependencies),
            "Physical repo execution prep cannot claim readiness until registry, doctrine validation, operator-review packet, and dashboard artifacts exist in-repo.",
        ),
        _phase(
            "phase_05_operator_review_gate",
            "Global pipeline operator review gate",
            "blocked" if operator_review_hold else "ready",
            [
                "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json",
                "out/global_pipeline_aal_viz/dashboard_packet.latest.json",
            ],
            "Physical repo execution prep remains fail-closed until doctrine review and dashboard posture stop requiring operator review or repair.",
        ),
    ]

    packet: dict[str, Any] = {
        "schema_version": PREP_SCHEMA_VERSION,
        "prep_packet_id": "",
        "command": "RUN_GLOBAL_PIPELINE_REPO_EXECUTION_PREP_001",
        "status": "REPO_EXECUTION_PREP_PACKET_READY" if readiness_ready else "REPO_EXECUTION_PREP_PACKET_BLOCKED",
        "execution_mode": "PREP_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "execution_authority": False,
        "repo_execution_status": "NOT_EXECUTED_IN_CHAT",
        "source_hashes": {
            "operator_review_queue": queue["run_id"],
            "global_pipeline_projection": projection["projection_id"],
            "canon_sync_receipt_candidate": sync_receipt["receipt_id"],
            "repo_execution_receipt_standard": receipt_standard["receipt_id"],
        },
        "queue_summary": {
            "queue_item_count": queue["queue_item_count"],
            "recommended_next_state": queue["recommended_next_state"],
            "repo_execution_required_count": queue["repo_execution_required_count"],
            "state_counts": queue["state_counts"],
        },
        "projection_summary": {
            "queue_item_count": projection["queue_item_count"],
            "repo_execution_required_count": projection["repo_execution_required_count"],
            "stabilization_ready_count": projection["stabilization_ready_count"],
            "recommended_next_state": projection["recommended_next_state"],
        },
        "canon_sync_summary": {
            "receipt_id": sync_receipt["receipt_id"],
            "repo_receipts_linked_count": len(sync_receipt["repo_receipts_linked"]),
            "recommended_next_state": sync_receipt["recommended_next_state"],
        },
        "missing_dependency_paths": missing_dependencies,
        "physical_repo_implementation_ready": readiness_ready,
        "phases": phases,
        "not_computable_reasons": (
            []
            if readiness_ready
            else [
                "MISSING_GLOBAL_PIPELINE_SPINE_SURFACES",
                *[f"MISSING:{path}" for path in missing_dependencies],
                *(
                    ["GLOBAL_PIPELINE_OPERATOR_REVIEW_REQUIRED"]
                    if operator_review_hold
                    else []
                ),
            ]
        ),
        "recommended_next_state": "ready_for_physical_repo_implementation" if readiness_ready else "hold",
        "recommended_next_commands": (
            [
                "APPLY_GLOBAL_PIPELINE_AUTOMATION_STACK_TO_REPO",
                "RUN_GLOBAL_PIPELINE_REPO_EXECUTION_RECEIPT_001",
            ]
            if readiness_ready
            else [
                *(
                    []
                    if not operator_review_hold
                    else ["HOLD_FOR_OPERATOR_REVIEW", "REQUEST_GLOBAL_PIPELINE_REPAIR"]
                ),
                *(
                    [
                        "BUILD_GLOBAL_PIPELINE_REGISTRY_001",
                        "RUN_GLOBAL_PIPELINE_DOCTRINE_VALIDATOR_PROOF_001",
                        "BUILD_GLOBAL_PIPELINE_AAL_VIZ_DASHBOARD_001",
                    ]
                    if missing_dependencies
                    else []
                ),
                "HOLD_FOR_OPERATOR_REVIEW",
            ]
        ),
    }
    packet["prep_packet_id"] = canonical_hash({k: v for k, v in packet.items() if k != "prep_packet_id"})
    return packet


def write_global_pipeline_repo_execution_prep_artifacts(
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    base = Path(root)
    packet = build_global_pipeline_repo_execution_prep_packet(base, source_root=source_root)

    receipt = build_spec_only_receipt(
        "RUN_GLOBAL_PIPELINE_REPO_EXECUTION_PREP_001",
        "python Scripts/run_global_pipeline_repo_execution_prep.py",
        pipeline_id="global_pipeline_spine",
        repo_name="Abraxas-v2.0",
        branch="main",
        source_artifact_refs=[
            PREP_JSON_PATH.as_posix(),
            QUEUE_PATH.as_posix(),
            PROJECTION_PATH.as_posix(),
            SYNC_RECEIPT_PATH.as_posix(),
            EXECUTION_RECEIPT_STANDARD_PATH.as_posix(),
        ],
    )

    write_canonical_json(base / PREP_JSON_PATH, packet)
    _write_markdown(
        base / PREP_MD_PATH,
        [
            "# Global Pipeline Repo Execution Prep",
            "",
            f"- `command`: `{packet['command']}`",
            f"- `status`: `{packet['status']}`",
            f"- `physical_repo_implementation_ready`: `{packet['physical_repo_implementation_ready']}`",
            f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
            "",
            "## Missing Dependencies",
            *(
                [f"- `{path}`" for path in packet["missing_dependency_paths"]]
                if packet["missing_dependency_paths"]
                else ["- none"]
            ),
            "",
            "## Next Commands",
            *[f"- `{command}`" for command in packet["recommended_next_commands"]],
        ],
    )

    write_canonical_json(base / RECEIPT_JSON_PATH, receipt.to_dict())
    (base / RECEIPT_MD_PATH).write_text(
        build_receipt_markdown(receipt, base / RECEIPT_JSON_PATH),
        encoding="utf-8",
    )

    return {
        "prep_packet": packet,
        "repo_execution_receipt": receipt.to_dict(),
    }
