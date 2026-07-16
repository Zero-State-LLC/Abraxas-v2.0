from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from core.aal_viz_yggdrasil_topology_delta_intelligence import (
    YggdrasilTopologyDeltaIntelligenceError,
    evaluate_yggdrasil_topology_delta_intelligence,
    validate_yggdrasil_topology_delta_intelligence,
)
from scripts.operator.run_yggdrasil_topology_delta_intelligence import (
    main as runner_main,
)


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_PATH = ROOT / "out/projections/aal_viz_yggdrasil_topology_v1.latest.json"
INTEGRITY_PATH = (
    ROOT / "out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json"
)
SCHEMA_PATH = (
    ROOT
    / "contracts/canon/aal_viz_yggdrasil_topology_delta_intelligence.v1.schema.json"
)


def _load(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def _artifact(*, integrity: bool = True) -> dict[str, Any]:
    topology, topology_hash = _load(TOPOLOGY_PATH)
    integrity_artifact, integrity_hash = _load(INTEGRITY_PATH)
    return evaluate_yggdrasil_topology_delta_intelligence(
        topology,
        topology,
        prior_integrity=integrity_artifact if integrity else None,
        current_integrity=integrity_artifact if integrity else None,
        source_paths={
            "prior_topology": "out/projections/aal_viz_yggdrasil_topology_v1.latest.json",
            "current_topology": "out/projections/aal_viz_yggdrasil_topology_v1.latest.json",
            "prior_integrity": "out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json",
            "current_integrity": "out/projections/aal_viz_yggdrasil_topology_integrity_v1.latest.json",
            "temporal_diff": "out/projections/aal_viz_temporal_diff_v1.latest.json",
        },
        content_hashes={
            "prior_topology": topology_hash,
            "current_topology": topology_hash,
            "prior_integrity": integrity_hash if integrity else None,
            "current_integrity": integrity_hash if integrity else None,
            "temporal_diff": None,
        },
        generated_at="2026-07-15T00:00:00Z",
    )


def test_real_corpus_is_deterministic_and_schema_valid() -> None:
    first = _artifact()
    second = _artifact()
    assert first == second
    assert first["status"] == "PARTIAL"
    assert first["summary"]["finding_state_counts"] == {"PERSISTENT": 162}
    assert first["summary"]["structural_class_counts"] == {}
    assert first["summary"]["active_priority_count"] == 162
    validate_yggdrasil_topology_delta_intelligence(first, SCHEMA_PATH)


def test_fixed_epoch_is_byte_identical_across_roots_and_hash_seeds(
    tmp_path: Path,
) -> None:
    script = """
import hashlib, json
from pathlib import Path
from core.aal_viz_yggdrasil_topology_delta_intelligence import evaluate_yggdrasil_topology_delta_intelligence as evaluate
topology_raw = Path('topology.json').read_bytes()
integrity_raw = Path('integrity.json').read_bytes()
topology = json.loads(topology_raw)
integrity = json.loads(integrity_raw)
artifact = evaluate(
    topology, topology, prior_integrity=integrity, current_integrity=integrity,
    source_paths={
        'prior_topology': 'topology.json', 'current_topology': 'topology.json',
        'prior_integrity': 'integrity.json', 'current_integrity': 'integrity.json',
        'temporal_diff': 'temporal.json',
    },
    content_hashes={
        'prior_topology': hashlib.sha256(topology_raw).hexdigest(),
        'current_topology': hashlib.sha256(topology_raw).hexdigest(),
        'prior_integrity': hashlib.sha256(integrity_raw).hexdigest(),
        'current_integrity': hashlib.sha256(integrity_raw).hexdigest(),
        'temporal_diff': None,
    },
    generated_at='2026-07-15T00:00:00Z',
)
print(json.dumps(artifact, sort_keys=True, separators=(',', ':')))
"""
    outputs: list[str] = []
    for index, seed in enumerate(("1", "8675309")):
        root = tmp_path / f"root-{index}"
        root.mkdir()
        (root / "topology.json").write_bytes(TOPOLOGY_PATH.read_bytes())
        (root / "integrity.json").write_bytes(INTEGRITY_PATH.read_bytes())
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=root,
            env=os.environ
            | {
                "PYTHONHASHSEED": seed,
                "PYTHONPATH": str(ROOT),
                "SOURCE_DATE_EPOCH": "1784073600",
            },
            check=True,
            capture_output=True,
            text=True,
        )
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1]
    assert "research_canary" not in outputs[0]


def test_missing_integrity_is_explicitly_not_computable() -> None:
    artifact = _artifact(integrity=False)
    section = artifact["sections"]["finding_correlation"]
    assert artifact["status"] == "PARTIAL"
    assert section["status"] == "NOT_COMPUTABLE"
    assert section["entries"] is None
    assert artifact["summary"]["finding_state_counts"] == {}
    validate_yggdrasil_topology_delta_intelligence(artifact, SCHEMA_PATH)


def test_generation_mismatch_suppresses_optional_integrity() -> None:
    topology, topology_hash = _load(TOPOLOGY_PATH)
    integrity, integrity_hash = _load(INTEGRITY_PATH)
    stale = copy.deepcopy(integrity)
    stale["generation"]["topology_generation_id"] = "f" * 64
    artifact = evaluate_yggdrasil_topology_delta_intelligence(
        topology,
        topology,
        prior_integrity=stale,
        current_integrity=integrity,
        source_paths={
            "prior_topology": "out/prior.json",
            "current_topology": "out/current.json",
            "prior_integrity": "out/prior-integrity.json",
            "current_integrity": "out/current-integrity.json",
            "temporal_diff": "out/temporal.json",
        },
        content_hashes={
            "prior_topology": topology_hash,
            "current_topology": topology_hash,
            "prior_integrity": integrity_hash,
            "current_integrity": integrity_hash,
            "temporal_diff": None,
        },
        generated_at="2026-07-15T00:00:00Z",
    )
    assert artifact["sections"]["finding_correlation"]["status"] == "NOT_COMPUTABLE"
    assert any("mismatch" in item.lower() for item in artifact["validation_findings"])


def test_partial_topology_never_implies_no_structural_change() -> None:
    topology, topology_hash = _load(TOPOLOGY_PATH)
    partial = copy.deepcopy(topology)
    partial["status"] = "PARTIAL"
    artifact = evaluate_yggdrasil_topology_delta_intelligence(
        partial,
        topology,
        source_paths={
            "prior_topology": "out/prior.json",
            "current_topology": "out/current.json",
            "prior_integrity": "out/prior-integrity.json",
            "current_integrity": "out/current-integrity.json",
            "temporal_diff": "out/temporal.json",
        },
        content_hashes={
            "prior_topology": topology_hash,
            "current_topology": topology_hash,
            "prior_integrity": None,
            "current_integrity": None,
            "temporal_diff": None,
        },
        generated_at="2026-07-15T00:00:00Z",
    )
    assert artifact["sections"]["structural_deltas"]["status"] == "NOT_COMPUTABLE"
    assert artifact["sections"]["structural_deltas"]["entries"] is None
    assert artifact["sections"]["changed_paths"]["status"] == "NOT_COMPUTABLE"


def test_absolute_published_path_is_rejected() -> None:
    topology, topology_hash = _load(TOPOLOGY_PATH)
    with pytest.raises(
        YggdrasilTopologyDeltaIntelligenceError, match="repository-relative"
    ):
        evaluate_yggdrasil_topology_delta_intelligence(
            topology,
            topology,
            source_paths={
                "prior_topology": "/tmp/prior.json",
                "current_topology": "out/current.json",
                "prior_integrity": "out/prior-integrity.json",
                "current_integrity": "out/current-integrity.json",
                "temporal_diff": "out/temporal.json",
            },
            content_hashes={
                "prior_topology": topology_hash,
                "current_topology": topology_hash,
                "prior_integrity": None,
                "current_integrity": None,
                "temporal_diff": None,
            },
            generated_at="2026-07-15T00:00:00Z",
        )


def test_runner_requires_explicit_pair_and_rejects_traversal() -> None:
    with pytest.raises(SystemExit):
        runner_main([])
    assert (
        runner_main(
            [
                "--prior-topology",
                "../prior.json",
                "--current-topology",
                "out/current.json",
            ]
        )
        == 1
    )
def test_runner_rejects_temporal_authority_and_hash_violations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    topology, _ = _load(TOPOLOGY_PATH)
    temporal_fixture = json.loads(
        (ROOT / "tests/fixtures/aal_viz_temporal_diff_v1/valid_cases.json").read_text(
            encoding="utf-8"
        )
    )
    temporal = temporal_fixture["cases"][0]["artifact"]
    malformed = copy.deepcopy(temporal)
    malformed["authority"]["projection_only"] = False
    input_path = tmp_path / "temporal.json"
    input_path.write_text(json.dumps(malformed), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.operator.run_yggdrasil_topology_delta_intelligence.ROOT", tmp_path
    )
    monkeypatch.setattr(
        "scripts.operator.run_yggdrasil_topology_delta_intelligence.TOPOLOGY_SCHEMA",
        ROOT / "contracts/canon/aal_viz_yggdrasil_topology.v1.schema.json",
    )
    monkeypatch.setattr(
        "scripts.operator.run_yggdrasil_topology_delta_intelligence.TEMPORAL_SCHEMA",
        ROOT / "contracts/canon/aal_viz_temporal_diff.v1.schema.json",
    )
    (tmp_path / "prior.json").write_text(json.dumps(topology), encoding="utf-8")
    (tmp_path / "current.json").write_text(json.dumps(topology), encoding="utf-8")
    assert (
        runner_main(
            [
                "--prior-topology",
                "prior.json",
                "--current-topology",
                "current.json",
                "--temporal-diff",
                "temporal.json",
            ]
        )
        == 1
    )
    malformed["authority"]["projection_only"] = True
    malformed["canonical_hash"] = "f" * 64
    input_path.write_text(json.dumps(malformed), encoding="utf-8")
    assert (
        runner_main(
            [
                "--prior-topology",
                "prior.json",
                "--current-topology",
                "current.json",
                "--temporal-diff",
                "temporal.json",
            ]
        )
        == 1
    )
