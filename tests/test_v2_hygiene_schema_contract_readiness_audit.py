from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_schema_contract_readiness_audit import (
    OUT_JSON,
    build_v2_hygiene_schema_contract_readiness_audit,
    render_v2_hygiene_schema_contract_readiness_audit_markdown,
    write_v2_hygiene_schema_contract_readiness_audit,
)
from scripts import run_v2_hygiene_schema_contract_readiness_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_schema_contract_readiness_audit.v1.schema.json"


def test_v2_hygiene_schema_contract_readiness_audit_held() -> None:
    packet = build_v2_hygiene_schema_contract_readiness_audit(REPO_ROOT)

    assert packet["status"] == "V2_HYGIENE_SCHEMA_CONTRACT_READINESS_AUDIT_HELD_FOR_OPERATOR"
    assert packet["source_ready"] is True
    assert packet["contract_summary"]["expected_contract_count"] == 5
    assert packet["contract_summary"]["missing_contract_count"] == 5
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_v2_hygiene_schema_contract_readiness_audit_contract_records() -> None:
    packet = build_v2_hygiene_schema_contract_readiness_audit(REPO_ROOT)
    records = {record["contract_id"]: record for record in packet["contract_records"]}

    assert set(records) == {
        "loop_dynamics",
        "v2_output",
        "v2_hygiene_rune_base",
        "hygiene_mode",
        "individual_hygiene_rune_contracts",
    }
    assert records["loop_dynamics"]["repo_observed"] is False
    assert records["hygiene_mode"]["schema_file_creation_authorized"] is False
    assert all(record["authority_granted"] is False for record in records.values())


def test_v2_hygiene_schema_contract_readiness_audit_denies_authority() -> None:
    packet = build_v2_hygiene_schema_contract_readiness_audit(REPO_ROOT)

    assert packet["schema_file_creation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["strict_mode_enablement_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_schema_contract_readiness_audit_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_schema_contract_readiness_audit(REPO_ROOT)
    without_hash = dict(packet)
    audit_hash = without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_schema_contract_readiness_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_schema_contract_readiness_audit(REPO_ROOT, out_root=tmp_path)
    out_json = tmp_path / OUT_JSON
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_schema_contract_readiness_audit.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["audit_hash"] == packet["audit_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_schema_contract_readiness_audit_markdown() -> None:
    packet = build_v2_hygiene_schema_contract_readiness_audit(REPO_ROOT)
    markdown = render_v2_hygiene_schema_contract_readiness_audit_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Schema Contract Readiness Audit"
    assert any("loop_dynamics" in line for line in markdown)
    assert any("missing_contract_count" in line for line in markdown)
