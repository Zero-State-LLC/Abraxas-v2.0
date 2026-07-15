"""Contract inventory — classify public surfaces (read-only advisory scan)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contracts import CONTRACT_CLASSIFICATIONS
from .models import ContractRecord, stable_hash

INVENTORY_SURFACES = [
    ("python", "core", "CONTRACT.CONTROLLED"),
    ("python", "scripts", "CONTRACT.INTERNAL"),
    ("typescript", "aal-viz", "CONTRACT.CONTROLLED"),
    ("schema", "contracts/", "CONTRACT.VERSIONED"),
    ("cli", "hermes/cli", "CONTRACT.CONTROLLED"),
    ("artifact", "out/", "CONTRACT.CONTROLLED"),
    ("env", "environment", "CONTRACT.CONTROLLED"),
    ("registry", "yggdrasil", "CONTRACT.INTERNAL"),
]


def _schema_files(repo_root: Path) -> List[str]:
    contracts = repo_root / "contracts"
    if not contracts.is_dir():
        return []
    return sorted(str(p.relative_to(repo_root)) for p in contracts.rglob("*.schema.json"))


def _classify_surface(language: str, surface: str, default: str, schemas: List[str]) -> str:
    if surface == "contracts/" and schemas:
        return "CONTRACT.VERSIONED"
    if "status_result" in surface.lower():
        return "CONTRACT.FROZEN"
    return default if default in CONTRACT_CLASSIFICATIONS else "CONTRACT.NOT_COMPUTABLE"


def build_contract_inventory(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = repo_root or Path(".")
    schemas = _schema_files(root)
    records: List[ContractRecord] = []

    for language, surface, default_class in INVENTORY_SURFACES:
        classification = _classify_surface(language, surface, default_class, schemas)
        linked = [s for s in schemas if surface.rstrip("/") in s][:5]
        cid = f"CONTRACT.{language.upper()}.{surface.replace('/', '.').upper()}.V1"
        records.append(
            ContractRecord(
                contract_id=cid,
                language=language,
                surface=surface,
                classification=classification,
                consumers=[],
                validators=["schema_validation"] if linked else [],
                schemas=linked,
                compatibility_policy="BACKWARD_COMPATIBLE",
                evidence_complete=bool(linked) or surface in ("core", "contracts/"),
            )
        )

    # Exemplar frozen contract from spec
    records.append(
        ContractRecord(
            contract_id="CONTRACT.RUNTIME.STATUS_RESULT.V1",
            language="python",
            surface="core.status_result",
            classification="CONTRACT.FROZEN",
            consumers=[],
            validators=[],
            schemas=[],
            compatibility_policy="BACKWARD_COMPATIBLE",
            evidence_complete=False,
        )
    )

    payload = {
        "boundary": "ADVISORY_ONLY | CLASSIFY_ONLY | NO_FREEZE_WITHOUT_OPERATOR",
        "inventory_id": "abx_stabilization_contract_inventory_v1",
        "contracts": [r.to_dict() for r in records],
        "schema_files_found": len(schemas),
    }
    payload["inventory_hash"] = stable_hash(
        {"contracts": payload["contracts"], "schema_count": len(schemas)}
    )
    return payload


def write_inventory_artifact(repo_root: Path, out_dir: Optional[Path] = None) -> Path:
    out = out_dir or repo_root / "out" / "stabilization_readiness"
    out.mkdir(parents=True, exist_ok=True)
    data = build_contract_inventory(repo_root)
    path = out / "contract_inventory.latest.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path