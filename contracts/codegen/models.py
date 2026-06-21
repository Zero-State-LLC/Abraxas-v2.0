from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

HEX_64_PATTERN = r"^[a-f0-9]{64}$"


class StrictCodegenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuthorityLocks(StrictCodegenModel):
    advisory_only: Literal[True] = True
    canon_mutation: Literal[False] = False
    runtime_mutation: Literal[False] = False
    execution_authority: Literal[False] = False
    code_generation: Literal[False] = False
    code_mutation: Literal[False] = False
    file_writeback: Literal[False] = False
    github_writeback: Literal[False] = False
    notion_writeback: Literal[False] = False
    queue_mutation: Literal[False] = False
    scheduler_mutation: Literal[False] = False
    auto_approval: Literal[False] = False
    production_activation: Literal[False] = False


class LaneSignals(StrictCodegenModel):
    lane: Literal["ADVISORY_STACK_HELD_FOR_OPERATOR"]
    downstream: Literal["NOT_COMPUTABLE"]
    advisory_only: Literal[True] = True
    projection_only: Literal[True] = True
    shadow_replay_emphasis: Literal[True] = True
    safe_to_auto_continue: Literal[False] = False
    valid_for_execution: Literal[False] = False


class Provenance(StrictCodegenModel):
    source_gap_analysis: str = Field(min_length=1)
    continuity_lane: str = Field(min_length=1)
    generated_by: Literal["ABX_CODEGEN_INTELLIGENCE_SPINE"]


class ReplayConstraints(StrictCodegenModel):
    max_runtime_ms: int = Field(default=30000, ge=0)
    max_memory_mb: int = Field(default=512, ge=0)
    no_network: Literal[True] = True
    no_file_write: Literal[True] = True


class PatchContract(StrictCodegenModel):
    schema_version: Literal["PatchContract.v1"]
    patch_id: str = Field(pattern=HEX_64_PATTERN)
    target_path: str = Field(min_length=1)
    change_type: Literal["ADD", "MODIFY", "DEPRECATE"]
    proposed_content: dict[str, Any]
    rationale: str = Field(min_length=1)
    authority_locks: AuthorityLocks = Field(default_factory=AuthorityLocks)
    lane_signals: LaneSignals
    provenance: Provenance


class CodeDropEnvelope(StrictCodegenModel):
    schema_version: Literal["CodeDropEnvelope.v1"]
    envelope_id: str = Field(pattern=HEX_64_PATTERN)
    timestamp: str = Field(min_length=1)
    patches: tuple[PatchContract, ...]
    required_fixtures: tuple[str, ...] = ()
    validation_commands: tuple[str, ...]
    residual_risks: tuple[str, ...]
    authority_locks: AuthorityLocks = Field(default_factory=AuthorityLocks)
    lane_signals: LaneSignals
    provenance: Provenance
    canonical_hash: str | None = Field(default=None, pattern=HEX_64_PATTERN)

    @field_validator("patches")
    @classmethod
    def _require_patch(
        cls, patches: tuple[PatchContract, ...]
    ) -> tuple[PatchContract, ...]:
        if not patches:
            raise ValueError("CodeDropEnvelope requires at least one patch")
        return patches


class MetaGateSeal(StrictCodegenModel):
    schema_version: Literal["MetaGateSeal.v1"]
    seal_id: str = Field(pattern=HEX_64_PATTERN)
    timestamp: str = Field(min_length=1)
    reviewed_envelope_id: str = Field(pattern=HEX_64_PATTERN)
    operator_gate_required: Literal[True] = True
    operator_attestation_required: Literal[True] = True
    promotion_allowed: Literal[False] = False
    recommendation: Literal[
        "HOLD_FOR_OPERATOR",
        "HOLD_FOR_META_GATE",
        "BLOCK_POLICY_VIOLATION",
        "BLOCK_REPLAY_FAILURE",
        "REJECT",
    ]
    brier_score: float = Field(ge=0, le=1)
    authority_locks: AuthorityLocks = Field(default_factory=AuthorityLocks)
    lane_signals: LaneSignals
    provenance: Provenance


class CodegenTaskPacket(StrictCodegenModel):
    schema_version: Literal["CodegenTaskPacket.v1"]
    task_id: str = Field(pattern=HEX_64_PATTERN)
    phase: Literal[
        "PHASE_1_CONTRACTS_CODEGEN_SCHEMAS",
        "PHASE_2_CORE_CODEGEN_HARNESS",
        "PHASE_3_FIXTURE_VALIDATION_SHADOW_REPLAY",
        "PHASE_4_META_GATE_OPERATOR_PROMOTION",
        "PHASE_5_NOTION_RECONCILIATION_DRYRUN",
    ]
    evidence_packet_sections: tuple[
        Literal[
            "BOUNDARY",
            "EVIDENCE PACKET",
            "TASK",
            "OUTPUT",
            "VALIDATION",
            "RESIDUAL RISKS",
            "RECOMMENDED NEXT ADVISORY ACTION",
        ],
        ...,
    ]
    target_paths: tuple[str, ...]
    validation_commands: tuple[str, ...]
    operator_gate_required: Literal[True] = True
    authority_locks: AuthorityLocks = Field(default_factory=AuthorityLocks)
    lane_signals: LaneSignals
    provenance: Provenance

    @model_validator(mode="after")
    def _require_targets_and_validation(self) -> CodegenTaskPacket:
        if not self.target_paths:
            raise ValueError("CodegenTaskPacket requires at least one target path")
        if not self.validation_commands:
            raise ValueError("CodegenTaskPacket requires validation commands")
        return self


class ShadowReplayFixture(StrictCodegenModel):
    schema_version: Literal["ShadowReplayFixture.v1"]
    fixture_id: str = Field(pattern=HEX_64_PATTERN)
    proposal_path: str = Field(min_length=1)
    expected_recommendation: Literal[
        "PROMOTE_TO_CANARY",
        "HOLD_FOR_OPERATOR",
        "HOLD_FOR_META_GATE",
        "BLOCK_POLICY_VIOLATION",
        "BLOCK_REPLAY_FAILURE",
        "REJECT",
        "REFINE_PROPOSAL",
    ]
    run_count: int = Field(default=12, ge=1)
    constraints: ReplayConstraints = Field(default_factory=ReplayConstraints)
    expected_authority_locks: AuthorityLocks = Field(default_factory=AuthorityLocks)
    provenance: Provenance
