"""Executable-surface and interface inventory for Production Convergence Phase 1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

ENTRYPOINT_CLASSES = (
    "SUPPORTED_CLI",
    "SUPPORTED_SERVICE",
    "SUPPORTED_LIBRARY_API",
    "INTERNAL_ENGINEERING_TOOL",
    "MIGRATION",
    "FIXTURE_OR_TEST",
    "EXPERIMENTAL",
    "GENERATED_RUNNER",
    "DEPRECATED",
    "INACTIVE_OR_DEAD",
    "UNKNOWN",
)

INTERFACE_CLASSES = (
    "SUPPORTED",
    "INTERNAL",
    "EXPERIMENTAL",
    "DEPRECATED",
    "ACCIDENTALLY_PUBLIC",
)

# Domain → default classification for scripts/<domain>/run_*.py
_DOMAIN_DEFAULT: dict[str, str] = {
    "alembic": "EXPERIMENTAL",
    "artifact": "INTERNAL_ENGINEERING_TOOL",
    "belief": "INTERNAL_ENGINEERING_TOOL",
    "campaign": "INTERNAL_ENGINEERING_TOOL",
    "codegen": "INTERNAL_ENGINEERING_TOOL",
    "geometry": "INTERNAL_ENGINEERING_TOOL",
    "governance": "INTERNAL_ENGINEERING_TOOL",
    "hygiene": "INTERNAL_ENGINEERING_TOOL",
    "ingest": "INTERNAL_ENGINEERING_TOOL",
    "metric": "INTERNAL_ENGINEERING_TOOL",
    "notion": "INTERNAL_ENGINEERING_TOOL",
    "operator": "INTERNAL_ENGINEERING_TOOL",
    "readiness": "INTERNAL_ENGINEERING_TOOL",
    "research": "INTERNAL_ENGINEERING_TOOL",
    "runtime": "INTERNAL_ENGINEERING_TOOL",
    "temporal": "INTERNAL_ENGINEERING_TOOL",
    "tools": "INTERNAL_ENGINEERING_TOOL",
    "transport": "INTERNAL_ENGINEERING_TOOL",
    "viz": "INTERNAL_ENGINEERING_TOOL",
}

_PATH_OVERRIDES: dict[str, dict[str, Any]] = {
    "scripts/run_fast_ci.py": {
        "classification": "SUPPORTED_CLI",
        "owner_module": "scripts",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": None,
        "confidence": "HIGH",
        "notes": "SUPPORTED pre-PR validation entry (WS1 interface registry).",
    },
    "scripts/run_validation_service.py": {
        "classification": "SUPPORTED_SERVICE",
        "owner_module": "core.services.validation_service",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": "apps/api validation router + library API",
        "confidence": "HIGH",
    },
    "scripts/artifact/run_artifact_provenance_service.py": {
        "classification": "SUPPORTED_LIBRARY_API",
        "owner_module": "core.services.artifact_provenance_service",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": "unified abraxas CLI analyze/validate",
        "confidence": "HIGH",
    },
    "scripts/alembic/run_alembic_spine.py": {
        "classification": "EXPERIMENTAL",
        "owner_module": "core.alembic",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": "abraxas analyze --architecture-route (future CLI)",
        "confidence": "HIGH",
        "notes": "Alembic Spine advisory CLI; not a parallel product kernel.",
    },
    "apps/api/main.py": {
        "classification": "SUPPORTED_SERVICE",
        "owner_module": "apps.api",
        "activation_lane": "SANDBOX",
        "replacement_candidate": "create_app(settings) factory (Phase 8)",
        "confidence": "HIGH",
    },
    "api/hybrid_server.py": {
        "classification": "EXPERIMENTAL",
        "owner_module": "api",
        "activation_lane": "SANDBOX",
        "replacement_candidate": "apps/api/main.py",
        "confidence": "MEDIUM",
    },
    "api/sse_server.py": {
        "classification": "EXPERIMENTAL",
        "owner_module": "api",
        "activation_lane": "SANDBOX",
        "replacement_candidate": "apps/api/main.py",
        "confidence": "MEDIUM",
    },
    "api/websocket_server.py": {
        "classification": "EXPERIMENTAL",
        "owner_module": "api",
        "activation_lane": "SANDBOX",
        "replacement_candidate": "apps/api/main.py",
        "confidence": "MEDIUM",
    },
    "core/canonical/json.py": {
        "classification": "SUPPORTED_LIBRARY_API",
        "owner_module": "core.canonical",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": None,
        "confidence": "HIGH",
    },
    "core/services/validation_service.py": {
        "classification": "SUPPORTED_LIBRARY_API",
        "owner_module": "core.services",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": None,
        "confidence": "HIGH",
    },
    "core/services/artifact_provenance_service.py": {
        "classification": "SUPPORTED_LIBRARY_API",
        "owner_module": "core.services",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": None,
        "confidence": "HIGH",
    },
    "core/governance/activation_policy.py": {
        "classification": "SUPPORTED_LIBRARY_API",
        "owner_module": "core.governance",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": None,
        "confidence": "HIGH",
        "notes": "Canonical bounded activation policy (Governance V3).",
    },
    "core/application/advisory_spine.py": {
        "classification": "SUPPORTED_LIBRARY_API",
        "owner_module": "core.application",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": None,
        "confidence": "HIGH",
        "notes": "Golden-path application orchestration (advisory).",
    },
    "abraxas/__init__.py": {
        "classification": "UNKNOWN",
        "owner_module": "abraxas",
        "activation_lane": "LOCAL_DEV",
        "replacement_candidate": "abraxas.AbraxasClient public API",
        "confidence": "MEDIUM",
        "notes": "Package root exists but is not yet a supported product client.",
    },
}


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _domain_for_runner(rel: str) -> str:
    parts = Path(rel).parts
    if len(parts) >= 3 and parts[0] == "scripts":
        return parts[1]
    if rel == "scripts/run_fast_ci.py":
        return "_root"
    return "_unknown"


def _classify_runner(rel: str, domain: str) -> dict[str, Any]:
    if rel in _PATH_OVERRIDES:
        override = dict(_PATH_OVERRIDES[rel])
        classification = override.pop("classification")
        return {
            "path": rel,
            "classification": classification,
            "owner_module": override.get("owner_module", f"scripts.{domain}"),
            "inputs": ["CLI args", "RuntimePaths / fixtures"],
            "outputs": ["stdout", "optional out/ artifacts"],
            "writes_to_disk": True,
            "external_io": False,
            "activation_lane": override.get("activation_lane", "LOCAL_DEV"),
            "called_by": ["operators", "CI"] if classification.startswith("SUPPORTED") else ["operators"],
            "calls": [override.get("owner_module", "core")],
            "tests": _guess_tests(rel),
            "replacement_candidate": override.get("replacement_candidate"),
            "confidence": override.get("confidence", "MEDIUM"),
            "notes": override.get("notes"),
        }

    name = Path(rel).name.lower()
    classification = _DOMAIN_DEFAULT.get(domain, "UNKNOWN")
    confidence = "MEDIUM" if classification != "UNKNOWN" else "LOW"
    notes = None

    ceremony_tokens = (
        "authorization",
        "decision_record",
        "eligibility",
        "approval",
        "seal",
        "operator_review",
        "gate_",
        "_gate",
    )
    if any(token in name for token in ceremony_tokens):
        classification = "GENERATED_RUNNER"
        confidence = "MEDIUM"
        notes = "Historical governance/ceremony runner; not a product entry point."
    elif "receipt" in name or "plan" in name:
        classification = "GENERATED_RUNNER"
        confidence = "MEDIUM"
        notes = "Receipt/plan emitter; classify as audit/workflow, not product spine."
    elif "fixture" in name or "fixture" in domain:
        classification = "FIXTURE_OR_TEST"
    elif "migrat" in name:
        classification = "MIGRATION"

    return {
        "path": rel,
        "classification": classification,
        "owner_module": f"scripts.{domain}" if domain not in {"_root", "_unknown"} else "scripts",
        "inputs": ["CLI args", "prior artifacts / fixtures"],
        "outputs": ["out/ artifacts", "stdout"],
        "writes_to_disk": True,
        "external_io": domain in {"notion"} or "notion" in name or "external" in name,
        "activation_lane": "LOCAL_DEV",
        "called_by": ["operators", "agents"],
        "calls": ["core/* builders"],
        "tests": _guess_tests(rel),
        "replacement_candidate": "unified abraxas CLI subcommand or archive",
        "confidence": confidence,
        "notes": notes,
    }


def _guess_tests(rel: str) -> list[str]:
    stem = Path(rel).stem
    candidates = [
        f"tests/test_{stem}.py",
        f"tests/test_{stem.removeprefix('run_')}.py",
    ]
    return candidates


def build_entrypoint_inventory(repo_root: Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    entries: list[dict[str, Any]] = []

    for path in sorted(root.glob("scripts/**/run_*.py")):
        rel = _rel(path, root)
        domain = _domain_for_runner(rel)
        entries.append(_classify_runner(rel, domain))

    # Non-runner executable / library surfaces declared in overrides.
    for rel in sorted(_PATH_OVERRIDES):
        is_runner = rel.endswith("run_fast_ci.py") or (
            rel.startswith("scripts/") and Path(rel).name.startswith("run_")
        )
        if is_runner or any(e["path"] == rel for e in entries):
            continue
        path = root / rel
        override = dict(_PATH_OVERRIDES[rel])
        classification = override.pop("classification")
        entries.append(
            {
                "path": rel,
                "classification": classification,
                "owner_module": override.get("owner_module"),
                "inputs": ["library/service call"],
                "outputs": ["typed responses / artifacts via runners"],
                "writes_to_disk": False,
                "external_io": False,
                "activation_lane": override.get("activation_lane", "LOCAL_DEV"),
                "called_by": ["CLI", "API", "tests"],
                "calls": [],
                "tests": _guess_tests(rel),
                "replacement_candidate": override.get("replacement_candidate"),
                "confidence": override.get("confidence", "MEDIUM"),
                "notes": override.get("notes"),
                "presence": "OBSERVED" if path.exists() else "DECLARED_IN_INVENTORY",
            }
        )

    # Shell scripts
    for path in sorted(root.glob("scripts/**/*.sh")):
        rel = _rel(path, root)
        entries.append(
            {
                "path": rel,
                "classification": "INTERNAL_ENGINEERING_TOOL",
                "owner_module": "scripts",
                "inputs": ["shell env"],
                "outputs": ["process side effects"],
                "writes_to_disk": True,
                "external_io": False,
                "activation_lane": "LOCAL_DEV",
                "called_by": ["operators"],
                "calls": [],
                "tests": [],
                "replacement_candidate": None,
                "confidence": "MEDIUM",
            }
        )

    by_class: dict[str, int] = {c: 0 for c in ENTRYPOINT_CLASSES}
    unknown: list[str] = []
    for entry in entries:
        cls = entry["classification"]
        by_class[cls] = by_class.get(cls, 0) + 1
        if cls == "UNKNOWN":
            unknown.append(entry["path"])

    payload = {
        "artifact_type": "entrypoint_inventory",
        "schema_version": "entrypoint_inventory.v1",
        "evidence_state": "Partial",
        "classification_method": "path_override_plus_domain_heuristic",
        "notes": [
            "OBSERVED: 700+ scripts/run_*.py surfaces exist; most are engineering/ceremony tools.",
            "UNKNOWN entries must not be silently ignored in later CLEAR phases.",
            "Alembic CLI is EXPERIMENTAL advisory specialist, not a second product OS.",
        ],
        "summary": {
            "entry_count": len(entries),
            "by_classification": by_class,
            "unknown_count": len(unknown),
            "unknown_paths": unknown,
            "supported_count": sum(
                by_class.get(c, 0)
                for c in ("SUPPORTED_CLI", "SUPPORTED_SERVICE", "SUPPORTED_LIBRARY_API")
            ),
        },
        "entries": entries,
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload


def build_interface_inventory(repo_root: Path) -> dict[str, Any]:
    """Curated public/semipublic interface inventory (assimilates WS1 registry)."""
    root = Path(repo_root).resolve()
    ws1 = root / "out/production_readiness/ws1/interface_registry_snapshot.v1.json"
    interfaces: list[dict[str, Any]] = [
        {
            "name": "canonical_json",
            "path": "core/canonical/json.py",
            "classification": "SUPPORTED",
            "kind": "library",
            "evidence": ["out/production_readiness/ws1/interface_registry_snapshot.v1.json"],
        },
        {
            "name": "run_fast_ci",
            "path": "scripts/run_fast_ci.py",
            "classification": "SUPPORTED",
            "kind": "cli",
            "evidence": ["out/production_readiness/ws1/interface_registry_snapshot.v1.json"],
        },
        {
            "name": "validation_service.v1",
            "path": "core/services/validation_service.py",
            "classification": "SUPPORTED",
            "kind": "library_service",
            "evidence": ["out/production_readiness/ws1/interface_registry_snapshot.v1.json"],
        },
        {
            "name": "artifact_and_provenance_service.v0",
            "path": "core/services/artifact_provenance_service.py",
            "classification": "SUPPORTED",
            "kind": "library_service",
            "evidence": ["out/production_readiness/ws1/interface_registry_snapshot.v1.json"],
        },
        {
            "name": "activation_policy",
            "path": "core/governance/activation_policy.py",
            "classification": "SUPPORTED",
            "kind": "library",
            "evidence": [
                "GOVERNANCE_V3.md",
                "docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md",
                "docs/adr/ADR-0017-BOUNDED-ACTIVATION-POLICY.md",
            ],
        },
        {
            "name": "apps_api",
            "path": "apps/api/main.py",
            "classification": "SUPPORTED",
            "kind": "service",
            "evidence": ["apps/api/main.py", "tests/test_api.py"],
            "notes": "Module-level FastAPI app; create_app(settings) still a Phase 8 target.",
        },
        {
            "name": "advisory_spine",
            "path": "core/application/advisory_spine.py",
            "classification": "INTERNAL",
            "kind": "application",
            "evidence": ["docs/architecture/PRODUCTION_TARGET_ARCHITECTURE_001.md"],
            "notes": "Golden-path orchestrator; promote after integration tests harden.",
        },
        {
            "name": "alembic_spine",
            "path": "core/alembic/pipeline.py",
            "classification": "EXPERIMENTAL",
            "kind": "specialist_orchestrator",
            "evidence": [
                "docs/alembic/ALEMBIC_SPINE.md",
                "contracts/pipelines/alembic_spine.v1_1.json",
                "contracts/yggdrasil/routes/alembic_spine.route.v1.json",
            ],
            "notes": "Optional architecture-routing stage on the golden path; ADVISORY_ONLY.",
        },
        {
            "name": "abraxas_package_root",
            "path": "abraxas/__init__.py",
            "classification": "ACCIDENTALLY_PUBLIC",
            "kind": "package",
            "notes": "Empty product namespace; target AbraxasClient not yet implemented.",
        },
        {
            "name": "legacy_api_servers",
            "path": "api/",
            "classification": "EXPERIMENTAL",
            "kind": "service",
            "notes": "hybrid/sse/websocket servers; converge under apps/api.",
        },
    ]

    by_class: dict[str, int] = {c: 0 for c in INTERFACE_CLASSES}
    for item in interfaces:
        by_class[item["classification"]] = by_class.get(item["classification"], 0) + 1

    payload = {
        "artifact_type": "interface_inventory",
        "schema_version": "interface_inventory.v1",
        "evidence_state": "Partial",
        "ws1_registry_present": ws1.is_file(),
        "ws1_registry_path": "out/production_readiness/ws1/interface_registry_snapshot.v1.json",
        "notes": [
            "Assimilates WS1 SUPPORTED set; does not create a parallel promotion authority.",
            "activation_policy added as SUPPORTED library under Governance V3.",
            "alembic_spine remains EXPERIMENTAL specialist, not a supported product API.",
        ],
        "summary": {
            "interface_count": len(interfaces),
            "by_classification": by_class,
            "supported_count": by_class.get("SUPPORTED", 0),
        },
        "interfaces": interfaces,
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
