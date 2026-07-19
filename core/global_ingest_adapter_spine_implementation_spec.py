from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestAdapterSpineImplementationSpec.v1"
SPEC_PLAN_JSON_PATH = Path("out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json")
SPEC_JSON_PATH = Path("out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json")
SPEC_MD_PATH = Path("out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.md")
FUTURE_ADDITIVE_CONTRACTS = (
    "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
    "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
    "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
)
FUTURE_CANDIDATE_RUNNER = "scripts/ingest/run_oracle_signal_intake_boundary.py"
FUTURE_SHADOW_RECEIPT = "out/oracle/oracle_signal_intake_receipt.latest.json"
ADDITIVE_SHADOW_PATCH_ID = "PATCH-ABX-GLOBAL-INGEST-ADDITIVE-SHADOW-CONTRACTS-001"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_weight": False,
        "github_writeback": False,
        "implementation_authority": False,
        "ingest_runner_mutation": False,
        "notion_writeback": False,
        "pipeline_or_route_mutation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def _spec_sections() -> list[dict[str, Any]]:
    return [
        {
            "section_id": "GI-SPEC-001",
            "section_name": "operator_decision_evidence_binding",
            "requirement": "Bind the future implementation lane to the approved operator decision record and separate spec-plan hashes.",
            "status": "SPECIFIED_ADVISORY_ONLY",
        },
        {
            "section_id": "GI-SPEC-002",
            "section_name": "oracle_signal_contract_boundary",
            "requirement": "Additive contracts may define candidate signal packets, input envelope references, and shadow intake receipts only.",
            "status": "SPECIFIED_ADVISORY_ONLY",
        },
        {
            "section_id": "GI-SPEC-003",
            "section_name": "ingest_runner_non_mutation_boundary",
            "requirement": "Do not change run_ingest_once.py or run_oracle_intake.py behavior in the spec PR or any implementation PR without a later governed authorization lane.",
            "status": "AUTHORITY_DENIED",
        },
        {
            "section_id": "GI-SPEC-004",
            "section_name": "pipeline_route_non_mutation_boundary",
            "requirement": "Do not bind oracle_signal into runtime pipelines, YGGDRASIL routes, scheduler decisions, queues, or forecast weighting.",
            "status": "AUTHORITY_DENIED",
        },
        {
            "section_id": "GI-SPEC-005",
            "section_name": "deterministic_serialization_contract",
            "requirement": "Future receipts must use canonical JSON serialization, stable ordering, and deterministic hashes with no wall-clock or random inputs.",
            "status": "SPECIFIED_ADVISORY_ONLY",
        },
        {
            "section_id": "GI-SPEC-006",
            "section_name": "shadow_only_validation_plan",
            "requirement": "Validation may prove schema conformance and shadow receipt generation only; it must not prove execution readiness.",
            "status": "SPECIFIED_ADVISORY_ONLY",
        },
        {
            "section_id": "GI-SPEC-007",
            "section_name": "authority_lock_validation_matrix",
            "requirement": "Tests must assert every authority lock remains false and reject any implementation-authority drift.",
            "status": "SPECIFIED_ADVISORY_ONLY",
        },
        {
            "section_id": "GI-SPEC-008",
            "section_name": "rollback_and_fail_closed_plan",
            "requirement": "Missing upstream evidence, hash drift, schema mismatch, or authority-lock drift must route to NOT_COMPUTABLE or held status.",
            "status": "SPECIFIED_ADVISORY_ONLY",
        },
    ]


def build_global_ingest_adapter_spine_implementation_spec(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    spec_plan = _read_json(root / SPEC_PLAN_JSON_PATH)
    plan_ready = (
        spec_plan.get("status")
        in {
            "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_READY",
            "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_CONSUMED_BY_IMPLEMENTATION_SPEC",
        }
        and spec_plan.get("spec_authoring_allowed") is True
        and spec_plan.get("implementation_authorized") is False
        and spec_plan.get("execution_authority") is False
    )
    observed_additive_contracts = [
        path for path in FUTURE_ADDITIVE_CONTRACTS if (root / path).exists()
    ]
    missing_additive_contracts = sorted(
        set(FUTURE_ADDITIVE_CONTRACTS) - set(observed_additive_contracts)
    )
    candidate_runner_observed = (root / FUTURE_CANDIDATE_RUNNER).exists()
    shadow_receipt_observed = (root / FUTURE_SHADOW_RECEIPT).exists()
    additive_shadow_surfaces_observed = (
        not missing_additive_contracts
        and candidate_runner_observed
        and shadow_receipt_observed
    )
    implementation_pr_consumed = plan_ready and additive_shadow_surfaces_observed
    safe_to_prepare_implementation_pr = plan_ready and not implementation_pr_consumed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY"
            if implementation_pr_consumed
            else "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY"
            if plan_ready
            else "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_BLOCKED"
        ),
        "spec_id": "global_ingest_adapter_spine_implementation_spec_001",
        "spec_hash": "",
        "command": "BUILD_GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "target_pipeline_id": "oracle_signal",
        "target_display_name": "Oracle Signal Layer Pipeline",
        "patch_id": "PATCH-ABX-GLOBAL-INGEST-SEPARATE-IMPLEMENTATION-SPEC-001",
        "source_spec_plan_path": str(SPEC_PLAN_JSON_PATH),
        "source_spec_plan_hash": str(spec_plan.get("spec_plan_hash", "NOT_COMPUTABLE")),
        "source_decision_record_path": str(spec_plan.get("source_decision_record_path", "NOT_COMPUTABLE")),
        "source_decision_record_hash": str(spec_plan.get("source_decision_record_hash", "NOT_COMPUTABLE")),
        "source_selected_decision": str(spec_plan.get("source_selected_decision", "NOT_COMPUTABLE")),
        "spec_authoring_allowed": plan_ready,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_implementation_pr": safe_to_prepare_implementation_pr,
        "implementation_pr_consumed": implementation_pr_consumed,
        "additive_shadow_surfaces_observed": additive_shadow_surfaces_observed,
        "authority_locks": _authority_locks(),
        "future_additive_contracts": list(FUTURE_ADDITIVE_CONTRACTS),
        "observed_additive_contracts": sorted(observed_additive_contracts),
        "missing_additive_contracts": missing_additive_contracts,
        "future_candidate_runner": FUTURE_CANDIDATE_RUNNER,
        "candidate_runner_observed": candidate_runner_observed,
        "future_shadow_receipt": FUTURE_SHADOW_RECEIPT,
        "shadow_receipt_observed": shadow_receipt_observed,
        "preserved_surfaces": [
            "core/oracle_signal.py must remain absent unless a later governed implementation lane authorizes creation",
            "scripts/ingest/run_ingest_once.py behavior remains unchanged",
            "scripts/ingest/run_oracle_intake.py behavior remains unchanged",
            "contracts/pipelines runtime bindings remain unchanged",
            "contracts/yggdrasil route bindings remain unchanged",
        ],
        "blocked_actions": [
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "QUEUE_MUTATION",
            "FORECAST_WEIGHTING",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "TOKEN_MINTING",
        ],
        "spec_sections": _spec_sections(),
        "acceptance_criteria": [
            "consume the separate implementation spec-plan hash",
            "preserve advisory_only/projection_only/non_authoritative posture",
            "keep implementation_authorized false",
            "keep execution_authority false",
            "deny runtime, scheduler, canon, queue, route, and forecast mutation",
            "define additive contract and candidate-runner boundaries without implementing them",
            "produce deterministic JSON and markdown artifacts",
            "include targeted tests and fast-ci validation",
        ],
        "recommended_next_action": (
            "hold; additive shadow contracts, candidate runner, and shadow receipt are already repo-observed as advisory-only evidence"
            if implementation_pr_consumed
            else "prepare a future additive contract-and-candidate-runner implementation PR only after this spec is merged and reviewed"
            if safe_to_prepare_implementation_pr
            else "repair implementation spec evidence before any additive shadow contract planning"
        ),
        "recommended_next_patch": ADDITIVE_SHADOW_PATCH_ID
        if safe_to_prepare_implementation_pr
        else "NOT_COMPUTABLE",
    }
    packet["spec_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "spec_hash"})
    return packet


def render_global_ingest_adapter_spine_implementation_spec_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Global Ingest Adapter Spine Implementation Spec",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `patch_id`: `{packet['patch_id']}`",
        f"- `spec_authoring_allowed`: `{packet['spec_authoring_allowed']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `safe_to_prepare_implementation_pr`: `{packet['safe_to_prepare_implementation_pr']}`",
        f"- `implementation_pr_consumed`: `{packet['implementation_pr_consumed']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Future Additive Contracts",
        "",
    ]
    for item in packet["future_additive_contracts"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Observed Additive Contracts", ""])
    for item in packet["observed_additive_contracts"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Missing Additive Contracts", ""])
    for item in packet["missing_additive_contracts"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Preserved Surfaces", ""])
    for item in packet["preserved_surfaces"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Spec Sections", ""])
    for section in packet["spec_sections"]:
        lines.append(f"- `{section['section_id']}` `{section['section_name']}`: {section['status']}")
    return lines


def write_global_ingest_adapter_spine_implementation_spec(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_adapter_spine_implementation_spec(root)
    write_canonical_json(target_root / SPEC_JSON_PATH, packet)
    _write_markdown(target_root / SPEC_MD_PATH, render_global_ingest_adapter_spine_implementation_spec_markdown(packet))
    return packet
