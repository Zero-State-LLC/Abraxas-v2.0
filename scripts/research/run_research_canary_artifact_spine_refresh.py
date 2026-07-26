from __future__ import annotations

# ---------------------------------------------------------------------------
# Research Canary Artifact Spine Refresh (Phase 6 helper)
# ---------------------------------------------------------------------------
# Runs P103→P129 research-canary lane runners in strict deterministic order,
# stops on first failure, and emits a summary artifact.
#
# Authority posture: advisory/projection-only, no source authority.
# Does NOT implement P130 or any operative activation.
# ---------------------------------------------------------------------------
import importlib
import json
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import canonical_hash, write_classified_json

ARTIFACT_TYPE = "ResearchCanaryArtifactSpineRefresh.v1"
LANE_ID = "RESEARCH_CANARY_ARTIFACT_SPINE_REFRESH"
CANONICAL_STATUS = "ADVISORY_ONLY"
OUT_PATH = Path("out/research_canary_artifact_spine_refresh/latest.json")

# ---------------------------------------------------------------------------
# Strict ordered list of P103→P129 runner modules (no P130).
# ---------------------------------------------------------------------------
SPINE_RUNNERS: tuple[str, ...] = (
    "scripts.research.run_research_shadow_replay_audit",
    "scripts.research.run_research_boundary_decay_analysis",
    "scripts.research.run_research_promotion_blocker_ledger",
    "scripts.research.run_research_canary_eligibility_dossier",
    "scripts.research.run_research_canary_review_packet",
    "scripts.research.run_research_canary_decision_record",
    "scripts.research.run_research_canary_plan_draft",
    "scripts.research.run_research_canary_plan_review_record",
    "scripts.research.run_research_canary_authorization_draft",
    "scripts.research.run_research_canary_authorization_review_record",
    "scripts.research.run_research_canary_final_precheck_record",
    "scripts.research.run_research_canary_authorization_package_draft",
    "scripts.research.run_research_canary_authorization_package_review_record",
    "scripts.research.run_research_canary_authorization_decision_record",
    "scripts.research.run_research_canary_authorization_denial_hold_routing",
    "scripts.research.run_research_controlled_canary_envelope_draft",
    "scripts.research.run_research_canary_runtime_observation_record",
    "scripts.research.run_research_canary_rollback_termination_governance",
    "scripts.research.run_research_canary_operator_go_no_go_review",
    "scripts.research.run_research_canary_activation_package_draft",
    "scripts.research.run_research_canary_activation_package_review_record",
    "scripts.research.run_research_canary_activation_decision_record",
    "scripts.research.run_research_canary_activation_decision_review_record",
    "scripts.research.run_research_canary_activation_denial_hold_routing",
    "scripts.research.run_research_canary_activation_envelope_draft",
    "scripts.research.run_research_canary_activation_envelope_review_record",
    "scripts.research.run_research_canary_activation_readiness_evidence_record",
)

LANE_IDS: tuple[str, ...] = (
    "P103_RESEARCH_SHADOW_REPLAY_AUDIT",
    "P104_RESEARCH_BOUNDARY_DECAY_ANALYSIS",
    "P105_RESEARCH_PROMOTION_BLOCKER_LEDGER",
    "P106_RESEARCH_CANARY_ELIGIBILITY_DOSSIER",
    "P107_RESEARCH_CANARY_REVIEW_PACKET",
    "P108_RESEARCH_CANARY_DECISION_RECORD",
    "P109_RESEARCH_CANARY_PLAN_DRAFT",
    "P110_RESEARCH_CANARY_PLAN_REVIEW_RECORD",
    "P111_RESEARCH_CANARY_AUTHORIZATION_DRAFT",
    "P112_RESEARCH_CANARY_AUTHORIZATION_REVIEW_RECORD",
    "P113_RESEARCH_CANARY_FINAL_PRECHECK_RECORD",
    "P114_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_DRAFT",
    "P115_RESEARCH_CANARY_AUTHORIZATION_PACKAGE_REVIEW_RECORD",
    "P116_RESEARCH_CANARY_AUTHORIZATION_DECISION_RECORD",
    "P117_RESEARCH_CANARY_AUTHORIZATION_DENIAL_HOLD_ROUTING",
    "P118_RESEARCH_CONTROLLED_CANARY_ENVELOPE_DRAFT",
    "P119_RESEARCH_CANARY_RUNTIME_OBSERVATION_RECORD",
    "P120_RESEARCH_CANARY_ROLLBACK_TERMINATION_GOVERNANCE",
    "P121_RESEARCH_CANARY_OPERATOR_GO_NO_GO_REVIEW",
    "P122_RESEARCH_CANARY_ACTIVATION_PACKAGE_DRAFT",
    "P123_RESEARCH_CANARY_ACTIVATION_PACKAGE_REVIEW_RECORD",
    "P124_RESEARCH_CANARY_ACTIVATION_DECISION_RECORD",
    "P125_RESEARCH_CANARY_ACTIVATION_DECISION_REVIEW_RECORD",
    "P126_RESEARCH_CANARY_ACTIVATION_DENIAL_HOLD_ROUTING",
    "P127_RESEARCH_CANARY_ACTIVATION_ENVELOPE_DRAFT",
    "P128_RESEARCH_CANARY_ACTIVATION_ENVELOPE_REVIEW_RECORD",
    "P129_RESEARCH_CANARY_ACTIVATION_READINESS_EVIDENCE_RECORD",
)

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "forecast_influence",
    "execution_authority",
    "repair_execution_authority",
    "regeneration_execution_authority",
    "token_minting_allowed",
)


def _read_artifact(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    target = Path(out_path) if out_path is not None else repo_root / OUT_PATH

    refreshed_lanes: list[str] = []
    generated_artifacts: list[str] = []
    failed_lane: str | None = None
    failure_reason: str | None = None

    for module_path, lane_id in zip(SPINE_RUNNERS, LANE_IDS, strict=True):
        try:
            mod = importlib.import_module(module_path)
            mod.run(repo_root=repo_root)
            refreshed_lanes.append(lane_id)
        except Exception:  # noqa: BLE001 — fail-closed lane halt
            failed_lane = lane_id
            failure_reason = traceback.format_exc()
            break

    # Discover generated artifacts from out/research_*/latest.json
    for artifact_path in sorted(repo_root.glob("out/research_*/latest.json")):
        generated_artifacts.append(str(artifact_path.relative_to(repo_root)))

    # Read final P129 artifact for frontier fields
    p129_path = repo_root / "out/research_canary_activation_readiness_evidence_record/latest.json"
    p129_artifact = _read_artifact(p129_path)
    final_lane = LANE_IDS[-1] if refreshed_lanes else None
    final_recommended_next_lane: str | None = None
    if p129_artifact is not None:
        final_recommended_next_lane = str(p129_artifact.get("recommended_next_lane", "NOT_COMPUTABLE"))

    governance_locks = {key: False for key in AUTHORITY_LOCK_KEYS}

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "lane_id": LANE_ID,
        "canonical_status": CANONICAL_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "status": "FAILURE" if failed_lane else "COMPLETE",
        "refreshed_lanes": refreshed_lanes,
        "generated_artifacts": generated_artifacts,
        "failed_lane": failed_lane,
        "failure_reason": failure_reason,
        "final_lane": final_lane,
        "final_recommended_next_lane": final_recommended_next_lane,
        "governance_locks": governance_locks,
    }

    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    packet = json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    write_classified_json(
        target,
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=ROOT / "out",
    )
    return packet


def main() -> int:
    packet = run()
    print(f"status: {packet['status']}")
    print(f"refreshed_lanes: {len(packet['refreshed_lanes'])}")
    print(f"generated_artifacts: {len(packet['generated_artifacts'])}")
    if packet["failed_lane"]:
        print(f"failed_lane: {packet['failed_lane']}", file=sys.stderr)
        return 1
    print(f"final_lane: {packet['final_lane']}")
    print(f"final_recommended_next_lane: {packet['final_recommended_next_lane']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
