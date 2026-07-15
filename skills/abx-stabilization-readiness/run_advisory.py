#!/usr/bin/env python3
"""Advisory stabilization readiness runner (WO-ABX-STABILIZATION-SKILL-FOUNDATION-001)."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_PKG = Path(__file__).resolve().parent
PKG_NAME = "abx_stabilization_readiness"


def _ensure_pkg() -> None:
    if PKG_NAME not in sys.modules:
        pkg = types.ModuleType(PKG_NAME)
        pkg.__path__ = [str(_PKG)]  # type: ignore[attr-defined]
        sys.modules[PKG_NAME] = pkg


def _load(mod_name: str, filename: str):
    _ensure_pkg()
    full_name = f"{PKG_NAME}.{mod_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    spec = importlib.util.spec_from_file_location(full_name, _PKG / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    mod.__package__ = PKG_NAME
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _bootstrap():
    _load("contracts", "contracts.py")
    _load("models", "models.py")
    return {
        "ci": _load("contract_inventory", "contract_inventory.py"),
        "ch": _load("conformance_harness", "conformance_harness.py"),
        "dr": _load("director", "director.py"),
        "ra": _load("reproducibility_auditor", "reproducibility_auditor.py"),
        "sg": _load("stabilization_gate", "stabilization_gate.py"),
    }


def run_advisory(repo_root: Path, emit: bool = True) -> dict:
    m = _bootstrap()
    out_dir = repo_root / "out" / "stabilization_readiness"
    out_dir.mkdir(parents=True, exist_ok=True)

    state = m["dr"].default_campaign_state()
    inventory = m["ci"].build_contract_inventory(repo_root)
    repro = m["ra"].audit_reproducibility(repo_root)
    fixtures = _PKG / "fixtures"
    harness = m["ch"].build_harness_report(fixtures)

    receipt = m["dr"].stabilization_direct(
        repo_state={"repo_root": str(repo_root)},
        contract_inventory=inventory,
        validation_evidence={},
        residual_risks=[],
        phase=state.phase,
    )

    if emit:
        m["ci"].write_inventory_artifact(repo_root, out_dir)
        m["ra"].write_reproducibility_artifact(repo_root, out_dir)
        m["ch"].write_harness_artifact(repo_root, fixtures)
        (out_dir / "director_receipt.latest.json").write_text(
            json.dumps(receipt.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        m["sg"].write_gate_artifact(repo_root, out_dir)

    gate = m["sg"].evaluate_entry_gate(repo_root, out_dir)

    bundle = {
        "work_order_id": "WO-ABX-STABILIZATION-SKILL-FOUNDATION-001",
        "boundary": "ADVISORY_ONLY | READ_ONLY | NO_PRODUCTION_ACTIVATION",
        "campaign_state": state.to_dict(),
        "director_receipt": receipt.to_dict(),
        "contract_inventory_summary": {
            "count": len(inventory.get("contracts", [])),
            "hash": inventory.get("inventory_hash"),
        },
        "reproducibility_overall": repro.get("overall_classification"),
        "conformance_corpus_ready": harness.get("corpus_ready"),
        "gate_decision": gate.to_dict(),
    }
    if emit:
        bundle_path = out_dir / "advisory_bundle.latest.json"
        bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
        bundle["artifacts_dir"] = str(out_dir)
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Run stabilization readiness advisory pipeline")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--no-emit", action="store_true", help="Compute only, do not write artifacts")
    args = parser.parse_args()
    bundle = run_advisory(args.repo_root, emit=not args.no_emit)
    print(json.dumps(bundle, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())