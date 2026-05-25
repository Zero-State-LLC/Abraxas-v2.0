from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.canonical.json import canonical_hash
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_narrative_export_preview_archive_index import (
    ARCHIVE_INDEX_ID,
    PATCH_ID,
    SCHEMA_VERSION,
    build_operator_narrative_export_preview_archive_index_markdown,
    build_operator_narrative_export_preview_archive_index_packet,
    write_operator_narrative_export_preview_archive_index,
)

_EXPECTED_ROLE_ORDER = [
    "p46_export_bundle_json",
    "p46_export_bundle_markdown",
    "p47_export_bundle_governance_audit_json",
    "p47_export_bundle_governance_audit_markdown",
    "p48_static_preview_json",
    "p48_static_preview_markdown",
    "p49_static_preview_governance_audit_json",
    "p49_static_preview_governance_audit_markdown",
]
_P51_REPAIRED_BLOCKERS = {
    "source_missing:p42_report_json",
    "source_missing:p44_ui_overlay_json",
    "overlay report hash lineage mismatch",
}
_ACTIVE_TOKENS = ["command_url", "action_url", "href", "onclick", "javascript:", "data:", "http://", "https://"]
_FORBIDDEN_PROSE = ["recommend", "should do", "forecast", "will happen", "readiness", "take action", "execute", "approve", "route", "mutate", "prediction", "next move", "package", "distribution", "deploy", "release"]


def _write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path.as_posix()


def _write_json(path: Path, payload: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path.as_posix()


def _seed(tmp_path: Path, *, blocked: bool = False) -> dict[str, str]:
    export_bundle = {
        "schema_version": "OperatorNarrativeExportBundle.v1",
        "patch_id": "PATCH-P46-OPERATOR-NARRATIVE-EXPORT-BUNDLE-001",
        "bundle_id": "operator_narrative_export_bundle_001",
        "final_status": "BLOCKED" if blocked else "EXPORT_ONLY",
        "export_posture": "BLOCKED" if blocked else "COMPLETE",
        "blocker_summary": ["upstream structural blocker"] if blocked else [],
        "bundle_hash": "p46_bundle_hash",
    }
    export_audit = {
        "schema_version": "OperatorNarrativeExportBundleGovernanceAudit.v1",
        "patch_id": "PATCH-P47-OPERATOR-NARRATIVE-EXPORT-BUNDLE-GOVERNANCE-AUDIT-001",
        "audit_id": "operator_narrative_export_bundle_governance_audit_001",
        "final_status": "PASS",
        "audit_posture": "CLEAN",
        "blocker_summary": [],
        "audit_hash": "p47_audit_hash",
    }
    preview = {
        "schema_version": "OperatorNarrativeStaticPreviewBundle.v1",
        "patch_id": "PATCH-P48-OPERATOR-NARRATIVE-STATIC-PREVIEW-BUNDLE-001",
        "preview_id": "operator_narrative_static_preview_001",
        "final_status": "BLOCKED" if blocked else "PREVIEW_ONLY",
        "preview_posture": "BLOCKED" if blocked else "COMPLETE",
        "blocker_summary": ["upstream structural blocker"] if blocked else [],
        "preview_hash": "p48_preview_hash",
    }
    preview_audit = {
        "schema_version": "OperatorNarrativeStaticPreviewGovernanceAudit.v1",
        "patch_id": "PATCH-P49-OPERATOR-NARRATIVE-STATIC-PREVIEW-GOVERNANCE-AUDIT-001",
        "audit_id": "operator_narrative_static_preview_governance_audit_001",
        "final_status": "PASS",
        "audit_posture": "CLEAN",
        "blocker_summary": [],
        "audit_hash": "p49_audit_hash",
    }
    return {
        "p46_export_bundle_json": _write_json(tmp_path / "p46.json", export_bundle),
        "p46_export_bundle_markdown": _write(tmp_path / "p46.md", "P46 passive index source\n"),
        "p47_export_bundle_governance_audit_json": _write_json(tmp_path / "p47.json", export_audit),
        "p47_export_bundle_governance_audit_markdown": _write(tmp_path / "p47.md", "P47 passive receipt source\n"),
        "p48_static_preview_json": _write_json(tmp_path / "p48.json", preview),
        "p48_static_preview_markdown": _write(tmp_path / "p48.md", "P48 passive preview source\n"),
        "p49_static_preview_governance_audit_json": _write_json(tmp_path / "p49.json", preview_audit),
        "p49_static_preview_governance_audit_markdown": _write(tmp_path / "p49.md", "P49 passive receipt source\n"),
    }


def _payload_without_governance(packet: dict) -> str:
    clone = deepcopy(packet)
    clone["governance_flags"] = {}
    return json.dumps(clone, sort_keys=True).lower()


def test_status_ladder_role_order_and_determinism(tmp_path: Path) -> None:
    paths = _seed(tmp_path)
    packet = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=paths)
    assert packet["final_status"] == "ARCHIVE_INDEX_ONLY"
    assert packet["archive_posture"] == "COMPLETE"
    assert packet["artifact_role_order"] == _EXPECTED_ROLE_ORDER
    assert [entry["artifact_id"] for entry in packet["archive_manifest"]] == _EXPECTED_ROLE_ORDER
    assert all(entry["passive_reference_only"] is True for entry in packet["archive_manifest"])
    assert packet["archive_index_hash"] == build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=paths)["archive_index_hash"]

    blocked = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=_seed(tmp_path / "blocked", blocked=True))
    assert blocked["final_status"] == "ARCHIVE_INDEX_DEGRADED"
    assert blocked["archive_posture"] == "DEGRADED"
    assert blocked["blocker_summary"] == ["upstream structural blocker"]


def test_missing_and_corrupt_sources_are_not_computable(tmp_path: Path) -> None:
    paths = _seed(tmp_path)
    missing = dict(paths)
    missing["p46_export_bundle_json"] = (tmp_path / "missing.json").as_posix()
    missing_packet = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=missing)
    assert missing_packet["final_status"] == "NOT_COMPUTABLE"
    assert "source_missing:p46_export_bundle_json" in missing_packet["blocker_summary"]
    assert missing_packet["hash_inventory"]["p46_export_bundle_json"] == "NOT_COMPUTABLE"

    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text("{", encoding="utf-8")
    corrupt = dict(paths)
    corrupt["p47_export_bundle_governance_audit_json"] = corrupt_path.as_posix()
    corrupt_packet = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=corrupt)
    assert corrupt_packet["final_status"] == "NOT_COMPUTABLE"
    assert "source_corrupt:p47_export_bundle_governance_audit_json" in corrupt_packet["blocker_summary"]


def test_hashes_blockers_and_p51_repairs(tmp_path: Path) -> None:
    paths = _seed(tmp_path, blocked=True)
    packet = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=paths)
    assert packet["receipt_hashes"]["p46_export_bundle_json"] == "p46_bundle_hash"
    assert packet["receipt_hashes"]["p47_export_bundle_governance_audit_json"] == "p47_audit_hash"
    assert packet["receipt_hashes"]["p48_static_preview_json"] == "p48_preview_hash"
    assert packet["receipt_hashes"]["p49_static_preview_governance_audit_json"] == "p49_audit_hash"
    assert packet["source_hashes"]["p46_export_bundle_json"] == canonical_hash(json.loads(Path(paths["p46_export_bundle_json"]).read_text(encoding="utf-8")))
    assert "upstream structural blocker" in packet["blocker_summary"]
    assert packet["provenance"]["display_blocker_summary_normalized"] is True
    assert packet["provenance"]["raw_blocker_count"] == 1
    assert len(packet["provenance"]["raw_blocker_hashes"]) == 1
    assert not (_P51_REPAIRED_BLOCKERS & set(packet["blocker_summary"]))



def test_blocker_language_normalization_and_p53_pass(tmp_path: Path) -> None:
    paths = _seed(tmp_path, blocked=True)
    blocked_payload = json.loads(Path(paths["p46_export_bundle_json"]).read_text(encoding="utf-8"))
    blocked_payload["blocker_summary"] = ["forbidden phrase present: approve", "forbidden phrase present: execute", "forbidden phrase present: forecast", "forbidden phrase present: prediction", "forbidden phrase present: readiness", "forbidden phrase present: recommend"]
    Path(paths["p46_export_bundle_json"]).write_text(json.dumps(blocked_payload, sort_keys=True), encoding="utf-8")

    packet = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=paths)
    markdown = build_operator_narrative_export_preview_archive_index_markdown(packet).lower()

    assert packet["final_status"] == "ARCHIVE_INDEX_DEGRADED"
    assert packet["archive_posture"] == "DEGRADED"
    assert packet["provenance"]["raw_blocker_count"] > 0
    for forbidden in _FORBIDDEN_PROSE:
        assert forbidden not in markdown

    from core.operator_narrative_export_preview_archive_index_governance_audit import build_operator_narrative_export_preview_archive_index_governance_audit_packet

    audit = build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=packet, archive_markdown_text=markdown)
    assert audit["final_status"] == "PASS"


def test_registry_governance_language_schema_and_writer(tmp_path: Path) -> None:
    packet = build_operator_narrative_export_preview_archive_index_packet(source_artifact_paths=_seed(tmp_path))
    flags = packet["governance_flags"]
    for key in {"archive_index_only", "passive_index_only", "read_only", "non_authoritative", "source_linked", "deterministic_manifest", "advisory_only"}:
        assert flags[key] is True
    for key, value in flags.items():
        if key not in {"archive_index_only", "passive_index_only", "read_only", "non_authoritative", "source_linked", "deterministic_manifest", "advisory_only"}:
            assert value is False

    payload_text = _payload_without_governance(packet)
    markdown_without_governance = build_operator_narrative_export_preview_archive_index_markdown({**packet, "governance_flags": {}}).lower()
    for token in _ACTIVE_TOKENS:
        assert token not in payload_text
        assert token not in markdown_without_governance

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    ci_targets = set(list_ci_drift_artifact_paths(registry))
    emap = {entry.artifact_path: entry for entry in registry.entries}
    for path in (
        "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
        "out/archive/operator_narrative_export_preview_archive_index_001.latest.md",
    ):
        assert path in emap
        assert emap[path].determinism_class == "DERIVED_OPTIONAL"
        assert emap[path].authority_granted is False
        assert path not in ci_targets

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_export_preview_archive_index.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["archive_index_id"]["const"] == ARCHIVE_INDEX_ID

    out = tmp_path / "archive_index.json"
    write_operator_narrative_export_preview_archive_index(out, packet)
    assert out.read_text(encoding="utf-8").endswith("\n")
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
