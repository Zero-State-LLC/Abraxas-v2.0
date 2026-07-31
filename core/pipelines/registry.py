"""Pipeline registry for ABRAXAS v2.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.file_cache import read_text_cached
from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_REGISTRY
from core.pipelines.models import PipelineContractV11

_PIPELINE_CONTRACT_CACHE: dict[str, tuple[str, PipelineContractV11]] = {}

GLOBAL_REQUIRED_ARTIFACTS = (
    "contract",
    "input_contract",
    "typed_ir",
    "route_packet",
    "validation_packet",
    "positive_proof_packet",
    "negative_proof_packet",
    "conflict_scan_packet",
    "aal_viz_projection_packet",
    "operator_review_packet",
    "canon_sync_receipt",
    "stabilization_decision",
)

ORACLE_SIGNAL_ADDITIVE_SHADOW_CONTRACT_ARTIFACTS = (
    "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
    "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
    "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
    "scripts/ingest/run_oracle_signal_intake_boundary.py",
    "core/oracle_signal.py",
)

V2_MODULE_REGISTRY: tuple[str, ...] = (
    "Retrocausal Signal Hygiene Module",
    "Mandatory Output Schema Enforcer",
    "Self-Adversarial Testing Loop",
    "Hyperstition Potency Evaluator",
    "Retrocausal Hygiene",
    "Output Schema Enforcer",
    "Self-Adversarial Loop",
    "Hyperstition Evaluator",
)

PIPELINE_INVENTORY: tuple[dict[str, Any], ...] = (
    {
        "pipeline_id": "research_intake",
        "display_name": "Research Intake Pipeline",
        "trigger": "intake research",
        "owner_subsystem": "Research Intake Automation",
        "tier": 1,
        "lane": "GOVERNANCE_SHADOW",
        "migration_status": "partial",
        "next_action": "implement one-shot automator from AUTOMATE_RESEARCH_INTAKE_TO_VALIDATION_PIPELINE_001",
    },
    {
        "pipeline_id": "universal_ingest",
        "display_name": "Universal Ingest Pipeline",
        "trigger": "ingest source",
        "owner_subsystem": "Universal Ingest",
        "tier": 1,
        "lane": "GOVERNANCE_SHADOW",
        "migration_status": "specified",
        "next_action": "convert ingest source to global pipeline contract",
    },
    {
        "pipeline_id": "pse_forecast",
        "display_name": "PSE Forecast Pipeline",
        "trigger": "run forecast",
        "owner_subsystem": "PSE Forecast Engine",
        "tier": 1,
        "lane": "FORECAST_GATED",
        "migration_status": "specified",
        "next_action": "add positive and negative proof packets before forecast influence",
    },
    {
        "pipeline_id": "outcome_brier",
        "display_name": "Outcome Binding + Brier Scoring Pipeline",
        "trigger": "score outcome",
        "owner_subsystem": "Outcome Binding / Brier Ledger",
        "tier": 1,
        "lane": "FORECAST_GOVERNANCE",
        "migration_status": "specified",
        "next_action": "add doctrine-compatible operator review and canon sync receipts",
    },
    {
        "pipeline_id": "canon_sync",
        "display_name": "Canon Sync Pipeline",
        "trigger": "sync canon",
        "owner_subsystem": "Canon Governance",
        "tier": 1,
        "lane": "GOVERNANCE",
        "migration_status": "specified",
        "next_action": "formalize canon sync receipts and repo execution boundaries",
    },
    {
        "pipeline_id": "research_drop_validation",
        "display_name": "Research Drop Validation Pipeline",
        "trigger": "validate research drops",
        "owner_subsystem": "Research Validation",
        "tier": 1,
        "lane": "GOVERNANCE_SHADOW",
        "migration_status": "partial",
        "next_action": "bind validation harness to global pipeline spine",
    },
    {
        "pipeline_id": "aal_viz_projection",
        "display_name": "AAL-Viz Projection Pipeline",
        "trigger": "build viz",
        "owner_subsystem": "AAL-Viz",
        "tier": 1,
        "lane": "PROJECTION",
        "migration_status": "specified",
        "next_action": "enforce projection-only packet contract globally",
    },
    {
        "pipeline_id": "hollersports_ticket",
        "display_name": "HollerSports Ticket Pipeline",
        "trigger": "compose ticket",
        "owner_subsystem": "HollerSports",
        "tier": 2,
        "lane": "FORECAST_GATED",
        "migration_status": "specified",
        "next_action": (
            "HollerSportsTicketOperatorPacket.v0 landed (forecast proof + outcome "
            "binding seed); next: optional live ingest wire; forecast routing still gated"
        ),
        "contract_path": "contracts/holler/ticket_operator_packet.v0.schema.json",
        "builder_module": "core.holler.ticket_operator_packet",
    },

    {
        "pipeline_id": "memetic_futurecast",
        "display_name": "Memetic Futurecast Pipeline",
        "trigger": "run memetic futurecast",
        "owner_subsystem": "Oracle / ASE / Memetic Futurecast",
        "tier": 2,
        "lane": "SHADOW_FORECAST_GATED",
        "migration_status": "specified",
        "next_action": (
            "MemeticFuturecastOperatorPacket.v0 landed (horizon policy + gates + "
            "Brier bridge seed); next: optional ledger dry-run wire; routing still gated"
        ),
        "contract_path": "contracts/memetic/futurecast_operator_packet.v0.schema.json",
        "builder_module": "core.memetic.futurecast_operator_packet",
    },

    {
        "pipeline_id": "oracle_signal",
        "display_name": "Oracle Signal Layer Pipeline",
        "trigger": "run oracle",
        "owner_subsystem": "Oracle Signal Layer",
        "tier": 2,
        "lane": "SHADOW",
        "migration_status": "specified",
        "next_action": "bind Oracle packets to global pipeline envelope",
    },
    {
        "pipeline_id": "familiar_ingestion",
        "display_name": "FAMILIAR Ingestion Pipeline",
        "trigger": "run familiar",
        "owner_subsystem": "abx-familiar",
        "tier": 2,
        "lane": "SHADOW",
        "migration_status": "specified",
        "next_action": (
            "operator-review disposition seed landed (FamiliarOperatorReviewPacket.v0); "
            "no queue write; residual: live dual-control only when operator attests"
        ),
        "contract_path": "contracts/ingest/familiar_ingestion_receipt.v0.schema.json",
        "builder_module": "core.ingest.familiar_ingestion_receipt",
        "bridge_contract_path": (
            "contracts/signal/familiar_oracle_belief_bridge.v0.schema.json"
        ),
        "bridge_module": "core.signal.familiar_oracle_belief_bridge",
        "review_contract_path": (
            "contracts/signal/familiar_operator_review_packet.v0.schema.json"
        ),
        "review_module": "core.signal.familiar_operator_review",
    },


    {
        "pipeline_id": "drift_scan",
        "display_name": "Drift Scan Pipeline",
        "trigger": "scan drift",
        "owner_subsystem": "Governance / Drift Detection",
        "tier": 2,
        "lane": "SHADOW_GOVERNANCE",
        "migration_status": "specified",
        "next_action": "standardize drift scan outputs as pipeline receipts",
    },
    {
        "pipeline_id": "operator_review_queue",
        "display_name": "Operator Review Queue Pipeline",
        "trigger": "review queue",
        "owner_subsystem": "Operator Governance",
        "tier": 2,
        "lane": "GOVERNANCE",
        "migration_status": "specified",
        "next_action": "bind operator review queue to doctrine validation and canon sync receipt surfaces",
    },
    {
        "pipeline_id": "noctis_dream",
        "display_name": "Noctis Dream Pipeline",
        "trigger": "process dream",
        "owner_subsystem": "Noctis",
        "tier": 3,
        "lane": "SHADOW_SYMBOLIC",
        "migration_status": "specified",
        "next_action": (
            "NoctisDreamOperatorPacket.v0 + IR landed; "
            "next: optional continuity/history link + operator review wire"
        ),
        "contract_path": "contracts/noctis/dream_operator_packet.v0.schema.json",
        "builder_module": "core.noctis.dream_operator_packet",
    },

    {
        "pipeline_id": "neon_genie_ideation",
        "display_name": "Neon Genie App Ideation Pipeline",
        "trigger": "run neon genie",
        "owner_subsystem": "Neon Genie",
        "tier": 3,
        "lane": "SHADOW_PRODUCT",
        "migration_status": "specified",
        "next_action": "skill package/router wired to IdeationOperatorPacket.v0; optional fixture corpus; Hermes packaging handoff remains external",
        "contract_path": "contracts/neon_genie/ideation_operator_packet.v0.schema.json",
        "builder_module": "core.neon_genie.ideation_operator_packet",
    },
    {
        "pipeline_id": "level99_content",
        "display_name": "Level 99 Content Pipeline",
        "trigger": "build level 99 content",
        "owner_subsystem": "Level 99",
        "tier": 3,
        "lane": "SHADOW_MEDIA",
        "migration_status": "specified",
        "next_action": (
            "Level99ContentOperatorPacket.v0 landed (virality bounds + route + "
            "operator review); next: optional performance ingest wire; no auto-publish"
        ),
        "contract_path": "contracts/level99/content_operator_packet.v0.schema.json",
        "builder_module": "core.level99.content_operator_packet",
    },

    {
        "pipeline_id": "phonomicon_artifact",
        "display_name": "Phonomicon Artifact Pipeline",
        "trigger": "mint phonomicon artifact",
        "owner_subsystem": "Phonomicon",
        "tier": 3,
        "lane": "ARTIFACT_GOVERNANCE",
        "migration_status": "specified",
        "next_action": (
            "PhonomiconArtifactOperatorPacket.v0 landed (provenance chain + Proof "
            "of Resonance); next: optional export candidate wire; mint still blocked"
        ),
        "contract_path": "contracts/phonomicon/artifact_operator_packet.v0.schema.json",
        "builder_module": "core.phonomicon.artifact_operator_packet",
    },

    {
        "pipeline_id": "beatoven_psyfi_integration",
        "display_name": "BeatOven / PsyFi Integration Pipeline",
        "trigger": "run psychosonic integration",
        "owner_subsystem": "BeatOven / PsyFi",
        "tier": 3,
        "lane": "SHADOW_ARTIFACT",
        "migration_status": "specified",
        "next_action": (
            "BeatOvenPsyFiIntegrationOperatorPacket.v0 landed (shared runic core + "
            "sonic plan seed); next: optional graph materialization; plan-only"
        ),
        "contract_path": "contracts/beatoven/integration_operator_packet.v0.schema.json",
        "builder_module": "core.beatoven.integration_operator_packet",
    },
)


LANE_NORMALIZATION = {
    "SHADOW": "SHADOW",
    "GOVERNANCE": "GOVERNANCE",
    "GOVERNANCE_SHADOW": "GOVERNANCE_SHADOW",
    "PROJECTION": "PROJECTION",
    "FORECAST_GATED": "FORECAST_GATED",
    "FORECAST_GOVERNANCE": "FORECAST_GATED",
    "SHADOW_FORECAST_GATED": "FORECAST_GATED",
    "SHADOW_GOVERNANCE": "GOVERNANCE_SHADOW",
    "SHADOW_SYMBOLIC": "SHADOW",
    "SHADOW_PRODUCT": "SHADOW",
    "SHADOW_MEDIA": "SHADOW",
    "ARTIFACT_GOVERNANCE": "GOVERNANCE",
    "SHADOW_ARTIFACT": "SHADOW",
}


def load_pipeline_contract(path: str | Path) -> PipelineContractV11:
    target = Path(path)
    cache_key = target.resolve().as_posix()
    text = read_text_cached(target)
    cached = _PIPELINE_CONTRACT_CACHE.get(cache_key)
    if cached is not None and cached[0] == text:
        return cached[1].model_copy(deep=True)
    contract = PipelineContractV11.model_validate(json.loads(text))
    _PIPELINE_CONTRACT_CACHE[cache_key] = (text, contract)
    return contract.model_copy(deep=True)


def load_contracts(directory: str | Path) -> list[PipelineContractV11]:
    contracts = []
    for p in sorted(Path(directory).glob("*.json")):
        contracts.append(load_pipeline_contract(p))
    return contracts


def _validation_by_pipeline(root: Path) -> dict[str, dict[str, Any]]:
    validation_path = root / "out/validation/latest.json"
    if not validation_path.exists():
        return {}
    payload = json.loads(validation_path.read_text(encoding="utf-8"))
    return {item["pipeline_id"]: item for item in payload.get("results", [])}


def _gate_status(result: dict[str, Any] | None, gate_id: str) -> str:
    if not result:
        return "not_computable"
    for gate in result.get("gate_results", []):
        if gate.get("gate_id") == gate_id:
            status = gate.get("status")
            if status == "passed":
                return "passed"
            if status == "failed":
                return "failed"
            return "not_computable"
    return "not_computable"


def _status_from_result(result: dict[str, Any] | None) -> str:
    if result is None:
        return "missing"
    return str(result.get("status", "not_computable"))


def _oracle_signal_additive_shadow_contracts_observed(root: Path, pipeline_id: str) -> bool:
    if pipeline_id != "oracle_signal":
        return False
    return all((root / path).exists() for path in ORACLE_SIGNAL_ADDITIVE_SHADOW_CONTRACT_ARTIFACTS)


def _entry_from_spec(
    spec: dict[str, Any],
    contract: PipelineContractV11 | None,
    validation_result: dict[str, Any] | None,
    root: Path,
) -> dict[str, Any]:
    additive_shadow_contracts_observed = _oracle_signal_additive_shadow_contracts_observed(
        root,
        str(spec["pipeline_id"]),
    )
    observed_required_artifacts = (
        contract.required_artifacts
        if contract
        else list(ORACLE_SIGNAL_ADDITIVE_SHADOW_CONTRACT_ARTIFACTS)
        if additive_shadow_contracts_observed
        else []
    )
    lane = contract.lane.value if contract else LANE_NORMALIZATION[spec["lane"]]
    contract_status = (
        "observed"
        if contract
        else "additive_shadow_contracts_observed"
        if additive_shadow_contracts_observed
        else "missing"
    )
    typed_ir_status = "observed" if contract and contract.typed_ir_schema else "missing"
    validation_status = _status_from_result(validation_result)
    positive_proof_status = _gate_status(validation_result, "positive_proof_gate")
    negative_proof_status = _gate_status(validation_result, "negative_proof_gate")
    conflict_scan_status = _gate_status(validation_result, "conflict_drift_gate")
    if contract and spec["pipeline_id"] == "aal_viz_projection":
        aal_viz_projection_status = "passed"
    elif contract:
        aal_viz_projection_status = _gate_status(validation_result, "aal_viz_projection_gate")
    else:
        aal_viz_projection_status = "missing"
    operator_review_status = "missing"
    canon_sync_status = "missing"
    stabilization_status = "not_started" if contract else "not_computable"

    if validation_result and validation_result.get("status") == "legacy_contract_posture":
        migration_status = "partial"
    elif contract:
        migration_status = "implemented"
    else:
        migration_status = spec["migration_status"]

    authority = locked_authority()
    return {
        "schema_version": "PipelineRegistryEntry.v1",
        "pipeline_id": spec["pipeline_id"],
        "display_name": spec["display_name"],
        "trigger": spec["trigger"],
        "owner_subsystem": spec["owner_subsystem"],
        "tier": spec["tier"],
        "lane": lane,
        "migration_status": migration_status,
        "contract_status": contract_status,
        "typed_ir_status": typed_ir_status,
        "validation_status": validation_status,
        "positive_proof_status": positive_proof_status,
        "negative_proof_status": negative_proof_status,
        "conflict_scan_status": conflict_scan_status,
        "aal_viz_projection_status": aal_viz_projection_status,
        "operator_review_status": operator_review_status,
        "canon_sync_status": canon_sync_status,
        "stabilization_status": stabilization_status,
        "required_artifacts": list(GLOBAL_REQUIRED_ARTIFACTS),
        "observed_contract_artifacts": list(observed_required_artifacts),
        "additive_shadow_contract_coverage": additive_shadow_contracts_observed,
        "authority": authority,
        "next_action": spec["next_action"],
    }


def build_registry(
    contracts: list[PipelineContractV11],
    *,
    root: str | Path = ".",
) -> dict[str, Any]:
    validate_registry_contracts(contracts)
    root_path = Path(root)
    contract_map = {contract.pipeline_id: contract for contract in contracts}
    validation_map = _validation_by_pipeline(root_path)

    entries = [
        _entry_from_spec(
            spec,
            contract_map.get(spec["pipeline_id"]),
            validation_map.get(spec["pipeline_id"]),
            root_path,
        )
        for spec in PIPELINE_INVENTORY
    ]
    entries.sort(key=lambda entry: (entry["tier"], entry["pipeline_id"]))

    tier_counts = {
        "1": sum(1 for entry in entries if entry["tier"] == 1),
        "2": sum(1 for entry in entries if entry["tier"] == 2),
        "3": sum(1 for entry in entries if entry["tier"] == 3),
    }
    seen_pipeline_ids: set[str] = set()
    seen_triggers: set[str] = set()
    duplicate_pipeline_id_count = 0
    duplicate_trigger_count = 0
    for entry in entries:
        if entry["pipeline_id"] in seen_pipeline_ids:
            duplicate_pipeline_id_count += 1
        seen_pipeline_ids.add(entry["pipeline_id"])
        if entry["trigger"] in seen_triggers:
            duplicate_trigger_count += 1
        seen_triggers.add(entry["trigger"])
    authority_violation_count = sum(
        1
        for entry in entries
        if any(value is not False for value in entry["authority"].values())
    )
    invalid_entry_count = sum(
        1
        for entry in entries
        if entry["contract_status"] == "missing" and entry["tier"] == 1
    )

    registry = {
        "schema_version": SCHEMA_VERSION_REGISTRY,
        "registry_id": "",
        "status": "shadow_candidate",
        "pipeline_count": len(entries),
        "tier_counts": tier_counts,
        "invalid_entry_count": invalid_entry_count,
        "duplicate_pipeline_id_count": duplicate_pipeline_id_count,
        "duplicate_trigger_count": duplicate_trigger_count,
        "authority_violation_count": authority_violation_count,
        "pipelines": entries,
        "authority": locked_authority(),
        "generated_at_policy": "deterministic_or_receipt_bound",
        "recommended_next_state": "eligible_for_shadow_stabilization",
    }
    registry["registry_id"] = canonical_hash({k: v for k, v in registry.items() if k != "registry_id"})
    return registry


def validate_registry_contracts(contracts: list[PipelineContractV11]) -> None:
    seen_ids: set[str] = set()
    seen_triggers: set[str] = set()
    for c in contracts:
        if c.pipeline_id in seen_ids:
            raise ValueError(f"Duplicate pipeline_id: {c.pipeline_id}")
        if c.trigger in seen_triggers:
            raise ValueError(f"Duplicate trigger: {c.trigger}")
        seen_ids.add(c.pipeline_id)
        seen_triggers.add(c.trigger)


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if registry.get("schema_version") != SCHEMA_VERSION_REGISTRY:
        raise ValueError("Invalid registry schema_version")
    if not isinstance(registry.get("pipelines"), list):
        raise ValueError("Registry missing pipelines list")
    if registry.get("pipeline_count") != len(registry["pipelines"]):
        raise ValueError("Registry pipeline_count mismatch")
    expected_tier_counts = {
        "1": sum(1 for item in registry["pipelines"] if item.get("tier") == 1),
        "2": sum(1 for item in registry["pipelines"] if item.get("tier") == 2),
        "3": sum(1 for item in registry["pipelines"] if item.get("tier") == 3),
    }
    if registry.get("tier_counts") != expected_tier_counts:
        raise ValueError("Registry tier_counts mismatch")
    if any(value is not False for value in registry.get("authority", {}).values()):
        raise ValueError("Registry authority must remain fully locked")
    return registry
