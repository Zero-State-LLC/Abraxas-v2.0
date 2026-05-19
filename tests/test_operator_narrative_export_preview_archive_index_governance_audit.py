from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.operator_narrative_export_preview_archive_index import build_operator_narrative_export_preview_archive_index_packet
from core.operator_narrative_export_preview_archive_index_governance_audit import (
    AUDIT_ID,
    PATCH_ID,
    SCHEMA_VERSION,
    build_operator_narrative_export_preview_archive_index_governance_audit_packet,
    write_operator_narrative_export_preview_archive_index_governance_audit,
)


def _base() -> tuple[dict, str]:
    pkt = build_operator_narrative_export_preview_archive_index_packet()
    md = Path("out/archive/operator_narrative_export_preview_archive_index_001.latest.md").read_text(encoding="utf-8")
    from core.canonical.json import canonical_hash
    recompute = deepcopy(pkt)
    recompute.pop("archive_index_hash", None)
    pkt["archive_index_hash"] = canonical_hash(recompute)
    return pkt, md


def _pass_base() -> tuple[dict, str]:
    pkt, md = _base()
    pkt["final_status"] = "ARCHIVE_INDEX_ONLY"
    pkt["archive_posture"] = "COMPLETE"
    pkt["blocker_summary"] = ["upstream structural blocker"]
    for key in ("p46_export_bundle_json", "p48_static_preview_json"):
        if key in pkt.get("status_summary", {}):
            pkt["status_summary"][key]["status"] = "EXPORT_ONLY" if "p46" in key else "PREVIEW_ONLY"
    md = """# P52

## Artifact Role Order
## Archive Manifest
## Receipt Status Summary
## Source Hashes
## Receipt Hashes
## Registry Classification Summary
## Blockers
## Governance Boundary
"""
    from core.canonical.json import canonical_hash
    recompute = deepcopy(pkt)
    recompute.pop("archive_index_hash", None)
    pkt["archive_index_hash"] = canonical_hash(recompute)
    return pkt, md


def _is_fail(packet: dict, needle: str) -> bool:
    return any(f["severity"] == "FAIL" and needle in f["message"] for f in packet["findings"])


def test_pass_and_repeatability() -> None:
    pkt, md = _pass_base()
    a = build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=pkt, archive_markdown_text=md)
    b = build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=deepcopy(pkt), archive_markdown_text=md)
    assert a["final_status"] == "PASS"
    assert a["audit_hash"] == b["audit_hash"]


def test_not_computable_missing_sources(tmp_path: Path) -> None:
    p = build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_index_json_path=tmp_path / "x.json", archive_index_markdown_path=tmp_path / "x.md")
    assert p["final_status"] == "NOT_COMPUTABLE"


def test_fail_conditions() -> None:
    pkt, md = _base()
    bad = deepcopy(pkt)
    bad["artifact_role_order"] = ["x"]
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["archive_manifest"] = list(reversed(bad["archive_manifest"]))
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["archive_manifest"][0]["passive_reference_only"] = False
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    for k in ["command_url", "action_url", "href", "onclick"]:
        bad = deepcopy(pkt)
        bad[k] = "x"
        assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    for s in ["javascript:", "data:", "http://", "https://"]:
        bad = deepcopy(pkt)
        bad["x"] = s + "evil"
        assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["archive_index_hash"] = "x"
    assert _is_fail(build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md), "archive_index_hash mismatch")

    bad = deepcopy(pkt)
    bad["hash_inventory"]["p46_export_bundle_json"] = "x"
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["governance_receipt_summary"]["p47_export_bundle_governance_audit"]["final_status"] = "FAIL"
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["blocker_summary"] = ["source_missing:p42_report_json"]
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["archive_manifest"][0]["payload_blob"] = "abc"
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"

    bad_md = md.replace("## Archive Manifest", "## X")
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=pkt, archive_markdown_text=bad_md)["final_status"] == "FAIL"

    bad = deepcopy(pkt)
    bad["note"] = "we recommend a package release"
    assert build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=bad, archive_markdown_text=md)["final_status"] == "FAIL"


def test_writer_and_schema(tmp_path: Path) -> None:
    pkt, md = _base()
    packet = build_operator_narrative_export_preview_archive_index_governance_audit_packet(archive_packet=pkt, archive_markdown_text=md)
    out = tmp_path / "audit.json"
    write_operator_narrative_export_preview_archive_index_governance_audit(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_export_preview_archive_index_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["audit_id"]["const"] == AUDIT_ID
