from __future__ import annotations

from pathlib import Path

import pytest

from core.generated_artifact_registry import (
    GeneratedArtifactEntry,
    GeneratedArtifactRegistry,
    execute_artifact_regeneration,
)
from scripts import run_artifact_regeneration


def _registry_for(entries: list[GeneratedArtifactEntry]) -> GeneratedArtifactRegistry:
    return GeneratedArtifactRegistry(
        entries=entries,
        dependency_edges=[],
        artifact_source_map={entry.artifact_path: {} for entry in entries},
        regeneration_capability={},
        orphaned_artifacts=[],
        stale_artifact_tests=[],
        derived_vs_canonical_ratio={"derived_artifact_count": len(entries), "canonical_generator_count": 1, "ratio": 1.0},
        giant_artifact_churn_zones=[],
        dirty_pr_paths=[],
        downstream_impact_summary={},
        final_status="PASS",
    )


def _write_generator(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_deterministic_regeneration_order_and_normalization(tmp_path: Path) -> None:
    repo_root = tmp_path
    gen_a = repo_root / "scripts" / "gen_a.py"
    gen_b = repo_root / "scripts" / "gen_b.py"
    _write_generator(
        gen_a,
        """
from pathlib import Path

def main() -> None:
    path = Path('out/contracts/a.latest.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"beta":2,"alpha":1}', encoding='utf-8')
""".strip()
        + "\n",
    )
    _write_generator(
        gen_b,
        """
from pathlib import Path

def main() -> None:
    json_path = Path('out/contracts/b.latest.json')
    md_path = Path('out/contracts/b.latest.md')
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text('{"gamma":3,"alpha":1}', encoding='utf-8')
    md_path.write_text('line1\\r\\nline2', encoding='utf-8')
""".strip()
        + "\n",
    )
    registry = _registry_for(
        [
            GeneratedArtifactEntry(
                artifact_path="out/contracts/a.latest.json",
                canonical_generator="scripts/gen_a.py",
                canonical_schema="ExampleA.v1",
                deterministic_inputs=[],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=["out/contracts/b.latest.json"],
                final_status="managed",
                artifact_kind="json",
                tracked=False,
            ),
            GeneratedArtifactEntry(
                artifact_path="out/contracts/b.latest.json",
                canonical_generator="scripts/gen_b.py",
                canonical_schema="ExampleB.v1",
                deterministic_inputs=["out/contracts/a.latest.json"],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=False,
            ),
            GeneratedArtifactEntry(
                artifact_path="out/contracts/b.latest.md",
                canonical_generator="scripts/gen_b.py",
                canonical_schema="GeneratedArtifactMarkdown.v1",
                deterministic_inputs=["out/contracts/a.latest.json"],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="markdown",
                tracked=False,
            ),
        ]
    )

    first = execute_artifact_regeneration(registry, repo_root=repo_root, full=True)
    second = execute_artifact_regeneration(registry, repo_root=repo_root, full=True)

    assert first.generator_sequence == ["scripts/gen_a.py", "scripts/gen_b.py"]
    assert second.generator_sequence == first.generator_sequence
    assert first.final_status == "PASS"
    assert second.final_status == "PASS"
    assert (repo_root / "out/contracts/a.latest.json").read_text(encoding="utf-8") == '{"alpha":1,"beta":2}\n'
    assert (repo_root / "out/contracts/b.latest.json").read_text(encoding="utf-8") == '{"alpha":1,"gamma":3}\n'
    assert (repo_root / "out/contracts/b.latest.md").read_text(encoding="utf-8") == 'line1\nline2\n'
    assert [status.normalized_hash for status in first.statuses] == [status.normalized_hash for status in second.statuses]
    assert all(status.authority_granted is False for status in first.statuses)
    assert all(status.mutation_allowed is False for status in first.statuses)


def test_validation_only_detects_stale_artifact_drift(tmp_path: Path) -> None:
    repo_root = tmp_path
    gen = repo_root / "scripts" / "gen.py"
    _write_generator(
        gen,
        """
from pathlib import Path

def main() -> None:
    path = Path('out/contracts/example.latest.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"beta":2,"alpha":1}', encoding='utf-8')
""".strip()
        + "\n",
    )
    registry = _registry_for(
        [
            GeneratedArtifactEntry(
                artifact_path="out/contracts/example.latest.json",
                canonical_generator="scripts/gen.py",
                canonical_schema="Example.v1",
                deterministic_inputs=[],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=False,
            )
        ]
    )

    execute_artifact_regeneration(registry, repo_root=repo_root, full=True)
    (repo_root / "out/contracts/example.latest.json").write_text(
        '{\r\n  "beta": 2,\r\n  "alpha": 1\r\n}',
        encoding="utf-8",
    )

    plan = execute_artifact_regeneration(
        registry,
        repo_root=repo_root,
        full=True,
        validation_only=True,
    )

    assert plan.final_status == "FAILED"
    assert plan.statuses[0].drift_detected is True
    assert plan.statuses[0].canonical_json_normalized is False
    assert plan.statuses[0].newline_normalized is False


def test_full_regeneration_excludes_runtime_volatile_outputs(tmp_path: Path) -> None:
    repo_root = tmp_path
    deterministic = repo_root / "scripts" / "gen_deterministic.py"
    runtime = repo_root / "scripts" / "gen_runtime.py"
    _write_generator(
        deterministic,
        """
from pathlib import Path

def main() -> None:
    path = Path('out/contracts/stable.latest.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"stable":true}', encoding='utf-8')
""".strip()
        + "\n",
    )
    _write_generator(
        runtime,
        """
from pathlib import Path

def main() -> None:
    path = Path('out/validation/latest.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"summary":{"status":"runtime"}}', encoding='utf-8')
""".strip()
        + "\n",
    )
    registry = _registry_for(
        [
            GeneratedArtifactEntry(
                artifact_path="out/contracts/stable.latest.json",
                canonical_generator="scripts/gen_deterministic.py",
                canonical_schema="Stable.v1",
                deterministic_inputs=[],
                regeneration_required=True,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=True,
                determinism_class="CI_REGENERATED",
            ),
            GeneratedArtifactEntry(
                artifact_path="out/validation/latest.json",
                canonical_generator="scripts/gen_runtime.py",
                canonical_schema="Runtime.v1",
                deterministic_inputs=[],
                regeneration_required=False,
                committed_policy="tracked-derived",
                downstream_dependencies=[],
                final_status="managed",
                artifact_kind="json",
                tracked=True,
                determinism_class="RUNTIME_VOLATILE",
            ),
        ]
    )

    plan = execute_artifact_regeneration(registry, repo_root=repo_root, full=True)

    assert plan.final_status == "PASS"
    assert plan.selected_artifacts == ["out/contracts/stable.latest.json"]
    assert (repo_root / "out/contracts/stable.latest.json").exists()
    assert not (repo_root / "out/validation/latest.json").exists()


def test_check_drift_fails_only_on_deterministic_paths(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    registry = _registry_for([])
    monkeypatch.setattr(
        run_artifact_regeneration,
        "build_generated_artifact_registry",
        lambda _repo_root: registry,
    )

    monkeypatch.setattr(
        run_artifact_regeneration,
        "detect_ci_artifact_drift_paths",
        lambda _registry, *, repo_root: [],
    )
    run_artifact_regeneration.main(["--check-drift"])
    assert capsys.readouterr().out == ""

    monkeypatch.setattr(
        run_artifact_regeneration,
        "detect_ci_artifact_drift_paths",
        lambda _registry, *, repo_root: ["out/contracts/stable.latest.json"],
    )
    with pytest.raises(SystemExit, match="1"):
        run_artifact_regeneration.main(["--check-drift"])
    assert capsys.readouterr().out.strip() == "out/contracts/stable.latest.json"
