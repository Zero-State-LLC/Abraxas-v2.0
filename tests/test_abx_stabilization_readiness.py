"""Tests for abx-stabilization-readiness (WO-001 foundation)."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "skills" / "abx-stabilization-readiness"
PKG_NAME = "abx_stabilization_readiness"


def _ensure_pkg() -> None:
    if PKG_NAME not in sys.modules:
        pkg = types.ModuleType(PKG_NAME)
        pkg.__path__ = [str(PKG)]  # type: ignore[attr-defined]
        sys.modules[PKG_NAME] = pkg


def _load(mod_name: str, filename: str):
    _ensure_pkg()
    full_name = f"{PKG_NAME}.{mod_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    spec = importlib.util.spec_from_file_location(full_name, PKG / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    mod.__package__ = PKG_NAME
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_all():
    _load("contracts", "contracts.py")
    _load("models", "models.py")
    return {
        "director": _load("director", "director.py"),
        "models": sys.modules[f"{PKG_NAME}.models"],
        "contract_inventory": _load("contract_inventory", "contract_inventory.py"),
        "reproducibility": _load("reproducibility_auditor", "reproducibility_auditor.py"),
        "harness": _load("conformance_harness", "conformance_harness.py"),
        "gate": _load("stabilization_gate", "stabilization_gate.py"),
        "runner": _load("run_advisory", "run_advisory.py"),
    }


@pytest.fixture(scope="module")
def mods():
    return _load_all()


@pytest.fixture(scope="module")
def director(mods):
    return mods["director"]


@pytest.fixture(scope="module")
def models(mods):
    return mods["models"]


@pytest.fixture(scope="module")
def contract_inventory(mods):
    return mods["contract_inventory"]


@pytest.fixture(scope="module")
def reproducibility(mods):
    return mods["reproducibility"]


@pytest.fixture(scope="module")
def harness(mods):
    return mods["harness"]


@pytest.fixture(scope="module")
def gate(mods):
    return mods["gate"]


def test_default_campaign_state_hash_stable(director, models):
    a = director.default_campaign_state()
    b = director.default_campaign_state()
    assert a.state_hash == b.state_hash
    assert a.campaign_class == "STABILIZATION_READINESS"
    assert a.feature_expansion_allowed is False


def test_stabilization_direct_receipt_hash_stable(director):
    r1 = director.stabilization_direct(phase="PHASE.0_BASELINE_DISCOVERY")
    r2 = director.stabilization_direct(phase="PHASE.0_BASELINE_DISCOVERY")
    assert r1.receipt_hash == r2.receipt_hash
    assert r1.rune == "RUNE.STABILIZATION_DIRECT"
    assert r1.selected_packets


def test_contract_inventory_deterministic(contract_inventory):
    inv1 = contract_inventory.build_contract_inventory(REPO)
    inv2 = contract_inventory.build_contract_inventory(REPO)
    assert inv1["inventory_hash"] == inv2["inventory_hash"]
    assert any(c["contract_id"] == "CONTRACT.RUNTIME.STATUS_RESULT.V1" for c in inv1["contracts"])


def test_conformance_fixture_loads(harness):
    report = harness.build_harness_report(PKG / "fixtures")
    assert report["corpus_ready"] is True
    assert report["case_count"] >= 1
    assert "STATUS_RESULT_NOT_COMPUTABLE_001" in [c["case_id"] for c in report["cases"]]


def test_reproducibility_audit_has_overall(reproducibility):
    audit = reproducibility.audit_reproducibility(REPO)
    assert audit["overall_classification"] in (
        "REPRODUCIBLE",
        "REPRODUCIBLE_WITH_DECLARED_VARIANCE",
        "NON_REPRODUCIBLE",
        "NOT_COMPUTABLE",
    )


def test_gate_held_without_artifacts(gate, tmp_path):
    decision = gate.evaluate_entry_gate(tmp_path, tmp_path / "empty_evidence")
    assert decision.decision == "STABILIZATION_ENTRY_HELD"
    assert decision.operator_action_required is True
    assert decision.blocking_findings


def test_gate_with_emitted_evidence(gate, contract_inventory, reproducibility, harness, director, tmp_path):
    ev = tmp_path / "evidence"
    ev.mkdir()
    inv = contract_inventory.build_contract_inventory(REPO)
    (ev / "contract_inventory.latest.json").write_text(json.dumps(inv), encoding="utf-8")
    repro = reproducibility.audit_reproducibility(REPO)
    (ev / "reproducibility_audit.latest.json").write_text(json.dumps(repro), encoding="utf-8")
    rep = harness.build_harness_report(PKG / "fixtures")
    (ev / "conformance_harness.latest.json").write_text(json.dumps(rep), encoding="utf-8")
    receipt = director.stabilization_direct()
    (ev / "director_receipt.latest.json").write_text(json.dumps(receipt.to_dict()), encoding="utf-8")

    decision = gate.evaluate_entry_gate(REPO, ev)
    assert decision.decision in (
        "STABILIZATION_ENTRY_READY",
        "STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS",
        "STABILIZATION_ENTRY_HELD",
    )
    assert decision.decision_hash.startswith("sha256:")


def test_stabilization_campaign_routing():
    from core.campaign_director.stabilization_campaign import (
        campaign_should_stop_on_terminal,
        is_stabilization_campaign,
        stabilization_routing_packet,
    )

    assert is_stabilization_campaign(campaign_class="STABILIZATION_READINESS")
    pkt = stabilization_routing_packet(REPO)
    assert pkt["delegated_skill"] == "abx-stabilization-readiness"
    assert campaign_should_stop_on_terminal(REPO) is False


def test_run_advisory_no_emit(tmp_path, mods):
    runner = mods["runner"]
    # Minimal repo root: copy pyproject if exists
    if (REPO / "pyproject.toml").exists():
        (tmp_path / "pyproject.toml").write_text((REPO / "pyproject.toml").read_text())
    bundle = runner.run_advisory(tmp_path, emit=False)
    assert bundle["work_order_id"] == "WO-ABX-STABILIZATION-SKILL-FOUNDATION-001"
    assert "gate_decision" in bundle