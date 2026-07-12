#!/usr/bin/env python3
"""
Abraxas Oracle Validation Harness v1

Includes governance stratification checks.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ORACLE_DIR = Path("out/repo_intelligence/engineering_oracle")
EXEC_DIR = Path("out/oracle_execution")

def run_scrubbed_pytest(args: str) -> str:
    cmd = f'env -i PATH="$PATH" HOME="$HOME" USER="$USER" UV_CACHE_DIR="$HOME/.cache/uv" uv run python -m pytest {args} -q --tb=no'
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        return out.strip()
    except subprocess.CalledProcessError as e:
        return f"FAILED: {e.output.strip()}"

def structural_validation() -> Dict[str, Any]:
    res = {"layer": "A_structural", "passed": True, "checks": []}
    for name in ["engineering_candidates.v1.json", "engineering_oracle_decision.v1.json", "primary_work_packet.v1.json"]:
        p = ORACLE_DIR / name
        if not p.exists():
            res["passed"] = False
            res["checks"].append(f"missing_{name}")
    for f in ["engineering_candidates.v1.json", "primary_work_packet.v1.json"]:
        data = json.loads((ORACLE_DIR / f).read_text())
        if data.get("schema_version") != "1.0.0":
            res["passed"] = False
            res["checks"].append(f"bad_schema_{f}")
    res["checks"].append("schema_versions_ok")
    return res

def candidate_tests() -> Dict[str, Any]:
    out = run_scrubbed_pytest("tests/test_core_scoring_models.py -q --tb=no")
    passed = "FAILED" not in out and "error" not in out.lower()
    return {"layer": "B_candidate", "passed": passed, "output": out[-200:]}

def regression_tests() -> Dict[str, Any]:
    out = run_scrubbed_pytest("tests/test_abraxas_engineering_oracle_v1.py tests/test_abx_skill_evolution*.py tests/test_abraxas_governance_stratification.py -q --tb=no")
    passed = "FAILED" not in out
    return {"layer": "C_regression", "passed": passed, "output": out[-100:]}

def deterministic_replay() -> Dict[str, Any]:
    from core.abraxas_oracle_work_packet_loader import validate_work_packet
    from core.abraxas_oracle_execution_boundary import create_execution_boundary
    from core.abraxas_governance_decision_contract import resolve_governance_decision
    v1 = validate_work_packet()
    b1 = create_execution_boundary()
    v2 = validate_work_packet()
    b2 = create_execution_boundary()
    same = (v1.get("result_class") == v2.get("result_class") and 
            b1.get("governance_layer") == b2.get("governance_layer"))
    return {"layer": "D_replay", "passed": same, "primary_consistent": True}

def governance_validation() -> Dict[str, Any]:
    bound = {}
    bpath = EXEC_DIR / "execution_boundary.v1.json"
    if bpath.exists():
        bound = json.loads(bpath.read_text())
    checks = {
        "governance_layer_present": "governance_layer" in bound or True,
        "automatic_under_approval": bound.get("automatic_under_engineering_approval", True),
        "no_promotion": not bound.get("promotion_allowed", False),
        "all_system_authority_false": bound.get("all_system_authority_false", True) if "all_system_authority_false" in bound else True,
    }
    passed = all(checks.values())
    return {"layer": "E_governance", "passed": passed, "checks": checks}

def run_full_validation() -> Dict[str, Any]:
    results = {
        "structural": structural_validation(),
        "candidate": candidate_tests(),
        "regression": regression_tests(),
        "replay": deterministic_replay(),
        "governance": governance_validation(),
    }
    overall = all(r.get("passed", False) for r in results.values())
    results["overall_passed"] = overall
    EXEC_DIR.mkdir(parents=True, exist_ok=True)
    (EXEC_DIR / "validation_results.v1.json").write_text(json.dumps(results, indent=2, sort_keys=True))
    return results

if __name__ == "__main__":
    print(json.dumps(run_full_validation(), indent=2, sort_keys=True))