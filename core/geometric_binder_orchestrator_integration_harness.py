from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.pipelines.models import PipelineContractV11
from core.pipelines.orchestrator import describe_pipeline

ARTIFACT_TYPE = "GeometricBinderOrchestratorIntegrationHarness.v1"
STATUS = "GEOMETRIC_BINDER_ORCHESTRATOR_INTEGRATION_HARNESS_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-53"
DEFAULT_OUT_PATH = (
    "out/audit/geometric_binder_orchestrator_integration_harness_001.latest.json"
)

BINDER_CONTRACT_PATH = "out/temporal_continuity_spine_binder_contract/latest.json"
BINDER_READINESS_PATH = "out/temporal_continuity_binder_readiness_audit/latest.json"
GEOMETRIC_PROJECTION_PATH = "out/projections/geometric_projection_spec_001.latest.json"
PIPELINE_CONTRACT_PATH = "contracts/pipelines/aal_viz_projection.v1_1.json"

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "pipeline_execution": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
    "secret_capture": False,
    "unlock_engine_implementation": False,
}


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "NOT_COMPUTABLE"
    if not isinstance(payload, dict):
        return None, "NOT_COMPUTABLE"
    return payload, "OBSERVED"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_summary(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    payload, status = _load_json(path)
    return {
        "path": relative_path,
        "observed": status == "OBSERVED",
        "source_status": status,
        "sha256": _sha256_file(path) if status == "OBSERVED" else "NOT_COMPUTABLE",
        "artifact_type": payload.get("artifact_type") if payload else "NOT_COMPUTABLE",
        "canonical_status": payload.get("canonical_status") if payload else "NOT_COMPUTABLE",
        "packet_hash": payload.get("packet_hash") if payload else "NOT_COMPUTABLE",
        "canonical_hash": payload.get("canonical_hash") if payload else "NOT_COMPUTABLE",
    }


def _pipeline_summary(root: Path) -> dict[str, Any]:
    path = root / PIPELINE_CONTRACT_PATH
    payload, status = _load_json(path)
    if payload is None:
        return {
            "path": PIPELINE_CONTRACT_PATH,
            "observed": False,
            "source_status": status,
            "description": "NOT_COMPUTABLE",
            "authority_locked": False,
            "lane": "NOT_COMPUTABLE",
            "pipeline_id": "NOT_COMPUTABLE",
            "sha256": "NOT_COMPUTABLE",
        }

    contract = PipelineContractV11.model_validate(payload)
    return {
        "path": PIPELINE_CONTRACT_PATH,
        "observed": True,
        "source_status": "OBSERVED",
        "description": describe_pipeline(contract),
        "authority_locked": contract.authority.forbidden_true_flags() == [],
        "lane": contract.lane.value,
        "pipeline_id": contract.pipeline_id,
        "sha256": _sha256_file(path),
    }


def build_geometric_binder_orchestrator_integration_harness(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    binder_contract = _source_summary(root, BINDER_CONTRACT_PATH)
    binder_readiness = _source_summary(root, BINDER_READINESS_PATH)
    geometric_projection = _source_summary(root, GEOMETRIC_PROJECTION_PATH)
    pipeline = _pipeline_summary(root)
    source_summaries = [
        binder_contract,
        binder_readiness,
        geometric_projection,
        pipeline,
    ]

    all_sources_observed = all(source["observed"] for source in source_summaries)
    integration_status = (
        "READY_WITH_DEGRADED_EVIDENCE"
        if all_sources_observed
        else "NOT_COMPUTABLE"
    )
    readiness_payload, _ = _load_json(root / BINDER_READINESS_PATH)
    readiness_status = (
        readiness_payload.get("readiness_status")
        if readiness_payload is not None
        else "NOT_COMPUTABLE"
    )
    recommended_next_lane = (
        readiness_payload.get("recommended_next_lane")
        if readiness_payload is not None
        else "NOT_COMPUTABLE"
    )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "authority_locks": AUTHORITY_LOCKS,
        "integration_status": integration_status,
        "binder_readiness_status": readiness_status,
        "recommended_next_lane": recommended_next_lane,
        "source_summaries": source_summaries,
        "integration_matrix": [
            {
                "stage": "binder_contract",
                "source_path": BINDER_CONTRACT_PATH,
                "integration_role": "temporal continuity source grouping",
                "execution_authority": False,
            },
            {
                "stage": "binder_readiness",
                "source_path": BINDER_READINESS_PATH,
                "integration_role": "readiness posture and degraded evidence routing",
                "execution_authority": False,
            },
            {
                "stage": "geometric_projection",
                "source_path": GEOMETRIC_PROJECTION_PATH,
                "integration_role": "AAL-Viz geometric metadata boundary",
                "execution_authority": False,
            },
            {
                "stage": "pipeline_orchestrator_description",
                "source_path": PIPELINE_CONTRACT_PATH,
                "integration_role": "read-only pipeline contract description",
                "execution_authority": False,
            },
        ],
        "compatibility_notes": [
            "No repo paths named geometric_binder.py or unlock/orchestrator.py were observed.",
            "core/pipelines/orchestrator.py is used only for describe_pipeline().",
            "Harness validates compatibility and does not execute pipeline stages.",
        ],
        "boundary": {
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "notion_writeback": False,
            "github_writeback": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "mcp_exposure": False,
        },
        "validation_plan": [
            "python scripts/viz/run_geometric_binder_orchestrator_integration_harness.py",
            "python scripts/run_artifact_regeneration.py --artifact "
            f"{DEFAULT_OUT_PATH}",
            "python -m py_compile core/geometric_binder_orchestrator_integration_harness.py "
            "scripts/viz/run_geometric_binder_orchestrator_integration_harness.py",
            "python -m pytest tests/test_geometric_binder_orchestrator_integration_harness.py "
            "tests/test_generated_artifact_registry.py -q -k geometric_binder_orchestrator",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 53 + "
            "Geometric Binder Orchestrator Integration Harness"
        ),
    }
    return {**packet_base, "canonical_hash": canonical_hash(packet_base)}


def write_geometric_binder_orchestrator_integration_harness(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
