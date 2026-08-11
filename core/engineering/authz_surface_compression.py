"""Track D authorization surface compression receipt.

Advisory-only closeout surface for #1120. It records the repository rule that
new plan work must cite Track A/B/C/D or be explicitly marked historical/sealed,
and that operator disposition should stop at one decision record plus one hold
receipt instead of recursive plan -> gate -> plan trees.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

ARTIFACT_TYPE = "AuthzSurfaceCompressionReceipt.v1"
STATUS = "TRACK_D_AUTHZ_SURFACE_COMPRESSED_ADVISORY_ONLY"
TRACK_ID = "D"
ISSUE = 1120

TRACK_MARKERS = (
    "Track A",
    "Track B",
    "Track C",
    "Track D",
    "Track A-D",
    "Tracks A-D",
    "A/B/C/D",
)
TERMINAL_MARKERS = (
    "HISTORICAL",
    "SEALED_HOLD",
    "SUPERSEDED",
    "sealed",
    "do not extend",
)

AUTHORITY = {
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "production_authority": False,
    "clear_unhold_authorized": False,
    "auto_unhold_authorized": False,
    "plan_tree_generation_authorized": False,
    "mass_plan_rewrite_authorized": False,
}


def classify_plan_text(text: str) -> str:
    """Classify plan text for Track D routing without mutating it."""
    if any(marker in text for marker in TRACK_MARKERS):
        return "TRACK_ROUTED"
    if any(marker in text for marker in TERMINAL_MARKERS):
        return "TERMINAL_CLASSIFIED"
    return "LEGACY_UNROUTED"


def _plan_rows(plan_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(plan_root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append(
            {
                "path": path.as_posix(),
                "classification": classify_plan_text(text),
                "has_track_marker": any(marker in text for marker in TRACK_MARKERS),
                "has_terminal_marker": any(marker in text for marker in TERMINAL_MARKERS),
            }
        )
    return rows


def build_authz_surface_compression_receipt(
    *, repo_root: str | Path = "."
) -> dict[str, Any]:
    root = Path(repo_root)
    rows = _plan_rows(root / "docs" / "plans")
    counts = {
        "total_plan_docs": len(rows),
        "track_routed": sum(1 for row in rows if row["classification"] == "TRACK_ROUTED"),
        "terminal_classified": sum(
            1 for row in rows if row["classification"] == "TERMINAL_CLASSIFIED"
        ),
        "legacy_unrouted": sum(1 for row in rows if row["classification"] == "LEGACY_UNROUTED"),
    }
    receipt: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": ARTIFACT_TYPE,
        "status": STATUS,
        "issue": ISSUE,
        "track_id": TRACK_ID,
        "plan": "docs/plans/AUTHZ_SURFACE_COMPRESSION_TRACK_D_001.md",
        "closeout_doc": "docs/status/AUTHZ_SURFACE_COMPRESSION_TRACK_D_CLOSEOUT.md",
        "authority": dict(AUTHORITY),
        "advisory_only": True,
        "plan_inventory": {
            "counts": counts,
            "rows": rows,
            "legacy_unrouted_policy": (
                "Legacy docs are observed only; do not mass rewrite. On touch, add Track A/B/C/D "
                "or a terminal HISTORICAL/SEALED_HOLD/SUPERSEDED classification."
            ),
        },
        "new_work_policy": {
            "required_track_citation": ["Track A", "Track B", "Track C", "Track D"],
            "orphan_plan_creation_authorized": False,
            "new_plan_without_track_or_terminal_class": "REJECT",
        },
        "decision_record_policy": {
            "preferred_shape": "ONE_DECISION_RECORD_PLUS_ONE_HOLD_RECEIPT",
            "nested_plan_gate_plan_chains_authorized": False,
            "operator_packet_required_for_new_authz_tree": True,
        },
        "bulk_hold_policy": {
            "bulk_hold_families_remain_held": True,
            "auto_unhold_authorized": False,
            "attestation_required_to_unhold": True,
        },
        "validation_commands": [
            "python -m pytest tests/test_authz_surface_compression_track_d.py -q",
            "abraxas os authz-compression",
        ],
    }
    receipt["canonical_hash"] = canonical_hash(
        {key: value for key, value in receipt.items() if key != "canonical_hash"}
    )
    return receipt
