#!/usr/bin/env python3
"""
abx-skill-patch-generator v0.1 (stub)
Given a SkillEvolutionCandidate, emits a minimal SkillPatchCandidate diff.
Never mutates active skills. Advisory only.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
import sys

_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from abx_skill_stabilization_evolution_constants import PATCH_MODE_MINIMAL_COMPATIBILITY_REPAIR  # noqa: E402

def generate_patch(candidate: dict, patch_mode: str | None = None) -> dict:
    skill = candidate.get("skill_id", "unknown")
    patch = {
        "patch_id": f"patch-{skill}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        "skill_id": skill,
        "base_version": "0.1.0",
        "proposed_version": "0.2.0",
        "changed_sections": ["invocation_conditions", "completion_criteria"],
        "rationale_refs": candidate.get("triggering_patterns", []),
        "expected_behavior_change": "Improve success_rate on recurring failure signatures",
        "rollback_plan": "Revert to base_version if canary brier_delta > 0.05",
        "patch_mode": patch_mode or (
            PATCH_MODE_MINIMAL_COMPATIBILITY_REPAIR
            if candidate.get("task_class") == "STABILIZATION"
            else "PATCH_MODE.STANDARD"
        ),
        "promotion_authorized": False,
        "status": "CANDIDATE_ONLY"
    }
    return patch

def main():
    # load latest analyzer candidate if present
    cand_path = Path("out/audit/skill_evolution_analyzer_stub_receipt.json")
    if cand_path.exists():
        data = json.loads(cand_path.read_text())
        cands = data.get("candidates", [])
    else:
        cands = [{"skill_id": "example-skill", "triggering_patterns": ["test_pattern"]}]
    patches = [generate_patch(c) for c in cands]
    out = {
        "boundary": "ADVISORY_ONLY | SHADOW | SKILL_PATCH_GENERATOR_STUB",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "patches": patches
    }
    Path("out/audit/skill_patch_generator_stub_receipt.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
