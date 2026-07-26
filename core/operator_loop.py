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


def build_truth_surfaces(
    *,
    github: Mapping[str, Any] | None = None,
    notion: Mapping[str, Any] | None = None,
    ci: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize GitHub / Notion / CI evidence for projection.

    Surfaces are display-only. They never grant merge, assignment, or deploy
    authority. Missing sources are visible as empty lists with explicit status.
    """

    def _surface(
        *,
        role: str,
        truth_claim: str,
        glyph: str,
        payload: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        data = dict(payload or {})
        items = data.get("items")
        if not isinstance(items, list):
            items = []
        status = str(data.get("status") or ("PRESENT" if items else "NOT_COMPUTABLE"))
        return {
            "role": role,
            "truth_claim": truth_claim,
            "glyph": glyph,
            "status": status,
            "source": str(data.get("source") or "none"),
            "items": [dict(i) if isinstance(i, Mapping) else {"value": i} for i in items],
            "notes": list(data.get("notes") or []),
            "authority_implication": "none",
            "can_assign": False,
            "can_approve": False,
            "can_merge": False,
            "can_deploy": False,
        }

    return {
        "github": _surface(
            role="implementation_truth",
            truth_claim="GitHub is implementation, PR, CI, and merge truth.",
            glyph="github_implementation_truth",
            payload=github,
        ),
        "notion": _surface(
            role="architecture_truth",
            truth_claim="Notion is architecture, ownership, and durable-spec truth.",
            glyph="notion_architecture_truth",
            payload=notion,
        ),
        "ci": _surface(
            role="deterministic_evidence",
            truth_claim="CI/validation supplies deterministic technical evidence only.",
            glyph="ci_validator",
            payload=ci,
        ),
        "lineage_rule": (
            "Lineage projects request → packet → handoff → PR/commit → Notion update; "
            "producer badges are provenance only."
        ),
    }


def collect_local_truth_surfaces(
    *,
    repo_root: Path | None = None,
    evidence_dir: Path | None = None,
    git_head: str | None = None,
    git_branch: str | None = None,
    include_local_git: bool = True,
) -> dict[str, Any]:
    """Collect offline-friendly truth surfaces from files + optional git refs.

    Never calls the network. Optional evidence files:
      out/operator_loop/evidence/github.v1.json
      out/operator_loop/evidence/notion.v1.json
      out/operator_loop/evidence/ci.v1.json
    each shaped as {status?, source?, items: [], notes?: []}.
    """
    root = repo_root or ROOT
    evidence = evidence_dir or (root / "out" / "operator_loop" / "evidence")

    def _load_optional(name: str) -> dict[str, Any]:
        path = evidence / name
        if not path.is_file():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {
                "status": "NOT_COMPUTABLE",
                "source": str(path),
                "items": [],
                "notes": [f"failed to parse {name}"],
            }
        return payload if isinstance(payload, dict) else {}

    github = _load_optional("github.v1.json")
    notion = _load_optional("notion.v1.json")
    ci = _load_optional("ci.v1.json")

    # Local git tip (no network) — implementation-truth pointer only.
    if not github.get("items") and include_local_git:
        head = git_head
        branch = git_branch
        if head is None or branch is None:
            head_path = root / ".git" / "HEAD"
            if head_path.is_file():
                try:
                    head_text = head_path.read_text(encoding="utf-8").strip()
                except OSError:
                    head_text = ""
                if head_text.startswith("ref:"):
                    ref = head_text.split(" ", 1)[1].strip()
                    branch = branch or ref.rsplit("/", 1)[-1]
                    ref_file = root / ".git" / ref
                    if ref_file.is_file():
                        try:
                            head = ref_file.read_text(encoding="utf-8").strip()
                        except OSError:
                            head = None
                elif len(head_text) >= 7:
                    head = head_text
        items: list[dict[str, Any]] = []
        if head:
            items.append(
                {
                    "kind": "git_tip",
                    "sha": head[:40],
                    "branch": branch or "unknown",
                    "authority_implication": "none",
                }
            )
        github = {
            "status": "PRESENT" if items else "NOT_COMPUTABLE",
            "source": "local_git_refs",
            "items": items,
            "notes": [
                (
                    "Local tip only — open PR/CI lists require optional evidence "
                    "files or an explicit live gatherer; never auto-merged."
                )
            ],
        }
    elif not github.get("items"):
        github = {
            "status": "NOT_COMPUTABLE",
            "source": "none",
            "items": [],
            "notes": ["local git tip disabled; no github.v1.json evidence file"],
        }

    if not notion.get("items"):
        notion = {
            "status": "PRESENT",
            "source": "repo_architecture_pointers",
            "items": [
                {
                    "kind": "architecture_doc",
                    "path": "docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md",
                    "title": "Multi-Agent Operator Loop 001",
                },
                {
                    "kind": "status_doc",
                    "path": "STATUS.md",
                    "title": "Repository STATUS (readiness table)",
                },
                {
                    "kind": "plans_doc",
                    "path": "PLANS.md",
                    "title": "PLANS roadmap front door",
                },
                {
                    "kind": "notion_pointer",
                    "title": "Abraxas — Master System (AAL Canon)",
                    "note": "Architecture truth lives in Notion; repo docs are pointers.",
                },
            ],
            "notes": [
                "Notion remains architecture/ownership truth; these are projection pointers only."
            ],
        }

    if not ci.get("items"):
        ci = {
            "status": "NOT_COMPUTABLE",
            "source": "none",
            "items": [],
            "notes": [
                (
                    "Provide out/operator_loop/evidence/ci.v1.json for check "
                    "evidence, or rely on GitHub Actions UI. Projection never "
                    "flips deploy gates."
                )
            ],
        }

    return build_truth_surfaces(github=github, notion=notion, ci=ci)


def build_operator_loop_projection(
    *,
    work_packets: Sequence[Mapping[str, Any]] | None = None,
    handoffs: Sequence[Mapping[str, Any]] | None = None,
    source_paths: Sequence[str] | None = None,
    truth_surfaces: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only AAL-Viz operator-loop projection.

    Never assigns work, approves merges, or mutates repository state.
    Invalid or unvalidated packets are still projected with validation flags
    so operators can see gaps (fail-visible, not fail-silent).
    """
    packets = list(work_packets or [])
    envelopes = list(handoffs or [])
    surfaces = (
        dict(truth_surfaces)
        if truth_surfaces is not None
        else build_truth_surfaces()
    )

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
            "github_item_count": len(
                (surfaces.get("github") or {}).get("items") or []
            ),
            "notion_item_count": len(
                (surfaces.get("notion") or {}).get("items") or []
            ),
            "ci_item_count": len((surfaces.get("ci") or {}).get("items") or []),
        },
        "work_packets": packet_nodes,
        "handoffs": handoff_nodes,
        "file_overlaps": overlaps,
        "truth_surfaces": surfaces,
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
            (
                "GitHub = implementation truth; Notion = architecture truth; "
                "CI = deterministic evidence; none assign or approve."
            ),
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
            "Sequence 9–10: truth surfaces project only; assignment stays outside AAL-Viz"
        ],
        "next_recommended_action": (
            "Operator review of contracts; project truth surfaces via builder script"
        ),
        "branch": "feat/operator-loop-work-packet-contracts",
        "pull_request": None,
        "notes": None,
        "authority": default_authority(),
    }
