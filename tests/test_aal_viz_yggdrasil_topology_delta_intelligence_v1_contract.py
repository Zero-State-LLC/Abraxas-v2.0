from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "contracts/canon/aal_viz_yggdrasil_topology_delta_intelligence.v1.schema.json"
)
FIXTURE_ROOT = ROOT / "tests/fixtures/aal_viz_yggdrasil_topology_delta_intelligence_v1"
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64

AUTHORITY = {
    "projection_only": True,
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "graph_driven_execution_allowed": False,
    "production_activation_allowed": False,
    "route_receipt_triggering_allowed": False,
    "scheduling_allowed": False,
    "alert_delivery_allowed": False,
    "acknowledgement_state_allowed": False,
    "browser_persistence_allowed": False,
    "automatic_remediation_allowed": False,
    "autonomous_escalation_allowed": False,
}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _typed_id(prefix: str, *identity: Any) -> str:
    return f"{prefix}:{_hash(list(identity))}"


def _delta_generation_id(artifact: dict[str, Any]) -> str:
    semantic = copy.deepcopy(artifact)
    semantic.pop("canonical_hash", None)
    semantic["generation"].pop("generated_at", None)
    semantic["generation"].pop("delta_generation_id", None)
    return _hash(semantic)


def _canonical_hash(artifact: dict[str, Any]) -> str:
    return _hash(
        {key: value for key, value in artifact.items() if key != "canonical_hash"}
    )


def _section(entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "status": "AVAILABLE",
        "provenance": "OBSERVED",
        "not_computable_reason": None,
        "validation_findings": [],
        "entries": [] if entries is None else entries,
    }


def _sources(*, optional: bool = True) -> list[dict[str, Any]]:
    records = [
        ("current_integrity", "out/projections/current_integrity.json", optional),
        ("current_topology", "out/projections/current_topology.json", True),
        ("prior_integrity", "out/projections/prior_integrity.json", optional),
        ("prior_topology", "out/projections/prior_topology.json", True),
        ("temporal_diff", "out/projections/temporal_diff.json", optional),
    ]
    return [
        {
            "id": f"source:{key}",
            "source_key": key,
            "path": path,
            "declared_canonical_hash": HASH_A if available else None,
            "content_sha256": HASH_B if available else None,
            "integrity_state": "VERIFIED" if available else "NOT_COMPUTABLE",
        }
        for key, path, available in records
    ]


def _correlation(
    finding_type: str,
    entity_id: str,
    state: str,
    prior_id: str | None,
    current_id: str | None,
    severity: str,
) -> dict[str, Any]:
    key = _typed_id("correlation", finding_type, "TOPOLOGY_NODE", entity_id, entity_id)
    return {
        "id": key,
        "correlation_key": key,
        "state": state,
        "correlation_state": "CHANGE_CORRELATED",
        "prior_finding_id": prior_id,
        "current_finding_id": current_id,
        "entity_ref": {"category": "TOPOLOGY_NODE", "entity_id": entity_id},
        "subject_key": entity_id,
        "prior_severity": severity if prior_id else None,
        "current_severity": severity if current_id else None,
        "severity_change": "UNCHANGED" if state == "PERSISTENT" else "NOT_COMPUTABLE",
        "provenance": "INFERRED",
        "confidence": "SUPPORTED",
        "supporting_entity_ids": [entity_id],
        "supporting_temporal_entry_ids": [],
        "observed_generation_count": 2 if state == "PERSISTENT" else 1,
        "persistence_seconds_lower_bound": 86400 if state == "PERSISTENT" else None,
        "true_age_status": "NOT_COMPUTABLE",
        "evidence_refs": ["source:current_integrity", "source:prior_integrity"],
    }


def _structural(structural_class: str, entity_id: str) -> dict[str, Any]:
    return {
        "id": _typed_id("structural", structural_class, entity_id),
        "structural_class": structural_class,
        "entity_refs": [{"category": "TOPOLOGY_NODE", "entity_id": entity_id}],
        "prior_value": False,
        "current_value": True,
        "provenance": "OBSERVED",
        "confidence": "VERIFIED",
        "reason": f"Deterministic {structural_class.lower()} rule matched.",
        "evidence_refs": ["source:current_topology", "source:prior_topology"],
        "computability": "COMPUTABLE",
    }


def _priority(source_id: str, structural_id: str) -> dict[str, Any]:
    breakdown = {
        "severity": 25,
        "structural": 25,
        "operational_surfaces": 8,
        "persistence": 5,
        "confidence": 5,
    }
    return {
        "id": _typed_id("priority", structural_id),
        "rank": 1,
        "source_ref": {"category": "STRUCTURAL_DELTA", "entity_id": structural_id},
        "score": sum(breakdown.values()),
        "score_breakdown": breakdown,
        "severity": "MEDIUM",
        "structural_classes": ["ORPHANED_CONTRACT"],
        "confidence": "VERIFIED",
        "evidence_count": 2,
        "affected_surface_ids": [source_id],
        "why_this_matters": "The contract no longer has complete operational coverage.",
        "evidence_refs": ["source:current_topology", "source:prior_topology"],
    }


def _base() -> dict[str, Any]:
    artifact: dict[str, Any] = {
        "schema_version": "AALViz.YggdrasilTopologyDeltaIntelligence.v1",
        "generation": {
            "generated_at": "2026-07-15T00:00:00Z",
            "generated_by": "YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_001",
            "delta_generation_id": "0" * 64,
            "prior_topology_generation_id": HASH_A,
            "current_topology_generation_id": HASH_B,
            "prior_operator_platform_generation_id": HASH_C,
            "current_operator_platform_generation_id": HASH_D,
            "prior_integrity_generation_id": HASH_A,
            "current_integrity_generation_id": HASH_B,
            "temporal_diff_generation_id": HASH_D,
        },
        "status": "AVAILABLE",
        "provenance": "INFERRED",
        "source_artifacts": _sources(),
        "sections": {
            "finding_correlation": _section(),
            "structural_deltas": _section(),
            "changed_paths": _section(),
            "review_priorities": _section(),
        },
        "summary": {
            "finding_state_counts": {},
            "structural_class_counts": {},
            "changed_path_count": 0,
            "active_priority_count": 0,
            "not_computable_count": 0,
            "highest_score": None,
        },
        "authority": copy.deepcopy(AUTHORITY),
        "validation_findings": [],
        "canonical_hash": "0" * 64,
    }
    return _finalize(artifact)


def _summary(artifact: dict[str, Any]) -> None:
    correlations = artifact["sections"]["finding_correlation"]["entries"] or []
    structural = artifact["sections"]["structural_deltas"]["entries"] or []
    paths = artifact["sections"]["changed_paths"]["entries"] or []
    priorities = artifact["sections"]["review_priorities"]["entries"] or []
    artifact["summary"] = {
        "finding_state_counts": dict(
            sorted(Counter(entry["state"] for entry in correlations).items())
        ),
        "structural_class_counts": dict(
            sorted(Counter(entry["structural_class"] for entry in structural).items())
        ),
        "changed_path_count": len(paths),
        "active_priority_count": len(priorities),
        "not_computable_count": sum(
            section["status"] == "NOT_COMPUTABLE"
            for section in artifact["sections"].values()
        ),
        "highest_score": max((entry["score"] for entry in priorities), default=None),
    }


def _finalize(artifact: dict[str, Any]) -> dict[str, Any]:
    _summary(artifact)
    artifact["generation"]["delta_generation_id"] = _delta_generation_id(artifact)
    artifact["canonical_hash"] = _canonical_hash(artifact)
    return artifact


def _artifact(scenario: str) -> dict[str, Any]:
    artifact = _base()
    if scenario == "NO_CHANGE":
        return artifact
    if scenario == "FINDING_CORRELATION":
        records = [
            _correlation(
                "MISSING_EVIDENCE",
                "node:new",
                "NEW",
                None,
                "finding:" + "1" * 64,
                "LOW",
            ),
            _correlation(
                "UNRESOLVED_ENTITY",
                "node:persistent",
                "PERSISTENT",
                "finding:" + "2" * 64,
                "finding:" + "3" * 64,
                "MEDIUM",
            ),
            _correlation(
                "STALE_ENTITY",
                "node:resolved",
                "RESOLVED",
                "finding:" + "4" * 64,
                None,
                "MEDIUM",
            ),
        ]
        artifact["sections"]["finding_correlation"]["entries"] = sorted(
            records, key=lambda entry: entry["id"]
        )
    elif scenario == "STRUCTURAL_CLASSES":
        classes = [
            "ISOLATED_NODE_EMERGENCE",
            "ORPHANED_CONTRACT",
            "VALIDATOR_COVERAGE_LOSS",
            "BROKEN_PRODUCER_CONSUMER_PATH",
            "OWNERSHIP_DRIFT",
            "STALE_EVIDENCE_CHAIN",
            "TOPOLOGY_FRAGMENTATION",
            "UNEXPECTED_CLUSTER_FUSION",
        ]
        records = [
            _structural(value, f"node:{index}") for index, value in enumerate(classes)
        ]
        artifact["sections"]["structural_deltas"]["entries"] = sorted(
            records, key=lambda entry: entry["id"]
        )
        orphan = next(
            entry
            for entry in records
            if entry["structural_class"] == "ORPHANED_CONTRACT"
        )
        artifact["sections"]["review_priorities"]["entries"] = [
            _priority("system:aal_viz", orphan["id"])
        ]
    elif scenario in {"PARTIAL", "GENERATION_MISMATCH"}:
        artifact["status"] = "PARTIAL"
        artifact["generation"]["prior_integrity_generation_id"] = None
        artifact["generation"]["current_integrity_generation_id"] = None
        artifact["generation"]["temporal_diff_generation_id"] = None
        artifact["source_artifacts"] = _sources(optional=False)
        section = artifact["sections"]["finding_correlation"]
        section.update(
            {
                "status": "NOT_COMPUTABLE",
                "entries": None,
                "not_computable_reason": "Optional integrity evidence is unavailable.",
            }
        )
        if scenario == "GENERATION_MISMATCH":
            artifact["validation_findings"] = [
                "Optional generation bindings do not match and were suppressed."
            ]
    return _finalize(artifact)


def _semantic_errors(artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        errors.append("canonical hash mismatch")
    if artifact.get("generation", {}).get(
        "delta_generation_id"
    ) != _delta_generation_id(artifact):
        errors.append("delta generation id mismatch")
    sources = artifact.get("source_artifacts", [])
    source_ids = {source.get("id") for source in sources}
    if sources != sorted(sources, key=lambda source: source.get("id", "")):
        errors.append("source artifacts not canonically ordered")
    if artifact.get("validation_findings") != sorted(
        artifact.get("validation_findings", [])
    ):
        errors.append("validation findings not canonically ordered")
    all_ids: set[str] = set()
    sections = artifact.get("sections", {})
    for name, section in sections.items():
        entries = section.get("entries")
        if section.get("status") == "NOT_COMPUTABLE":
            if entries is not None or not section.get("not_computable_reason"):
                errors.append(f"{name} NOT_COMPUTABLE envelope mismatch")
            continue
        if entries is None or section.get("not_computable_reason") is not None:
            errors.append(f"{name} available envelope mismatch")
            continue
        ids = [entry.get("id") for entry in entries]
        if ids != sorted(ids) and name != "review_priorities":
            errors.append(f"{name} not canonically ordered")
        if len(ids) != len(set(ids)):
            errors.append(
                "duplicate correlation id"
                if name == "finding_correlation"
                else f"duplicate {name} id"
            )
        all_ids.update(str(value) for value in ids)
        for entry in entries:
            if entry.get("evidence_refs") != sorted(entry.get("evidence_refs", [])):
                errors.append("evidence references not canonically ordered")
            if any(
                reference not in source_ids
                for reference in entry.get("evidence_refs", [])
            ):
                errors.append("dangling evidence reference")
    correlations = sections.get("finding_correlation", {}).get("entries") or []
    complete_integrity = all(
        next((source for source in sources if source.get("source_key") == key), {}).get(
            "integrity_state"
        )
        == "VERIFIED"
        for key in ("prior_integrity", "current_integrity")
    )
    if (
        any(entry.get("state") == "RESOLVED" for entry in correlations)
        and not complete_integrity
    ):
        errors.append("resolution without complete evidence")
    paths = sections.get("changed_paths", {}).get("entries") or []
    topology_complete = artifact.get("status") == "AVAILABLE" and all(
        next((source for source in sources if source.get("source_key") == key), {}).get(
            "integrity_state"
        )
        == "VERIFIED"
        for key in ("prior_topology", "current_topology")
    )
    if (
        any(entry.get("change") == "REMOVED" for entry in paths)
        and not topology_complete
    ):
        errors.append("path removal without complete evidence")
    priorities = sections.get("review_priorities", {}).get("entries") or []
    expected_order = sorted(
        priorities,
        key=lambda item: (
            -item.get("score", 0),
            -{"HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}.get(item.get("severity"), 0),
            -item.get("evidence_count", 0),
            item.get("id", ""),
        ),
    )
    if priorities != expected_order or [
        item.get("rank") for item in priorities
    ] != list(range(1, len(priorities) + 1)):
        errors.append("review priorities not canonically ordered")
    for item in priorities:
        if item.get("score") != sum(item.get("score_breakdown", {}).values()):
            errors.append("score arithmetic mismatch")
        if item.get("source_ref", {}).get("entity_id") not in all_ids:
            errors.append("dangling priority source")
    generation = artifact.get("generation", {})
    if (
        generation.get("prior_integrity_generation_id") is not None
        and not complete_integrity
    ):
        errors.append("generation binding mismatch")
    return errors


def _rehash(artifact: dict[str, Any]) -> None:
    artifact["generation"]["delta_generation_id"] = _delta_generation_id(artifact)
    artifact["canonical_hash"] = _canonical_hash(artifact)


def _invalid_artifact(mutation: str) -> dict[str, Any]:
    artifact = _artifact(
        "STRUCTURAL_CLASSES"
        if mutation in {"DANGLING_REFERENCE", "SCORE"}
        else "FINDING_CORRELATION"
    )
    if mutation == "AUTHORITY":
        artifact["authority"]["projection_only"] = False
    elif mutation == "CANONICAL_HASH":
        artifact["canonical_hash"] = "0" * 64
    elif mutation == "ABSOLUTE_PATH":
        artifact["source_artifacts"][0]["path"] = "/tmp/input.json"
    elif mutation == "DUPLICATE_ID":
        artifact["sections"]["finding_correlation"]["entries"].append(
            copy.deepcopy(artifact["sections"]["finding_correlation"]["entries"][0])
        )
    elif mutation == "DANGLING_REFERENCE":
        artifact["sections"]["review_priorities"]["entries"][0]["source_ref"][
            "entity_id"
        ] = "structural:missing"
    elif mutation == "ENUM":
        artifact["sections"]["finding_correlation"]["entries"][0]["state"] = "UNKNOWN"
    elif mutation == "ORDER":
        artifact["sections"]["finding_correlation"]["entries"].reverse()
    elif mutation == "SCORE":
        artifact["sections"]["review_priorities"]["entries"][0]["score"] += 1
    elif mutation == "FALSE_RESOLUTION":
        artifact["status"] = "PARTIAL"
        for source in artifact["source_artifacts"]:
            if source["source_key"] == "current_integrity":
                source.update(
                    {
                        "integrity_state": "NOT_COMPUTABLE",
                        "declared_canonical_hash": None,
                        "content_sha256": None,
                    }
                )
    elif mutation == "FALSE_PATH":
        artifact["status"] = "PARTIAL"
        artifact["source_artifacts"][1].update(
            {
                "integrity_state": "NOT_COMPUTABLE",
                "declared_canonical_hash": None,
                "content_sha256": None,
            }
        )
        path = {
            "id": _typed_id("path", "a", "b"),
            "source_id": "a",
            "target_id": "b",
            "change": "REMOVED",
            "prior_node_ids": ["a", "b"],
            "prior_edge_ids": ["edge:a:b"],
            "current_node_ids": [],
            "current_edge_ids": [],
            "evidence_refs": ["source:prior_topology"],
        }
        artifact["sections"]["changed_paths"]["entries"] = [path]
    elif mutation == "BINDING":
        for source in artifact["source_artifacts"]:
            if source["source_key"] == "prior_integrity":
                source.update(
                    {
                        "integrity_state": "NOT_COMPUTABLE",
                        "declared_canonical_hash": None,
                        "content_sha256": None,
                    }
                )
    if mutation != "CANONICAL_HASH":
        _rehash(artifact)
    return artifact


def test_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_fixed_identity_vectors() -> None:
    assert (
        _typed_id(
            "correlation",
            "UNRESOLVED_ENTITY",
            "TOPOLOGY_NODE",
            "node:example",
            "node:example",
        )
        == "correlation:d0fa1cbf50a3716cdfa1d09a986c69ea2b464ec061e22bd9055e65a22eef8b56"
    )
    assert (
        _typed_id("structural", "ORPHANED_CONTRACT", "contract:example")
        == "structural:514e45e4908ed0a3ba2df82572922bf808469b8041cb416898f4614c1003e609"
    )


def test_valid_contract_fixtures_and_fixed_hash_vector() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    fixture = json.loads(
        (FIXTURE_ROOT / "valid_cases.json").read_text(encoding="utf-8")
    )
    artifacts = []
    for case in fixture["cases"]:
        artifact = _artifact(case["scenario"])
        validator.validate(artifact)
        assert not _semantic_errors(artifact), case["name"]
        artifacts.append(artifact)
    assert (
        artifacts[0]["canonical_hash"]
        == "fd0ed77a110922f9c493c04018fede47fa61c4af8ae9d38dda46385b48951612"
    )


def test_invalid_contract_fixtures_fail_for_expected_reason() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    fixture = json.loads(
        (FIXTURE_ROOT / "invalid_cases.json").read_text(encoding="utf-8")
    )
    for case in fixture["cases"]:
        artifact = _invalid_artifact(case["mutation"])
        rendered = " | ".join(
            [
                *(error.message for error in validator.iter_errors(artifact)),
                *_semantic_errors(artifact),
            ]
        )
        assert case["expected_error"] in rendered, (case["name"], rendered)
