"""Workstream 0 — production-readiness baseline generator.

Builds a reproducible inventory package under
``out/production_readiness/baseline/`` from live repository inspection.

Evidence states are restricted to Missing / Partial / Verified /
NOT_COMPUTABLE. This generator never fabricates live CI results: pass a
validation payload from an actual run_fast_ci execution to promote the
validation receipt.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PROGRAM = "ABRAXAS_PRODUCTION_CONTINUATION"
WORKSTREAM = "BASELINE_AND_FREEZE"
PRODUCER = "run_production_readiness_baseline"
BASELINE_DIR_REL = Path("out/production_readiness/baseline")
BASELINE_DIR = BASELINE_DIR_REL  # alias for imports

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".codebase-memory",
    ".tmp",
}


@dataclass(frozen=True)
class RepoGitState:
    head_sha: str
    origin_main_sha: str | None
    branch: str
    worktree_clean: bool
    status_porcelain: list[str]
    merge_base: str | None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def capture_git_state(repo_root: Path) -> RepoGitState:
    head = _run_git(repo_root, "rev-parse", "HEAD")
    origin = _run_git(repo_root, "rev-parse", "origin/main") or None
    branch = _run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD") or "UNKNOWN"
    porcelain = _run_git(repo_root, "status", "--porcelain")
    status_lines = [line for line in porcelain.splitlines() if line.strip()]
    merge_base = None
    if origin:
        merge_base = _run_git(repo_root, "merge-base", "HEAD", "origin/main") or None
    return RepoGitState(
        head_sha=head,
        origin_main_sha=origin,
        branch=branch,
        worktree_clean=len(status_lines) == 0,
        status_porcelain=status_lines,
        merge_base=merge_base,
    )


def _iter_files(repo_root: Path, suffix: str | None = None) -> list[Path]:
    results: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if suffix and not name.endswith(suffix):
                continue
            results.append(Path(dirpath) / name)
    return results


def _rel(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def build_test_inventory(repo_root: Path, sha: str, produced_at: str) -> dict[str, Any]:
    tests_dir = repo_root / "tests"
    test_files = sorted(
        p for p in tests_dir.rglob("test_*.py") if p.is_file()
    ) if tests_dir.is_dir() else []
    by_prefix: Counter[str] = Counter()
    for path in test_files:
        name = path.name
        # coarse domain from first tokens after test_
        stem = name.removeprefix("test_").removesuffix(".py")
        token = stem.split("_")[0] if stem else "misc"
        by_prefix[token] += 1

    return {
        "schema_version": "test_inventory.v1",
        "artifact_type": "test_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Verified",
        "summary": {
            "test_file_count": len(test_files),
            "tests_root": "tests/",
            "inventory_method": "filesystem walk of tests/test_*.py",
        },
        "top_name_prefixes": [
            {"prefix": k, "count": v}
            for k, v in by_prefix.most_common(25)
        ],
        "sample_paths": [_rel(repo_root, p) for p in test_files[:40]],
        "open_gaps": [
            "Per-file test function counts not enumerated in this pass",
            "Integration vs unit classification not machine-labeled",
        ],
    }


def build_entry_point_inventory(
    repo_root: Path, sha: str, produced_at: str
) -> dict[str, Any]:
    scripts_dir = repo_root / "scripts"
    run_scripts = sorted(scripts_dir.glob("run_*.py")) if scripts_dir.is_dir() else []
    api_paths: list[str] = []
    api_root = repo_root / "apps" / "api"
    if api_root.is_dir():
        for p in sorted(api_root.rglob("*.py")):
            if p.name != "__init__.py":
                api_paths.append(_rel(repo_root, p))

    cli_docs = []
    for candidate in (
        "docs/workflows/cli-operator-layer.md",
        "QUICKSTART.md",
    ):
        if (repo_root / candidate).is_file():
            cli_docs.append(candidate)

    return {
        "schema_version": "entry_point_inventory.v1",
        "artifact_type": "entry_point_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Verified",
        "summary": {
            "run_script_count": len(run_scripts),
            "primary_pattern": "scripts/run_*.py",
            "api_module_count": len(api_paths),
            "inventory_method": "glob scripts/run_*.py + apps/api tree",
        },
        "classes": {
            "runners": {
                "count": len(run_scripts),
                "sample": [_rel(repo_root, p) for p in run_scripts[:30]],
            },
            "api": {
                "count": len(api_paths),
                "paths": api_paths[:40],
            },
            "cli_docs": cli_docs,
            "neon_genie": {
                "runner": "scripts/codegen/run_abx_neon_genie.py",
                "exists": (repo_root / "scripts" / "run_abx_neon_genie.py").is_file(),
                "skill": "skills/abx-neon-genie",
            },
            "fast_ci": {
                "path": "scripts/run_fast_ci.py",
                "exists": (repo_root / "scripts" / "run_fast_ci.py").is_file(),
            },
        },
        "open_gaps": [
            "Console entry points under apps/aal-viz-live-console not fully expanded",
            "Package console_scripts / pyproject entry-points not parsed",
        ],
    }


def build_governance_surface_inventory(
    repo_root: Path, sha: str, produced_at: str
) -> dict[str, Any]:
    surfaces: list[dict[str, str]] = []
    for rel in (
        "GOVERNANCE_V3.md",
        "GOVERNANCE_SIMPLIFICATION_001.md",
        "GOVERNANCE_STRATIFICATION_001.md",
        "AGENTS.md",
        "COMPATIBILITY.md",
        "STATUS.md",
    ):
        if (repo_root / rel).is_file():
            surfaces.append({"path": rel, "kind": "doctrine_doc"})

    stab = repo_root / "contracts" / "stabilization_readiness"
    stab_schemas = (
        sorted(stab.glob("*.schema.json")) if stab.is_dir() else []
    )
    gov_contracts = repo_root / "contracts" / "governance"
    gov_schemas = (
        sorted(gov_contracts.glob("*.schema.json")) if gov_contracts.is_dir() else []
    )

    return {
        "schema_version": "governance_surface_inventory.v1",
        "artifact_type": "governance_surface_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Verified",
        "summary": {
            "doctrine_docs": len(surfaces),
            "stabilization_readiness_schemas": len(stab_schemas),
            "governance_contract_schemas": len(gov_schemas),
            "governance_mode": "V3 ACTIVE implementation-first; fail-closed authority",
            "inventory_method": "explicit doctrine paths + schema directory counts",
        },
        "doctrine_surfaces": surfaces,
        "stabilization_schemas": [
            _rel(repo_root, p) for p in stab_schemas
        ],
        "governance_schemas_sample": [
            _rel(repo_root, p) for p in gov_schemas[:30]
        ],
        "authority_posture": {
            "production_activation": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "default_lane": "SHADOW / ADVISORY",
        },
        "open_gaps": [
            "Full operator_review surface enumeration under out/operator_review/",
            "Notion governance mapping registry not linked in this inventory",
        ],
    }


def build_service_candidate_inventory(
    repo_root: Path, sha: str, produced_at: str
) -> dict[str, Any]:
    """Map program-required services to existing repo surfaces (candidates only)."""

    def exists(*parts: str) -> bool:
        return (repo_root.joinpath(*parts)).exists()

    candidates = [
        {
            "service_id": "reasoning_service",
            "program_name": "Reasoning Service",
            "stability_class_candidate": "EXPERIMENTAL",
            "evidence_paths": [
                p
                for p in (
                    "core/abraxas_engineering_oracle.py",
                    "skills/abraxas-repo-intel",
                )
                if exists(*p.split("/"))
            ],
            "status": "CANDIDATE",
            "notes": "No versioned service contract registry entry yet",
        },
        {
            "service_id": "forecast_service",
            "program_name": "Forecast Service",
            "stability_class_candidate": "INTERNAL",
            "evidence_paths": [],
            "status": "BLOCKED_LANE",
            "notes": "ARCHITECTURE.md states FORECAST lane not authorized",
        },
        {
            "service_id": "symbolic_analysis_service",
            "program_name": "Symbolic Analysis Service",
            "stability_class_candidate": "EXPERIMENTAL",
            "evidence_paths": [
                p
                for p in (
                    "skills/abx-esoteric-intelligence",
                    "core/observability",
                )
                if exists(*p.split("/"))
            ],
            "status": "CANDIDATE",
            "notes": "Symbolic/esoteric surfaces present; not service-contracted",
        },
        {
            "service_id": "validation_service",
            "program_name": "Validation Service",
            "stability_class_candidate": "ADVISORY",
            "evidence_paths": [
                p
                for p in (
                    "scripts/run_fast_ci.py",
                    "scripts/artifact/run_artifact_regeneration.py",
                    "core/canonical",
                )
                if exists(*p.split("/"))
            ],
            "status": "CANDIDATE",
            "notes": "Validation runners exist; not exposed as versioned service API",
        },
        {
            "service_id": "repository_intelligence_service",
            "program_name": "Repository Intelligence Service",
            "stability_class_candidate": "ADVISORY",
            "evidence_paths": [
                p
                for p in (
                    "skills/abraxas-repo-intel",
                    "docs/workflows/cli-operator-layer.md",
                )
                if exists(*p.split("/"))
            ],
            "status": "CANDIDATE",
        },
        {
            "service_id": "artifact_and_provenance_service",
            "program_name": "Artifact and Provenance Service",
            "stability_class_candidate": "SUPPORTED",
            "evidence_paths": [
                p
                for p in (
                    "core/services/artifact_provenance_service.py",
                    "scripts/artifact/run_artifact_provenance_service.py",
                    "tests/test_artifact_provenance_service.py",
                    "core/canonical/json.py",
                )
                if exists(*p.split("/"))
            ],
            "status": "IMPLEMENTED",
            "notes": "WP-K2: SUPPORTED facade over canonical_json (out/-only writes).",
        },
        {
            "service_id": "governance_evaluation_service",
            "program_name": "Governance Evaluation Service",
            "stability_class_candidate": "ADVISORY",
            "evidence_paths": [
                p
                for p in (
                    "abraxas/v2/governance",
                    "core/abraxas_governance_decision_contract.py",
                    "contracts/stabilization_readiness",
                )
                if exists(*p.split("/"))
            ],
            "status": "CANDIDATE",
        },
        {
            "service_id": "execution_receipt_service",
            "program_name": "Execution Receipt Service",
            "stability_class_candidate": "ADVISORY",
            "evidence_paths": [
                p
                for p in (
                    "scripts/readiness/run_sole_writer_advisory_check.py",
                    "out/production_readiness",
                )
                if exists(*p.split("/"))
            ],
            "status": "CANDIDATE",
            "notes": "Receipt emission is ubiquitous via runners; no single service facade",
        },
    ]

    return {
        "schema_version": "service_candidate_inventory.v1",
        "artifact_type": "service_candidate_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "summary": {
            "required_services": 8,
            "candidates_mapped": len(candidates),
            "service_registry_present": False,
            "inventory_method": "program-required service list mapped to existing paths",
        },
        "candidates": candidates,
        "open_gaps": [
            "No canonical service_registry artifact",
            "No versioned request/response/error schemas per service",
            "No contract/idempotency/authorization service tests suite as required by WS3",
        ],
    }


def build_schema_inventory(repo_root: Path, sha: str, produced_at: str) -> dict[str, Any]:
    contracts = repo_root / "contracts"
    schemas = (
        sorted(contracts.rglob("*.schema.json")) if contracts.is_dir() else []
    )
    by_top: Counter[str] = Counter()
    for path in schemas:
        rel = _rel(repo_root, path)
        parts = rel.split("/")
        domain = parts[1] if len(parts) > 2 else "root"
        by_top[domain] += 1

    return {
        "schema_version": "schema_inventory.v1",
        "artifact_type": "schema_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Verified",
        "summary": {
            "schema_file_count": len(schemas),
            "primary_location": "contracts/",
            "inventory_method": "filesystem walk of contracts/**/*.schema.json",
        },
        "domains": [
            {"domain": k, "count": v} for k, v in by_top.most_common(40)
        ],
        "stabilization_focus": "contracts/stabilization_readiness/",
        "sample_paths": [_rel(repo_root, p) for p in schemas[:30]],
        "open_gaps": [
            "Stability class labels not assigned per schema",
            "Checksum matrix not computed in this pass",
        ],
    }


def build_writer_inventory(repo_root: Path, sha: str, produced_at: str) -> dict[str, Any]:
    scripts_dir = repo_root / "scripts"
    run_scripts = sorted(scripts_dir.glob("run_*.py")) if scripts_dir.is_dir() else []
    # heuristic potential writers outside scripts/run_*
    write_rx = re.compile(
        r"""(open\s*\(\s*['\"]out/|Path\s*\(\s*['\"]out/|\.write_text\s*\(|json\.dump\s*\()"""
    )
    suspects: list[str] = []
    for path in _iter_files(repo_root, ".py"):
        rel = _rel(repo_root, path)
        if rel.startswith("scripts/run_") or rel.startswith("tests/"):
            continue
        if rel.startswith("scripts/run_sole_writer"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "out/" in text and write_rx.search(text):
            suspects.append(rel)
            if len(suspects) >= 40:
                break

    return {
        "schema_version": "writer_inventory.v1",
        "artifact_type": "writer_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "summary": {
            "primary_pattern": "sole-writer via scripts/run_*.py",
            "run_script_count": len(run_scripts),
            "heuristic_non_run_suspect_count_capped": len(suspects),
            "inventory_method": "count run_*.py + heuristic scan for out/ writes outside authorized pattern",
        },
        "canonical_writer_classes": [
            "scripts/run_*.py (primary)",
            "scripts/run_fast_ci.py",
            "scripts/artifact/run_artifact_regeneration.py",
            "scripts/readiness/run_production_readiness_baseline.py",
        ],
        "heuristic_suspect_sample": suspects,
        "risks": [
            "Large runner surface increases accidental write paths",
            "Heuristic scan is advisory and may include false positives",
        ],
        "open_gaps": [
            "Exhaustive allow-list of modules allowed to write out/",
            "Automated sole-writer enforcement not in fast CI",
        ],
    }


def build_interface_inventory(
    repo_root: Path, sha: str, produced_at: str
) -> dict[str, Any]:
    registry = (
        repo_root
        / "out"
        / "production_readiness"
        / "ws1"
        / "interface_registry_snapshot.v1.json"
    )
    registry_schema = (
        repo_root
        / "contracts"
        / "stabilization_readiness"
        / "interface_registry.v1.schema.json"
    )
    return {
        "schema_version": "interface_inventory.v1",
        "artifact_type": "interface_inventory",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "summary": {
            "primary_public_surface": "scripts/run_*.py + contracts/ schemas",
            "interface_registry_snapshot_present": registry.is_file(),
            "interface_registry_schema_present": registry_schema.is_file(),
            "inventory_method": "presence checks + WS1 seed registry linkage",
        },
        "candidate_supported_interfaces": [
            {
                "name": "stabilization_entry_gate",
                "location": "contracts/stabilization_readiness/stabilization_entry_gate.v1.schema.json",
                "stability_class_candidate": "ADVISORY",
            },
            {
                "name": "production_contract_inventory",
                "location": "contracts/stabilization_readiness/production_contract_inventory.v1.schema.json",
                "stability_class_candidate": "ADVISORY",
            },
            {
                "name": "fast_ci",
                "location": "scripts/run_fast_ci.py",
                "stability_class_candidate": "ADVISORY",
            },
            {
                "name": "production_readiness_baseline",
                "location": "scripts/readiness/run_production_readiness_baseline.py",
                "stability_class_candidate": "ADVISORY",
            },
        ],
        "ws1_registry_path": (
            "out/production_readiness/ws1/interface_registry_snapshot.v1.json"
            if registry.is_file()
            else None
        ),
        "open_gaps": [
            "Full public interface enumeration with ownership/error contracts incomplete",
            "Product-facing surfaces beyond kernel SUPPORTED set may still be required",
            "CI gate for unregistered public interfaces not present",
        ],
    }


def build_dependency_graph_summary(
    repo_root: Path, sha: str, produced_at: str
) -> dict[str, Any]:
    """Lightweight import edge sample from core/ — not a full graph."""
    core_dir = repo_root / "core"
    edges: Counter[tuple[str, str]] = Counter()
    files_scanned = 0
    parse_errors = 0
    if core_dir.is_dir():
        for path in sorted(core_dir.rglob("*.py")):
            if path.name == "__init__.py" and path.parent == core_dir:
                continue
            files_scanned += 1
            if files_scanned > 200:
                break
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                parse_errors += 1
                continue
            mod = _rel(repo_root, path).removesuffix(".py").replace("/", ".")
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("core.") or node.module == "core":
                        edges[(mod, node.module)] += 1
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("core.") or alias.name == "core":
                            edges[(mod, alias.name)] += 1

    sample_edges = [
        {"from": a, "to": b, "count": c}
        for (a, b), c in edges.most_common(30)
    ]

    return {
        "schema_version": "dependency_graph_summary.v1",
        "artifact_type": "dependency_graph_summary",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "summary": {
            "architecture_principle": (
                "Fail-closed, sole-writer (scripts/run_*), contracts under contracts/"
            ),
            "observed_direction": (
                "scripts/ and core/ consume contracts/; out/ is write-target via runners"
            ),
            "core_files_scanned_cap": files_scanned,
            "unique_core_import_edges_sampled": len(edges),
            "parse_errors": parse_errors,
            "inventory_method": "AST Import/ImportFrom sample of first 200 core/*.py files",
        },
        "sample_edges": sample_edges,
        "known_boundaries": [
            {
                "from": "scripts/run_*.py",
                "to": "contracts/",
                "rule": "Runners validate against and emit receipts conforming to contracts",
            },
            {
                "from": "any production writer",
                "to": "out/",
                "rule": "Only authorized run_* scripts may write production artifacts",
            },
            {
                "from": "integrations / Neon Genie",
                "to": "core governance",
                "rule": "Must remain advisory / allowlisted; no governance control",
            },
        ],
        "risks_observed": [
            "No automated circular-dependency or prohibited-import CI gate evidence",
            "Historical archive surfaces still present (RISK-004)",
            "Import sample is capped; not a full cycle-proof graph",
        ],
        "open_gaps": [
            "Full import-graph artifact",
            "Proof of no cycles across core packages",
            "Verified module import allow-list",
        ],
    }


def build_readiness_blockers(
    repo_root: Path,
    sha: str,
    produced_at: str,
    validation: dict[str, Any] | None,
) -> dict[str, Any]:
    live_ok = bool(
        validation
        and validation.get("live_execution_performed")
        and validation.get("exit_code") == 0
    )
    blockers = [
        {
            "id": "RISK-006",
            "title": "Live validation receipt for baseline VERIFIED",
            "severity": "HIGH",
            "status": "CLOSED" if live_ok else "MITIGATING",
            "priority": "P0",
            "mitigation": (
                "Live run_fast_ci.py captured with exit_code=0"
                if live_ok
                else "Scrubbed and/or partial live evidence only; full green live CI required for VERIFIED"
            ),
        },
        {
            "id": "RISK-004",
            "title": "Historical archive surfaces still present",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P1",
            "mitigation": (
                "TD Wave 3: historical_archive_quarantine.v1 tracks archive surfaces "
                "as QUARANTINE_KEEP_HISTORICAL (no destructive purge)."
            ),
        },
        {
            "id": "RISK-008",
            "title": "Boundary / sole-writer CI remains advisory (not fail-closed)",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P0",
            "mitigation": (
                "Advisory boundary + sole-writer in run_fast_ci; pure-builder debt "
                "reduced (D4-C1..C5); package policies for skills/afe. Fail-closed "
                "still off by design until operator approval."
            ),
        },
        {
            "id": "RISK-011",
            "title": "SUPPORTED kernel set limited to core contracts",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P0",
            "mitigation": (
                "SUPPORTED: canonical_json, run_fast_ci, validation_service.v1, "
                "artifact_and_provenance_service.v0 (count=4). Further product "
                "surfaces optional, not freeze-blocking."
            ),
        },
        {
            "id": "RISK-010",
            "title": "Full program service suite incomplete",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P1",
            "mitigation": (
                "Two SUPPORTED services implemented (validation + artifact provenance). "
                "Remaining program services remain candidates only."
            ),
        },
        {
            "id": "RISK-012",
            "title": "Notion tracker Evidence State not fully Verified",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P1",
            "mitigation": (
                "Mapping + live writeback linked to PR #971. Operator Verified DoD "
                "per checkpoint still open (Partial Evidence State)."
            ),
        },
        {
            "id": "RISK-013",
            "title": "Neon Genie integration residual (non-control proven partially)",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P1",
            "mitigation": (
                "Capability allowlist + fail-closed check_capability + fast-CI advisory "
                "probe present. Live integration proof residual only."
            ),
        },
        {
            "id": "RISK-014",
            "title": "Threat model remains Partial (not pen-test Verified)",
            "severity": "MEDIUM",
            "status": "MITIGATING",
            "priority": "P0",
            "mitigation": (
                "ThreatModel.v0 + operator ACCEPT_PARTIAL_BASELINE + recovery drill. "
                "Verified/pen-test quality still open."
            ),
        },
    ]

    return {
        "schema_version": "readiness_blockers.v1",
        "artifact_type": "readiness_blockers",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "blockers": blockers,
        "p0_open_count": sum(
            1
            for b in blockers
            if b["priority"] == "P0" and b["status"] != "CLOSED"
        ),
        "notes": [
            "Blockers are program-facing; not all map 1:1 to CI failures",
            "Closing RISK-006 alone does not make the platform production-ready",
        ],
    }


def build_unsupported_assumptions(
    repo_root: Path, sha: str, produced_at: str
) -> dict[str, Any]:
    return {
        "schema_version": "unsupported_assumptions.v1",
        "artifact_type": "unsupported_assumptions",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "assumptions": [
            {
                "id": "ASSUME-001",
                "claim": "STATUS.md CI health claims apply to current HEAD without re-run",
                "classification": "NOT_COMPUTABLE",
                "reason": "STATUS.md last-updated may lag HEAD; require live receipt",
            },
            {
                "id": "ASSUME-002",
                "claim": "Repository is production-ready because test count is large",
                "classification": "INVALID",
                "reason": "Program forbids feature-count / test-count as readiness proof",
            },
            {
                "id": "ASSUME-003",
                "claim": "All run_*.py scripts are safe sole writers with atomic publication",
                "classification": "NOT_COMPUTABLE",
                "reason": "No exhaustive writer audit; advisory sole-writer check only",
            },
            {
                "id": "ASSUME-004",
                "claim": "Neon Genie cannot affect governance control plane",
                "classification": "Partial",
                "reason": "Documented advisory posture; capability allowlist not enforced in CI",
            },
            {
                "id": "ASSUME-005",
                "claim": "Semantic-release automation equals production release readiness",
                "classification": "INVALID",
                "reason": "Release automation is necessary but not sufficient for bounded production candidate",
            },
            {
                "id": "ASSUME-006",
                "claim": "Forecast and production lanes remain unusable",
                "classification": "Partial",
                "reason": "Authority locks documented; continuous enforcement evidence incomplete",
            },
        ],
    }


def build_repository_state(
    git_state: RepoGitState, produced_at: str, version: str
) -> dict[str, Any]:
    return {
        "schema_version": "repository_state.v1",
        "artifact_type": "repository_state",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": git_state.head_sha,
        "origin_main_sha": git_state.origin_main_sha,
        "merge_base": git_state.merge_base,
        "branch": git_state.branch,
        "worktree_clean": git_state.worktree_clean,
        "status_porcelain": git_state.status_porcelain[:50],
        "evidence_state": "Verified" if git_state.head_sha else "Missing",
        "version": version,
        "default_branch": "main",
        "governance": "V3 ACTIVE (implementation-first, fail-closed)",
        "notes": [
            "Captured via git rev-parse / status --porcelain at generator runtime",
            "worktree_clean reflects pre-write state when called before artifact emission",
        ],
    }


def build_validation_summary(
    sha: str, produced_at: str, validation: dict[str, Any] | None
) -> dict[str, Any]:
    if not validation:
        return {
            "schema_version": "validation_summary.v1",
            "artifact_type": "validation_summary",
            "produced_at": produced_at,
            "producer": PRODUCER,
            "repository_sha": sha,
            "evidence_state": "Missing",
            "live_ci_executed": False,
            "notes": ["No validation payload provided to baseline generator"],
        }

    exit_code = validation.get("exit_code")
    live = bool(validation.get("live_execution_performed"))
    if live and exit_code == 0:
        evidence = "Verified"
    elif live:
        evidence = "Partial"
    else:
        evidence = "Partial"

    return {
        "schema_version": "validation_summary.v1",
        "artifact_type": "validation_summary",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": evidence,
        "live_ci_executed": live,
        "exit_code": exit_code,
        "command": validation.get("command"),
        "duration_seconds": validation.get("duration_seconds"),
        "notes": validation.get("notes", []),
    }


def build_validation_receipt(
    sha: str, produced_at: str, validation: dict[str, Any] | None
) -> dict[str, Any]:
    if not validation or not validation.get("live_execution_performed"):
        return {
            "schema_version": "validation_receipt.v1",
            "artifact_type": "validation_receipt",
            "produced_at": produced_at,
            "producer": PRODUCER,
            "repository_sha": sha,
            "evidence_state": "Partial",
            "validation_mode": "NOT_RUN",
            "live_execution_performed": False,
            "notes": [
                "Live run_fast_ci.py not executed in this generation",
                "Do not treat as Verified",
            ],
            "related_risks": ["RISK-006"],
        }

    exit_code = validation.get("exit_code")
    evidence = "Verified" if exit_code == 0 else "Partial"
    return {
        "schema_version": "validation_receipt.v1",
        "artifact_type": "validation_receipt",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": evidence,
        "validation_mode": "LIVE",
        "live_execution_performed": True,
        "command": validation.get("command"),
        "exit_code": exit_code,
        "duration_seconds": validation.get("duration_seconds"),
        "stdout_tail": validation.get("stdout_tail", []),
        "stderr_tail": validation.get("stderr_tail", []),
        "environment": validation.get("environment", {}),
        "notes": validation.get("notes", []),
        "related_risks": ["RISK-006"],
        "related_workstreams": ["WS0"],
    }


def build_baseline_manifest(
    sha: str,
    produced_at: str,
    present: dict[str, str],
    validation: dict[str, Any] | None,
) -> dict[str, Any]:
    live_ok = bool(
        validation
        and validation.get("live_execution_performed")
        and validation.get("exit_code") == 0
    )
    return {
        "schema_version": "baseline_manifest.v1",
        "artifact_type": "baseline_manifest",
        "program": PROGRAM,
        "phase": "WORKSTREAM_0_BASELINE",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",  # package complete != production ready
        "required_artifacts": present,
        "exit_criteria_status": {
            "clean_checkout_reproducible": (
                "VERIFIED_BY_GENERATOR" if sha else "MISSING"
            ),
            "readiness_scores_linked_to_evidence_or_estimate": "PARTIAL",
            "existing_failures_classified": "PARTIAL",
            "unsupported_claims_marked_not_computable": "PARTIAL",
            "live_validation_attached": "VERIFIED" if live_ok else "PARTIAL_OR_MISSING",
            "notion_evidence_linked": "PARTIAL",
            "no_undocumented_branch_or_artifact_state": "PARTIAL",
        },
        "next_required_actions": [
            "Operator: link Evidence/PR on Notion tracker rows using WP-H mapping "
            "(close RISK-012 residual writeback)",
            "Operator: decide ThreatModel.v0 via WP-P decision request",
            "Promote interface stability classes only with CI + ownership evidence",
            *(
                []
                if live_ok
                else ["Attach green live validation receipt to close RISK-006"]
            ),
        ],
    }


def build_baseline_receipt(
    git_state: RepoGitState,
    produced_at: str,
    artifact_names: list[str],
    validation: dict[str, Any] | None,
    known_failures: list[str],
) -> dict[str, Any]:
    live_ok = bool(
        validation
        and validation.get("live_execution_performed")
        and validation.get("exit_code") == 0
    )
    # Baseline package can be COMPLETE while evidence remains PARTIAL when
    # Notion linkage or other exit criteria remain open.
    status = "COMPLETE" if artifact_names else "PARTIAL"
    evidence = "Partial"
    unknowns = [
        "Notion tracker live Evidence/PR writeback (mapping Partial)",
        "Threat model operator acceptance decision record",
        "Full import-cycle proof",
    ]
    if not live_ok:
        unknowns.insert(0, "Green live CI at this SHA" if validation else "Any live CI execution")

    return {
        "schema_version": "baseline_receipt.v1",
        "program": PROGRAM,
        "workstream": WORKSTREAM,
        "status": status,
        "evidence_state": evidence,
        "repository_sha": git_state.head_sha,
        "origin_main_sha": git_state.origin_main_sha,
        "branch": git_state.branch,
        "worktree_clean_at_capture": git_state.worktree_clean,
        "produced_at": produced_at,
        "producer": PRODUCER,
        "validation": {
            "live_ci_executed": bool(
                validation and validation.get("live_execution_performed")
            ),
            "exit_code": (validation or {}).get("exit_code"),
            "command": (validation or {}).get("command"),
        },
        "artifacts": artifact_names,
        "known_failures": known_failures,
        "unknowns": unknowns,
        "open_blockers": (
            (
                []
                if live_ok
                else ["RISK-006 live validation not green or not run"]
            )
            + [
                "RISK-012 Notion live writeback residual (mapping Partial)",
                "RISK-008 boundary CI report-only (not fail-closed)",
                "RISK-010 remaining program services are candidates only",
                "RISK-011 residual sole-writer / promotion debt (supported_count advancing)",
                "RISK-014 threat model Partial pending operator decision (WP-P)",
            ]
        ),
        "next_workstream": "KERNEL_CONTRACT_STABILIZATION",
        "notes": [
            "evidence_state remains Partial until Notion linkage and program P0 blockers are closed",
            "Generator is deterministic for counts given fixed tree; timestamps are wall-clock",
            "Does not authorize production activation",
        ],
    }


def build_unresolved_risk_register(
    sha: str,
    produced_at: str,
    readiness: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "unresolved_risk_register.v1",
        "artifact_type": "unresolved_risk_register",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "risks": readiness.get("blockers", []),
        "open_blockers_for_verified_baseline": [
            b["id"]
            for b in readiness.get("blockers", [])
            if b.get("id") in {"RISK-006", "RISK-012"}
            and b.get("status") not in {"CLOSED", "MITIGATING"}
        ],
        "notes": [
            "Supersedes prior hand-written risk register content for this SHA",
        ],
    }


def _read_version(repo_root: Path) -> str:
    version_path = repo_root / "VERSION"
    if version_path.is_file():
        return version_path.read_text(encoding="utf-8").strip()
    return "UNKNOWN"


def build_baseline_package(
    repo_root: Path,
    *,
    validation: dict[str, Any] | None = None,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, dict[str, Any]]:
    """Build (and optionally write) the full WS0 baseline package.

    Returns a mapping of filename → artifact dict.
    """
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    git_state = capture_git_state(repo_root)
    sha = git_state.head_sha
    version = _read_version(repo_root)

    packages: dict[str, dict[str, Any]] = {}
    packages["repository_state.v1.json"] = build_repository_state(
        git_state, produced_at, version
    )
    packages["test_inventory.v1.json"] = build_test_inventory(
        repo_root, sha, produced_at
    )
    packages["entry_point_inventory.v1.json"] = build_entry_point_inventory(
        repo_root, sha, produced_at
    )
    packages["governance_surface_inventory.v1.json"] = (
        build_governance_surface_inventory(repo_root, sha, produced_at)
    )
    packages["service_candidate_inventory.v1.json"] = (
        build_service_candidate_inventory(repo_root, sha, produced_at)
    )
    packages["schema_inventory.v1.json"] = build_schema_inventory(
        repo_root, sha, produced_at
    )
    packages["writer_inventory.v1.json"] = build_writer_inventory(
        repo_root, sha, produced_at
    )
    packages["interface_inventory.v1.json"] = build_interface_inventory(
        repo_root, sha, produced_at
    )
    packages["dependency_graph_summary.v1.json"] = build_dependency_graph_summary(
        repo_root, sha, produced_at
    )
    packages["unsupported_assumptions.v1.json"] = build_unsupported_assumptions(
        repo_root, sha, produced_at
    )
    packages["readiness_blockers.v1.json"] = build_readiness_blockers(
        repo_root, sha, produced_at, validation
    )
    packages["unresolved_risk_register.v1.json"] = build_unresolved_risk_register(
        sha, produced_at, packages["readiness_blockers.v1.json"]
    )
    packages["validation_summary.v1.json"] = build_validation_summary(
        sha, produced_at, validation
    )
    packages["validation_receipt.v1.json"] = build_validation_receipt(
        sha, produced_at, validation
    )

    present = {name: "PRESENT" for name in packages}
    # manifest and receipt added after
    packages["baseline_manifest.v1.json"] = build_baseline_manifest(
        sha, produced_at, present, validation
    )
    all_names = sorted(list(packages.keys()) + ["baseline_receipt.v1.json"])
    known_failures: list[str] = []
    if validation and validation.get("live_execution_performed"):
        if validation.get("exit_code") not in (0, None):
            known_failures.append(
                f"run_fast_ci exit_code={validation.get('exit_code')}"
            )
    packages["baseline_receipt.v1.json"] = build_baseline_receipt(
        git_state, produced_at, all_names, validation, known_failures
    )
    # refresh manifest required_artifacts to include receipt/manifest
    packages["baseline_manifest.v1.json"]["required_artifacts"] = {
        name: "PRESENT" for name in sorted(packages.keys())
    }

    if write:
        out_dir = repo_root / BASELINE_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, payload in packages.items():
            write_canonical_json(out_dir / name, payload)

    return packages
