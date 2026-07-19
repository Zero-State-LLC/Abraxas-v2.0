"""Workstream 1 — Interface Registry builder.

Builds a merged, evidence-honest registry of public and internal interfaces.
Never auto-promotes to SUPPORTED; promotions require explicit attestation flags.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_interface_registry_snapshot"
WS1_DIR_REL = Path("out/production_readiness/ws1")
REGISTRY_ID = "WS1_KERNEL_CONTRACT_STABILIZATION_MERGED_004"
STABILITY = frozenset(
    {"SUPPORTED", "ADVISORY", "INTERNAL", "EXPERIMENTAL", "DEPRECATED", "REMOVED"}
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _exists(repo_root: Path, rel: str) -> bool:
    return (repo_root / rel).is_file() or (repo_root / rel).is_dir()


def _entry(
    *,
    contract_id: str,
    path: str,
    stability_class: str,
    ownership: str,
    version_policy: str = "v1_locked",
    language: list[str] | None = None,
    producers: list[str] | None = None,
    consumers: list[str] | None = None,
    notes: str | None = None,
    version: str = "1",
    input_contract: str | None = None,
    output_contract: str | None = None,
    error_contract: str | None = None,
    side_effects: str | None = None,
    authorization: str | None = None,
    determinism: str | None = None,
    compatibility_policy: str | None = None,
    deprecation_state: str | None = None,
    replacement: str | None = None,
    implementation_paths: list[str] | None = None,
    tests: list[str] | None = None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    if stability_class not in STABILITY:
        raise ValueError(f"invalid stability_class: {stability_class}")
    entry: dict[str, Any] = {
        "contract_id": contract_id,
        "path": path,
        "stability_class": stability_class,
        "ownership": ownership,
        "version_policy": version_policy,
        "version": version,
    }
    optional: dict[str, Any] = {
        "language": language,
        "producers": producers,
        "consumers": consumers,
        "notes": notes,
        "input_contract": input_contract,
        "output_contract": output_contract,
        "error_contract": error_contract,
        "side_effects": side_effects,
        "authorization": authorization,
        "determinism": determinism,
        "compatibility_policy": compatibility_policy,
        "deprecation_state": deprecation_state,
        "replacement": replacement,
        "implementation_paths": implementation_paths,
        "tests": tests,
        "evidence": evidence,
    }
    for key, value in optional.items():
        if value is not None:
            entry[key] = value
    return entry


def _stabilization_entries(repo_root: Path) -> list[dict[str, Any]]:
    stab = repo_root / "contracts" / "stabilization_readiness"
    if not stab.is_dir():
        return []
    advisory_ids = {
        "production_contract_inventory",
        "surface_resolution_receipt",
        "stabilization_entry_gate",
        "stabilization_operator_decision",
        "stabilization_state",
        "contract_inventory_receipt",
        "contract_inventory_current",
        "production_slice_candidate",
        "interface_registry",
    }
    entries: list[dict[str, Any]] = []
    for path in sorted(stab.glob("*.schema.json")):
        stem = path.name.removesuffix(".schema.json")
        # production_contract_inventory.v1 -> production_contract_inventory
        base = re.sub(r"\.v\d+$", "", stem)
        contract_id = stem if stem.endswith((".v1", ".v2")) else f"{stem}.v1"
        if not re.search(r"\.v\d+$", contract_id):
            contract_id = f"{contract_id}.v1"
        stability = "ADVISORY" if base in advisory_ids else "INTERNAL"
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        entries.append(
            _entry(
                contract_id=contract_id if ".v" in contract_id else f"{base}.v1",
                path=rel,
                stability_class=stability,
                ownership="abraxas-core",
                version_policy="v1_locked",
                language=["json_schema"],
                side_effects="none (schema definition only)",
                authorization="schema_only",
                determinism="n/a",
                deprecation_state="active",
                notes=(
                    "Stabilization-readiness schema. Candidate for SUPPORTED after "
                    "CI contract tests + ownership attestation."
                    if stability == "ADVISORY"
                    else "Internal stabilization inventory/graph surface."
                ),
            )
        )
    return entries


def _curated_entries(repo_root: Path) -> list[dict[str, Any]]:
    """High-signal production-readiness and compatibility surfaces."""
    curated: list[dict[str, Any]] = []

    def add(**kwargs: Any) -> None:
        path = kwargs["path"]
        if _exists(repo_root, path):
            curated.append(_entry(**kwargs))

    add(
        contract_id="run_fast_ci",
        path="scripts/run_fast_ci.py",
        stability_class="SUPPORTED",
        ownership="abraxas-core",
        version_policy="semver",
        language=["python"],
        producers=["scripts/run_fast_ci.py"],
        consumers=[".github/workflows/ci.yml", "contributors", "operators"],
        input_contract=(
            "Repository checkout; optional env ABRAXAS_FAST_CI_PYRIGHT_SCOPE "
            "(bounded|full), ABRAXAS_PYRIGHT_TIMEOUT_SECONDS, "
            "ABRAXAS_FAST_CI_SKIP_ADVISORY"
        ),
        output_contract=(
            "process exit code: 0=ok, non-zero=check failure, 3=drift, 124=timeout; "
            "stdout/stderr logs; optional advisory reports under out/production_readiness/ws1/"
        ),
        error_contract=(
            "non-zero exit on pytest/ruff/pyright/drift failure; advisory gates never fail the build"
        ),
        side_effects=(
            "may restore generated worktree drift; after status, may write advisory reports "
            "(boundary/sole-writer) without affecting exit code"
        ),
        authorization="local_or_ci_operator",
        determinism="partial (tooling versions, wall-clock, advisory timestamps)",
        compatibility_policy=(
            "semver: patch=defect fix preserving gate semantics; minor=additive report-only "
            "steps; major=removing/changing required gates or exit codes"
        ),
        deprecation_state="active",
        implementation_paths=["scripts/run_fast_ci.py"],
        tests=["tests/test_run_fast_ci.py"],
        evidence=[
            "out/production_readiness/baseline/validation_receipt.v1.json",
            ".github/workflows/ci.yml",
            "tests/test_run_fast_ci.py",
        ],
        notes=(
            "SECOND SUPPORTED interface (WS1.7). Mandatory pre-PR / CI validation entry point. "
            "Does not grant production activation authority."
        ),
    )
    add(
        contract_id="production_readiness_baseline",
        path="scripts/run_production_readiness_baseline.py",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["python"],
        producers=["scripts/run_production_readiness_baseline.py"],
        consumers=["operators", "CI_optional"],
        input_contract="--with-fast-ci | --validation-json | default inventory-only",
        output_contract="out/production_readiness/baseline/*.v1.json",
        error_contract="generator always exits 0; embeds CI exit_code as evidence",
        side_effects="writes baseline package via canonical JSON writer",
        authorization="operator_local",
        determinism="counts deterministic for fixed tree; timestamps wall-clock",
        deprecation_state="active",
        implementation_paths=[
            "core/production_readiness/baseline_generator.py",
            "scripts/run_production_readiness_baseline.py",
        ],
        tests=["tests/test_production_readiness_baseline.py"],
        evidence=["out/production_readiness/baseline/baseline_receipt.v1.json"],
    )
    add(
        contract_id="interface_registry_snapshot",
        path="scripts/run_interface_registry_snapshot.py",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["python"],
        producers=["scripts/run_interface_registry_snapshot.py"],
        output_contract="out/production_readiness/ws1/interface_registry_snapshot.v1.json",
        side_effects="writes WS1 registry snapshot",
        authorization="operator_local",
        determinism="entry set deterministic for fixed tree; timestamps wall-clock",
        deprecation_state="active",
        implementation_paths=[
            "core/production_readiness/interface_registry.py",
            "scripts/run_interface_registry_snapshot.py",
        ],
        tests=["tests/test_interface_registry.py"],
    )
    add(
        contract_id="sole_writer_advisory_check",
        path="scripts/run_sole_writer_advisory_check.py",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["python"],
        output_contract="out/production_readiness/ws1/sole_writer_advisory_report.v1.json",
        error_contract="always exit 0 (advisory)",
        side_effects="writes advisory report only",
        authorization="advisory_only",
        determinism="heuristic scan order filesystem-dependent for findings order",
        deprecation_state="active",
        notes=(
            "WS1.7: hardened heuristic (exclude tests/; write+out same-line). "
            "Report-only in fast CI. Not fail-closed."
        ),
        implementation_paths=[
            "scripts/run_sole_writer_advisory_check.py",
            "core/production_readiness/sole_writer_check.py",
        ],
        tests=["tests/test_sole_writer_advisory_check.py"],
    )
    add(
        contract_id="boundary_advisory_check",
        path="scripts/run_boundary_advisory_check.py",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["python"],
        output_contract="out/production_readiness/ws1/boundary_advisory_report.v1.json",
        error_contract="always exit 0 unless --fail-closed",
        side_effects="writes advisory report only",
        authorization="advisory_only",
        determinism="partial",
        deprecation_state="active",
        notes="Prohibited-import + unregistered-surface advisory. RISK-008 mitigation step 1.",
    )
    add(
        contract_id="repo_execution_receipt.v1",
        path="contracts/receipts/repo_execution_receipt.v1.schema.json",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["json_schema"],
        notes="Mature fail-closed receipt surface. SUPPORTED candidate with contract tests.",
        deprecation_state="active",
    )
    add(
        contract_id="rune_catalog.v1",
        path="contracts/runes/catalog.v1.json",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["json"],
        compatibility_policy="COMPATIBILITY.md public surface",
        deprecation_state="active",
        notes="Listed on COMPATIBILITY.md public compatibility surface.",
    )
    add(
        contract_id="canonical_json",
        path="core/canonical/json.py",
        stability_class="SUPPORTED",
        ownership="abraxas-core",
        version_policy="semver",
        language=["python"],
        producers=["core/canonical/json.py"],
        consumers=["scripts/run_*.py", "core/*", "skills/* (allowlisted)"],
        input_contract=(
            "JSON-serializable Python values for canonical_dumps/canonical_hash; "
            "path + value for write_canonical_json*"
        ),
        output_contract=(
            "canonical_dumps: stable JSON string (sorted keys, minimal separators); "
            "canonical_hash: sha256 hex; write_*: atomic file publish with trailing newline"
        ),
        error_contract=(
            "OSError/FileExistsError on atomic write failure; TypeError on non-serializable input"
        ),
        side_effects=(
            "write_canonical_json / write_canonical_json_if_changed mutate filesystem atomically "
            "via exclusive temp + replace; reads may prime file cache"
        ),
        authorization="library_internal_no_authority_grant",
        determinism="declared_deterministic",
        compatibility_policy=(
            "semver: patch=bugfix preserving hash for same logical value; "
            "minor=additive helpers; major=hash/serialization change (ARCHITECTURE.md: do not bypass)"
        ),
        deprecation_state="active",
        implementation_paths=["core/canonical/json.py", "core/canonical/__init__.py"],
        tests=["tests/test_canonical_json.py"],
        evidence=[
            "ARCHITECTURE.md (canonical serializer doctrine)",
            "tests/test_canonical_json.py",
            "out/production_readiness/ws1/interface_registry_snapshot.v1.json",
        ],
        notes=(
            "FIRST SUPPORTED interface (WS1.6). Production consumers may depend on "
            "canonical serialization/hash/atomic write behavior. Do not bypass with "
            "ad-hoc json.dumps for governed artifacts. Ownership: abraxas-core."
        ),
    )
    add(
        contract_id="contracts_pipelines_root",
        path="contracts/pipelines",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["json_schema"],
        compatibility_policy="COMPATIBILITY.md public surface",
        deprecation_state="active",
        notes="Pipeline contracts root (COMPATIBILITY.md). Expand per-schema later.",
    )
    add(
        contract_id="contracts_yggdrasil_root",
        path="contracts/yggdrasil",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="v1_locked",
        language=["json_schema"],
        compatibility_policy="COMPATIBILITY.md public surface",
        deprecation_state="active",
        notes="YGGDRASIL route graphs root (COMPATIBILITY.md). Expand per-schema later.",
    )
    add(
        contract_id="cli_operator_layer",
        path="docs/workflows/cli-operator-layer.md",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="semver",
        language=["markdown"],
        compatibility_policy="COMPATIBILITY.md public surface",
        deprecation_state="active",
        notes="CLI operator layer docs (COMPATIBILITY.md). Not an execution API.",
    )
    add(
        contract_id="neon_genie_entry",
        path="scripts/run_abx_neon_genie.py",
        stability_class="ADVISORY",
        ownership="neon-genie (advisory only)",
        version_policy="advisory-only",
        language=["python"],
        side_effects="venture skill surface; must not control governance plane",
        authorization="advisory_only_no_governance_control",
        determinism="partial",
        deprecation_state="active",
        notes="Explicitly non-governance. Capability allowlist still open (RISK-013).",
        implementation_paths=[
            "scripts/run_abx_neon_genie.py",
            "skills/abx-neon-genie",
        ],
    )
    add(
        contract_id="compatibility_policy",
        path="COMPATIBILITY.md",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="semver",
        language=["markdown"],
        deprecation_state="active",
        notes="Documents public compatibility surface; not an execution API.",
    )
    add(
        contract_id="validation_service.v1",
        path="core/services/validation_service.py",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="semver",
        language=["python"],
        producers=["core/services/validation_service.py", "scripts/run_validation_service.py"],
        input_contract="contracts/services/validation_service.request.v1.schema.json",
        output_contract="contracts/services/validation_service.response.v1.schema.json",
        error_contract="machine-readable ERROR with error_class enum",
        side_effects="none by default",
        authorization="local_library_call",
        determinism="declared_deterministic_for_fixed_schema_files",
        deprecation_state="active",
        implementation_paths=[
            "core/services/validation_service.py",
            "scripts/run_validation_service.py",
        ],
        tests=["tests/test_validation_service.py"],
        evidence=["out/production_readiness/ws3/service_registry.v1.json"],
        notes="WP-B first WS3 service facade. Not SUPPORTED yet.",
    )
    add(
        contract_id="artifact_and_provenance_service.v0",
        path="core/services/artifact_provenance_service.py",
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="semver",
        language=["python"],
        producers=[
            "core/services/artifact_provenance_service.py",
            "scripts/run_artifact_provenance_service.py",
        ],
        input_contract="contracts/services/artifact_provenance_service.request.v1.schema.json",
        output_contract="contracts/services/artifact_provenance_service.response.v1.schema.json",
        error_contract="PATH_DENIED|REQUEST_INVALID|WRITE_FAILED machine-readable",
        side_effects="write ops only under out/ via SUPPORTED canonical_json",
        authorization="local_library_call",
        determinism="hash/dumps deterministic; write timestamps none",
        deprecation_state="active",
        implementation_paths=[
            "core/services/artifact_provenance_service.py",
            "scripts/run_artifact_provenance_service.py",
        ],
        tests=["tests/test_artifact_provenance_service.py"],
        evidence=["out/production_readiness/ws3/service_registry.v1.json"],
        notes="WP-J facade. Depends on SUPPORTED canonical_json.",
    )
    return curated


def build_interface_registry(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    by_id: dict[str, dict[str, Any]] = {}
    for entry in _stabilization_entries(repo_root) + _curated_entries(repo_root):
        # Prefer curated (later) over auto when same id
        by_id[entry["contract_id"]] = entry

    # Normalize contract_ids that may collide with .v1 suffix variants
    entries = sorted(by_id.values(), key=lambda e: e["contract_id"])

    # Unregistered stabilization schemas should not happen (auto-scanned),
    # but track other candidate public roots not in registry.
    registered_paths = {e["path"] for e in entries}
    unregistered: list[str] = []
    for rel in (
        "contracts/pipelines",
        "contracts/yggdrasil",
        "docs/workflows/cli-operator-layer.md",
    ):
        path = repo_root / rel
        if path.exists() and rel not in registered_paths:
            unregistered.append(rel)

    counts: dict[str, int] = {}
    for entry in entries:
        cls = entry["stability_class"]
        counts[cls] = counts.get(cls, 0) + 1

    registry: dict[str, Any] = {
        "schema_version": "InterfaceRegistry.v1",
        "registry_id": REGISTRY_ID,
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "PARTIAL",
        "entries": entries,
        "summary": {
            "entry_count": len(entries),
            "by_stability_class": counts,
            "supported_count": counts.get("SUPPORTED", 0),
            "unregistered_candidate_roots": unregistered,
        },
        "notes": [
            "Merged WS1 registry: stabilization_readiness + curated production surfaces.",
            "SUPPORTED: canonical_json (WS1.6), run_fast_ci (WS1.7).",
            "COMPATIBILITY.md roots (pipelines, yggdrasil, CLI) registered as ADVISORY roots.",
            "Boundary/sole-writer checks are report-only in run_fast_ci (RISK-008 MITIGATING).",
        ],
    }

    if write:
        out_dir = repo_root / WS1_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "interface_registry_snapshot.v1.json", registry)

        progress = {
            "schema_version": "ws1_progress_receipt.v1",
            "artifact_type": "ws1_progress_receipt",
            "produced_at": produced_at,
            "producer": PRODUCER,
            "repository_sha": sha,
            "evidence_state": "PARTIAL",
            "workstream": "WS1_Kernel_Contract_Stabilization",
            "completed_this_increment": [
                "WS1.7: sole-writer heuristic hardened (exclude tests/; write+out same-line)",
                "WS1.7: promoted run_fast_ci to SUPPORTED (second supported interface)",
                "WS1.6 retained: canonical_json SUPPORTED",
                "Boundary advisory remains report-only with seeded import allow-list",
            ],
            "ws1_actions_status": {
                "formalize_stability_classes": "DONE",
                "canonical_interface_registry": "DONE_MERGED_GENERATOR",
                "tighten_sole_writer_evidence": "DONE_HARDENED_REPORT_ONLY",
                "boundary_advisory_check": "DONE_REPORT_ONLY_IN_FAST_CI",
                "supported_promotions": "canonical_json,run_fast_ci",
                "risk_008_status": "MITIGATING",
                "risk_011_status": "MITIGATING",
                "close_risk_006_live_validation": "CLOSED_IN_WS0",
                "neon_genie_advisory_only": "CONFIRMED",
            },
            "summary": registry["summary"],
            "fail_closed_promotion_criteria": [
                "false_positive_rate low enough for N consecutive green main days",
                "allow_list owned, reviewed, versioned",
                "supported_count >= 1 with real tests",
                "operator explicitly approves fail-closed",
            ],
            "next_recommended": [
                "Triage remaining sole-writer findings in core/ (builder vs runner debt)",
                "Expand per-schema registration under pipelines/yggdrasil",
                "Third SUPPORTED only with contract tests (e.g. receipt builder if canonicalized)",
                "Do not fail-close sole-writer while core/ still has 100+ candidate writes",
            ],
            "notes": [
                "Advisory checks remain fail-open inside run_fast_ci.",
                "supported_count==2 does not make the platform production-ready.",
                "No production activation or authority expansion.",
            ],
        }
        write_canonical_json(out_dir / "ws1_progress_receipt.v1.json", progress)

    return registry
