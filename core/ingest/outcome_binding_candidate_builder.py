from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

AUTHORITY = "FORECAST_CANDIDATE_ONLY"
PATCH_ID = "PATCH-ABX-AUTO-INGEST-004"
BUILDER_ID = "abx_outcome_binding_candidate_builder_v1"

_REQUIRED_TRUE_KEYS = ("advisory_only", "projection_only", "non_authoritative")
_REQUIRED_FALSE_KEYS = ("forecast_authority", "canon_mutation", "runtime_mutation", "execution_authority")
_SUPPORTED_CANDIDATE_TYPES = (
    "policy_market_attention",
    "market_volatility_anomaly",
    "social_market_coupling",
    "news_market_coupling",
    "geopolitical_context_support",
)


def _require_boundary(packet: dict[str, Any], *, schema_version: str) -> None:
    if packet.get("schema_version") != schema_version:
        raise ValueError(f"expected {schema_version}")
    for key in _REQUIRED_TRUE_KEYS:
        if packet.get(key) is not True:
            raise ValueError(f"{schema_version} must set {key}=true")
    for key in _REQUIRED_FALSE_KEYS:
        if packet.get(key) is not False:
            raise ValueError(f"{schema_version} must set {key}=false")


def _queue_entries(queue: dict[str, Any]) -> list[dict[str, Any]]:
    _require_boundary(queue, schema_version="OracleIntakeQueue.v1")
    entries = queue.get("queue_entries", [])
    if not isinstance(entries, list):
        raise ValueError("oracle intake queue must provide queue_entries")
    normalized: list[dict[str, Any]] = []
    for row in entries:
        if not isinstance(row, dict):
            raise ValueError("queue entries must be objects")
        queue_status = str(row.get("queue_status", "")).strip()
        if queue_status != "READY_FOR_ORACLE_INTAKE":
            continue
        normalized.append(row)
    return normalized


def _candidate_type(domains: set[str]) -> str:
    if "policy" in domains and "finance" in domains:
        return "policy_market_attention"
    if "anomaly" in domains and "finance" in domains:
        return "market_volatility_anomaly"
    if "social" in domains and "finance" in domains:
        return "social_market_coupling"
    if "news" in domains and "finance" in domains:
        return "news_market_coupling"
    if "geopolitics" in domains and len(domains) >= 2:
        return "geopolitical_context_support"
    return "NOT_COMPUTABLE"


def _required_sources(candidate_type: str) -> list[str]:
    mapping = {
        "policy_market_attention": [
            "market_close_source",
            "policy_decision_source",
            "news_archive_source",
        ],
        "market_volatility_anomaly": [
            "market_close_source",
            "volatility_source",
        ],
        "social_market_coupling": [
            "market_close_source",
            "social_trend_source",
        ],
        "news_market_coupling": [
            "market_close_source",
            "news_archive_source",
        ],
        "geopolitical_context_support": [
            "geopolitical_event_source",
            "market_close_source",
        ],
    }
    return mapping.get(candidate_type, [])


def build_outcome_binding_candidate_packet(queue: dict[str, Any]) -> dict[str, Any]:
    entries = _queue_entries(queue)
    source_receipt_hashes = sorted(
        {
            str(row["source_pull_receipt_id"])
            for row in entries
            if isinstance(row.get("source_pull_receipt_id"), str) and row["source_pull_receipt_id"]
        }
    )
    domains = sorted(
        {
            str(row["domain"])
            for row in entries
            if isinstance(row.get("domain"), str) and row["domain"]
        }
    )
    unique_domains = set(domains)
    candidate_type = _candidate_type(unique_domains)
    cross_domain_ready = len(unique_domains) >= 2 and len(entries) >= 2 and candidate_type in _SUPPORTED_CANDIDATE_TYPES
    required_resolution_sources = _required_sources(candidate_type) if cross_domain_ready else []
    candidate_status = (
        "CANDIDATE_READY_ADVISORY_ONLY" if cross_domain_ready else "NOT_COMPUTABLE_CROSS_DOMAIN_EVIDENCE_REQUIRED"
    )
    activation_status = "OPERATOR_REQUIRED" if cross_domain_ready else "BLOCKED_PENDING_CROSS_DOMAIN_EVIDENCE"

    packet = {
        "schema_version": "OutcomeBindingCandidatePacket.v1",
        "patch_id": PATCH_ID,
        "builder_id": BUILDER_ID,
        "source_queue_hash": queue["queue_hash"],
        "candidate_type": candidate_type,
        "candidate_status": candidate_status,
        "source_receipt_hashes": source_receipt_hashes,
        "source_domains": domains,
        "required_resolution_sources": required_resolution_sources,
        "candidate_window": "T+24h" if cross_domain_ready else "NOT_COMPUTABLE",
        "cross_domain_receipt_count": len(entries),
        "brier_ready": False,
        "activation_status": activation_status,
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }
    packet["candidate_id"] = canonical_hash(packet)
    return packet


def build_resolution_source_requirement_set(candidate_packet: dict[str, Any]) -> dict[str, Any]:
    _require_boundary(candidate_packet, schema_version="OutcomeBindingCandidatePacket.v1")
    requirements = [
        {
            "source_id": source_id,
            "source_status": "REQUIRED_UNVERIFIED",
            "required": True,
        }
        for source_id in candidate_packet.get("required_resolution_sources", [])
    ]
    requirement_status = "REQUIREMENTS_DECLARED" if requirements else "NOT_COMPUTABLE_CANDIDATE_NOT_READY"
    packet = {
        "schema_version": "ResolutionSourceRequirementSet.v1",
        "patch_id": PATCH_ID,
        "candidate_id": candidate_packet["candidate_id"],
        "candidate_type": candidate_packet["candidate_type"],
        "requirement_status": requirement_status,
        "requirements": requirements,
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }
    packet["requirement_set_hash"] = canonical_hash(packet)
    return packet


def build_brier_readiness_precheck(
    candidate_packet: dict[str, Any],
    requirement_set: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _require_boundary(candidate_packet, schema_version="OutcomeBindingCandidatePacket.v1")
    requirement_packet = requirement_set or build_resolution_source_requirement_set(candidate_packet)
    _require_boundary(requirement_packet, schema_version="ResolutionSourceRequirementSet.v1")

    missing: list[str] = []
    if candidate_packet.get("candidate_status") != "CANDIDATE_READY_ADVISORY_ONLY":
        missing.append("cross_domain_candidate_evidence")
    if not candidate_packet.get("source_receipt_hashes"):
        missing.append("source_receipt_hashes")
    if not requirement_packet.get("requirements"):
        missing.append("required_resolution_sources")
    missing.append("operator_approved_outcome_binding_contract")

    packet = {
        "schema_version": "BrierReadinessPrecheck.v1",
        "patch_id": PATCH_ID,
        "candidate_id": candidate_packet["candidate_id"],
        "precheck_status": "NOT_READY_OPERATOR_REVIEW_REQUIRED",
        "brier_ready": False,
        "missing_requirements": sorted(missing),
        "authority": AUTHORITY,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "forecast_authority": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
    }
    packet["precheck_hash"] = canonical_hash(packet)
    return packet


def render_candidate_markdown(
    candidate_packet: dict[str, Any],
    requirement_set: dict[str, Any],
    precheck: dict[str, Any],
) -> tuple[str, str, str]:
    candidate_lines = [
        "# Outcome Binding Candidate Packet",
        "",
        f"- candidate_id: `{candidate_packet['candidate_id']}`",
        f"- candidate_type: `{candidate_packet['candidate_type']}`",
        f"- candidate_status: `{candidate_packet['candidate_status']}`",
        f"- source_receipt_count: `{len(candidate_packet['source_receipt_hashes'])}`",
        f"- authority: `{candidate_packet['authority']}`",
        "",
    ]
    requirement_lines = [
        "# Resolution Source Requirement Set",
        "",
        f"- candidate_id: `{requirement_set['candidate_id']}`",
        f"- requirement_status: `{requirement_set['requirement_status']}`",
        f"- requirement_count: `{len(requirement_set['requirements'])}`",
        f"- authority: `{requirement_set['authority']}`",
        "",
    ]
    precheck_lines = [
        "# Brier Readiness Precheck",
        "",
        f"- candidate_id: `{precheck['candidate_id']}`",
        f"- precheck_status: `{precheck['precheck_status']}`",
        f"- missing_requirement_count: `{len(precheck['missing_requirements'])}`",
        f"- authority: `{precheck['authority']}`",
        "",
    ]
    return "\n".join(candidate_lines), "\n".join(requirement_lines), "\n".join(precheck_lines)


def write_outcome_binding_candidate_outputs(
    out_dir: Path | str,
    *,
    candidate_packet: dict[str, Any],
    requirement_set: dict[str, Any],
    precheck: dict[str, Any],
) -> None:
    target_dir = Path(out_dir)
    candidate_json = target_dir / "outcome_binding_candidate_packet_001.latest.json"
    requirements_json = target_dir / "resolution_source_requirement_set_001.latest.json"
    precheck_json = target_dir / "brier_readiness_precheck_001.latest.json"

    write_canonical_json(candidate_json, candidate_packet)
    write_canonical_json(requirements_json, requirement_set)
    write_canonical_json(precheck_json, precheck)

    candidate_md, requirements_md, precheck_md = render_candidate_markdown(
        candidate_packet,
        requirement_set,
        precheck,
    )
    candidate_json.with_suffix(".md").write_text(candidate_md, encoding="utf-8")
    requirements_json.with_suffix(".md").write_text(requirements_md, encoding="utf-8")
    precheck_json.with_suffix(".md").write_text(precheck_md, encoding="utf-8")
