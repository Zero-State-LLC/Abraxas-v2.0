"""Multi-agent operator loop contracts — validation, overlap, projection.

Companion to docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md.

Authority rules (always enforced):
  - Producer identity records provenance only; it never grants authority.
  - Detection and classification only for overlaps; no auto-disposition.
  - AAL-Viz projection is read-only (projection_only, no assignment/approve).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
WORK_PACKET_SCHEMA_PATH = (
    ROOT / "contracts" / "engineering" / "work_packet.v1.schema.json"
)
HANDOFF_SCHEMA_PATH = (
    ROOT / "contracts" / "engineering" / "handoff_envelope.v1.schema.json"
)

AUTHORITY_LOCKS: dict[str, bool] = {
    "producer_identity_grants_authority": False,
    "auto_merge": False,
    "auto_canon_promotion": False,
    "auto_deploy": False,
    "assignment_authority": False,
    "execution_authority": False,
    "operator_review_on_semantic_conflict": True,
}

PROJECTION_AUTHORITY: dict[str, bool] = {
    "projection_only": True,
    "runtime_mutation_allowed": False,
    "promotion_allowed": False,
    "production_activation_allowed": False,
    "assignment_authority": False,
    "approval_authority": False,
    "producer_identity_grants_authority": False,
}

ACTIVE_OVERLAP_STATES = frozenset({"ACTIVE", "WAITING", "BLOCKED", "REVIEW"})

CONFLICT_CLASS_FILE_OVERLAP = "FILE_OVERLAP"


def default_authority() -> dict[str, bool]:
    """Return a fresh authority lock object (safe for embedding in packets)."""
    return dict(AUTHORITY_LOCKS)


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def work_packet_schema() -> dict[str, Any]:
    return _load_schema(WORK_PACKET_SCHEMA_PATH)


def handoff_schema() -> dict[str, Any]:
    return _load_schema(HANDOFF_SCHEMA_PATH)


def validate_work_packet(payload: Mapping[str, Any]) -> None:
    """Validate a WorkPacket.v1 payload. Raises jsonschema.ValidationError."""
    Draft202012Validator(work_packet_schema()).validate(dict(payload))


def validate_handoff(payload: Mapping[str, Any]) -> None:
    """Validate a HandoffEnvelope.v1 payload. Raises jsonschema.ValidationError."""
    Draft202012Validator(handoff_schema()).validate(dict(payload))


def producer_grants_authority(payload: Mapping[str, Any]) -> bool:
    """Return True only if authority block claims producer grants authority.

    Schemas force this false; this helper is for runtime defense-in-depth and tests.
    """
    authority = payload.get("authority")
    if not isinstance(authority, Mapping):
        return False
    return bool(authority.get("producer_identity_grants_authority") is True)


def authority_decision_matrix(
    *,
    producer_system: str,
    has_ci_pass: bool,
    operator_approved: bool,
) -> dict[str, bool]:
    """Map evidence + operator gate to authority outcomes.

    Producer identity is intentionally unused for any true grant.
    """
    _ = producer_system  # provenance only — never consulted for grants
    return {
        "merge_allowed": bool(has_ci_pass and operator_approved),
        "canon_promotion_allowed": bool(operator_approved),
        "deploy_allowed": bool(has_ci_pass and operator_approved),
        "producer_identity_used_for_grant": False,
    }


def detect_work_packet_file_overlaps(
    packets: Sequence[Mapping[str, Any]],
    *,
    active_states: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Detect FILE_OVERLAP among concurrent work packets.

    Only packets whose work_state is in active_states (default: ACTIVE,
    WAITING, BLOCKED, REVIEW) are considered. Integrated/superseded packets
    do not conflict. Returns advisory findings; never auto-resolves.
    """
    states = frozenset(active_states or ACTIVE_OVERLAP_STATES)
    active: list[Mapping[str, Any]] = [
        p
        for p in packets
        if str(p.get("work_state", "")) in states
        and isinstance(p.get("scope"), Mapping)
    ]

    file_owners: dict[str, list[str]] = {}
    for packet in active:
        packet_id = str(packet.get("work_packet_id", ""))
        files = packet.get("scope", {}).get("files") or []
        if not isinstance(files, list):
            continue
        for raw in files:
            path = str(raw)
            if not path:
                continue
            file_owners.setdefault(path, []).append(packet_id)

    findings: list[dict[str, Any]] = []
    for path, owners in sorted(file_owners.items()):
        unique_owners = sorted({o for o in owners if o})
        if len(unique_owners) < 2:
            continue
        findings.append(
            {
                "finding_id": f"file-overlap:{path}",
                "conflict_class": CONFLICT_CLASS_FILE_OVERLAP,
                "severity": "high",
                "subject_ids": unique_owners,
                "detail": (
                    f"File {path!r} is in scope for concurrent work packets "
                    f"{unique_owners}"
                ),
                "resolution_required": True,
                "auto_resolve_allowed": False,
            }
        )
    return findings


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _projection_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_operator_loop_projection(
    *,
    work_packets: Sequence[Mapping[str, Any]] | None = None,
    handoffs: Sequence[Mapping[str, Any]] | None = None,
    source_paths: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build a read-only AAL-Viz operator-loop projection.

    Never assigns work, approves merges, or mutates repository state.
    Invalid or unvalidated packets are still projected with validation flags
    so operators can see gaps (fail-visible, not fail-silent).
    """
    packets = list(work_packets or [])
    envelopes = list(handoffs or [])

    validated_packets: list[dict[str, Any]] = []
    packet_errors: list[dict[str, str]] = []
    for packet in packets:
        as_dict = dict(packet)
        try:
            validate_work_packet(as_dict)
            validated_packets.append(as_dict)
        except Exception as exc:  # noqa: BLE001 — surface validation for projection
            packet_errors.append(
                {
                    "work_packet_id": str(as_dict.get("work_packet_id", "")),
                    "error": str(exc).split("\n", 1)[0],
                }
            )

    validated_handoffs: list[dict[str, Any]] = []
    handoff_errors: list[dict[str, str]] = []
    for handoff in envelopes:
        as_dict = dict(handoff)
        try:
            validate_handoff(as_dict)
            validated_handoffs.append(as_dict)
        except Exception as exc:  # noqa: BLE001
            handoff_errors.append(
                {
                    "handoff_id": str(as_dict.get("handoff_id", "")),
                    "error": str(exc).split("\n", 1)[0],
                }
            )

    overlaps = detect_work_packet_file_overlaps(validated_packets)

    by_producer: dict[str, int] = {}
    by_state: dict[str, int] = {}
    for packet in validated_packets:
        producer = str(packet.get("producer_system", "UNKNOWN"))
        state = str(packet.get("work_state", "UNKNOWN"))
        by_producer[producer] = by_producer.get(producer, 0) + 1
        by_state[state] = by_state.get(state, 0) + 1

    packet_nodes = [
        {
            "work_packet_id": p["work_packet_id"],
            "goal": p["goal"],
            "producer_system": p["producer_system"],
            "primary_agent": p["primary_agent"],
            "work_state": p["work_state"],
            "scope_files": list(p["scope"]["files"]),
            "scope_concepts": list(p["scope"]["concepts"]),
            "activation_lane": p["activation_lane"],
            "glyph_role": _producer_to_glyph_role(str(p["producer_system"])),
            "authority_implication": "none",
        }
        for p in validated_packets
    ]

    handoff_nodes = [
        {
            "handoff_id": h["handoff_id"],
            "work_packet_id": h["work_packet_id"],
            "producer_system": h["producer_system"],
            "status": h["status"],
            "conflict_count": len(h.get("conflicts_detected") or []),
            "next_recommended_action": h["next_recommended_action"],
            "authority_implication": "none",
        }
        for h in validated_handoffs
    ]

    body: dict[str, Any] = {
        "schema_version": "OperatorLoopProjection.v1",
        "companion_spec": (
            "docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md"
        ),
        "asset_pack": "design-system/aal-viz/operator_loop/",
        "summary": {
            "work_packet_count": len(validated_packets),
            "handoff_count": len(validated_handoffs),
            "file_overlap_count": len(overlaps),
            "by_producer": dict(sorted(by_producer.items())),
            "by_work_state": dict(sorted(by_state.items())),
            "validation_error_count": len(packet_errors) + len(handoff_errors),
        },
        "work_packets": packet_nodes,
        "handoffs": handoff_nodes,
        "file_overlaps": overlaps,
        "validation_errors": {
            "work_packets": packet_errors,
            "handoffs": handoff_errors,
        },
        "source_paths": list(source_paths or []),
        "glyph_refs": {
            "roles": [
                "human_operator",
                "hermes_orchestrator",
                "grok_producer",
                "codex_cursor_producer",
                "github_implementation_truth",
                "notion_architecture_truth",
                "ci_validator",
                "aal_viz_projection",
            ],
            "nodes": [
                "work_packet",
                "handoff",
                "integration",
                "conflict",
                "operator_decision",
            ],
            "edges": [
                "assignment",
                "peer_review",
                "validation",
                "handoff_edge",
                "merge",
                "blocked_dependency",
            ],
            "badges": ["HERMES", "GROK", "CODEX", "MIXED", "HUMAN"],
            "work_states": [
                "ACTIVE",
                "WAITING",
                "BLOCKED",
                "REVIEW",
                "INTEGRATED",
                "SUPERSEDED",
            ],
        },
        "authority": dict(PROJECTION_AUTHORITY),
        "notes": [
            "Producer identity records provenance; it does not grant authority.",
            "AAL-Viz projects the operator loop; it does not run it.",
            "Semantic and architectural conflicts require operator disposition.",
        ],
    }
    body["projection_hash"] = _projection_hash(
        {k: v for k, v in body.items() if k != "projection_hash"}
    )
    return body


def _producer_to_glyph_role(producer: str) -> str:
    return {
        "HERMES": "hermes_orchestrator",
        "GROK": "grok_producer",
        "CODEX": "codex_cursor_producer",
        "MIXED": "codex_cursor_producer",
        "HUMAN": "human_operator",
    }.get(producer, "aal_viz_projection")


def example_work_packet(
    *,
    work_packet_id: str = "WP-example-001",
    producer_system: str = "CODEX",
    files: Sequence[str] | None = None,
    work_state: str = "ACTIVE",
) -> dict[str, Any]:
    """Deterministic example packet for tests and dry-run projection."""
    return {
        "schema_version": "WorkPacket.v1",
        "work_packet_id": work_packet_id,
        "goal": "Formalize operator-loop work packet contracts",
        "producer_system": producer_system,
        "primary_agent": "codex-or-cursor",
        "secondary_reviewer": "hermes",
        "scope": {
            "files": list(files or ["contracts/engineering/work_packet.v1.schema.json"]),
            "concepts": ["operator_loop", "work_packet"],
        },
        "exclusions": ["scripts/operator/__init__.py"],
        "inputs": {
            "notion_pages": ["Abraxas — Master System (AAL Canon)"],
            "repository_paths": [
                "docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md"
            ],
            "source_artifacts": [],
        },
        "activation_lane": "LOCAL_DEV",
        "expected_outputs": [
            "contracts/engineering/work_packet.v1.schema.json",
            "tests/test_operator_loop_contracts.py",
        ],
        "validation_commands": [
            "python3 -m pytest tests/test_operator_loop_contracts.py -q"
        ],
        "acceptance_criteria": [
            "Schema rejects producer authority escalation",
            "File overlaps are detected and require operator disposition",
        ],
        "dependencies": [],
        "conflict_policy": "DETECT_CLASSIFY_OPERATOR_DISPOSITION",
        "handoff_target": "operator_review_or_integration",
        "work_state": work_state,
        "branch": "feat/operator-loop-work-packet-contracts",
        "pull_request": None,
        "notes": None,
        "authority": default_authority(),
    }


def example_handoff(
    *,
    handoff_id: str = "HO-example-001",
    work_packet_id: str = "WP-example-001",
    producer_system: str = "CODEX",
) -> dict[str, Any]:
    """Deterministic example handoff for tests and dry-run projection."""
    return {
        "schema_version": "HandoffEnvelope.v1",
        "handoff_id": handoff_id,
        "work_packet_id": work_packet_id,
        "producer_system": producer_system,
        "status": "COMPLETE",
        "changed_files": [
            "contracts/engineering/work_packet.v1.schema.json",
            "core/operator_loop.py",
        ],
        "generated_assets": [],
        "commands_run": [
            "python3 -m pytest tests/test_operator_loop_contracts.py -q"
        ],
        "tests": {
            "passed": ["tests/test_operator_loop_contracts.py"],
            "failed": [],
        },
        "observed_findings": ["Schemas enforce authority locks via const:false"],
        "inferred_findings": [],
        "conflicts_detected": [],
        "residual_risks": [
            "Hermes/Grok prompt updates still pending (implementation sequence 6–8)"
        ],
        "next_recommended_action": (
            "Operator review of contracts; wire Hermes skills to emit WorkPacket.v1"
        ),
        "branch": "feat/operator-loop-work-packet-contracts",
        "pull_request": None,
        "notes": None,
        "authority": default_authority(),
    }
