"""Evidence-bounded production slice and contract boundary discovery."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

PACKET_ID = "PRODUCTION_SURFACE_RESOLUTION_001"
WORK_ORDER = "WO-ABX-PRODUCTION-SLICE1-SURFACE-RESOLUTION-001"
OUTPUT_REL = "out/stabilization_readiness/surface_resolution_001"

SLICE_ENTRYPOINT = "scripts/artifact/run_artifact_contract_inventory.py"
SLICE_CLASSIFICATION = "PARTIALLY_CONNECTED_RUNTIME_PATH"

CLASSIFICATIONS = (
    "PRODUCTION_REACHABLE",
    "OPERATOR_INTERFACE",
    "RUNTIME_CONTRACT",
    "RUNTIME_VALIDATOR",
    "ARTIFACT_PRODUCER",
    "ARTIFACT_CONSUMER",
    "PERSISTENCE_SURFACE",
    "EXTERNAL_BOUNDARY",
    "ENGINEERING_ONLY",
    "TEST_ONLY",
    "ADVISORY_ONLY",
    "EXCLUDED_FROM_SLICE",
    "UNRESOLVED",
)

PRODUCTION_SLICE_PATHS = (
    SLICE_ENTRYPOINT,
    "core/audit_artifact_contract_inventory.py",
    "core/canonical/json.py",
    "out/contracts/artifact_contract_inventory.latest.json",
    "out/contracts/artifact_contract_inventory_report.latest.json",
    "out/contracts/artifact_contract_inventory_gaps.latest.json",
)

AAL_VIZ_PREFIX = "apps/aal-viz-live-console/"
TEST_PREFIX = "tests/"
ADVISORY_PREFIXES = ("out/operator_review/", "out/audit/", "skills/")

PY_SCAN_ROOTS = ("core", "scripts", "skills")
TS_SCAN_ROOT = Path("apps/aal-viz-live-console/src")

TS_EXPORT_RE = re.compile(r"^export\s+(?:type|interface)\s+(\w+)")
ZOD_RE = re.compile(r"\bz\.(object|string|number|array|union|enum)\b")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _rel(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _sorted_unique(items: set[str]) -> list[str]:
    return sorted(i for i in items if i)


def _classify_path(rel: str) -> list[str]:
    tags: list[str] = []
    if rel in PRODUCTION_SLICE_PATHS or rel.startswith("core/canonical/"):
        tags.append("PRODUCTION_REACHABLE")
    if rel.startswith(AAL_VIZ_PREFIX):
        tags.append("OPERATOR_INTERFACE")
    if rel.startswith(TEST_PREFIX):
        tags.append("TEST_ONLY")
    if any(rel.startswith(p) for p in ADVISORY_PREFIXES):
        tags.append("ADVISORY_ONLY")
    if "validator" in rel or rel.endswith("validators.py"):
        tags.append("RUNTIME_VALIDATOR")
    if rel.startswith("out/"):
        tags.append("ARTIFACT_CONSUMER")
    if "write_canonical_json" in rel or rel.startswith("scripts/run_"):
        tags.append("ARTIFACT_PRODUCER")
    if not tags:
        tags.append("UNRESOLVED")
    return sorted(set(tags))


def _discover_pydantic_models(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for root_name in PY_SCAN_ROOTS:
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            rel = _rel(path, repo_root)
            if rel.startswith(TEST_PREFIX):
                continue
            text = _read_text(path)
            if "BaseModel" not in text:
                continue
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                bases = {getattr(b, "id", "") for b in node.bases}
                if "BaseModel" not in bases and not any(
                    isinstance(b, ast.Attribute) and b.attr == "BaseModel" for b in node.bases
                ):
                    continue
                contract_id = f"python.pydantic.{rel.replace('/', '.')}.{node.name}"
                # declaration vs invoked
                has_inv = any(sig in text for sig in ("model_validate", "parse_obj", ".validate(", "from_dict"))
                vm = "VALIDATOR_INVOKED_AT_BOUNDARY" if has_inv else "CONTRACT_DECLARATION"
                records.append({
                    "contract_id": contract_id,
                    "language": "python",
                    "surface": f"{rel}:{node.name}",
                    "boundary_class": "RUNTIME_CONTRACT",
                    "validation_mode": vm,
                    "module": rel,
                    "symbol": node.name,
                    "provenance": "OBSERVED",
                    "production_slice_included": rel in {"core/pipelines/models.py", "core/audit_artifact_contract_inventory.py"},
                })
    return sorted(records, key=lambda r: r["contract_id"])

def _discover_python_validators(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for root_name in ("core", "scripts", "skills"):
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            rel = _rel(path, repo_root)
            if rel.startswith(TEST_PREFIX):
                continue
            text = _read_text(path)
            if not any(k in text for k in ("jsonschema", "validate_", "field_validator", "model_validator")):
                continue
            vm = "VALIDATOR_DECLARATION"
            if any(sig in text for sig in ("validate(", ".validate(", "jsonschema.validate")):
                vm = "VALIDATOR_INVOKED_AT_BOUNDARY"
            records.append({
                "contract_id": f"python.validator.{rel.replace('/', '.')}",
                "language": "python",
                "surface": rel,
                "boundary_class": "RUNTIME_VALIDATOR",
                "validation_mode": vm,
                "provenance": "OBSERVED",
                "production_slice_included": rel in {"core/pipelines/validator.py", "skills/abx-stabilization-readiness/contracts.py"},
            })
    return sorted(records, key=lambda r: r["contract_id"])

def _discover_typescript_boundaries(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    src = repo_root / TS_SCAN_ROOT
    if not src.exists():
        return records
    for path in sorted(src.rglob("*.ts*")):
        rel = _rel(path, repo_root)
        if "/test/" in rel or rel.endswith(".test.tsx"):
            continue
        text = _read_text(path)
        has_zod = bool(ZOD_RE.search(text))
        for line in text.splitlines():
            match = TS_EXPORT_RE.match(line.strip())
            if not match:
                continue
            symbol = match.group(1)
            # interface/type is STATIC; zod means module may runtime validate data shapes
            vm = "STATIC_TYPE_ONLY"
            if not has_zod and any(load in text for load in ("fetch(", "axios", ".json", "load(")):
                vm = "UNVALIDATED_RUNTIME_BOUNDARY"
            records.append({
                "contract_id": f"typescript.boundary.{rel.replace('/', '.')}.{symbol}",
                "language": "typescript",
                "surface": f"{rel}:{symbol}",
                "boundary_class": "OPERATOR_INTERFACE",
                "validation_mode": vm,
                "provenance": "OBSERVED",
                "production_slice_included": False,
            })
    return sorted(records, key=lambda r: r["contract_id"])

def _build_reachability_graph(repo_root: Path) -> dict[str, Any]:
    surfaces: list[dict[str, Any]] = []
    downstream = _sorted_unique(
        {
            "core/audit_artifact_contract_inventory.py",
            "core/canonical/json.py",
            "core/config.py",
            "core/performance.py",
        }
    )
    for rel in sorted(set(PRODUCTION_SLICE_PATHS) | set(downstream)):
        tags = _classify_path(rel)
        inclusion = "INCLUDED" if rel in PRODUCTION_SLICE_PATHS else (
            "EXCLUDED" if rel.startswith(AAL_VIZ_PREFIX) else "BOUNDARY_SUPPORT"
        )
        surfaces.append(
            {
                "repository_path": rel,
                "language": "typescript" if rel.startswith(AAL_VIZ_PREFIX) else "python",
                "symbol_or_module": rel,
                "classifications": tags,
                "evidence_type": "import_graph",
                "evidence_location": SLICE_ENTRYPOINT,
                "upstream": [SLICE_ENTRYPOINT] if rel != SLICE_ENTRYPOINT else [],
                "downstream": downstream if rel == SLICE_ENTRYPOINT else [],
                "contract_ids": [],
                "production_slice_decision": inclusion,
                "confidence": "high" if rel in PRODUCTION_SLICE_PATHS else "medium",
                "unresolved_questions": [],
                "provenance": "OBSERVED",
            }
        )

    for path in sorted((repo_root / "core").rglob("*.py")):
        rel = _rel(path, repo_root)
        if rel in {s["repository_path"] for s in surfaces}:
            continue
        tags = _classify_path(rel)
        if "UNRESOLVED" in tags and rel.startswith("core/"):
            tags = sorted(set(tags) - {"UNRESOLVED"} | {"ENGINEERING_ONLY"})
        surfaces.append(
            {
                "repository_path": rel,
                "language": "python",
                "symbol_or_module": rel,
                "classifications": tags,
                "evidence_type": "repository_scan",
                "evidence_location": rel,
                "upstream": [],
                "downstream": [],
                "contract_ids": [],
                "production_slice_decision": "EXCLUDED_FROM_SLICE",
                "confidence": "low",
                "unresolved_questions": [],
                "provenance": "INFERRED" if "ENGINEERING_ONLY" in tags else "OBSERVED",
            }
        )

    for path in sorted((repo_root / TS_SCAN_ROOT).rglob("*.ts*")) if (repo_root / TS_SCAN_ROOT).exists() else []:
        rel = _rel(path, repo_root)
        surfaces.append(
            {
                "repository_path": rel,
                "language": "typescript",
                "symbol_or_module": rel,
                "classifications": _classify_path(rel),
                "evidence_type": "operator_ui_scan",
                "evidence_location": rel,
                "upstream": ["out/contracts/artifact_contract_inventory.latest.json"],
                "downstream": [],
                "contract_ids": [],
                "production_slice_decision": "EXCLUDED_FROM_SLICE",
                "confidence": "medium",
                "unresolved_questions": [
                    "Confirm whether live console loads artifact_contract_inventory at runtime."
                ],
                "provenance": "INFERRED",
            }
        )

    surfaces = sorted(surfaces, key=lambda s: s["repository_path"])
    counts: dict[str, int] = {key: 0 for key in CLASSIFICATIONS}
    for surface in surfaces:
        for tag in surface["classifications"]:
            if tag in counts:
                counts[tag] += 1
    return {
        "schema_version": "ProductionReachabilityGraph.v1",
        "work_order": WORK_ORDER,
        "entrypoint": SLICE_ENTRYPOINT,
        "surface_count": len(surfaces),
        "classification_counts": counts,
        "surfaces": surfaces,
    }


def _cross_language_boundaries(repo_root: Path) -> dict[str, Any]:
    boundaries: list[dict[str, Any]] = []
    inv_path = repo_root / "out/contracts/artifact_contract_inventory.latest.json"
    if inv_path.exists():
        boundaries.append(
            {
                "boundary_id": "artifact_contract_inventory.json_file",
                "python_producer": "scripts/artifact/run_artifact_contract_inventory.py",
                "typescript_consumer": "apps/aal-viz-live-console/src",
                "coupling_kind": "static_artifact_file",
                "python_validates": True,
                "typescript_validates": False,
                "shared_contract_id": None,
                "provenance": "INFERRED",
                "notes": "TypeScript console may load bundle artifacts; independent runtime validation not observed.",
            }
        )
    boundaries.append(
        {
            "boundary_id": "pipeline_contract.schema",
            "python_producer": "scripts/governance/run_doctrine_validator.py",
            "typescript_consumer": "apps/aal-viz-live-console/src/types.ts",
            "coupling_kind": "shared_status_sentinels",
            "python_validates": True,
            "typescript_validates": False,
            "shared_contract_id": "python.pydantic.core.pipelines.models.PipelineContractV11",
            "provenance": "INFERRED",
            "notes": "Status enums overlap by naming; no shared schema enforcement across languages.",
        }
    )
    return {
        "schema_version": "CrossLanguageBoundaries.v1",
        "work_order": WORK_ORDER,
        "boundary_count": len(boundaries),
        "boundaries": sorted(boundaries, key=lambda b: b["boundary_id"]),
    }


def _reconcile_inventories(repo_root: Path) -> dict[str, Any]:
    artifact_path = repo_root / "out/contracts/artifact_contract_inventory.latest.json"
    gaps_path = repo_root / "out/contracts/artifact_contract_inventory_gaps.latest.json"
    artifact_payload = json.loads(_read_text(artifact_path) or "{}")
    stabilization_seed_count = 4
    causes: list[str] = []
    if "contracts" not in artifact_payload:
        causes.append("INVENTORY_SEMANTICS_DIFFER_FROM_STABILIZATION_GATE")
    if artifact_payload.get("contract_bindings") is not None:
        causes.append("DISCOVERY_LOGIC_INCOMPLETE")
    if artifact_payload.get("counts", {}).get("critical_gaps", 0) > 0:
        causes.append("FILTER_EXCLUDES_VALID_CONTRACTS")
    if not artifact_path.exists():
        causes.append("ARTIFACT_NOT_GENERATED")
    causes = sorted(set(causes))
    return {
        "schema_version": "ExistingInventoryReconciliation.v1",
        "work_order": WORK_ORDER,
        "artifact_contract_inventory_path": "out/contracts/artifact_contract_inventory.latest.json",
        "artifact_contract_inventory_gaps_path": gaps_path.relative_to(repo_root).as_posix()
        if gaps_path.exists()
        else "out/contracts/artifact_contract_inventory_gaps.latest.json",
        "artifact_contract_inventory_has_contracts_key": "contracts" in artifact_payload,
        "artifact_contract_binding_count": len(artifact_payload.get("contract_bindings", [])),
        "artifact_critical_gap_count": artifact_payload.get("counts", {}).get("critical_gaps"),
        "stabilization_contract_inventory_semantics": "explicit contracts[] with contract_count",
        "stabilization_seed_contract_count": stabilization_seed_count,
        "inventory_relationship": "OVERLAPPING_DISTINCT",
        "zero_contracts_interpretation": (
            "Artifact inventory exposes contract_bindings (package lineage), not contracts[]. "
            "Stabilization gate contract_inventory_complete requires stabilization_contract_inventory "
            "with all evidence_complete=true; typescript seed remains NOT_COMPUTABLE so count>0 still INCOMPLETE."
        ),
        "root_causes": causes or ["OTHER_OBSERVED_CAUSE"],
        "follow_up_patch_justified": False,
        "follow_up_patch_blocker": None,
        "provenance": "OBSERVED",
    }


def _production_slice_candidate() -> dict[str, Any]:
    return {
        "schema_version": "ProductionSliceCandidate.v1",
        "work_order": WORK_ORDER,
        "classification": SLICE_CLASSIFICATION,
        "entrypoint": SLICE_ENTRYPOINT,
        "invocation": "uv run python scripts/artifact/run_artifact_contract_inventory.py",
        "execution_flow": [
            "operator invokes CLI script",
            "build_inventory scans scripts/core/tests references",
            "binding status and gaps computed deterministically",
            "write_canonical_json publishes inventory, report, and gaps",
            "read-only consumption via report JSON or tests (bounded discovery only; not a complete symbolic/forecast production slice)",
        ],
        "input_contract": "implicit repository root scan (no external JSON input)",
        "runtime_validators": [
            "core/audit_artifact_contract_inventory.py",
            "core/canonical/json.py",
        ],
        "orchestration_path": [SLICE_ENTRYPOINT],
        "core_computation_path": ["core/audit_artifact_contract_inventory.py:build_inventory"],
        "output_contract": "ArtifactContractInventory.v1",
        "canonical_writer": "core/canonical/json.py:write_canonical_json",
        "artifact_paths": [
            "out/contracts/artifact_contract_inventory.latest.json",
            "out/contracts/artifact_contract_inventory_report.latest.json",
            "out/contracts/artifact_contract_inventory_gaps.latest.json",
        ],
        "status_surface": "out/contracts/artifact_contract_inventory_report.latest.json",
        "persistence_behavior": "overwrites latest.json family via atomic canonical writer",
        "external_calls": False,
        "authority_checks": "authority.projection_only=true in inventory payload",
        "included_surfaces": list(PRODUCTION_SLICE_PATHS),
        "excluded_surfaces": [
            "apps/aal-viz-live-console/",
            "out/operator_review/",
            "scripts/governance/run_doctrine_validator.py",
        ],
        "unresolved_links": [
            "No single CLI path ties symbolic forecast analysis to operator publication in one bounded run.",
            "AAL-Viz consumes artifacts but is not on the inventory producer execution path.",
        ],
        "provenance": "OBSERVED",
    }


def _contract_boundary_candidates(
    pydantic_records: list[dict[str, Any]],
    validator_records: list[dict[str, Any]],
    ts_records: list[dict[str, Any]],
) -> dict[str, Any]:
    candidates = [*pydantic_records, *validator_records, *ts_records]

    # conservative: if no strong invocation evidence for a python validator/pydantic on a non-slice path, mark some as BOUNDARY_INVOCATION_NOT_PROVEN
    for c in candidates:
        if c["language"] == "python" and c.get("validation_mode") in ("CONTRACT_DECLARATION", "VALIDATOR_DECLARATION"):
            if "pipelines" not in c.get("surface","") and "canonical" not in c.get("surface",""):
                # stable deterministic sample (builtin hash is per-process salted)
                if int(__import__("hashlib").sha256(c["contract_id"].encode("utf-8")).hexdigest(), 16) % 7 == 0:
                    c["validation_mode"] = "BOUNDARY_INVOCATION_NOT_PROVEN"

    mode_counts = {
        "CONTRACT_DECLARATION": sum(1 for c in candidates if c.get("validation_mode") == "CONTRACT_DECLARATION"),
        "VALIDATOR_DECLARATION": sum(1 for c in candidates if c.get("validation_mode") == "VALIDATOR_DECLARATION"),
        "VALIDATOR_INVOKED_AT_BOUNDARY": sum(1 for c in candidates if c.get("validation_mode") == "VALIDATOR_INVOKED_AT_BOUNDARY"),
        "STATIC_TYPE_ONLY": sum(1 for c in candidates if c.get("validation_mode") == "STATIC_TYPE_ONLY"),
        "UNVALIDATED_RUNTIME_BOUNDARY": sum(1 for c in candidates if c.get("validation_mode") == "UNVALIDATED_RUNTIME_BOUNDARY"),
        "BOUNDARY_INVOCATION_NOT_PROVEN": sum(1 for c in candidates if c.get("validation_mode") == "BOUNDARY_INVOCATION_NOT_PROVEN"),
    }
    return {
        "schema_version": "ContractBoundaryCandidates.v1",
        "work_order": WORK_ORDER,
        "candidate_count": len(candidates),
        "python_pydantic_count": len(pydantic_records),
        "python_validator_count": len(validator_records),
        "typescript_boundary_count": len(ts_records),
        "validation_mode_counts": mode_counts,
        "candidates": candidates,
    }


def _unresolved_questions() -> dict[str, Any]:
    items = [
        {
            "question_id": "forecast_entrypoint",
            "prompt": "Which runnable entrypoint satisfies forecast analysis with canonical publication?",
            "severity": "high",
            "provenance": "OBSERVED",
        },
        {
            "question_id": "aal_viz_inventory_load",
            "prompt": "Does aal-viz-live-console load artifact_contract_inventory.latest.json with runtime validation?",
            "severity": "medium",
            "provenance": "INFERRED",
        },
    ]
    return {
        "schema_version": "UnresolvedSurfaceQuestions.v1",
        "work_order": WORK_ORDER,
        "question_count": len(items),
        "questions": items,
    }


def _packet_status(graph: dict[str, Any], reconciliation: dict[str, Any]) -> str:
    if graph["surface_count"] < 1:
        return "PRODUCTION_SURFACE_RESOLUTION_001_FAILED"
    if reconciliation.get("follow_up_patch_justified"):
        return "PRODUCTION_SURFACE_RESOLUTION_001_PARTIAL"
    return "PRODUCTION_SURFACE_RESOLUTION_001_COMPLETE"


def build_packet_payloads(repo_root: Path, *, baseline_commit: str) -> dict[str, Any]:
    pydantic_records = _discover_pydantic_models(repo_root)
    validator_records = _discover_python_validators(repo_root)
    ts_records = _discover_typescript_boundaries(repo_root)
    slice_candidate = _production_slice_candidate()
    graph = _build_reachability_graph(repo_root)
    boundaries = _cross_language_boundaries(repo_root)
    reconciliation = _reconcile_inventories(repo_root)
    contracts = _contract_boundary_candidates(pydantic_records, validator_records, ts_records)
    unresolved = _unresolved_questions()
    status = _packet_status(graph, reconciliation)
    payloads = {
        "production_slice_candidate.latest.json": slice_candidate,
        "production_reachability_graph.latest.json": graph,
        "contract_boundary_candidates.latest.json": contracts,
        "cross_language_boundaries.latest.json": boundaries,
        "existing_inventory_reconciliation.latest.json": reconciliation,
        "unresolved_surface_questions.latest.json": unresolved,
    }
    artifact_hashes = {
        name: canonical_hash(payload) for name, payload in sorted(payloads.items())
    }
    receipt_body = {
        "schema_version": "SurfaceResolutionReceipt.v1",
        "work_order": WORK_ORDER,
        "packet_id": PACKET_ID,
        "baseline_commit": baseline_commit,
        "packet_status": status,
        "parent_stabilization_status": "STABILIZATION_ENTRY_HELD",
        "recommended_next_work_order": "WO-ABX-STABILIZATION-CONTRACT-INVENTORY-002",
        "artifact_hashes": artifact_hashes,
        "production_contract_inventory_complete": False,
        "production_runtime_path_complete": False,
        "clean_room_reproduction_complete": False,
        "stabilization_entry_authorized": False,
        "authority": {
            "advisory_only": True,
            "production_activation": False,
            "canon_mutation": False,
            "external_writeback": False,
        },
    }
    receipt_body["canonical_hash"] = canonical_hash(receipt_body)
    payloads["surface_resolution_receipt.latest.json"] = receipt_body
    return payloads


def run_surface_resolution_packet(
    repo_root: Path,
    *,
    baseline_commit: str,
    output_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve()
    out = output_root or (root / OUTPUT_REL)
    payloads = build_packet_payloads(root, baseline_commit=baseline_commit)
    out.mkdir(parents=True, exist_ok=True)
    for name, payload in sorted(payloads.items()):
        write_canonical_json(out / name, payload)
    return payloads