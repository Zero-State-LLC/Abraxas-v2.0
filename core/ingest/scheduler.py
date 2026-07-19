from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from core.canonical.json import canonical_hash

from .cadence import CadenceBounds, resolve_cadence_seconds
from .controlled_handoff_eligibility import build_controlled_handoff_eligibility
from .windowing import is_quiet_window, operator_window_active, parse_iso_datetime

AUTHORITY = "SHADOW_SCHEDULING_ONLY"
RUN_DECISION = "RUN"
TARGET_PATCH_ID = "PATCH-ABX-AUTO-INGEST-002"


def volatility_multiplier_for(domain_score: dict[str, Any], policy: dict[str, Any]) -> float:
    if not policy.get("enabled", False):
        return 1.0

    z_score = float(domain_score.get("z_score", 0.0) or 0.0)
    multiplier = 1.0
    for rule in policy.get("compression_thresholds", []):
        if rule.get("metric") == "z_score" and z_score >= float(rule.get("gte", 0.0)):
            multiplier = min(multiplier, float(rule.get("cadence_multiplier", 1.0)))
    for rule in policy.get("expansion_thresholds", []):
        if rule.get("metric") == "z_score" and z_score < float(rule.get("lt", 0.0)):
            multiplier = max(multiplier, float(rule.get("cadence_multiplier", 1.0)))
    return multiplier


def cooldown_satisfied(
    adapter_id: str,
    now: datetime,
    resolved_cadence_seconds: int,
    scheduler_state: dict[str, Any],
) -> bool:
    last_runs = scheduler_state.get("last_run_by_adapter", {})
    last_run = last_runs.get(adapter_id)
    if not isinstance(last_run, str) or not last_run:
        return True
    delta = now - parse_iso_datetime(last_run)
    return delta.total_seconds() >= resolved_cadence_seconds


def decide_ingest_windows(
    *,
    adapter_config_set: dict[str, Any],
    window_policy: dict[str, Any],
    scheduler_state: dict[str, Any],
    anomaly_state: dict[str, Any],
    now_iso: str,
) -> dict[str, Any]:
    now = parse_iso_datetime(now_iso)
    global_policy = window_policy.get("global", {})
    domain_policies = window_policy.get("domain_policies", {})
    volatility_policy = window_policy.get("volatility_policy", {})
    domain_scores = anomaly_state.get("domain_scores", {})
    active_windows = scheduler_state.get("active_operator_windows", [])
    blocked_adapters = set(scheduler_state.get("blocked_adapters", []))

    quiet_multiplier = 1.0
    quiet_window = global_policy.get("quiet_window", {})
    quiet = False
    if global_policy.get("quiet_window_enabled", False):
        quiet = is_quiet_window(
            now,
            int(quiet_window.get("start_hour", 2)),
            int(quiet_window.get("end_hour", 5)),
        )
        if quiet:
            quiet_multiplier = float(quiet_window.get("cadence_multiplier", 1.0))

    max_concurrent = int(global_policy.get("max_concurrent_adapters", 4))
    run_count = 0
    decisions: list[dict[str, Any]] = []
    adapters = sorted(adapter_config_set.get("adapters", []), key=lambda item: item.get("adapter_id", ""))

    for adapter in adapters:
        adapter_id = str(adapter.get("adapter_id", "NOT_COMPUTABLE"))
        domain = str(adapter.get("domain", "NOT_COMPUTABLE"))
        domain_policy = domain_policies.get(domain)
        if not isinstance(domain_policy, dict):
            decisions.append(
                {
                    "adapter_id": adapter_id,
                    "domain": domain,
                    "decision": "NOT_COMPUTABLE",
                    "resolved_cadence_seconds": None,
                    "reasons": ["missing_domain_policy"],
                    "authority": AUTHORITY,
                }
            )
            continue

        bounds = CadenceBounds(
            base_seconds=int(domain_policy["base_cadence_seconds"]),
            min_seconds=int(domain_policy["min_cadence_seconds"]),
            max_seconds=int(domain_policy["max_cadence_seconds"]),
        )
        vol_multiplier = volatility_multiplier_for(domain_scores.get(domain, {}), volatility_policy)
        resolved_cadence = resolve_cadence_seconds(
            bounds,
            quiet_window_multiplier=quiet_multiplier,
            volatility_multiplier=vol_multiplier,
        )

        reasons: list[str] = []
        decision = RUN_DECISION
        if adapter.get("enabled") is False:
            decision = "SKIP_DISABLED_ADAPTER"
            reasons.append("adapter_disabled")
        elif adapter_id in blocked_adapters:
            decision = "SKIP_BLOCKED_ADAPTER"
            reasons.append("adapter_blocked")
        elif bool(domain_policy.get("operator_window_required")) and not operator_window_active(active_windows, domain, now):
            decision = "SKIP_OPERATOR_WINDOW_REQUIRED"
            reasons.append("operator_window_required_not_active")
        elif not cooldown_satisfied(adapter_id, now, resolved_cadence, scheduler_state):
            decision = "SKIP_COOLDOWN_ACTIVE"
            reasons.append("cooldown_active")
        elif run_count >= max_concurrent:
            decision = "SKIP_GLOBAL_LIMIT"
            reasons.append("max_concurrent_adapters_reached")
        else:
            run_count += 1
            reasons.append("cooldown_satisfied")
            reasons.append("operator_window_active" if domain_policy.get("operator_window_required") else "operator_window_not_required")
            if quiet:
                reasons.append("quiet_window_applied")
            if vol_multiplier != 1.0:
                reasons.append("volatility_multiplier_applied")

        decisions.append(
            {
                "adapter_id": adapter_id,
                "domain": domain,
                "decision": decision,
                "resolved_cadence_seconds": resolved_cadence,
                "reasons": sorted(reasons),
                "authority": AUTHORITY,
            }
        )

    packet = {
        "schema_version": "IngestWindowDecisionSet.v1",
        "scheduler_id": str(window_policy.get("policy_id", "abx_controlled_ingest_scheduler_v1")),
        "generated_at": now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "decisions": decisions,
    }
    packet["decision_hash"] = canonical_hash(packet)
    return packet


def build_scheduled_manifest(
    decision_set: dict[str, Any],
    *,
    max_concurrent_adapters: int,
    oracle_signal_module_present: bool = False,
    shadow_receipt_valid: bool = True,
) -> dict[str, Any]:
    eligible = [row["adapter_id"] for row in decision_set["decisions"] if row["decision"] == RUN_DECISION]
    blocked = [row["adapter_id"] for row in decision_set["decisions"] if row["decision"] != RUN_DECISION]
    handoff_eligibility = build_controlled_handoff_eligibility(
        oracle_signal_module_present=oracle_signal_module_present,
        shadow_receipt_valid=shadow_receipt_valid,
    )
    packet = {
        "schema_version": "ScheduledIngestRunManifest.v1",
        "scheduler_id": decision_set["scheduler_id"],
        "generated_at": decision_set["generated_at"],
        "eligible_adapters": eligible,
        "blocked_adapters": blocked,
        "max_concurrent_adapters": max_concurrent_adapters,
        "handoff": {
            "target_pipeline": "abx_auto_ingest_v1",
            "target_patch": TARGET_PATCH_ID,
            "authority": "SHADOW_ONLY",
            "controlled_handoff_eligibility": handoff_eligibility,
        },
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }
    packet["run_id"] = canonical_hash(packet)
    return packet


def build_scheduler_receipt(decision_set: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    packet = {
        "schema_version": "SchedulerReceipt.v1",
        "scheduler_id": decision_set["scheduler_id"],
        "decision_hash": decision_set["decision_hash"],
        "run_id": manifest["run_id"],
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authority": AUTHORITY,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "status": "ADVISORY_ONLY",
    }
    packet["receipt_hash"] = canonical_hash(packet)
    return packet


def build_scheduler_markdown(decision_set: dict[str, Any], manifest: dict[str, Any], receipt: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Controlled Ingest Scheduler",
            "",
            f"- scheduler_id: `{decision_set['scheduler_id']}`",
            f"- decision_hash: `{decision_set['decision_hash']}`",
            f"- run_id: `{manifest['run_id']}`",
            f"- receipt_hash: `{receipt['receipt_hash']}`",
            f"- eligible_adapters: `{len(manifest['eligible_adapters'])}`",
            f"- blocked_adapters: `{len(manifest['blocked_adapters'])}`",
        ]
    ) + "\n"


# WP-D4-C2: publication moved to scripts/ingest/run_ingest_scheduler.py
