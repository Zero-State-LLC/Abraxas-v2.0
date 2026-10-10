"""Build a self-contained repo root for the P79-P86 temporal upstream route refreshes.

The route-refresh receipts read the P80 authorization-record-plan chain from
``out/``. The head of that chain
(``out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json``)
is git-ignored, so the tracked downstream packets flip between
``P80_REGENERATION_NOT_REQUIRED`` and ``P80_REGENERATION_PLAN_READY`` depending
on whether some earlier run left that file behind. Tests that pin the
"record plan present" route build the chain here, in ``tmp_path``, from the
tracked authorization gate using the real builders, instead of depending on
whatever generated artifacts happen to be in the working tree.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.temporal_continuity_p80_authorization_record_plan_regeneration_plan import (
    build_temporal_continuity_p80_authorization_record_plan_regeneration_plan,
)
from core.temporal_continuity_p80_authorization_record_regeneration_receipt import (
    DEFAULT_OUT_PATH as SLICE51_RECEIPT_PATH,
    build_temporal_continuity_p80_authorization_record_regeneration_receipt,
)
from core.temporal_continuity_p84_regeneration_plan_regeneration_plan import (
    build_temporal_continuity_p84_regeneration_plan_regeneration_plan,
)
from core.temporal_continuity_upstream_input_regeneration_authorization_record_plan import (
    build_temporal_continuity_upstream_input_regeneration_authorization_record_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

P80_RECORD_PLAN_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)
P80_REGENERATION_PLAN_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
)
P85_EXECUTION_PLAN_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
)
P86_REGENERATION_PLAN_PATH = (
    "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json"
)

# Tracked inputs copied verbatim from the checkout.
_TRACKED_FILES = (
    "README.md",
    "STATUS.md",
    "PLANS.md",
    "AGENTS.md",
    "core/generated_artifact_registry.py",
    "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json",
    "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json",
    "out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json",
    "out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json",
    # The tracked P85 execution plan is kept as committed (it routes back to P84
    # regeneration); P86 is then planned against it, which is the P85 -> P86 route.
    P85_EXECUTION_PLAN_PATH,
)
_TRACKED_DIRS = ("docs",)


def build_p80_record_plan_chain_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for rel in _TRACKED_DIRS:
        shutil.copytree(REPO_ROOT / rel, root / rel)
    for rel in _TRACKED_FILES:
        source = REPO_ROOT / rel
        if source.is_file():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    chain = (
        (
            P80_RECORD_PLAN_PATH,
            build_temporal_continuity_upstream_input_regeneration_authorization_record_plan,
        ),
        (
            P80_REGENERATION_PLAN_PATH,
            build_temporal_continuity_p80_authorization_record_plan_regeneration_plan,
        ),
        (SLICE51_RECEIPT_PATH, build_temporal_continuity_p80_authorization_record_regeneration_receipt),
        (P86_REGENERATION_PLAN_PATH, build_temporal_continuity_p84_regeneration_plan_regeneration_plan),
    )
    for rel, builder in chain:
        write_canonical_json(root / rel, builder(repo_root=root))
    return root
