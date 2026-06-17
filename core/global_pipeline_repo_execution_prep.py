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
DOCTRINE_DASHBOARD_REVIEW_RECORD_PATH = Path(
    "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json"
)
GLOBAL_INGEST_OPERATOR_DECISION_RECORD_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_record_001.latest.json"
)
GLOBAL_INGEST_IMPLEMENTATION_SPEC_PATH = Path(
    "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json"
)
ORACLE_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_PATH = Path(
    "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json"
)


def _read_json(root: Path, rel_path: Path) -> dict[str, Any]:
    import json

    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def _read_optional_json(root: Path, rel_path: Path) -> dict[str, Any] | None:
    path = root / rel_path
    if not path.exists():
        return None
    return _read_json(root, rel_path)


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


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


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
    doctrine_dashboard_review_record = _read_optional_json(source_base, DOCTRINE_DASHBOARD_REVIEW_RECORD_PATH)
    global_ingest_operator_decision_record = _read_optional_json(
        source_base, GLOBAL_INGEST_OPERATOR_DECISION_RECORD_PATH
    )
    global_ingest_implementation_spec = _read_optional_json(source_base, GLOBAL_INGEST_IMPLEMENTATION_SPEC_PATH)
    oracle_physical_implementation_review = _read_optional_json(
        source_base, ORACLE_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_PATH
    )
    doctrine_dashboard_review_accepted = bool(
        doctrine_dashboard_review_record
        and doctrine_dashboard_review_record.get("status") == "GLOBAL_PIPELINE_DOCTRINE_DASHBOARD_REVIEW_ACCEPTED"
        and doctrine_dashboard_review_record.get("dashboard_review_accepted_as_reviewed_evidence") is True
        and doctrine_dashboard_review_record.get("doctrine_review_accepted_as_reviewed_evidence") is True
        and doctrine_dashboard_review_record.get("implementation_authorized") is False
        and doctrine_dashboard_review_record.get("execution_authority") is False
        and doctrine_dashboard_review_record.get("valid_for_execution") is False
    )
    operator_review_hold = bool(
        dashboard_packet
        and doctrine_review
        and not doctrine_dashboard_review_accepted
        and (
            dashboard_packet.get("recommended_next_state") == "review"
            or doctrine_review.get("state") in {"repair_required", "held", "rejected"}
        )
    )
    operator_decision_status = (
        global_ingest_operator_decision_record.get("status")
        if global_ingest_operator_decision_record
        else None
    )
    operator_decision_recorded = bool(
        global_ingest_operator_decision_record
        and operator_decision_status
        in {
            "GLOBAL_INGEST_OPERATOR_DECISION_RECORDED",
            "GLOBAL_INGEST_OPERATOR_DECISION_CONSUMED_BY_SEPARATE_IMPLEMENTATION_SPEC_PLAN",
        }
        and global_ingest_operator_decision_record.get("selected_decision")
        == "APPROVE_SEPARATE_IMPLEMENTATION_SPEC"
        and global_ingest_operator_decision_record.get("implementation_spec_authoring_approved") is True
        and (
            global_ingest_operator_decision_record.get("safe_to_prepare_planning_pr") is True
            or (
                operator_decision_status
                == "GLOBAL_INGEST_OPERATOR_DECISION_CONSUMED_BY_SEPARATE_IMPLEMENTATION_SPEC_PLAN"
                and global_ingest_operator_decision_record.get("separate_spec_plan_observed") is True
            )
        )
        and global_ingest_operator_decision_record.get("implementation_authorized") is False
        and global_ingest_operator_decision_record.get("execution_authority") is False
        and global_ingest_operator_decision_record.get("valid_for_execution") is False
    )
    implementation_spec_ready = bool(
        global_ingest_implementation_spec
        and global_ingest_implementation_spec.get("status")
        in {
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY",
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY",
        }
        and (
            global_ingest_implementation_spec.get("recommended_next_patch")
            == "PATCH-ABX-GLOBAL-INGEST-ADDITIVE-SHADOW-CONTRACTS-001"
            or (
                global_ingest_implementation_spec.get("recommended_next_patch") == "NOT_COMPUTABLE"
                and global_ingest_implementation_spec.get("implementation_pr_consumed") is True
                and global_ingest_implementation_spec.get("additive_shadow_surfaces_observed") is True
            )
        )
        and global_ingest_implementation_spec.get("implementation_authorized") is False
        and global_ingest_implementation_spec.get("execution_authority") is False
    )
    implementation_planning_evidence_ready = operator_decision_recorded and implementation_spec_ready
    implementation_decision_required = bool(
        dashboard_packet
        and doctrine_dashboard_review_accepted
        and not implementation_planning_evidence_ready
        and (
            dashboard_packet.get("physical_repo_implementation_ready") is False
            or dashboard_packet.get("execution_authority") is False
        )
    )
    physical_implementation_authorization_required = bool(
        dashboard_packet
        and doctrine_dashboard_review_accepted
        and implementation_planning_evidence_ready
        and not (
            oracle_physical_implementation_review
            and oracle_physical_implementation_review.get("status")
            == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR"
            and oracle_physical_implementation_review.get("review_requested") is True
            and oracle_physical_implementation_review.get("implementation_authorized") is False
            and oracle_physical_implementation_review.get("execution_authority") is False
            and oracle_physical_implementation_review.get("valid_for_execution") is False
        )
        and (
            dashboard_packet.get("physical_repo_implementation_ready") is False
            or dashboard_packet.get("execution_authority") is False
        )
    )
    physical_implementation_authorization_review_held = bool(
        dashboard_packet
        and doctrine_dashboard_review_accepted
        and implementation_planning_evidence_ready
        and oracle_physical_implementation_review
        and oracle_physical_implementation_review.get("status")
        == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR"
        and oracle_physical_implementation_review.get("review_requested") is True
        and oracle_physical_implementation_review.get("implementation_authorized") is False
        and oracle_physical_implementation_review.get("execution_authority") is False
        and oracle_physical_implementation_review.get("valid_for_execution") is False
        and (
            dashboard_packet.get("physical_repo_implementation_ready") is False
            or dashboard_packet.get("execution_authority") is False
        )
    )
    readiness_ready = (
        (not missing_dependencies)
        and (not operator_review_hold)
        and (not implementation_decision_required)
        and (not physical_implementation_authorization_required)
        and (not physical_implementation_authorization_review_held)
    )
    queue_item_count = int(queue["queue_item_count"])
    queue_p0_count = int(queue.get("p0_count", 0))
    queue_state_counts = dict(queue["state_counts"])

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
            (
                "Current queue remains advisory-only and now shows "
                f"{queue_item_count} items, including {queue_p0_count} P0 held decision item(s), "
                f"with state counts {queue_state_counts}."
            ),
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
            "Global pipeline doctrine/dashboard review gate",
            "blocked" if operator_review_hold else "reviewed",
            [
                "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json",
                "out/global_pipeline_aal_viz/dashboard_packet.latest.json",
                "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json",
            ],
            (
                "Doctrine review and dashboard posture are accepted as reviewed evidence only; physical repo "
                "execution remains fail-closed until a separate operator implementation decision exists."
                if doctrine_dashboard_review_accepted
                else "Physical repo execution prep remains fail-closed until doctrine review and dashboard posture stop requiring review or repair."
            ),
        ),
        _phase(
            "phase_06_implementation_decision_gate",
            "Global ingest implementation decision gate",
            "blocked" if implementation_decision_required else "reviewed",
            [
                "out/operator_review/global_ingest_operator_decision_request_001.latest.json",
                "out/operator_review/global_ingest_operator_decision_record_001.latest.json",
                "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json",
                "out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json",
            ],
            (
                "Global Ingest operator decision evidence and the separate implementation spec are present; "
                "they authorize planning/spec evidence only, not physical Oracle implementation."
                if implementation_planning_evidence_ready
                else "Physical repo execution prep remains blocked until explicit Global Ingest operator decision evidence authorizes a separate implementation spec."
            ),
        ),
        _phase(
            "phase_07_physical_implementation_authorization_gate",
            "Oracle Signal physical implementation authorization gate",
            "held" if physical_implementation_authorization_review_held else ("blocked" if physical_implementation_authorization_required else "ready"),
            [
                "out/operator_review/global_ingest_operator_decision_record_001.latest.json",
                "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json",
                "out/operator_review/global_pipeline_gap_backlog_001.latest.json",
                "out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json",
            ],
            (
                "Oracle Signal physical implementation authorization review is requested and held for operator; core/oracle_signal.py creation remains denied."
                if physical_implementation_authorization_review_held
                else "Oracle Signal physical implementation remains blocked: the current decision and spec permit planning/spec evidence only and keep core/oracle_signal.py creation denied."
            ),
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
            "global_ingest_operator_decision_record": (
                str(global_ingest_operator_decision_record.get("decision_record_hash"))
                if global_ingest_operator_decision_record
                else "NOT_COMPUTABLE"
            ),
            "global_ingest_adapter_spine_implementation_spec": (
                str(global_ingest_implementation_spec.get("spec_hash"))
                if global_ingest_implementation_spec
                else "NOT_COMPUTABLE"
            ),
            "oracle_signal_physical_implementation_authorization_review": (
                str(oracle_physical_implementation_review.get("review_hash"))
                if oracle_physical_implementation_review
                else "NOT_COMPUTABLE"
            ),
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
            else _dedupe_preserve_order(
                [
                    *(
                        ["MISSING_GLOBAL_PIPELINE_SPINE_SURFACES"]
                        if missing_dependencies
                        else []
                    ),
                    *[f"MISSING:{path}" for path in missing_dependencies],
                    *(
                        ["GLOBAL_PIPELINE_DOCTRINE_DASHBOARD_REVIEW_REQUIRED"]
                        if operator_review_hold
                        else []
                    ),
                    *(
                        ["GLOBAL_PIPELINE_IMPLEMENTATION_DECISION_REQUIRED"]
                        if implementation_decision_required
                        else []
                    ),
                    *(
                        ["ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REQUIRED"]
                        if physical_implementation_authorization_required
                        else []
                    ),
                    *(
                        ["ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD"]
                        if physical_implementation_authorization_review_held
                        else []
                    ),
                ]
            )
        ),
        "recommended_next_state": "ready_for_physical_repo_implementation" if readiness_ready else "hold",
        "recommended_next_commands": (
            [
                "APPLY_GLOBAL_PIPELINE_AUTOMATION_STACK_TO_REPO",
                "RUN_GLOBAL_PIPELINE_REPO_EXECUTION_RECEIPT_001",
            ]
            if readiness_ready
            else _dedupe_preserve_order(
                [
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
                    *(
                        ["HOLD_FOR_OPERATOR_REVIEW"]
                        if operator_review_hold
                        else []
                    ),
                    *(
                        ["COLLECT_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE"]
                        if implementation_decision_required
                        else []
                    ),
                    *(
                        [
                            "HOLD_ORACLE_SIGNAL_IMPLEMENTATION_PENDING_AUTHORIZATION",
                            "REQUEST_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW",
                        ]
                        if physical_implementation_authorization_required
                        else []
                    ),
                    *(
                        [
                            "HOLD_ORACLE_SIGNAL_IMPLEMENTATION_PENDING_OPERATOR_AUTHORIZATION",
                            "COLLECT_EXPLICIT_PHYSICAL_IMPLEMENTATION_OPERATOR_AUTHORIZATION",
                        ]
                        if physical_implementation_authorization_review_held
                        else []
                    ),
                ]
            )
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
            GLOBAL_INGEST_OPERATOR_DECISION_RECORD_PATH.as_posix(),
            GLOBAL_INGEST_IMPLEMENTATION_SPEC_PATH.as_posix(),
            ORACLE_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_PATH.as_posix(),
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
