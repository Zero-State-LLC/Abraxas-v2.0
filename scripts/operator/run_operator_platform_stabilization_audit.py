#!/usr/bin/env python3
"""Emit deterministic advisory receipts for the operator-platform stabilization slice."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps" / "aal-viz-live-console"
SCHEMA_PATH = ROOT / "contracts" / "canon" / "aal_viz_operator_platform_projection.v0.2.schema.json"
RUNTIME_VALIDATOR_PATH = APP / "src" / "data" / "operatorPlatformContract.ts"
DEPENDENCY_RECEIPT_PATH = ROOT / "out" / "audit" / "operator_platform_dependency_risk_001.latest.json"
PARITY_RECEIPT_PATH = ROOT / "out" / "audit" / "operator_platform_cross_language_parity_001.latest.json"

SECTION_NAMES = [
    "system_status",
    "topology",
    "production_slice",
    "contract_graph",
    "evidence_index",
    "temporal_diff",
]
SECTION_STATUSES = ["AVAILABLE", "PARTIAL", "NOT_COMPUTABLE"]
PROVENANCE = ["OBSERVED", "INFERRED"]
ENTITY_TYPES = ["SYSTEM", "RUNE", "CONTRACT", "PACKET", "RECEIPT", "ROUTE"]
# Canonical ops must match contracts/canon/aal_viz_operator_platform_projection.v0.2.schema.json
# and apps/.../operatorPlatformContract.ts TEMPORAL_OPERATIONS. UNCHANGED is legacy-only in TS.
TEMPORAL_OPERATIONS = ["ADDED", "REMOVED", "CHANGED", "NOT_COMPUTABLE"]


def _canonical_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_receipt(path: Path, payload: dict[str, Any]) -> None:
    receipt = {**payload, "canonical_hash": _canonical_hash(payload)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_dependency_receipt() -> dict[str, Any]:
    lock_bytes = (APP / "package-lock.json").read_bytes()
    return {
        "schema_version": "OperatorPlatformDependencyRiskReceipt.v1",
        "receipt_id": "OPERATOR_PLATFORM_DEPENDENCY_RISK_001",
        "status": "DEVELOPMENT_RISKS_BOUNDED",
        "advisory_only": True,
        "production_runtime_vulnerability_count": 0,
        "audit_commands": ["npm audit --json", "npm audit --omit=dev --json", "npm outdated --json"],
        "lockfile_sha256": hashlib.sha256(lock_bytes).hexdigest(),
        "findings": [
            {
                "package": "vitest",
                "severity": "critical",
                "classifications": ["DIRECT_DEPENDENCY", "TEST_ONLY", "BUILD_CHAIN", "FIX_AVAILABLE_BREAKING"],
                "dependency_path": ["vitest"],
                "runtime_reachability": "NOT_PRODUCTION_RUNTIME_REACHABLE",
                "exploit_preconditions": "Vitest UI server must be explicitly started and network reachable; no UI script is configured.",
                "fixed_version": ">=3.2.6 (npm recommends 4.1.10)",
                "breaking_change_risk": "HIGH",
                "disposition": "DEFER_MAJOR_TOOLCHAIN_UPGRADE_AND_DO_NOT_RUN_VITEST_UI_SERVER",
            },
            {
                "package": "vite",
                "severity": "high",
                "classifications": ["DIRECT_DEPENDENCY", "BUILD_CHAIN", "FIX_AVAILABLE_BREAKING"],
                "dependency_path": ["vite"],
                "runtime_reachability": "DEVELOPMENT_SERVER_ONLY",
                "exploit_preconditions": "An affected development server must be reachable by an attacker.",
                "fixed_version": "8.1.4",
                "breaking_change_risk": "HIGH",
                "disposition": "BIND_LOOPBACK_RESTRICT_HOSTS_AND_DEFER_MAJOR_TOOLCHAIN_UPGRADE",
            },
            {
                "package": "esbuild",
                "severity": "moderate",
                "classifications": ["TRANSITIVE", "BUILD_CHAIN", "FIX_AVAILABLE_BREAKING"],
                "dependency_path": ["vite", "esbuild"],
                "runtime_reachability": "DEVELOPMENT_SERVER_ONLY",
                "exploit_preconditions": "An affected Vite development server must be network reachable.",
                "fixed_version": "via Vite 8.1.4",
                "breaking_change_risk": "HIGH",
                "disposition": "MITIGATED_BY_LOOPBACK_BINDING",
            },
            {
                "package": "@vitest/mocker",
                "severity": "moderate",
                "classifications": ["TRANSITIVE", "TEST_ONLY", "FIX_AVAILABLE_BREAKING"],
                "dependency_path": ["vitest", "@vitest/mocker"],
                "runtime_reachability": "NOT_PRODUCTION_RUNTIME_REACHABLE",
                "exploit_preconditions": "Test tooling must be invoked.",
                "fixed_version": "via Vitest 4.1.10",
                "breaking_change_risk": "HIGH",
                "disposition": "DEFER_MAJOR_TOOLCHAIN_UPGRADE",
            },
            {
                "package": "vite-node",
                "severity": "moderate",
                "classifications": ["TRANSITIVE", "TEST_ONLY", "FIX_AVAILABLE_BREAKING"],
                "dependency_path": ["vitest", "vite-node"],
                "runtime_reachability": "NOT_PRODUCTION_RUNTIME_REACHABLE",
                "exploit_preconditions": "Test tooling must be invoked.",
                "fixed_version": "via Vitest 4.1.10",
                "breaking_change_risk": "HIGH",
                "disposition": "DEFER_MAJOR_TOOLCHAIN_UPGRADE",
            },
        ],
        "authority": {"projection_only": True, "runtime_mutation_allowed": False},
    }


def build_parity_receipt() -> dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    runtime_text = RUNTIME_VALIDATOR_PATH.read_text(encoding="utf-8")
    checks: list[dict[str, str]] = []
    for value in SECTION_NAMES + SECTION_STATUSES + PROVENANCE + ENTITY_TYPES + TEMPORAL_OPERATIONS:
        observed = value in json.dumps(schema, sort_keys=True) and f"'{value}'" in runtime_text
        checks.append({"symbol": value, "status": "MATCH" if observed else "MISMATCH"})
    required = set(schema.get("required", []))
    for section in SECTION_NAMES:
        checks.append({"symbol": f"required:{section}", "status": "MATCH" if section in required else "MISMATCH"})
    status = "PARITY_CONFIRMED" if all(check["status"] == "MATCH" for check in checks) else "PARITY_FAILED"
    return {
        "schema_version": "OperatorPlatformCrossLanguageParityReceipt.v1",
        "receipt_id": "OPERATOR_PLATFORM_CROSS_LANGUAGE_PARITY_001",
        "status": status,
        "advisory_only": True,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "runtime_validator_path": str(RUNTIME_VALIDATOR_PATH.relative_to(ROOT)),
        "checks": checks,
        "authority": {"projection_only": True, "runtime_mutation_allowed": False},
    }


def main() -> int:
    dependency = build_dependency_receipt()
    parity = build_parity_receipt()
    _write_receipt(DEPENDENCY_RECEIPT_PATH, dependency)
    _write_receipt(PARITY_RECEIPT_PATH, parity)
    print(f"{dependency['status']} -> {DEPENDENCY_RECEIPT_PATH.relative_to(ROOT)}")
    print(f"{parity['status']} -> {PARITY_RECEIPT_PATH.relative_to(ROOT)}")
    return 0 if parity["status"] == "PARITY_CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
