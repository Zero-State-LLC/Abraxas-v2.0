from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.rune_equivalent_surface_audit import OUT_JSON as RUNE_EQUIVALENT_AUDIT_JSON

ARTIFACT_TYPE = "BeliefGraphGapVerification.v1"
VERIFICATION_ID = "BELIEF_GRAPH_GAP_VERIFICATION_001"
OUT_JSON = "out/audit/belief_graph_gap_verification_001.latest.json"
OUT_MD = "out/audit/belief_graph_gap_verification_001.latest.md"

_COMPONENTS: tuple[dict[str, Any], ...] = (
    {
        "component": "ClaimObject",
        "required_paths": (
            "core/belief_graph/claim_object.py",
            "contracts/belief_graph/claim_object.v1.schema.json",
            "tests/test_belief_graph_packet.py",
        ),
    },
    {
        "component": "EvidenceObject",
        "required_paths": (
            "core/belief_graph/evidence_object.py",
            "contracts/belief_graph/evidence_object.v1.schema.json",
            "tests/test_belief_graph_packet.py",
        ),
    },
    {
        "component": "TheoryObject",
        "required_paths": (
            "core/belief_graph/theory_object.py",
            "contracts/belief_graph/theory_object.v1.schema.json",
            "tests/test_belief_graph_packet.py",
        ),
    },
    {
        "component": "SignalGraph",
        "required_paths": (
            "core/belief_graph/signal_graph.py",
            "contracts/belief_graph/signal_graph.v1.schema.json",
            "tests/test_belief_graph_packet.py",
        ),
    },
    {
        "component": "BeliefGraphPacket",
        "required_paths": (
            "core/belief_graph/belief_graph_packet.py",
            "core/belief_graph/belief_graph_builder.py",
            "contracts/belief_graph/belief_graph_packet.v1.schema.json",
            "tests/test_belief_graph_packet.py",
        ),
    },
    {
        "component": "IngestBeliefGraphBridge",
        "required_paths": (
            "core/ingest/ingest_packet.py",
            "core/ingest/ingest_adapter.py",
            "tests/test_ingest_contracts.py",
        ),
    },
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _component_record(repo_root: Path, component: dict[str, Any]) -> dict[str, Any]:
    required_paths = tuple(str(path) for path in component["required_paths"])
    observed_paths = sorted(path for path in required_paths if (repo_root / path).is_file())
    missing_paths = sorted(path for path in required_paths if path not in observed_paths)
    status = "OBSERVED" if not missing_paths else "MISSING"
    return {
        "component": str(component["component"]),
        "status": status,
        "required_paths": list(required_paths),
        "observed_paths": observed_paths,
        "missing_paths": missing_paths,
        "source_hashes": {path: _sha256(repo_root / path) for path in observed_paths},
        "evidence_strength": "STRONG" if status == "OBSERVED" else ("WEAK" if observed_paths else "MISSING"),
        "recommended_action": (
            "preserve observed advisory scaffold; no new implementation required"
            if status == "OBSERVED"
            else "record missing surface before any contract plan"
        ),
    }


def build_belief_graph_gap_verification(
    *,
    repo_root: str | Path,
    rune_equivalent_surface_audit_path: str | Path = RUNE_EQUIVALENT_AUDIT_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    component_records = [_component_record(root, component) for component in _COMPONENTS]
    observed_count = sum(1 for record in component_records if record["status"] == "OBSERVED")
    missing_count = len(component_records) - observed_count
    equivalent_observed = missing_count == 0
    audit_target = root / rune_equivalent_surface_audit_path
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "verification_id": VERIFICATION_ID,
        "verification_status": (
            "GAP_VERIFICATION_EMITTED_ADVISORY_ONLY"
            if component_records
            else "NOT_COMPUTABLE"
        ),
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "patch_id": "PATCH-ABX-BELIEF-GRAPH-GAP-VERIFICATION-001",
        "depends_on_patch": "PATCH-ABX-RUNE-EQUIVALENT-SURFACE-AUDIT-001",
        "rune_equivalent_surface_audit_path": Path(rune_equivalent_surface_audit_path).as_posix(),
        "rune_equivalent_surface_audit_hash": _sha256(audit_target),
        "component_records": component_records,
        "summary": {
            "total_components": len(component_records),
            "observed_components": observed_count,
            "missing_components": missing_count,
        },
        "belief_graph_equivalent_observed": equivalent_observed,
        "belief_graph_implementation_performed": False,
        "graph_runtime_created": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": (
            "PATCH-ABX-RUNE-REGISTRY-FORMALIZATION-PLAN-001"
            if equivalent_observed
            else "PATCH-ABX-BELIEF-GRAPH-CONTRACT-PLAN-001"
        ),
        "authority_locks": {
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
            "truth_assignment": False,
            "belief_promotion": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_gap_verification(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_belief_graph_gap_verification_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Belief Graph Gap Verification",
        "",
        f"- verification_id: {packet['verification_id']}",
        f"- verification_status: {packet['verification_status']}",
        f"- belief_graph_equivalent_observed: {packet['belief_graph_equivalent_observed']}",
        f"- belief_graph_implementation_performed: {packet['belief_graph_implementation_performed']}",
        f"- graph_runtime_created: {packet['graph_runtime_created']}",
        f"- forecast_routing: {packet['forecast_routing']}",
        f"- canon_mutation: {packet['canon_mutation']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        "",
        "## Summary",
    ]
    for key in sorted(packet.get("summary", {})):
        lines.append(f"- {key}: {packet['summary'][key]}")
    lines.extend(["", "## Component Records"])
    for record in packet.get("component_records", []):
        lines.append(
            "- "
            f"{record['component']}: {record['status']} "
            f"(evidence_strength={record['evidence_strength']})"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
