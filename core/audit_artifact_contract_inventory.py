from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _sorted_unique(values: set[str]) -> list[str]:
    return sorted(v for v in values if v)


def _pkg_from_name(name: str) -> str:
    base = name.removeprefix("run_").removesuffix(".py")
    return base.removesuffix("_replay")


def build_inventory(repo_root: Path) -> dict[str, Any]:
    artifact_paths: set[str] = set()
    producer_scripts: set[str] = set()
    replay_scripts: set[str] = set()
    doctrine_gates: set[str] = set()
    aal_viz_summaries: set[str] = set()
    runtime_packages: set[str] = set()
    tests_by_pkg: dict[str, set[str]] = {}

    run_scripts = sorted((repo_root / "scripts").glob("run_*.py"))
    for s in run_scripts:
        rel = s.relative_to(repo_root).as_posix()
        if rel.endswith("_replay.py"):
            replay_scripts.add(rel)
        else:
            producer_scripts.add(rel)

    all_scan_files = [*sorted((repo_root / "scripts").glob("*.py")), *sorted((repo_root / "core").glob("**/*.py")), *sorted((repo_root / "tests").glob("test_*.py"))]
    out_pat = re.compile(r"out/[A-Za-z0-9_./-]+")
    gate_pat = re.compile(r"\b([a-z0-9_]+_gate)\b")

    for file in all_scan_files:
        text = _read(file)
        rel = file.relative_to(repo_root).as_posix()
        for m in out_pat.findall(text):
            artifact_paths.add(m.rstrip('"\''))
        for g in gate_pat.findall(text):
            doctrine_gates.add(g)
        if rel == "core/projections/aal_viz.py":
            for sm in re.findall(r"\b([a-z0-9_]+_summary)\b", text):
                aal_viz_summaries.add(sm)

    for rt in sorted((repo_root / "core").glob("*/runtime.py")):
        runtime_packages.add(rt.parent.name)
    for vt in sorted((repo_root / "core").glob("*/validators.py")):
        runtime_packages.add(vt.parent.name)

    for t in sorted((repo_root / "tests").glob("test_*.py")):
        name = t.name.removeprefix("test_").removesuffix(".py")
        pkg = name.split("_")[0]
        tests_by_pkg.setdefault(pkg, set()).add(t.relative_to(repo_root).as_posix())
        txt = _read(t)
        for m in out_pat.findall(txt):
            artifact_paths.add(m.rstrip('"\''))

    artifact_paths_list = _sorted_unique(artifact_paths)
    lineage_artifacts = [p for p in artifact_paths_list if "_lineage/latest.json" in p]
    diagnostic_artifacts = [p for p in artifact_paths_list if "_diagnostics/latest.json" in p]

    pkgs = set(runtime_packages)
    pkgs.update(_pkg_from_name(Path(p).name) for p in producer_scripts | replay_scripts)

    producer_map = {_pkg_from_name(Path(p).name): p for p in producer_scripts}
    replay_map = {_pkg_from_name(Path(p).name): p for p in replay_scripts}

    def find_artifact(pkg: str, suffix: str = "") -> str:
        needle = f"out/{pkg}{suffix}/latest.json"
        return needle if needle in artifact_paths else ""

    bindings = []
    gaps = []
    for pkg in sorted(pkgs):
        producer = producer_map.get(pkg, "")
        replay = replay_map.get(pkg, "")
        runtime_artifact = find_artifact(pkg)
        replay_artifact = find_artifact(pkg, "_replay")
        lineage_artifact = find_artifact(pkg, "_lineage")
        diagnostics_artifact = find_artifact(pkg, "_diagnostics")
        gates = sorted(g for g in doctrine_gates if g.startswith(pkg + "_") or pkg in g)
        summary = sorted(s for s in aal_viz_summaries if s.startswith(pkg + "_") or pkg in s)
        tests = sorted(tests_by_pkg.get(pkg, set()))

        status = "complete"
        if not runtime_artifact and (producer or replay or gates or summary):
            status = "missing"
        elif not all([producer, runtime_artifact]):
            status = "partial"
        if not any([producer, replay, runtime_artifact, replay_artifact, gates, summary]):
            status = "orphaned"

        if producer and not runtime_artifact:
            gaps.append({"gap_type": "missing_replay" if pkg.endswith("replay") else "missing_producer", "subject": pkg, "details": "producer script exists but runtime artifact path not discovered", "severity": "critical", "recommended_action": "align runtime writer out/<package>/latest.json or adjust script naming"})
        if runtime_artifact and not producer:
            gaps.append({"gap_type": "missing_producer", "subject": pkg, "details": "runtime artifact exists but producer script is missing", "severity": "critical", "recommended_action": "add matching run_<package>.py or mark legacy exception"})
        if replay and not replay_artifact:
            gaps.append({"gap_type": "missing_replay", "subject": pkg, "details": "replay script exists but replay artifact path not discovered", "severity": "critical", "recommended_action": "align replay writer out/<package>_replay/latest.json"})
        if gates and not runtime_artifact:
            gaps.append({"gap_type": "orphan_gate", "subject": pkg, "details": "doctrine gate exists without runtime artifact binding", "severity": "critical", "recommended_action": "bind gate to artifact contract or remove stale gate"})
        if summary and not runtime_artifact:
            gaps.append({"gap_type": "orphan_summary", "subject": pkg, "details": "AAL-Viz summary exists without runtime artifact binding", "severity": "critical", "recommended_action": "bind summary to artifact contract or remove stale summary"})
        if not tests:
            gaps.append({"gap_type": "missing_test", "subject": pkg, "details": "no package-matching tests discovered", "severity": "warning", "recommended_action": "add or map tests/test_<package>_*.py"})

        bindings.append({"package": pkg, "producer_script": producer, "replay_script": replay, "runtime_artifact": runtime_artifact, "replay_artifact": replay_artifact, "lineage_artifact": lineage_artifact, "diagnostics_artifact": diagnostics_artifact, "doctrine_gates": gates, "aal_viz_summary": summary[0] if summary else "", "tests": tests, "status": status})

    bindings = sorted(bindings, key=lambda b: b["package"])
    gaps = sorted(gaps, key=lambda g: (g["severity"], g["gap_type"], g["subject"]))
    critical = sum(1 for g in gaps if g["severity"] == "critical")
    warning = sum(1 for g in gaps if g["severity"] == "warning")
    status = "failed" if critical else ("repair_required" if warning else "passed")

    inv = {
        "schema": "ArtifactContractInventory.v1",
        "status": status,
        "generated_by": "RUN_ABRAXAS_ARTIFACT_CONTRACT_INVENTORY_AUDIT_001",
        "artifact_paths": artifact_paths_list,
        "producer_scripts": sorted(producer_scripts),
        "replay_scripts": sorted(replay_scripts),
        "lineage_artifacts": sorted(lineage_artifacts),
        "diagnostic_artifacts": sorted(diagnostic_artifacts),
        "doctrine_gates": sorted(doctrine_gates),
        "aal_viz_summaries": sorted(aal_viz_summaries),
        "runtime_packages": sorted(runtime_packages),
        "contract_bindings": bindings,
        "gaps": gaps,
        "counts": {
            "artifact_paths": len(artifact_paths_list),
            "producer_scripts": len(producer_scripts),
            "replay_scripts": len(replay_scripts),
            "doctrine_gates": len(doctrine_gates),
            "aal_viz_summaries": len(aal_viz_summaries),
            "runtime_packages": len(runtime_packages),
            "complete_bindings": sum(1 for b in bindings if b["status"] == "complete"),
            "partial_bindings": sum(1 for b in bindings if b["status"] == "partial"),
            "critical_gaps": critical,
        },
        "authority": {
            "projection_only": True,
            "inference_authority": False,
            "mutation_authority": False,
            "execution_authority": False,
        },
    }
    material = dict(inv)
    inv_hash = hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()
    inv["inventory_hash"] = f"sha256:{inv_hash}"
    return inv
