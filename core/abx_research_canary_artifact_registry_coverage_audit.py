from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import (
    _DERIVED_OPTIONAL_ARTIFACTS,
    build_generated_artifact_registry,
)
from scripts.research.run_research_canary_artifact_spine_refresh import LANE_IDS, SPINE_RUNNERS

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageAudit.v1"
AUDIT_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001"
OUT_JSON = "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
OUT_MD = "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.md"
REPAIR_SPEC_PLAN_LANE = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001"

P130_RUNNER_MODULE = "scripts.research.run_research_canary_final_activation_authorization_review"
P130_LANE_ID = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
SCOPED_EXECUTION_RECEIPT_JSON_PATH = (
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    "DIRECT_REGISTRY_REPAIR",
    "REGISTRY_ENTRY_MUTATION",
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "P130_ACTIVATION",
    "TEMPORAL_CONTINUITY_PROMOTION",
    "EXECUTION_AUTHORITY_GRANT",
    "TOKEN_MINTING",
)

AUTHORITY_LOCKS: dict[str, bool] = {
    "approval_granted": False,
    "authorization_granted": False,
    "authority_granted": False,
    "canon_mutation": False,
    "execution": False,
    "execution_authority": False,
    "implementation_authorized": False,
    "notion_writeback": False,
    "github_writeback": False,
    "queue_mutation": False,
    "registry_mutation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
    "token_minting": False,
}

_OUT_PATH_RE = re.compile(r'OUT_PATH\s*=\s*Path\(["\'](?P<path>out/[^"\']+)["\']\)')
_OUT_JSON_RE = re.compile(r'OUT_JSON\s*=\s*["\'](?P<path>out/[^"\']+)["\']')
_ARTIFACT_TYPE_RE = re.compile(r'ARTIFACT_TYPE\s*=\s*["\'](?P<value>[^"\']+)["\']')
_LANE_ID_RE = re.compile(r'LANE_ID\s*=\s*["\'](?P<value>[^"\']+)["\']')


def _canonical_runner_modules() -> tuple[str, ...]:
    return (*SPINE_RUNNERS, P130_RUNNER_MODULE)


def _canonical_lane_ids() -> tuple[str, ...]:
    return (*LANE_IDS, P130_LANE_ID)


def _family_from_runner_module(module_path: str) -> str:
    return module_path.rsplit(".", 1)[-1].replace("run_", "", 1)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _run_git(repo_root: Path, args: list[str]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _tracked_paths(repo_root: Path) -> set[str]:
    return set(_run_git(repo_root, ["ls-files"]))


def _extract_runner_output_path(runner_path: Path) -> str:
    if not runner_path.is_file():
        return NOT_COMPUTABLE
    text = runner_path.read_text(encoding="utf-8")
    for pattern in (_OUT_PATH_RE, _OUT_JSON_RE):
        match = pattern.search(text)
        if match:
            return match.group("path")
    family = runner_path.stem.replace("run_", "", 1)
    return f"out/{family}/latest.json"


def _extract_core_constants(core_path: Path) -> dict[str, str]:
    if not core_path.is_file():
        return {"artifact_type": NOT_COMPUTABLE, "lane_id": NOT_COMPUTABLE}
    text = core_path.read_text(encoding="utf-8")
    artifact_match = _ARTIFACT_TYPE_RE.search(text)
    lane_match = _LANE_ID_RE.search(text)
    return {
        "artifact_type": artifact_match.group("value") if artifact_match else NOT_COMPUTABLE,
        "lane_id": lane_match.group("value") if lane_match else NOT_COMPUTABLE,
    }


def _lane_record(
    repo_root: Path,
    *,
    runner_module: str,
    expected_lane_id: str,
    registry_source_text: str,
    registry_entry_paths: set[str],
    derived_optional_paths: set[str],
    tracked_paths: set[str],
) -> dict[str, Any]:
    family = _family_from_runner_module(runner_module)
    runner_path = f"scripts/run_{family}.py"
    core_module_path = f"core/{family}.py"
    test_path = f"tests/test_{family}.py"
    schema_path = f"contracts/canon/{family}.v1.schema.json"
    runner_file = repo_root / runner_path
    core_file = repo_root / core_module_path
    output_json_path = _extract_runner_output_path(runner_file)
    core_constants = _extract_core_constants(core_file)
    output_packet = _read_json(repo_root / output_json_path) if output_json_path != NOT_COMPUTABLE else None
    observed_lane_id = (
        str(output_packet.get("lane_id"))
        if isinstance(output_packet, dict) and isinstance(output_packet.get("lane_id"), str)
        else NOT_COMPUTABLE
    )
    artifact_type = (
        str(output_packet.get("artifact_type"))
        if isinstance(output_packet, dict) and isinstance(output_packet.get("artifact_type"), str)
        else core_constants["artifact_type"]
    )
    lane_id_in_registry_source = expected_lane_id in registry_source_text
    output_json_in_registry_entries = output_json_path in registry_entry_paths
    output_json_in_derived_optional = output_json_path in derived_optional_paths
    output_json_git_tracked = output_json_path in tracked_paths
    registry_coverage_status = (
        "COVERED"
        if lane_id_in_registry_source or output_json_in_derived_optional
        else "GAP_CONFIRMED"
    )
    return {
        "lane_id": expected_lane_id,
        "runner_module": runner_module,
        "artifact_type": artifact_type,
        "output_json_path": output_json_path,
        "schema_path": schema_path,
        "core_module_path": core_module_path,
        "runner_path": runner_path,
        "test_path": test_path,
        "core_lane_id_observed": core_constants["lane_id"],
        "output_lane_id_observed": observed_lane_id,
        "lane_id_matches_output": observed_lane_id == expected_lane_id,
        "core_module_observed": core_file.is_file(),
        "runner_observed": runner_file.is_file(),
        "test_observed": (repo_root / test_path).is_file(),
        "schema_observed": (repo_root / schema_path).is_file(),
        "output_json_observed": (
            (repo_root / output_json_path).is_file() if output_json_path != NOT_COMPUTABLE else False
        ),
        "lane_id_in_registry_source": lane_id_in_registry_source,
        "output_json_in_registry_entries": output_json_in_registry_entries,
        "output_json_in_derived_optional_artifacts": output_json_in_derived_optional,
        "output_json_git_tracked": output_json_git_tracked,
        "registry_coverage_status": registry_coverage_status,
    }


def _discover_research_outputs(repo_root: Path) -> list[str]:
    paths: list[str] = []
    for pattern in ("out/research_*/latest.json", "out/research_canary_*/latest.json"):
        paths.extend(
            str(path.relative_to(repo_root)).replace("\\", "/")
            for path in sorted(repo_root.glob(pattern))
        )
    return sorted(set(paths))


def _orphan_research_outputs(
    discovered_outputs: list[str],
    canonical_output_paths: set[str],
    derived_optional_paths: set[str] | None = None,
) -> list[dict[str, Any]]:
    orphans: list[dict[str, Any]] = []
    optional_paths = derived_optional_paths or set()
    for output_path in discovered_outputs:
        if output_path in canonical_output_paths or output_path in optional_paths:
            continue
        packet = _read_json(Path(output_path))
        orphans.append(
            {
                "output_json_path": output_path,
                "lane_id_observed": (
                    str(packet.get("lane_id"))
                    if isinstance(packet, dict) and isinstance(packet.get("lane_id"), str)
                    else NOT_COMPUTABLE
                ),
                "artifact_type_observed": (
                    str(packet.get("artifact_type"))
                    if isinstance(packet, dict) and isinstance(packet.get("artifact_type"), str)
                    else NOT_COMPUTABLE
                ),
                "classification": "ORPHAN_RESEARCH_OUTPUT",
            }
        )
    return orphans


def build_abx_research_canary_artifact_registry_coverage_audit(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    registry_source_path = root / "core/generated_artifact_registry.py"
    registry_source_text = (
        registry_source_path.read_text(encoding="utf-8") if registry_source_path.is_file() else ""
    )
    registry = build_generated_artifact_registry(root)
    registry_entry_paths = {entry.artifact_path for entry in registry.entries}
    derived_optional_paths = set(_DERIVED_OPTIONAL_ARTIFACTS)
    tracked_paths = _tracked_paths(root)

    lane_records = [
        _lane_record(
            root,
            runner_module=runner_module,
            expected_lane_id=lane_id,
            registry_source_text=registry_source_text,
            registry_entry_paths=registry_entry_paths,
            derived_optional_paths=derived_optional_paths,
            tracked_paths=tracked_paths,
        )
        for runner_module, lane_id in zip(_canonical_runner_modules(), _canonical_lane_ids(), strict=True)
    ]
    lane_records = sorted(lane_records, key=lambda record: record["lane_id"])

    canonical_output_paths = {
        record["output_json_path"]
        for record in lane_records
        if record["output_json_path"] != NOT_COMPUTABLE
    }
    discovered_outputs = _discover_research_outputs(root)
    orphan_outputs = _orphan_research_outputs(
        discovered_outputs, canonical_output_paths, derived_optional_paths
    )

    lane_id_gap_count = sum(1 for record in lane_records if not record["lane_id_in_registry_source"])
    output_path_gap_count = sum(
        1
        for record in lane_records
        if record["registry_coverage_status"] == "GAP_CONFIRMED"
    )
    direct_registry_lane_id_coverage = lane_id_gap_count == 0
    gap_confirmed = any(record["registry_coverage_status"] == "GAP_CONFIRMED" for record in lane_records)

    coverage_summary = {
        "implemented_artifacts_present": all(record["core_module_observed"] for record in lane_records),
        "output_artifacts_present": all(record["output_json_observed"] for record in lane_records),
        "tests_present": all(record["test_observed"] for record in lane_records),
        "schemas_present": all(record["schema_observed"] for record in lane_records),
        "direct_registry_lane_id_coverage": direct_registry_lane_id_coverage,
        "canonical_lane_count": len(lane_records),
        "lane_id_gap_count": lane_id_gap_count,
        "output_path_gap_count": output_path_gap_count,
        "discovered_research_output_count": len(discovered_outputs),
        "orphan_research_output_count": len(orphan_outputs),
    }

    if gap_confirmed:
        audit_status = "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
        recommended_next_lane = REPAIR_SPEC_PLAN_LANE
        downstream_status = "READY_FOR_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN"
    else:
        audit_status = NOT_COMPUTABLE
        recommended_next_lane = NOT_COMPUTABLE
        downstream_status = NOT_COMPUTABLE

    scoped_receipt_path = root / SCOPED_EXECUTION_RECEIPT_JSON_PATH
    scoped_receipt: dict[str, Any] | None = None
    if scoped_receipt_path.is_file():
        scoped_receipt = _read_json(scoped_receipt_path)
    scoped_receipt_observed = (
        isinstance(scoped_receipt, dict)
        and scoped_receipt.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageRepairScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("repair_execution_performed") is True
    )

    governance_boundaries = {
        "p102g_temporal_continuity_spine_edge_preserved": True,
        "p130_advisory_frontier_only": True,
        "research_canary_not_promoted_to_temporal_continuity": True,
        "registry_repair_performed": not gap_confirmed and scoped_receipt_observed,
        "research_canary_spine_refresh_performed": False,
    }

    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": AUDIT_ID,
        "audit_id": AUDIT_ID,
        "audit_status": audit_status,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_only": True,
        "coverage_summary": coverage_summary,
        "lane_records": lane_records,
        "orphan_research_outputs": orphan_outputs,
        "governance_boundaries": governance_boundaries,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "approval_granted": False,
        "authorization_granted": False,
        "authority_granted": False,
        "execution_allowed": False,
        "execution_authority": False,
        "implementation_authorized": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "recommended_next_action": (
            "consume this audit as advisory evidence only; do not repair registry entries or "
            "regenerate research-canary artifacts from this lane"
        ),
        "recommended_next_lane": recommended_next_lane,
        "downstream_status": downstream_status,
        "downstream": downstream_status,
        "registry_source_path": "core/generated_artifact_registry.py",
        "registry_entry_count": len(registry_entry_paths),
        "registry_research_output_entry_count": sum(
            1
            for path in registry_entry_paths
            if path.startswith("out/research_") or path.startswith("out/research_canary_")
        ),
    }
    if scoped_receipt_observed and isinstance(scoped_receipt, dict):
        base["scoped_execution_receipt"] = {
            "path": SCOPED_EXECUTION_RECEIPT_JSON_PATH,
            "hash": str(scoped_receipt.get("receipt_hash", NOT_COMPUTABLE)),
            "status": str(scoped_receipt.get("status", NOT_COMPUTABLE)),
            "observed": True,
        }
    return {**base, "audit_hash": canonical_hash(base)}


def render_abx_research_canary_artifact_registry_coverage_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Audit 001",
        "",
        f"- `audit_id`: `{packet['audit_id']}`",
        f"- `audit_status`: `{packet['audit_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        f"- `research_canary_spine_refresh_performed`: `{packet['governance_boundaries']['research_canary_spine_refresh_performed']}`",
        "",
        "## Coverage Summary",
    ]
    summary = packet.get("coverage_summary", {})
    if isinstance(summary, dict):
        for key in sorted(summary):
            lines.append(f"- `{key}`: `{summary[key]}`")
    lines.extend(["", "## Lane Records"])
    for record in packet.get("lane_records", []):
        if isinstance(record, dict):
            lines.append(
                f"- `{record['lane_id']}`: {record['registry_coverage_status']} "
                f"(lane_id_in_registry={record['lane_id_in_registry_source']}, "
                f"output_in_registry={record['output_json_in_registry_entries']})"
            )
    lines.extend(["", "## Orphan Research Outputs"])
    for record in packet.get("orphan_research_outputs", []):
        if isinstance(record, dict):
            lines.append(f"- `{record['output_json_path']}`: `{record.get('lane_id_observed', NOT_COMPUTABLE)}`")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- `{action}`")
    return lines


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_abx_research_canary_artifact_registry_coverage_audit(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=root)
    write_canonical_json(target_root / OUT_JSON, packet)
    _write_markdown(
        target_root / OUT_MD,
        render_abx_research_canary_artifact_registry_coverage_audit_markdown(packet),
    )
    return packet
