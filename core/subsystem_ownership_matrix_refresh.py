from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.pipelines.registry import PIPELINE_INVENTORY

ARTIFACT_TYPE = "SubsystemOwnershipMatrixRefreshReceipt.v1"
STATUS = "SUBSYSTEM_OWNERSHIP_MATRIX_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-58"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/subsystem_ownership_matrix_refresh_001.latest.json"
DOC_PATH = "docs/status/SUBSYSTEM_OWNERSHIP_MATRIX.md"

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
}

OWNER_SUBSYSTEM_ALIASES = {
    "AAL-Viz": {"aal-viz", "projection"},
    "Canon Governance": {"canon", "canon governance"},
    "Governance / Drift Detection": {"governance / drift detection", "governance_drift"},
    "Operator Governance": {"operator governance", "operator_governance"},
    "Oracle Signal Layer": {"oracle signal layer"},
    "Outcome Binding / Brier Ledger": {"outcome binding / brier ledger", "scoring"},
    "PSE Forecast Engine": {"forecast", "pse forecast engine"},
    "Research Intake Automation": {"research", "research intake automation"},
    "Research Validation": {"research", "research validation"},
    "Universal Ingest": {"ingest", "universal ingest"},
}


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), "OBSERVED"
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "NOT_COMPUTABLE"


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    return {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


# Full global-pipeline contracts (v1.1 inventory stack).
FULL_PIPELINE_CONTRACT_TEMPLATE = "contracts/pipelines/{pipeline_id}.v1_1.json"
# Familiar review + queue dry-run close the REVIEW_V0 tier on main.
FAMILIAR_DRY_RUN_SCHEMA = (
    "contracts/signal/familiar_operator_review_queue_dry_run.v0.schema.json"
)

ALIGNMENT_RANK = {
    "ALIGNED": 0,
    "REVIEW_V0": 1,
    "CONTRACT_V0": 2,
    "DRIFT_DETECTED": 3,
    "MISSING_CONTRACT": 4,
}


def _owners_align(expected_owner: str, observed_owner: str | None) -> bool:
    if not observed_owner:
        return False
    normalized_expected = expected_owner.strip().casefold()
    normalized_observed = observed_owner.strip().casefold()
    if normalized_expected == normalized_observed:
        return True
    aliases = OWNER_SUBSYSTEM_ALIASES.get(expected_owner, {normalized_expected})
    return normalized_observed in aliases


def _path_observed(repo_root: Path, relative: str | None) -> bool:
    if not relative:
        return False
    return (repo_root / relative).is_file()


def _classify_pipeline_contract(
    repo_root: Path,
    spec: dict[str, Any],
) -> dict[str, Any]:
    """Tiered contract posture for one pipeline inventory row.

    ALIGNED          — contracts/pipelines/{id}.v1_1.json observed (+ owner match)
    REVIEW_V0        — familiar receipt/bridge/review (+ dry-run schema when present)
    CONTRACT_V0      — inventory contract_path operator packet observed
    MISSING_CONTRACT — neither full pipeline nor operator packet observed
    DRIFT_DETECTED   — full pipeline contract owner mismatch
    """
    pipeline_id = str(spec["pipeline_id"])
    owner = str(spec["owner_subsystem"])
    full_rel = FULL_PIPELINE_CONTRACT_TEMPLATE.format(pipeline_id=pipeline_id)
    full_payload, full_status = _read_json(repo_root / full_rel)

    operator_paths: list[str] = []
    for key in (
        "contract_path",
        "bridge_contract_path",
        "review_contract_path",
    ):
        rel = spec.get(key)
        if isinstance(rel, str) and _path_observed(repo_root, rel):
            operator_paths.append(rel)
    if pipeline_id == "familiar_ingestion" and _path_observed(
        repo_root, FAMILIAR_DRY_RUN_SCHEMA
    ):
        operator_paths.append(FAMILIAR_DRY_RUN_SCHEMA)

    if full_status == "OBSERVED":
        contract_owner = (full_payload or {}).get("owner_subsystem")
        owner_matches = _owners_align(
            owner,
            str(contract_owner) if contract_owner is not None else None,
        )
        if owner_matches:
            return {
                "alignment": "ALIGNED",
                "contract_paths": [full_rel],
                "operator_packet_paths": operator_paths,
                "missing_contract_paths": [],
                "missing_full_pipeline_contract_paths": [],
                "owner_matches": True,
            }
        return {
            "alignment": "DRIFT_DETECTED",
            "contract_paths": [full_rel],
            "operator_packet_paths": operator_paths,
            "missing_contract_paths": [],
            "missing_full_pipeline_contract_paths": [],
            "owner_matches": False,
        }

    if operator_paths:
        has_review = any(
            "operator_review" in path or path.endswith("familiar_operator_review_packet.v0.schema.json")
            for path in operator_paths
        )
        has_dry_run = FAMILIAR_DRY_RUN_SCHEMA in operator_paths
        if pipeline_id == "familiar_ingestion" and (has_review or has_dry_run):
            alignment = "REVIEW_V0"
        else:
            alignment = "CONTRACT_V0"
        return {
            "alignment": alignment,
            "contract_paths": list(operator_paths),
            "operator_packet_paths": list(operator_paths),
            "missing_contract_paths": [],
            "missing_full_pipeline_contract_paths": [full_rel],
            "owner_matches": True,
        }

    return {
        "alignment": "MISSING_CONTRACT",
        "contract_paths": [],
        "operator_packet_paths": [],
        "missing_contract_paths": [full_rel],
        "missing_full_pipeline_contract_paths": [full_rel],
        "owner_matches": False,
    }


def _worst_alignment(alignments: list[str]) -> str:
    if not alignments:
        return "MISSING_CONTRACT"
    return max(alignments, key=lambda value: ALIGNMENT_RANK.get(value, 99))


def _build_ownership_rows(repo_root: Path) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for spec in PIPELINE_INVENTORY:
        owner = str(spec["owner_subsystem"])
        pipeline_id = str(spec["pipeline_id"])
        display_name = str(spec["display_name"])
        lane = str(spec["lane"])
        migration_status = str(spec["migration_status"])
        next_action = str(spec["next_action"])
        classified = _classify_pipeline_contract(repo_root, spec)

        row = grouped.setdefault(
            owner,
            {
                "subsystem": owner,
                "pipeline_ids": [],
                "display_names": [],
                "tiers": set(),
                "lanes": set(),
                "migration_statuses": set(),
                "contract_paths": [],
                "operator_packet_paths": [],
                "missing_contract_paths": [],
                "missing_full_pipeline_contract_paths": [],
                "alignments": [],
                "contract_owner_matches": [],
                "next_actions": [],
                "authority_granted": False,
            },
        )
        row["pipeline_ids"].append(pipeline_id)
        row["display_names"].append(display_name)
        row["tiers"].add(int(spec["tier"]))
        row["lanes"].add(lane)
        row["migration_statuses"].add(migration_status)
        row["next_actions"].append(next_action)
        row["alignments"].append(classified["alignment"])
        row["contract_owner_matches"].append(bool(classified["owner_matches"]))
        row["contract_paths"].extend(classified["contract_paths"])
        row["operator_packet_paths"].extend(classified["operator_packet_paths"])
        row["missing_contract_paths"].extend(classified["missing_contract_paths"])
        row["missing_full_pipeline_contract_paths"].extend(
            classified["missing_full_pipeline_contract_paths"]
        )

    materialized_rows: list[dict[str, Any]] = []
    for owner in sorted(grouped):
        row = grouped[owner]
        materialized_rows.append(
            {
                "subsystem": row["subsystem"],
                "pipeline_count": len(row["pipeline_ids"]),
                "pipeline_ids": sorted(row["pipeline_ids"]),
                "display_names": sorted(row["display_names"]),
                "tiers": sorted(row["tiers"]),
                "lanes": sorted(row["lanes"]),
                "migration_statuses": sorted(row["migration_statuses"]),
                "contract_paths": sorted(set(row["contract_paths"])),
                "operator_packet_paths": sorted(set(row["operator_packet_paths"])),
                "missing_contract_paths": sorted(set(row["missing_contract_paths"])),
                "missing_full_pipeline_contract_paths": sorted(
                    set(row["missing_full_pipeline_contract_paths"])
                ),
                "contract_owner_alignment": _worst_alignment(row["alignments"]),
                "next_action": sorted(row["next_actions"])[0],
                "authority_granted": False,
            }
        )
    return materialized_rows


def _matrix_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def _count(alignment: str) -> int:
        return sum(1 for row in rows if row["contract_owner_alignment"] == alignment)

    missing_contract_count = sum(len(row["missing_contract_paths"]) for row in rows)
    partial_subsystem_count = _count("CONTRACT_V0") + _count("REVIEW_V0")
    return {
        "subsystem_count": len(rows),
        "pipeline_count": sum(int(row["pipeline_count"]) for row in rows),
        "aligned_subsystem_count": _count("ALIGNED"),
        "contract_v0_subsystem_count": _count("CONTRACT_V0"),
        "review_v0_subsystem_count": _count("REVIEW_V0"),
        "partial_subsystem_count": partial_subsystem_count,
        "drift_subsystem_count": _count("DRIFT_DETECTED"),
        "missing_contract_count": missing_contract_count,
        "missing_full_pipeline_contract_count": sum(
            len(row.get("missing_full_pipeline_contract_paths", [])) for row in rows
        ),
        "source_status": (
            "READY"
            if missing_contract_count == 0
            else "READY_WITH_FINDINGS"
        ),
        "authority_granted": False,
    }


def build_subsystem_ownership_matrix_markdown(
    *,
    repo_root: str | Path = ".",
) -> str:
    rows = _build_ownership_rows(Path(repo_root))
    summary = _matrix_summary(rows)
    lines = [
        "# Subsystem Ownership Matrix",
        "",
        f"Status: `{STATUS}`",
        f"Brier Score: {BRIER_SCORE}",
        "",
        "This is a repo-native registry projection derived from pipeline inventory and observed pipeline contracts. "
        "It documents subsystem ownership without granting governance, runtime, sandbox, MCP, canon, or writeback authority.",
        "",
        "## Current Summary",
        "",
        f"- Subsystems observed: `{summary['subsystem_count']}`",
        f"- Pipelines observed: `{summary['pipeline_count']}`",
        f"- Contract-aligned subsystems: `{summary['aligned_subsystem_count']}` (ALIGNED)",
        f"- Partial contracts: `{summary['partial_subsystem_count']}` "
        f"(CONTRACT_V0 ×{summary['contract_v0_subsystem_count']} + "
        f"REVIEW_V0 ×{summary['review_v0_subsystem_count']})",
        f"- Missing contract paths: `{summary['missing_contract_count']}`",
        f"- Missing full pipeline v1.1 contracts (optional depth): "
        f"`{summary['missing_full_pipeline_contract_count']}`",
        "",
        "Alignment tiers: `ALIGNED` = `contracts/pipelines/*.v1_1.json`; "
        "`CONTRACT_V0` = operator packet + builder; "
        "`REVIEW_V0` = familiar receipt/bridge/review/dry-run chain; "
        "`MISSING_CONTRACT` = neither full nor operator packet observed.",
        "",
        "## Repo-Native Ownership Routes",
        "",
        "| Subsystem | Pipelines | Tier(s) | Lane(s) | Contract alignment | Next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                (
                    row["subsystem"],
                    ", ".join(row["pipeline_ids"]),
                    ", ".join(str(item) for item in row["tiers"]),
                    ", ".join(row["lanes"]),
                    row["contract_owner_alignment"],
                    row["next_action"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Why This Matters",
            "",
            "The repo previously preserved this surface only as a partial Notion mirror. Slice58 replaces that placeholder posture with repo-observed ownership evidence so contributors can route architecture, contracts, tests, and receipts without depending on an embedded database view.",
            "",
            "## Next Action",
            "",
            "- Verify the receipt: [`../out/audit/subsystem_ownership_matrix_refresh_001.latest.json`](../out/audit/subsystem_ownership_matrix_refresh_001.latest.json)",
            "- Use [`../core/pipelines/registry.py`](../core/pipelines/registry.py) when extending subsystem routes.",
            "- Keep `ORACLE_SANDBOX_PROBE_GATE_CONFIRMED` unissued unless the operator explicitly provides it in a future gate.",
            "",
            "## Boundary Note",
            "",
            "Projection and registry routing only. No sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous Notion/GitHub writeback is authorized.",
            "",
            "Provenance: Notion Sprint 001 Hub + Loop 805 Slice58 + Hash: receipt canonical_hash",
            "",
        ]
    )
    return "\n".join(lines)


def build_subsystem_ownership_matrix_refresh_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    ownership_rows = _build_ownership_rows(root)
    summary = _matrix_summary(ownership_rows)
    source_table = [
        _source_row(root, "core/pipelines/registry.py"),
        _source_row(root, "contracts/pipelines/aal_viz_projection.v1_1.json"),
        _source_row(root, "contracts/pipelines/oracle_signal.v1_1.json"),
        _source_row(root, DOC_PATH),
    ]
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "claimed_card": "Priority 3 - Subsystem Ownership Matrix population",
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": summary["source_status"],
        "source_table": source_table,
        "ownership_rows": ownership_rows,
        "matrix_summary": summary,
        "touched_docs": [
            "README.md",
            "PLANS.md",
            "docs/START_HERE.md",
            "docs/INDEX.md",
            DOC_PATH,
        ],
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
        },
        "validation_plan": [
            "python scripts/readiness/run_subsystem_ownership_matrix_refresh_receipt.py",
            f"python scripts/artifact/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/subsystem_ownership_matrix_refresh.py "
            "scripts/readiness/run_subsystem_ownership_matrix_refresh_receipt.py",
            "python -m pytest tests/test_subsystem_ownership_matrix_refresh.py "
            "tests/test_generated_artifact_registry.py -q -k subsystem_ownership",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice58 complete - Subsystem Ownership Matrix population shipped; "
            "repo-native ownership routes now derive from pipeline inventory and "
            "observed contracts; subsystem ownership matrix refresh receipt "
            "emitted; no sandbox probe, runtime activation, canon mutation, MCP "
            "exposure, external calls, or autonomous writeback authorized. "
            "Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Continue Priority 3 repository organization with continuity lineage "
            "or artifact classification follow-up unless the operator selects a "
            "different board card."
        ),
        "provenance": "Notion Sprint 001 Hub + Loop 805 Slice58 + Hash: canonical_hash",
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_subsystem_ownership_matrix_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
