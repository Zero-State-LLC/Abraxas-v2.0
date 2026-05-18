from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.motif_governance_audit import (
    build_motif_governance_audit_receipt,
    write_motif_governance_audit_receipt,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing_p36: bool = False, corrupt_p37: bool = False) -> dict[str, str]:
    p36 = {
        "motif_catalog": [{"motif_id": "motif.blocker_class.abc", "motif_class": "BLOCKER_CLASS", "motif_label": "queue lag", "normalized_token": "queue lag", "observed_count": 1, "source_surfaces": ["s"], "evidence_refs": ["e1"], "motif_hash": ""}],
        "motif_class_counts": {"BLOCKER_CLASS": 1},
        "motif_evidence_refs": ["e1"],
        "source_hash_lineage": {"x": "h"},
        "governance_flags": {"advisory_only": True, "projection_only": True, "non_authoritative": True, "authority_granted": False, "mutation_allowed": False, "execution_authority": False, "forecast_authority": False, "readiness_claims_allowed": False, "motif_learning_authority": False, "adaptive_ontology_mutation_allowed": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False, "runtime_mutation_allowed": False, "ui_command_authority": False, "command_channel": False, "bidirectional_control": False},
    }
    from core.canonical.json import canonical_hash
    p36["motif_catalog"][0]["motif_hash"] = canonical_hash({k: v for k, v in p36["motif_catalog"][0].items() if k != "motif_hash"})
    p36["registry_hash"] = canonical_hash(p36)

    p37 = {
        "overlay_nodes": [{"node_id": "n1", "motif_id": "motif.blocker_class.abc", "motif_class": "BLOCKER_CLASS"}],
        "overlay_cards": [{"card_id": "c1", "motif_id": "motif.blocker_class.abc", "motif_class": "BLOCKER_CLASS"}],
        "overlay_badges": [{"badge_id": "b1", "motif_class": "BLOCKER_CLASS"}],
        "source_hash_lineage": {"x": "h"},
        "governance_flags": deepcopy(p36["governance_flags"]),
    }
    p37["overlay_hash"] = canonical_hash(p37)

    src = {"pressure_motif_registry": tmp_path / "p36.json", "aal_viz_pressure_motif_overlay": tmp_path / "p37.json"}
    if not missing_p36:
        _write(src["pressure_motif_registry"], p36)
    if corrupt_p37:
        src["aal_viz_pressure_motif_overlay"].write_text("{", encoding="utf-8")
    else:
        _write(src["aal_viz_pressure_motif_overlay"], p37)
    return {k: v.as_posix() for k, v in src.items()}


def test_pass_and_stable_hash(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_motif_governance_audit_receipt(source_artifact_paths=src)
    b = build_motif_governance_audit_receipt(source_artifact_paths=src)
    assert a["final_status"] == "PASS"
    assert a["audit_hash"] == b["audit_hash"]


def test_missing_p36_not_computable(tmp_path: Path) -> None:
    assert build_motif_governance_audit_receipt(source_artifact_paths=_sources(tmp_path, missing_p36=True))["final_status"] == "NOT_COMPUTABLE"


def test_corrupt_p37_not_computable(tmp_path: Path) -> None:
    assert build_motif_governance_audit_receipt(source_artifact_paths=_sources(tmp_path, corrupt_p37=True))["final_status"] == "NOT_COMPUTABLE"


def test_unknown_motif_and_governance_and_class_and_counts_fail() -> None:
    p36 = {"motif_catalog": [{"motif_id": "motif.x", "motif_class": "BAD_CLASS", "motif_label": "x", "normalized_token": "x", "observed_count": 1, "source_surfaces": [], "evidence_refs": ["e2"], "motif_hash": "bad"}], "motif_class_counts": {"BLOCKER_CLASS": 1}, "motif_evidence_refs": ["e3", "e2"], "source_hash_lineage": {}, "governance_flags": {"advisory_only": True, "projection_only": True, "non_authoritative": True, "authority_granted": True}}
    p37 = {"overlay_nodes": [{"motif_id": "motif.unknown", "motif_class": "UNKNOWN"}], "overlay_cards": [], "overlay_badges": [], "governance_flags": {"advisory_only": False, "projection_only": True, "non_authoritative": True}}
    r = build_motif_governance_audit_receipt(source_packets={"pressure_motif_registry": p36, "aal_viz_pressure_motif_overlay": p37}, source_artifact_paths={})
    assert r["final_status"] == "FAIL"


def test_findings_sorted_and_writer_newline_and_inputs_not_mutated(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    r = build_motif_governance_audit_receipt(source_artifact_paths=src)
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    sorted_findings = sorted(r["findings"], key=lambda x: (order.get(str(x["severity"]), 9), str(x["category"]), str(x["finding_id"])))
    assert r["findings"] == sorted_findings
    out = tmp_path / "a.json"
    write_motif_governance_audit_receipt(out, r)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    packets = {"pressure_motif_registry": {"motif_catalog": [], "motif_class_counts": {}, "motif_evidence_refs": [], "source_hash_lineage": {}, "governance_flags": {"advisory_only": True, "projection_only": True, "non_authoritative": True}}, "aal_viz_pressure_motif_overlay": {"overlay_nodes": [], "overlay_cards": [], "overlay_badges": [], "governance_flags": {"advisory_only": True, "projection_only": True, "non_authoritative": True}}}
    before = deepcopy(packets)
    build_motif_governance_audit_receipt(source_packets=packets, source_artifact_paths={})
    assert packets == before


def test_schema_and_registry_classification() -> None:
    schema = json.loads(Path("contracts/operator_attention/motif_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "MotifGovernanceAudit.v1"
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/audit/motif_governance_audit_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/audit/motif_governance_audit_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
