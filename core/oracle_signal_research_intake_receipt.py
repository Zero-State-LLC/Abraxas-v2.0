from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalResearchIntakeReceipt.v1"
DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
RECEIPT_JSON_PATH = Path("out/sync/oracle_signal_research_intake_receipt/latest.json")
RECEIPT_MD_PATH = Path("out/sync/oracle_signal_research_intake_receipt/latest.md")
RECOMMENDED_NEXT_PLAN = "ORACLE_CONFIDENCE_CALIBRATION_PLAN_001"
DOWNSTREAM = "NOT_COMPUTABLE"


def _research_items() -> list[dict[str, Any]]:
    return [
        {
            "research_item_id": "RESEARCH-HDC-001",
            "topic": "hyperdimensional computing",
            "evidence_status": "APPLIED",
            "provenance": "RESEARCH",
            "notes": "symbolic vector encoding candidate for Oracle signal compression",
        },
        {
            "research_item_id": "RESEARCH-HDC-LOWDIM-001",
            "topic": "efficient low-dimensional hypervectors",
            "evidence_status": "APPLIED",
            "provenance": "RESEARCH",
            "notes": "dimension policy candidate for low-dimensional hypervector tests",
        },
        {
            "research_item_id": "RESEARCH-HDC-RECOVERY-001",
            "topic": "linear-code recovery for HDC",
            "evidence_status": "APPLIED",
            "provenance": "RESEARCH",
            "notes": "candidate recovery layer for bundled or ambiguous signal decomposition",
        },
        {
            "research_item_id": "RESEARCH-HDC-MARGIN-001",
            "topic": "large-margin HDC",
            "evidence_status": "APPLIED",
            "provenance": "RESEARCH",
            "notes": "candidate advisory classification boundary for routing confidence",
        },
        {
            "research_item_id": "RESEARCH-UQ-CALIBRATION-001",
            "topic": "uncertainty quantification and confidence calibration",
            "evidence_status": "APPLIED",
            "provenance": "RESEARCH",
            "notes": "candidate calibrated confidence layer for advisory uncertainty dimensions",
        },
        {
            "research_item_id": "RESEARCH-TRAJECTORY-CALIBRATION-001",
            "topic": "agentic trajectory calibration",
            "evidence_status": "APPLIED",
            "provenance": "RESEARCH",
            "notes": "candidate process-level confidence surface for multi-step Oracle chains",
        },
    ]


def _candidate_mappings() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "ORACLE_VECTOR_HDC_ENCODING",
            "provenance": "RESEARCH",
            "allowed_status": "ADVISORY_CANDIDATE",
            "proposed_role": "signal compression and symbolic vector representation",
            "supporting_research_item_ids": ["RESEARCH-HDC-001"],
        },
        {
            "candidate_id": "ORACLE_VECTOR_DIMENSION_POLICY",
            "provenance": "RESEARCH",
            "allowed_status": "ADVISORY_CANDIDATE",
            "proposed_role": "low-dimensional hypervector test policy",
            "supporting_research_item_ids": ["RESEARCH-HDC-LOWDIM-001"],
        },
        {
            "candidate_id": "ORACLE_SIGNAL_RECOVERY_LAYER",
            "provenance": "RESEARCH",
            "allowed_status": "SHADOW_CANDIDATE",
            "proposed_role": "decomposing bundled or ambiguous signals",
            "supporting_research_item_ids": ["RESEARCH-HDC-RECOVERY-001"],
        },
        {
            "candidate_id": "ORACLE_SIGNAL_MARGIN_CLASSIFIER",
            "provenance": "RESEARCH",
            "allowed_status": "FORECAST_CANDIDATE",
            "proposed_role": "advisory classification and routing confidence",
            "supporting_research_item_ids": ["RESEARCH-HDC-MARGIN-001"],
        },
        {
            "candidate_id": "ORACLE_CONFIDENCE_CALIBRATION",
            "provenance": "RESEARCH",
            "allowed_status": "ADVISORY_IMPLEMENTATION_CANDIDATE",
            "proposed_role": "calibrated confidence and uncertainty dimensions",
            "supporting_research_item_ids": ["RESEARCH-UQ-CALIBRATION-001"],
        },
        {
            "candidate_id": "ORACLE_TRAJECTORY_CONFIDENCE",
            "provenance": "RESEARCH",
            "allowed_status": "RESEARCH_CANDIDATE",
            "proposed_role": "process-level confidence over multi-step Oracle chains",
            "supporting_research_item_ids": ["RESEARCH-TRAJECTORY-CALIBRATION-001"],
        },
    ]


def _forbidden_actions() -> list[str]:
    return [
        "promote_research_to_canon",
        "authorize_runtime_execution",
        "bypass_operator_review",
        "mutate_governance",
        "add_live_prediction",
        "let_SHADOW_predict",
        "let_FORECAST_detect_drift",
        "treat_HDC_output_as_truth",
        "treat_calibrated_confidence_as_authorization",
    ]


def _governance_locks() -> dict[str, Any]:
    return {
        "governance_status": "FROZEN",
        "canon_status": "ADVISORY_ONLY",
        "execution_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "research_candidates_canonized": False,
        "downstream": DOWNSTREAM,
    }


def build_oracle_signal_research_intake_receipt() -> dict[str, Any]:
    research_items = _research_items()
    candidate_mappings = _candidate_mappings()
    advisory_candidates = [
        item["candidate_id"]
        for item in candidate_mappings
        if item["allowed_status"] in {"ADVISORY_CANDIDATE", "ADVISORY_IMPLEMENTATION_CANDIDATE"}
    ]
    shadow_candidates = [
        item["candidate_id"] for item in candidate_mappings if item["allowed_status"] == "SHADOW_CANDIDATE"
    ]
    forecast_candidates = [
        item["candidate_id"] for item in candidate_mappings if item["allowed_status"] == "FORECAST_CANDIDATE"
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": "",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "source_research_package": {
            "package_id": "ORACLE_SIGNAL_GLOBAL_INGEST_RESEARCH_SYNC_SEAL_2026_06_05",
            "package_status": "ASSIMILATED_ADVISORY_ONLY",
            "package_type": "ARXIV_RESEARCH_ASSIMILATION",
            "sync_seal": "Sync Seal — Research Assimilation Ready For Coding — 2026-06-05",
            "repo_notion_sync": "HIGH_CONFIDENCE",
            "research_intake": "APPLIED",
            "full_stack_assimilation": "APPLIED",
            "ready_for_codex_handoff": True,
        },
        "research_items": research_items,
        "candidate_mappings": candidate_mappings,
        "allowed_status": sorted({item["allowed_status"] for item in candidate_mappings}),
        "forbidden_actions": _forbidden_actions(),
        "governance_locks": _governance_locks(),
        "shadow_candidates": shadow_candidates,
        "forecast_candidates": forecast_candidates,
        "advisory_candidates": advisory_candidates,
        "not_computable_items": [
            {
                "item_id": RECOMMENDED_NEXT_PLAN,
                "reason": "planning artifact not emitted in repo; research intake receipt only recommends the next plan",
            },
            {
                "item_id": "ORACLE_SIGNAL_RESEARCH_RUNTIME_PROMOTION",
                "reason": "runtime Oracle logic is outside the authority boundary for this receipt",
            },
        ],
        "recommended_next_plan": RECOMMENDED_NEXT_PLAN,
        "downstream": DOWNSTREAM,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
    }
    packet["receipt_id"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_id"})
    return packet


def render_oracle_signal_research_intake_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Oracle Signal Research Intake Receipt",
        "",
        f"- `receipt_id`: `{packet['receipt_id']}`",
        f"- `generated_at`: `{packet['generated_at']}`",
        f"- `recommended_next_plan`: `{packet['recommended_next_plan']}`",
        f"- `downstream`: `{packet['downstream']}`",
        "",
        "## Candidate Mappings",
        "",
    ]
    for item in packet["candidate_mappings"]:
        lines.append(
            f"- `{item['candidate_id']}` -> `{item['allowed_status']}`: {item['proposed_role']}"
        )
    lines.extend(["", "## Not Computable Items", ""])
    for item in packet["not_computable_items"]:
        lines.append(f"- `{item['item_id']}`: {item['reason']}")
    return lines


def write_oracle_signal_research_intake_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    _ = Path(source_root)
    target_root = Path(out_root) if out_root is not None else Path(".")
    packet = build_oracle_signal_research_intake_receipt()
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    md_path = target_root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_oracle_signal_research_intake_receipt_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
