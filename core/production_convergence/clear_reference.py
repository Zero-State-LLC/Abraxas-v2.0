"""CLEAR-phase reference analysis — advisory inventory; no deletions."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

_INPUT_RELS: tuple[str, ...] = (
    "out/production_convergence/deprecation_ledger.v1.json",
    "out/production_convergence/entrypoint_inventory.v1.json",
    "out/production_convergence/interface_inventory.v1.json",
    "out/production_convergence/duplication_clusters.v1.json",
    "out/production_convergence/canonical_writer_bypass_advisory.v1.json",
    "out/production_convergence/phase8_writer_migration.v1.json",
)

_RECOMMENDED_ACTIONS = frozenset(
    {"KEEP", "DEPRECATE_DOCUMENT_ONLY", "DEFER_CLEAR", "MERGE_CANDIDATE"}
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _entry(
    *,
    path: str,
    classification: str,
    role: str,
    replacement_candidate: str | None,
    shim_behavior: str | None,
    deletion_blocker: list[str],
    recommended_action: str,
    business_logic_in_shim: bool = False,
) -> dict[str, Any]:
    if recommended_action not in _RECOMMENDED_ACTIONS:
        raise ValueError(f"invalid recommended_action: {recommended_action}")
    return {
        "path": path,
        "classification": classification,
        "role": role,
        "replacement_candidate": replacement_candidate,
        "shim_behavior": shim_behavior,
        "deletion_blocker": sorted(deletion_blocker),
        "recommended_action": recommended_action,
        "business_logic_in_shim": business_logic_in_shim,
    }


def build_clear_reference_analysis(repo_root: Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    inputs_consumed: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}
    not_computable: list[str] = []

    for rel in _INPUT_RELS:
        path = root / rel
        data = _load_json(path)
        if data is None:
            not_computable.append(f"missing_or_invalid:{rel}")
            inputs_consumed.append(
                {"path": rel, "present": False, "canonical_hash": None}
            )
            continue
        loaded[rel] = data
        inputs_consumed.append(
            {
                "path": rel,
                "present": True,
                "canonical_hash": data.get("canonical_hash"),
            }
        )

    entries: list[dict[str, Any]] = []

    deprecation = loaded.get("out/production_convergence/deprecation_ledger.v1.json")
    if deprecation:
        for item in deprecation.get("entries") or []:
            if not isinstance(item, dict):
                continue
            classification = str(item.get("classification") or "EXPERIMENTAL")
            role = (
                "SHIM"
                if "SHIM" in classification
                else "EXPERIMENTAL"
                if classification == "EXPERIMENTAL"
                else "LEGACY_WRITER"
            )
            blockers = ["OPERATOR_HOLD", "PROVENANCE_LINEAGE"]
            if role == "SHIM":
                blockers.append("TEST_REFERENCE")
            action = "DEPRECATE_DOCUMENT_ONLY" if role == "SHIM" else "DEFER_CLEAR"
            entries.append(
                _entry(
                    path=str(item.get("path")),
                    classification=classification,
                    role=role,
                    replacement_candidate=item.get("replacement"),
                    shim_behavior=item.get("shim_behavior"),
                    deletion_blocker=blockers,
                    recommended_action=action,
                    business_logic_in_shim=bool(item.get("business_logic_in_shim")),
                )
            )

    entrypoint = loaded.get("out/production_convergence/entrypoint_inventory.v1.json")
    experimental_count = 0
    generated_runner_count = 0
    if entrypoint:
        for item in entrypoint.get("entries") or []:
            if not isinstance(item, dict):
                continue
            classification = str(item.get("classification") or "")
            if classification == "EXPERIMENTAL":
                experimental_count += 1
            elif classification == "GENERATED_RUNNER":
                generated_runner_count += 1
        # Cap EXPERIMENTAL rollup entries to avoid megabyte receipt; summarize samples.
        experimental_paths = sorted(
            str(item.get("path"))
            for item in (entrypoint.get("entries") or [])
            if isinstance(item, dict) and item.get("classification") == "EXPERIMENTAL"
        )
        for path in experimental_paths[:20]:
            if any(e["path"] == path for e in entries):
                continue
            entries.append(
                _entry(
                    path=path,
                    classification="EXPERIMENTAL",
                    role="EXPERIMENTAL",
                    replacement_candidate=None,
                    shim_behavior=None,
                    deletion_blocker=["CI_REFERENCE", "PROVENANCE_LINEAGE", "OPERATOR_HOLD"],
                    recommended_action="DEFER_CLEAR",
                )
            )

    duplication = loaded.get("out/production_convergence/duplication_clusters.v1.json")
    if duplication:
        for cluster in duplication.get("clusters") or []:
            if not isinstance(cluster, dict):
                continue
            risk_raw = str(cluster.get("deletion_risk") or cluster.get("risk") or "")
            risk = risk_raw.upper()
            if "HIGH" not in risk and "MEDIUM" not in risk:
                continue
            paths = (
                cluster.get("implementations")
                or cluster.get("paths")
                or cluster.get("members")
                or []
            )
            action = "MERGE_CANDIDATE" if "HIGH" in risk else "KEEP"
            for path in paths:
                path_s = str(path)
                if any(e["path"] == path_s for e in entries):
                    continue
                entries.append(
                    _entry(
                        path=path_s,
                        classification=str(
                            cluster.get("responsibility")
                            or cluster.get("classification")
                            or "DUPLICATE"
                        ),
                        role="ALTERNATE_SERVER"
                        if path_s.startswith("api/")
                        else "GENERATED_RUNNER",
                        replacement_candidate=cluster.get("canonical_candidate"),
                        shim_behavior=None,
                        deletion_blocker=["DUPLICATION_CLUSTER_KEEP", "OPERATOR_HOLD"],
                        recommended_action=action,
                    )
                )

    # Stable order
    entries.sort(key=lambda e: (e["path"], e["role"]))

    blocker_counter: Counter[str] = Counter()
    for entry in entries:
        for blocker in entry["deletion_blocker"]:
            blocker_counter[blocker] += 1
    rollup = [
        {
            "blocker": name,
            "count": count,
            "example_paths": [
                e["path"] for e in entries if name in e["deletion_blocker"]
            ][:5],
        }
        for name, count in sorted(blocker_counter.items())
    ]

    shim_count = sum(1 for e in entries if e["role"] == "SHIM")
    payload: dict[str, Any] = {
        "artifact_type": "production_convergence_clear_reference_analysis",
        "schema_version": "clear_reference_analysis.v1",
        "evidence_state": "Partial",
        "mode": "advisory_report_only",
        "fail_closed": False,
        "influences_current_state": False,
        "mass_deletion_authorized": False,
        "external_production_authorized": False,
        "candidate_status": "NOT_READY",
        "inputs_consumed": inputs_consumed,
        "summary": {
            "shim_count": shim_count,
            "experimental_count": experimental_count,
            "generated_runner_count": generated_runner_count,
            "blocker_count": len(blocker_counter),
            "deletion_candidate_count": sum(
                1
                for e in entries
                if e["recommended_action"] in {"DEFER_CLEAR", "MERGE_CANDIDATE"}
            ),
            "entry_count": len(entries),
        },
        "entries": entries,
        "deletion_blockers_rollup": rollup,
        "not_computable": sorted(not_computable),
        "notes": [
            "No mass deletion in this phase.",
            "Historical out/ remains archived provenance.",
            "CLEAR analysis is advisory; operator review required before any removal.",
        ],
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
