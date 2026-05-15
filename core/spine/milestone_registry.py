from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class MilestoneEvidencePacket(BaseModel):
    schema_version: Literal["MilestoneEvidencePacket.v1"] = "MilestoneEvidencePacket.v1"
    milestone_id: str
    artifact_evidence: list[str]
    code_evidence: list[str]
    script_evidence: list[str]
    test_evidence: list[str]
    command_evidence: list[str]
    evidence_status: Literal[
        "artifact_verified",
        "code_verified",
        "command_verified",
        "sealed_report_verified",
        "partial",
        "missing",
        "not_computable",
    ]
    deterministic_evidence_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "partial", "missing", "not_computable"]

    @staticmethod
    def compute_hash(artifact: list[str], code: list[str], script: list[str], test: list[str], command: list[str], evidence_status: str) -> str:
        raw = "|".join([";".join(artifact), ";".join(code), ";".join(script), ";".join(test), ";".join(command), evidence_status])
        return hashlib.sha256(raw.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "MilestoneEvidencePacket":
        self.authority.assert_locked()
        if not (self.artifact_evidence and self.code_evidence and self.script_evidence and self.command_evidence):
            raise ValueError("evidence source list explicit")
        if self.deterministic_evidence_hash != self.compute_hash(
            self.artifact_evidence,
            self.code_evidence,
            self.script_evidence,
            self.test_evidence,
            self.command_evidence,
            self.evidence_status,
        ):
            raise ValueError("deterministic evidence hash mismatch")
        return self


MILESTONE_EVIDENCE_MAP: list[dict[str, object]] = [
    {"milestone_id": "v2.0.1-rune-layer", "artifact": ["out/execution/latest.json", "out/replay/latest.json"], "code": ["core/runes/runtime.py", "core/runes/execution.py", "core/runes/replay.py", "core/execution/shadow_runner.py"], "scripts": ["scripts/run_shadow_execution.py", "scripts/run_rune_replay.py"], "tests": ["tests/test_rune_replay.py"], "commands": ["uv run python scripts/run_shadow_execution.py", "uv run python scripts/run_rune_replay.py"]},
    {"milestone_id": "v2.0.2-yggdrasil-runtime", "artifact": ["out/yggdrasil/runtime.latest.json", "out/graph_replay/latest.json"], "code": ["core/yggdrasil/runtime.py", "core/yggdrasil/scheduler.py", "core/runtime/graph_runner.py"], "scripts": ["scripts/run_yggdrasil_runtime.py", "scripts/run_graph_replay.py"], "tests": ["tests/test_yggdrasil.py"], "commands": ["uv run python scripts/run_yggdrasil_runtime.py", "uv run python scripts/run_graph_replay.py"]},
    {"milestone_id": "v2.0.3-governed-observability", "artifact": ["out/observability/latest.json", "out/lineage/latest.json"], "code": ["core/observability/telemetry.py", "core/observability/lineage.py", "core/observability/aggregation.py"], "scripts": ["scripts/run_observability_pipeline.py", "scripts/run_lineage_validation.py"], "tests": ["tests/test_lineage_validation.py"], "commands": ["uv run python scripts/run_observability_pipeline.py", "uv run python scripts/run_lineage_validation.py"]},
    {"milestone_id": "v2.0.4-governed-state-engine", "artifact": ["out/state/latest.json", "out/state_replay/latest.json"], "code": ["core/state/runtime.py", "core/state/replay.py", "core/state/lineage.py"], "scripts": ["scripts/run_state_engine.py", "scripts/run_state_replay.py"], "tests": ["tests/test_state_validator.py"], "commands": ["uv run python scripts/run_state_engine.py", "uv run python scripts/run_state_replay.py"]},
    {"milestone_id": "v2.0.5-governed-adaptive-sandbox", "artifact": ["out/sandbox/latest.json", "out/sandbox_replay/latest.json"], "code": ["core/sandbox/runtime.py", "core/sandbox/replay.py", "core/sandbox/convergence.py"], "scripts": ["scripts/run_adaptive_sandbox.py", "scripts/run_sandbox_replay.py"], "tests": ["tests/test_sandbox_stabilization.py"], "commands": ["uv run python scripts/run_adaptive_sandbox.py", "uv run python scripts/run_sandbox_replay.py"]},
    {"milestone_id": "v2.0.6-governed-oracle-intake", "artifact": ["out/oracle/latest.json", "out/oracle_replay/latest.json"], "code": ["core/oracle/runtime.py", "core/oracle/replay.py", "core/oracle/validators.py"], "scripts": ["scripts/run_oracle_intake.py", "scripts/run_intake_replay.py"], "tests": ["tests/test_oracle_validator.py"], "commands": ["uv run python scripts/run_oracle_intake.py", "uv run python scripts/run_intake_replay.py"]},
    {"milestone_id": "v2.0.7-governed-forecast-candidate-layer", "artifact": ["out/forecast/latest.json", "out/forecast_replay/latest.json"], "code": ["core/forecast/runtime.py", "core/forecast/replay.py", "core/forecast/validators.py"], "scripts": ["scripts/run_forecast_candidates.py", "scripts/run_forecast_replay.py"], "tests": ["tests/test_forecast_validator.py"], "commands": ["uv run python scripts/run_forecast_candidates.py", "uv run python scripts/run_forecast_replay.py"]},
    {"milestone_id": "v2.0.8-governed-brier-ledger-layer", "artifact": ["out/brier/latest.json", "out/brier_replay/latest.json"], "code": ["core/brier/runtime.py", "core/brier/replay.py", "core/brier/validators.py"], "scripts": ["scripts/run_brier_ledger.py", "scripts/run_brier_replay.py"], "tests": ["tests/test_brier_replay.py"], "commands": ["uv run python scripts/run_brier_ledger.py", "uv run python scripts/run_brier_replay.py"]},
    {"milestone_id": "v2.0.9-governed-weight-drift-simulation", "artifact": ["out/drift/latest.json", "out/drift_replay/latest.json"], "code": ["core/drift/runtime.py", "core/drift/replay.py", "core/drift/validators.py"], "scripts": ["scripts/run_weight_drift_simulation.py", "scripts/run_drift_replay.py"], "tests": ["tests/test_drift_overlays.py"], "commands": ["uv run python scripts/run_weight_drift_simulation.py", "uv run python scripts/run_drift_replay.py"]},
]


class MilestoneLineageNode(BaseModel):
    milestone_id: str
    parent_milestone: str | None = None
    stabilization_hash: str
    generation: int


class MilestoneRegistryPacket(BaseModel):
    schema_version: Literal["MilestoneRegistryPacket.v1"] = "MilestoneRegistryPacket.v1"
    active_milestone: str
    stabilized_milestones: list[str]
    artifact_verified_milestones: list[str]
    code_verified_milestones: list[str]
    partial_milestones: list[str]
    missing_milestones: list[str]
    evidence_packets: list[MilestoneEvidencePacket]
    latest_stable_hash: str
    milestone_lineage: list[MilestoneLineageNode]
    deterministic_registry_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "partial", "failed", "not_computable"]

    @staticmethod
    def compute_hash(active_milestone: str, stabilized_milestones: list[str], latest_stable_hash: str, lineage: list[MilestoneLineageNode], evidence_packets: list[MilestoneEvidencePacket]) -> str:
        lineage_blob = "|".join(f"{n.milestone_id}:{n.parent_milestone}:{n.stabilization_hash}:{n.generation}" for n in lineage)
        evidence_blob = "|".join(f"{e.milestone_id}:{e.evidence_status}:{e.deterministic_evidence_hash}" for e in evidence_packets)
        return hashlib.sha256(f"{active_milestone}|{'|'.join(stabilized_milestones)}|{latest_stable_hash}|{lineage_blob}|{evidence_blob}".encode()).hexdigest()


def _status_for(
    cfg: dict[str, object], exists: Callable[[str], bool]
) -> tuple[str, str]:
    artifacts = cfg["artifact"]
    code = cfg["code"]
    scripts = cfg["scripts"]
    if not isinstance(artifacts, list) or not isinstance(code, list) or not isinstance(scripts, list):
        return "not_computable", "not_computable"
    has_artifact = all(exists(path) for path in artifacts)
    has_code_script = all(exists(path) for path in code) and all(exists(path) for path in scripts)
    any_exists = any(exists(path) for path in [*artifacts, *code, *scripts])
    if has_artifact:
        return "artifact_verified", "passed"
    if has_code_script:
        return "code_verified", "passed"
    if any_exists:
        return "partial", "partial"
    return "missing", "missing"


def build_milestone_registry(repo_root: Path) -> MilestoneRegistryPacket:
    evidence_packets: list[MilestoneEvidencePacket] = []
    evidence_by_id: dict[str, MilestoneEvidencePacket] = {}
    stabilized: list[str] = []
    artifact_verified: list[str] = []
    code_verified: list[str] = []
    partial: list[str] = []
    missing: list[str] = []
    exists_cache: dict[str, bool] = {}

    def exists(path: str) -> bool:
        if path not in exists_cache:
            exists_cache[path] = (repo_root / path).exists()
        return exists_cache[path]

    for item in MILESTONE_EVIDENCE_MAP:
        evidence_status, status = _status_for(item, exists)
        packet = MilestoneEvidencePacket(
            milestone_id=item["milestone_id"],
            artifact_evidence=item["artifact"],
            code_evidence=item["code"],
            script_evidence=item["scripts"],
            test_evidence=item["tests"],
            command_evidence=item["commands"],
            evidence_status=evidence_status,
            deterministic_evidence_hash=MilestoneEvidencePacket.compute_hash(item["artifact"], item["code"], item["scripts"], item["tests"], item["commands"], evidence_status),
            status=status,
        )
        evidence_packets.append(packet)
        evidence_by_id[packet.milestone_id] = packet
        if evidence_status in {"artifact_verified", "code_verified"}:
            stabilized.append(packet.milestone_id)
            if evidence_status == "artifact_verified":
                artifact_verified.append(packet.milestone_id)
            else:
                code_verified.append(packet.milestone_id)
        elif evidence_status == "partial":
            partial.append(packet.milestone_id)
        elif evidence_status == "missing":
            missing.append(packet.milestone_id)

    lineage: list[MilestoneLineageNode] = []
    parent: str | None = None
    for generation, milestone in enumerate(stabilized):
        ep = evidence_by_id.get(milestone)
        if ep is None:
            raise ValueError(
                "Internal error: stabilized milestone "
                f"{milestone} not found in evidence_by_id"
            )
        lineage.append(MilestoneLineageNode(milestone_id=milestone, parent_milestone=parent, stabilization_hash=ep.deterministic_evidence_hash, generation=generation))
        parent = milestone

    active = stabilized[-1] if stabilized else "unknown"
    latest_hash = lineage[-1].stabilization_hash if lineage else "missing-artifacts"
    if not stabilized:
        registry_status: Literal["passed", "partial", "failed", "not_computable"] = "not_computable"
    elif partial and partial[-1] == MILESTONE_EVIDENCE_MAP[-1]["milestone_id"]:
        registry_status = "partial"
    else:
        registry_status = "passed"

    det = MilestoneRegistryPacket.compute_hash(active, stabilized, latest_hash, lineage, evidence_packets)
    return MilestoneRegistryPacket(
        active_milestone=active,
        stabilized_milestones=stabilized,
        artifact_verified_milestones=artifact_verified,
        code_verified_milestones=code_verified,
        partial_milestones=partial,
        missing_milestones=missing,
        evidence_packets=evidence_packets,
        latest_stable_hash=latest_hash,
        milestone_lineage=lineage,
        deterministic_registry_hash=det,
        status=registry_status,
    )
