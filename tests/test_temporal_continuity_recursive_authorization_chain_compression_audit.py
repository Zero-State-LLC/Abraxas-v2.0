from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_dumps
from core.generated_artifact_registry import build_generated_artifact_registry
from core.temporal_continuity_recursive_authorization_chain_compression_audit import (
    _CHAIN_ARTIFACT_SPECS,
    _GOVERNANCE_LOCK_FIELDS,
    EXPECTED_LATEST_REQUIRED_NEXT_LANE,
    EXPECTED_LATEST_REQUIRED_STATUS,
    LATEST_REQUIRED_SOURCE_PATH,
    build_temporal_continuity_recursive_authorization_chain_compression_audit,
    write_temporal_continuity_recursive_authorization_chain_compression_audit,
)
from scripts.temporal import run_temporal_continuity_recursive_authorization_chain_compression_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = (
    "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json"
)



def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )



def _status_for_mode(index: int, *, mode: str) -> tuple[str, str]:
    if index == len(_CHAIN_ARTIFACT_SPECS) - 1:
        return EXPECTED_LATEST_REQUIRED_STATUS, EXPECTED_LATEST_REQUIRED_NEXT_LANE
    if mode == "seal":
        return ("CHAIN_READY", "P999_REGENERATION")
    if mode == "compress":
        if index < 12:
            return ("CHAIN_READY", "P999_REGENERATION")
        variants = (
            ("CHAIN_BLOCKED", "P999_AUTHORIZATION_GATE"),
            ("CHAIN_DENIED", "P999_RECORD_PLAN"),
            ("CHAIN_NOT_REQUIRED", "P999_EXECUTION_PLAN"),
        )
        return variants[index - 12]
    if mode == "continue":
        variants = (
            ("CHAIN_READY", f"P999_PLAN_{index}"),
            ("CHAIN_BLOCKED", f"P999_GATE_{index}"),
            ("CHAIN_DENIED", f"P999_RECORD_{index}"),
            ("CHAIN_OTHER", f"P999_ROUTE_{index}"),
        )
        return variants[index % len(variants)]
    return ("NOT_COMPUTABLE", "P999_REGENERATION")



def _payload_for_spec(
    spec: dict[str, str],
    index: int,
    *,
    mode: str,
    latest_eligible: bool,
    include_inherited: bool = False,
) -> dict[str, object]:
    status_value, next_lane = _status_for_mode(index, mode=mode)
    repeated_shape = {
        "blockers": ["repeat"],
        "governance": {"locks": list(_GOVERNANCE_LOCK_FIELDS)},
        "summary": {"kind": "repeat"},
    }
    unique_shape = {
        f"shape_{index}": {"nested": [index, f"value_{index}"]},
        "summary": {"kind": f"unique_{index}"},
    }
    payload: dict[str, object] = {
        "artifact_type": f"Synthetic.{spec['artifact_id']}.v1",
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        spec["status_field"]: status_value,
        "recommended_next_lane": next_lane,
        "shared_shape": repeated_shape if mode in {"seal", "compress"} else unique_shape,
        "degraded_evidence_inputs": [],
        "inherited_blockers": [],
        "inherited_drift_flags": [],
        "semantic_overlap_flags": [],
    }
    for field in _GOVERNANCE_LOCK_FIELDS:
        payload[field] = False
    if spec["path"] == LATEST_REQUIRED_SOURCE_PATH:
        payload["p83_sequence_record_creation_record_creation_authorization_eligible"] = (
            latest_eligible
        )
        payload["degraded_evidence_inputs"] = ["degraded-z", "degraded-a"]
        payload["inherited_blockers"] = ["blocker-z", "blocker-a"]
        payload["inherited_drift_flags"] = ["drift-z", "drift-a"]
        payload["semantic_overlap_flags"] = ["semantic-z", "semantic-a"]
        if include_inherited:
            payload["degraded_evidence_inputs"] = ["e3", {"nested": [2, 1]}, "e1"]
            payload["inherited_blockers"] = ["b3", {"nested": ["y", "x"]}, "b1"]
            payload["inherited_drift_flags"] = ["d3", {"nested": [True, False]}, "d1"]
            payload["semantic_overlap_flags"] = ["s3", {"nested": ["n2", "n1"]}, "s1"]
    return payload



def _seed_chain(
    root: Path,
    *,
    readable_indexes: set[int],
    mode: str,
    latest_eligible: bool = True,
    malformed_latest: bool = False,
    include_inherited: bool = False,
    reverse_write_order: bool = False,
) -> None:
    specs = list(_CHAIN_ARTIFACT_SPECS)
    if reverse_write_order:
        specs = list(reversed(specs))
    for spec in specs:
        index = next(
            idx for idx, candidate in enumerate(_CHAIN_ARTIFACT_SPECS) if candidate["path"] == spec["path"]
        )
        if index not in readable_indexes:
            continue
        target = root / spec["path"]
        if malformed_latest and spec["path"] == LATEST_REQUIRED_SOURCE_PATH:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{bad", encoding="utf-8")
            continue
        payload = _payload_for_spec(
            spec,
            index,
            mode=mode,
            latest_eligible=latest_eligible,
            include_inherited=include_inherited,
        )
        _write_json(target, payload)



def _build(root: Path) -> dict[str, object]:
    return build_temporal_continuity_recursive_authorization_chain_compression_audit(
        repo_root=root
    )


# 1

def test_missing_latest_p101_source_returns_not_computable(tmp_path: Path) -> None:
    packet = _build(tmp_path)
    assert packet["chain_compression_audit_status"] == "NOT_COMPUTABLE"
    assert packet["chain_recommendation"] == "NOT_COMPUTABLE"
    assert (
        packet["recommended_next_lane"]
        == "P101_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"
    )


# 2

def test_malformed_latest_p101_source_returns_not_computable(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes={len(_CHAIN_ARTIFACT_SPECS) - 1},
        mode="seal",
        malformed_latest=True,
    )
    packet = _build(tmp_path)
    assert packet["chain_compression_audit_status"] == "NOT_COMPUTABLE"
    assert packet["chain_recommendation"] == "NOT_COMPUTABLE"
    assert LATEST_REQUIRED_SOURCE_PATH in packet["malformed_artifacts"]


# 3

def test_p101_not_eligible_routes_to_degraded_regeneration(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes={len(_CHAIN_ARTIFACT_SPECS) - 1},
        mode="seal",
        latest_eligible=False,
    )
    packet = _build(tmp_path)
    assert packet["chain_compression_audit_status"] == "COMPRESSION_AUDIT_DEGRADED"
    assert packet["chain_recommendation"] == "NOT_COMPUTABLE"
    assert (
        packet["recommended_next_lane"]
        == "P101_SEQUENCE_RECORD_CREATION_RECORD_CREATION_AUTHORIZATION_GATE_REGENERATION"
    )


# 4

def test_p101_eligible_but_fewer_than_8_readable_returns_degraded(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes={0, 1, 2, 3, 4, 5, 15}, mode="seal")
    packet = _build(tmp_path)
    assert packet["chain_compression_audit_status"] == "COMPRESSION_AUDIT_DEGRADED"
    assert packet["chain_recommendation"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "P86_TO_P101_CHAIN_EVIDENCE_RESTORATION_PLAN"


# 5

def test_p101_eligible_and_enough_readable_returns_ready(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="continue")
    packet = _build(tmp_path)
    assert packet["chain_compression_audit_status"] == "COMPRESSION_AUDIT_READY"
    assert packet["structural_repetition_metrics"]["readable_artifact_count"] == 16


# 6

def test_high_repetition_low_unique_signal_chooses_compress(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="compress")
    packet = _build(tmp_path)
    assert packet["chain_recommendation"] == "COMPRESS_TO_GENERIC_TEMPLATE"
    assert (
        packet["recommended_next_lane"]
        == "P103_TEMPORAL_CONTINUITY_GENERIC_AUTHORIZATION_LANE_TEMPLATE_PLAN"
    )


# 7

def test_extreme_repetition_chooses_seal(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet = _build(tmp_path)
    assert packet["chain_recommendation"] == "SEAL_RECURSIVE_AUTHORIZATION_CHAIN"
    assert (
        packet["recommended_next_lane"]
        == "P103_TEMPORAL_CONTINUITY_RECURSIVE_AUTHORIZATION_CHAIN_SEAL_RECEIPT"
    )


# 8

def test_lower_repetition_chooses_continue(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="continue")
    packet = _build(tmp_path)
    assert packet["chain_recommendation"] == "CONTINUE_RECURSION"
    assert (
        packet["recommended_next_lane"]
        == "P103_TEMPORAL_CONTINUITY_RECURSION_CONTINUATION_PLAN"
    )


# 9

def test_seal_beats_compress_if_both_thresholds_pass(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet = _build(tmp_path)
    metrics = packet["structural_repetition_metrics"]
    assert metrics["repeated_authority_lock_ratio"] >= 0.8
    assert metrics["repeated_status_rule_ratio"] >= 0.7
    assert metrics["repeated_output_shape_ratio"] >= 0.7
    assert packet["chain_recommendation"] == "SEAL_RECURSIVE_AUTHORIZATION_CHAIN"


# 10

def test_inspected_artifacts_ordered_deterministically(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes={1, 4, 7, 15},
        mode="seal",
        reverse_write_order=True,
    )
    packet = _build(tmp_path)
    paths = [item["path"] for item in packet["inspected_artifacts"]]
    assert paths == sorted(paths)


# 11

def test_missing_artifacts_ordered_deterministically(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes={15, 0, 8}, mode="seal", reverse_write_order=True)
    packet = _build(tmp_path)
    missing_paths = packet["missing_artifacts"]
    assert missing_paths == sorted(missing_paths)


# 12

def test_repeated_lane_archetypes_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet = _build(tmp_path)
    archetypes = [item["archetype"] for item in packet["repeated_lane_archetypes"]]
    assert archetypes == sorted(archetypes)


# 13

def test_repeated_governance_locks_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet = _build(tmp_path)
    fields = [item["field"] for item in packet["repeated_governance_locks"]]
    assert fields == sorted(fields)


# 14

def test_repeated_routing_patterns_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="compress")
    packet = _build(tmp_path)
    pattern_ids = [item["pattern_id"] for item in packet["repeated_routing_patterns"]]
    assert pattern_ids == sorted(pattern_ids)


# 15

def test_repeated_artifact_shapes_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet = _build(tmp_path)
    shape_ids = [item["shape_id"] for item in packet["repeated_artifact_shapes"]]
    assert shape_ids == sorted(shape_ids)


# 16

def test_compression_findings_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet = _build(tmp_path)
    finding_ids = [item["finding_id"] for item in packet["compression_findings"]]
    assert finding_ids == sorted(finding_ids)


# 17

def test_reusable_lane_templates_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="compress")
    packet = _build(tmp_path)
    template_ids = [item["template_id"] for item in packet["reusable_lane_templates"]]
    assert template_ids == sorted(template_ids)


# 18

def test_implementation_authority_false_for_every_template(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="compress")
    packet = _build(tmp_path)
    assert packet["reusable_lane_templates"]
    assert all(
        template["implementation_authority"] is False
        for template in packet["reusable_lane_templates"]
    )


# 19

def test_all_authority_fields_false(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="continue")
    packet = _build(tmp_path)
    assert all(packet[field] is False for field in _GOVERNANCE_LOCK_FIELDS)


# 20

def test_inherited_degraded_evidence_preserved_exactly(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes=set(range(16)),
        mode="continue",
        include_inherited=True,
    )
    packet = _build(tmp_path)
    assert packet["degraded_evidence_inputs"] == ["e3", {"nested": [2, 1]}, "e1"]


# 21

def test_inherited_blockers_preserved_exactly(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes=set(range(16)),
        mode="continue",
        include_inherited=True,
    )
    packet = _build(tmp_path)
    assert packet["inherited_blockers"] == ["b3", {"nested": ["y", "x"]}, "b1"]


# 22

def test_inherited_drift_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes=set(range(16)),
        mode="continue",
        include_inherited=True,
    )
    packet = _build(tmp_path)
    assert packet["inherited_drift_flags"] == ["d3", {"nested": [True, False]}, "d1"]


# 23

def test_semantic_overlap_flags_preserved_exactly(tmp_path: Path) -> None:
    _seed_chain(
        tmp_path,
        readable_indexes=set(range(16)),
        mode="continue",
        include_inherited=True,
    )
    packet = _build(tmp_path)
    assert packet["semantic_overlap_flags"] == ["s3", {"nested": ["n2", "n1"]}, "s1"]


# 24

def test_packet_hash_deterministic(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="seal")
    packet_a = _build(tmp_path)
    packet_b = _build(tmp_path)
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert packet_a == packet_b


# 25

def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="compress")
    packet = _build(tmp_path)
    output_path = tmp_path / OUT_PATH
    write_temporal_continuity_recursive_authorization_chain_compression_audit(
        output_path, packet
    )
    text = output_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert text == canonical_dumps(packet) + "\n"


# 26

def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_chain(tmp_path, readable_indexes=set(range(16)), mode="continue")
    run_temporal_continuity_recursive_authorization_chain_compression_audit.run(
        repo_root=tmp_path
    )
    assert (tmp_path / OUT_PATH).exists()


# 27

def test_artifact_registry_classifies_output_as_derived_optional_and_not_ci_drift() -> None:
    registry = build_generated_artifact_registry(repo_root=REPO_ROOT)
    entry = next(item for item in registry.entries if item.artifact_path == OUT_PATH)
    source = registry.artifact_source_map[OUT_PATH]
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert source["ci_drift_enforced"] is False


# 28

def test_readme_agents_and_plans_include_p102_handoff_and_stop_guidance() -> None:
    required_strings = [
        "python scripts/temporal/run_temporal_continuity_recursive_authorization_chain_compression_audit.py",
        "out/temporal_continuity_recursive_authorization_chain_compression_audit/latest.json",
        "SEAL_RECURSIVE_AUTHORIZATION_CHAIN",
        "COMPRESS_TO_GENERIC_TEMPLATE",
        "do not add another hand-written recursive authorization lane",
    ]
    for rel_path in ("README.md", "AGENTS.md", "PLANS.md"):
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        for value in required_strings:
            assert value in text


# 29

def test_no_p103_implementation_added_by_this_pr() -> None:
    forbidden = []
    for pattern in (
        "core/*p103*",
        "scripts/run_*p103*",
        "tests/test_*p103*",
        "contracts/canon/*p103*",
    ):
        forbidden.extend(path.as_posix() for path in REPO_ROOT.glob(pattern))
    assert forbidden == []
