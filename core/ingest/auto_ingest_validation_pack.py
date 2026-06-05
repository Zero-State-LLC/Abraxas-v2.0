from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

from .aal_viz_ingest_projection_pack import build_aal_viz_ingest_projection_pack
from .outcome_binding_candidate_builder import (
    build_brier_readiness_precheck,
    build_outcome_binding_candidate_packet,
    build_resolution_source_requirement_set,
)
from .runtime_handoff_executor import (
    build_oracle_intake_queue,
    build_runtime_handoff_receipt_set,
    build_sample_manifest_and_config,
    build_source_pull_receipt_set,
)
from .scheduler import decide_ingest_windows

SCHEMA_VERSION = "ABXAutoIngestValidationPack.v1"
PATCH_ID = "PATCH-ABX-AUTO-INGEST-006"
VALIDATION_ID = "abx_auto_ingest_full_stack_validation_v1"
AUTHORITY = "VALIDATION_ONLY"
PATCH_SEQUENCE = ["001", "002", "003", "004", "005"]
CHECKS = [
    "schema_validation",
    "canonical_json_hashing",
    "12_run_invariance",
    "authority_leakage_scan",
    "not_computable_behavior",
    "empty_queue_behavior",
    "operator_window_gate",
    "cooldown_gate",
    "viz_projection_only",
]

_REQUIRED_TRUE_KEYS = ("advisory_only", "projection_only", "non_authoritative")
_REQUIRED_FALSE_KEYS = ("forecast_authority", "canon_mutation", "runtime_mutation", "execution_authority")


def _empty_queue() -> dict[str, Any]:
    return {
        "schema_version": "OracleIntakeQueue.v1",
        "patch_id": "PATCH-ABX-AUTO-INGEST-003",
        "scheduler_id": "abx_controlled_ingest_scheduler_v1",
        "run_id": "0" * 64,
        "authority": "SHADOW_HANDOFF_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "queue_entries": [],
        "queue_hash": "f" * 64,
    }


def _load_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def load_current_stack(repo_root: Path | str = Path(".")) -> dict[str, dict[str, Any]]:
    root = Path(repo_root)
    manifest, adapter_config = build_sample_manifest_and_config()
    source_pull = build_source_pull_receipt_set(manifest, adapter_config)
    runtime_handoff = build_runtime_handoff_receipt_set(
        manifest,
        adapter_config,
        source_pull_receipt_set=source_pull,
    )
    queue = _load_json(root / "out/ingest/oracle_intake_queue_001.latest.json")
    candidate = _load_json(root / "out/ingest/outcome_binding_candidate_packet_001.latest.json")
    precheck = _load_json(root / "out/ingest/brier_readiness_precheck_001.latest.json")
    projection = _load_json(root / "out/projections/aal_viz_ingest_projection_pack_001.latest.json")
    return {
        "adapter_config_set": adapter_config,
        "scheduled_ingest_run_manifest": manifest,
        "source_pull_receipt_set": source_pull,
        "runtime_handoff_receipt_set": runtime_handoff,
        "oracle_intake_queue": queue,
        "outcome_binding_candidate_packet": candidate,
        "brier_readiness_precheck": precheck,
        "aal_viz_ingest_projection_pack": projection,
    }


def build_replayed_stack() -> dict[str, dict[str, Any]]:
    manifest, adapter_config = build_sample_manifest_and_config()
    source_pull = build_source_pull_receipt_set(manifest, adapter_config)
    runtime_handoff = build_runtime_handoff_receipt_set(
        manifest,
        adapter_config,
        source_pull_receipt_set=source_pull,
    )
    queue = build_oracle_intake_queue(
        manifest,
        adapter_config,
        runtime_handoff_receipt_set=runtime_handoff,
    )
    candidate = build_outcome_binding_candidate_packet(queue)
    requirements = build_resolution_source_requirement_set(candidate)
    precheck = build_brier_readiness_precheck(candidate, requirement_set=requirements)
    projection = build_aal_viz_ingest_projection_pack(
        {
            "adapter_config_set": adapter_config,
            "scheduled_ingest_run_manifest": manifest,
            "source_pull_receipt_set": source_pull,
            "runtime_handoff_receipt_set": runtime_handoff,
            "oracle_intake_queue": queue,
            "outcome_binding_candidate_packet": candidate,
            "brier_readiness_precheck": precheck,
        }
    )
    return {
        "adapter_config_set": adapter_config,
        "scheduled_ingest_run_manifest": manifest,
        "source_pull_receipt_set": source_pull,
        "runtime_handoff_receipt_set": runtime_handoff,
        "oracle_intake_queue": queue,
        "outcome_binding_candidate_packet": candidate,
        "resolution_source_requirement_set": requirements,
        "brier_readiness_precheck": precheck,
        "aal_viz_ingest_projection_pack": projection,
    }


def run_12_invariance() -> dict[str, Any]:
    hashes: list[str] = []
    for _ in range(12):
        replayed = build_replayed_stack()
        hashes.append(
            canonical_hash(
                {
                    "queue": replayed["oracle_intake_queue"],
                    "candidate": replayed["outcome_binding_candidate_packet"],
                    "precheck": replayed["brier_readiness_precheck"],
                    "projection": replayed["aal_viz_ingest_projection_pack"],
                }
            )
        )
    unique_hashes = sorted(set(hashes))
    return {
        "status": "PASS_12_OF_12" if len(unique_hashes) == 1 else "FAIL_INVARIANCE_DRIFT",
        "run_count": 12,
        "unique_hash_count": len(unique_hashes),
        "canonical_hashes": unique_hashes,
    }


def authority_leakage_scan(stack: dict[str, dict[str, Any]]) -> dict[str, Any]:
    packets = {
        "source_pull_receipt_set": stack["source_pull_receipt_set"],
        "runtime_handoff_receipt_set": stack["runtime_handoff_receipt_set"],
        "oracle_intake_queue": stack["oracle_intake_queue"],
        "outcome_binding_candidate_packet": stack["outcome_binding_candidate_packet"],
        "brier_readiness_precheck": stack["brier_readiness_precheck"],
        "aal_viz_ingest_projection_pack": stack["aal_viz_ingest_projection_pack"],
    }
    findings: list[str] = []
    for name, packet in packets.items():
        for key in _REQUIRED_TRUE_KEYS:
            if packet.get(key) is not True:
                findings.append(f"{name}:{key}:expected_true")
        for key in _REQUIRED_FALSE_KEYS:
            if packet.get(key) is not False:
                findings.append(f"{name}:{key}:expected_false")
    return {
        "status": "PASS_NO_FORBIDDEN_FIELDS" if not findings else "FAIL_FORBIDDEN_FIELDS_PRESENT",
        "findings": sorted(findings),
    }


def validate_empty_queue_behavior() -> dict[str, Any]:
    queue = _empty_queue()
    candidate = build_outcome_binding_candidate_packet(queue)
    requirements = build_resolution_source_requirement_set(candidate)
    precheck = build_brier_readiness_precheck(candidate, requirement_set=requirements)
    return {
        "status": "PASS" if candidate["candidate_status"] == "NOT_COMPUTABLE_CROSS_DOMAIN_EVIDENCE_REQUIRED" else "FAIL",
        "candidate_status": candidate["candidate_status"],
        "requirement_status": requirements["requirement_status"],
        "precheck_status": precheck["precheck_status"],
    }


def validate_scheduler_gates() -> dict[str, Any]:
    manifest, adapter_config = build_sample_manifest_and_config()
    del manifest  # not needed below
    scheduler_state = {
        "schema_version": "SchedulerState.v1",
        "scheduler_id": "abx_controlled_ingest_scheduler_v1",
        "last_run_by_adapter": {"abx_market_feed_v1": "2026-06-04T02:58:00Z"},
        "last_decision_hash": None,
        "active_operator_windows": [],
        "cooldowns": {},
        "blocked_adapters": [],
    }
    window_policy = {
        "schema_version": "IngestWindowPolicy.v1",
        "policy_id": "abx_controlled_ingest_scheduler_v1",
        "timezone": "UTC",
        "global": {
            "min_seconds_between_runs": 300,
            "max_concurrent_adapters": 1,
            "quiet_window_enabled": True,
            "quiet_window": {"start_hour": 2, "end_hour": 5, "cadence_multiplier": 4.0},
        },
        "domain_policies": {
            "finance": {
                "base_cadence_seconds": 900,
                "min_cadence_seconds": 300,
                "max_cadence_seconds": 3600,
                "operator_window_required": False,
            },
            "geopolitics": {
                "base_cadence_seconds": 3600,
                "min_cadence_seconds": 1800,
                "max_cadence_seconds": 21600,
                "operator_window_required": True,
            },
        },
        "volatility_policy": {
            "enabled": True,
            "compression_thresholds": [{"metric": "z_score", "gte": 2.5, "cadence_multiplier": 0.5}],
            "expansion_thresholds": [{"metric": "z_score", "lt": 1.0, "cadence_multiplier": 2.0}],
        },
    }
    anomaly_state = {
        "schema_version": "ShadowAnomalyState.v1",
        "generated_at": "2026-06-04T00:00:00Z",
        "domain_scores": {
            "finance": {"z_score": 3.0, "source": "fixture"},
            "geopolitics": {"z_score": 0.5, "source": "fixture"},
        },
    }
    decision_set = decide_ingest_windows(
        adapter_config_set=adapter_config,
        window_policy=window_policy,
        scheduler_state=scheduler_state,
        anomaly_state=anomaly_state,
        now_iso="2026-06-04T03:00:00Z",
    )
    by_id = {row["adapter_id"]: row for row in decision_set["decisions"]}
    return {
        "status": "PASS"
        if by_id["abx_geo_feed_v1"]["decision"] == "SKIP_OPERATOR_WINDOW_REQUIRED"
        and by_id["abx_market_feed_v1"]["decision"] == "SKIP_COOLDOWN_ACTIVE"
        else "FAIL",
        "operator_window_decision": by_id["abx_geo_feed_v1"]["decision"],
        "cooldown_decision": by_id["abx_market_feed_v1"]["decision"],
    }


def validate_not_computable_behavior(stack: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = stack["outcome_binding_candidate_packet"]
    precheck = stack["brier_readiness_precheck"]
    return {
        "status": "PASS"
        if candidate["candidate_status"] == "NOT_COMPUTABLE_CROSS_DOMAIN_EVIDENCE_REQUIRED"
        and precheck["precheck_status"] == "NOT_READY_OPERATOR_REVIEW_REQUIRED"
        else "FAIL",
        "candidate_status": candidate["candidate_status"],
        "precheck_status": precheck["precheck_status"],
    }


def validate_viz_projection_only(stack: dict[str, dict[str, Any]]) -> dict[str, Any]:
    projection = stack["aal_viz_ingest_projection_pack"]
    tile_map = {tile["tile_id"]: tile for tile in projection["tiles"]}
    return {
        "status": "PASS_PROJECTION_ONLY"
        if projection["authority"] == "PROJECTION_ONLY" and tile_map["authority_lock_panel"]["status"] == "LOCKED"
        else "FAIL",
        "authority": projection["authority"],
        "authority_lock_status": tile_map["authority_lock_panel"]["status"],
    }


def validate_schema_and_hashing(stack: dict[str, dict[str, Any]]) -> dict[str, Any]:
    import json

    jsonschema = __import__("jsonschema")
    contract_dir = Path("contracts/ingest")
    jsonschema.validate(
        stack["oracle_intake_queue"],
        json.loads((contract_dir / "oracle_intake_queue.v1.schema.json").read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        stack["runtime_handoff_receipt_set"],
        json.loads((contract_dir / "runtime_handoff_receipt_set.v1.schema.json").read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        stack["outcome_binding_candidate_packet"],
        json.loads((contract_dir / "outcome_binding_candidate_packet.v1.schema.json").read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        stack["brier_readiness_precheck"],
        json.loads((contract_dir / "brier_readiness_precheck.v1.schema.json").read_text(encoding="utf-8")),
    )
    jsonschema.validate(
        stack["aal_viz_ingest_projection_pack"],
        json.loads((contract_dir / "aal_viz_ingest_projection_pack.v1.schema.json").read_text(encoding="utf-8")),
    )

    candidate = deepcopy(stack["outcome_binding_candidate_packet"])
    candidate_id = candidate.pop("candidate_id")
    precheck = deepcopy(stack["brier_readiness_precheck"])
    precheck_hash = precheck.pop("precheck_hash")
    projection = deepcopy(stack["aal_viz_ingest_projection_pack"])
    projection_hash = projection.pop("projection_hash")
    return {
        "status": "PASS",
        "candidate_hash_matches": candidate_id == canonical_hash(candidate),
        "precheck_hash_matches": precheck_hash == canonical_hash(precheck),
        "projection_hash_matches": projection_hash == canonical_hash(projection),
    }


def build_auto_ingest_validation_pack(repo_root: Path | str = Path(".")) -> dict[str, Any]:
    current = load_current_stack(repo_root)
    replayed = build_replayed_stack()
    invariance = run_12_invariance()
    authority_scan = authority_leakage_scan(current)
    not_computable = validate_not_computable_behavior(current)
    empty_queue = validate_empty_queue_behavior()
    scheduler_gates = validate_scheduler_gates()
    projection_only = validate_viz_projection_only(current)
    schema_hashing = validate_schema_and_hashing(current)
    full_stack_replay = {
        "status": "PASS"
        if current["oracle_intake_queue"] == replayed["oracle_intake_queue"]
        and current["outcome_binding_candidate_packet"] == replayed["outcome_binding_candidate_packet"]
        and current["brier_readiness_precheck"] == replayed["brier_readiness_precheck"]
        and current["aal_viz_ingest_projection_pack"] == replayed["aal_viz_ingest_projection_pack"]
        else "FAIL",
        "replayed_surfaces": [
            "oracle_intake_queue",
            "outcome_binding_candidate_packet",
            "brier_readiness_precheck",
            "aal_viz_ingest_projection_pack",
        ],
    }

    checks = {
        "schema_validation": schema_hashing["status"],
        "canonical_json_hashing": "PASS"
        if schema_hashing["candidate_hash_matches"]
        and schema_hashing["precheck_hash_matches"]
        and schema_hashing["projection_hash_matches"]
        else "FAIL",
        "12_run_invariance": invariance["status"],
        "authority_leakage_scan": authority_scan["status"],
        "not_computable_behavior": not_computable["status"],
        "empty_queue_behavior": empty_queue["status"],
        "operator_window_gate": "PASS" if scheduler_gates["operator_window_decision"] == "SKIP_OPERATOR_WINDOW_REQUIRED" else "FAIL",
        "cooldown_gate": "PASS" if scheduler_gates["cooldown_decision"] == "SKIP_COOLDOWN_ACTIVE" else "FAIL",
        "viz_projection_only": projection_only["status"],
        "full_stack_replay": full_stack_replay["status"],
    }
    all_pass = all(value.startswith("PASS") for value in checks.values())

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "validation_id": VALIDATION_ID,
        "patches": list(PATCH_SEQUENCE),
        "checks": list(CHECKS),
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "pass_required_for_next_stage": True,
        "check_results": checks,
        "success_criteria": {
            "determinism": invariance["status"],
            "schema_validation": schema_hashing["status"],
            "authority_leakage": authority_scan["status"],
            "forecast_activation": "PASS_BLOCKED"
            if current["outcome_binding_candidate_packet"]["activation_status"] == "BLOCKED_PENDING_CROSS_DOMAIN_EVIDENCE"
            else "FAIL",
            "canon_mutation": "PASS_BLOCKED" if authority_scan["status"] == "PASS_NO_FORBIDDEN_FIELDS" else "FAIL",
            "viz_authority": projection_only["status"],
        },
        "evidence": {
            "full_stack_replay": full_stack_replay,
            "invariance": invariance,
            "authority_leakage": authority_scan,
            "not_computable_behavior": not_computable,
            "empty_queue_behavior": empty_queue,
            "scheduler_gates": scheduler_gates,
            "projection_only": projection_only,
            "schema_and_hashing": schema_hashing,
        },
        "final_status": "PASS" if all_pass else "FAIL",
    }
    packet["validation_hash"] = canonical_hash(packet)
    return packet


def build_auto_ingest_validation_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# ABX Auto Ingest Validation Pack",
        "",
        f"- validation_id: `{packet['validation_id']}`",
        f"- authority: `{packet['authority']}`",
        f"- final_status: `{packet['final_status']}`",
        "",
        "## Checks",
        "",
    ]
    for name in packet["checks"]:
        lines.append(f"- `{name}`: `{packet['check_results'][name]}`")
    lines.append("")
    return "\n".join(lines)


def write_auto_ingest_validation_pack(path: Path | str, packet: dict[str, Any]) -> None:
    target = Path(path)
    write_canonical_json(target, packet)
    target.with_suffix(".md").write_text(
        build_auto_ingest_validation_markdown(packet),
        encoding="utf-8",
    )
