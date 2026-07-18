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
REGISTRY_ID = "WS1_KERNEL_CONTRACT_STABILIZATION_MERGED_002"
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
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="semver",
        language=["python"],
        producers=["scripts/run_fast_ci.py"],
        consumers=[".github/workflows/ci.yml", "contributors"],
        input_contract="clean worktree preferred; env ABRAXAS_FAST_CI_PYRIGHT_SCOPE",
        output_contract="process exit code; may restore drift under out/",
        error_contract="non-zero exit on check failure; 3=drift; 124=timeout",
        side_effects="may write/restore generated artifacts during validation",
        authorization="local_or_ci_operator",
        determinism="partial (tooling versions, wall-clock)",
        compatibility_policy="COMPATIBILITY.md + CI path filters",
        deprecation_state="active",
        implementation_paths=["scripts/run_fast_ci.py"],
        tests=["tests/test_run_fast_ci.py"],
        evidence=["out/production_readiness/baseline/validation_receipt.v1.json"],
        notes="Mandatory pre-PR gate. Strong SUPPORTED candidate after ownership attestation.",
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
        notes="Report-only write-path heuristic. Not fail-closed.",
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
        stability_class="ADVISORY",
        ownership="abraxas-core",
        version_policy="semver",
        language=["python"],
        producers=["core/canonical/json.py"],
        consumers=["scripts/run_*.py", "core/*"],
        input_contract="JSON-serializable Python values",
        output_contract="canonical JSON text + optional atomic write",
        side_effects="write_canonical_json mutates filesystem atomically",
        authorization="internal_library",
        determinism="declared_deterministic",
        deprecation_state="active",
        implementation_paths=["core/canonical/json.py"],
        tests=["tests/test_canonical_json.py"],
        notes="Canonical serializer. Do not bypass.",
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
            "Merged WS1 registry: all stabilization_readiness schemas + curated production surfaces.",
            "No SUPPORTED promotions in this increment (evidence-gated).",
            "Unregistered COMPATIBILITY.md roots listed for follow-on expansion.",
            "Schema fields expanded optionally; consumers must tolerate new optional keys.",
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
                "Merged interface registry generator (stabilization schemas + curated surfaces)",
                "Expanded optional contract fields (auth, determinism, error, tests, evidence)",
                "Boundary advisory check available (prohibited-import + unregistered surfaces)",
                "Still zero SUPPORTED promotions (intentional)",
            ],
            "ws1_actions_status": {
                "formalize_stability_classes": "DONE",
                "canonical_interface_registry": "DONE_MERGED_GENERATOR",
                "tighten_sole_writer_evidence": "DONE_ADVISORY",
                "boundary_advisory_check": "DONE_ADVISORY",
                "supported_promotions": "NONE",
                "close_risk_006_live_validation": "CLOSED_IN_WS0",
                "neon_genie_advisory_only": "CONFIRMED",
            },
            "summary": registry["summary"],
            "next_recommended": [
                "Run boundary advisory and refine allow-list",
                "Expand registry to pipelines/yggdrasil/CLI operator surfaces",
                "Promote first SUPPORTED only with CI contract tests + ownership attestation",
                "Wire advisory checks into fast CI as report-only after allow-list scrub",
            ],
            "notes": [
                "Advisory checks remain fail-open.",
                "No production activation or authority expansion.",
            ],
        }
        write_canonical_json(out_dir / "ws1_progress_receipt.v1.json", progress)

    return registry
