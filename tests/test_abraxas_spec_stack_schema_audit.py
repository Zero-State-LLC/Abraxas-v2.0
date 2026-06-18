from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from core.abraxas_spec_stack_belief_graph_schema_audit import (
    OUT_JSON as BELIEF_OUT_JSON,
    build_abraxas_spec_stack_belief_graph_schema_audit,
    write_abraxas_spec_stack_belief_graph_schema_audit,
)
from core.abraxas_spec_stack_binding_schema_audit import (
    OUT_JSON as BINDING_OUT_JSON,
    build_abraxas_spec_stack_binding_schema_audit,
    write_abraxas_spec_stack_binding_schema_audit,
)
from core.abraxas_spec_stack_codegen_spine_schema_audit import (
    OUT_JSON as CODEGEN_OUT_JSON,
    build_abraxas_spec_stack_codegen_spine_schema_audit,
    write_abraxas_spec_stack_codegen_spine_schema_audit,
)
from core.abraxas_spec_stack_ingest_schema_audit import (
    OUT_JSON as INGEST_OUT_JSON,
    build_abraxas_spec_stack_ingest_schema_audit,
    write_abraxas_spec_stack_ingest_schema_audit,
)
from core.abraxas_spec_stack_schema_audit_common import (
    authority_locks,
    spec_stack_governance_envelope,
)
from core.abraxas_spec_stack_schema_audit_receipt import (
    OUT_JSON as RECEIPT_OUT_JSON,
    build_abraxas_spec_stack_schema_audit_receipt,
    write_abraxas_spec_stack_schema_audit_receipt,
)
from core.abraxas_spec_stack_situation_runtime_schema_audit import (
    OUT_JSON as SITUATION_OUT_JSON,
    build_abraxas_spec_stack_situation_runtime_schema_audit,
    write_abraxas_spec_stack_situation_runtime_schema_audit,
)
from core.canonical.json import canonical_hash
from scripts import run_abraxas_spec_stack_schema_audit_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]

DOMAIN_CASES = (
    (
        "belief_graph",
        build_abraxas_spec_stack_belief_graph_schema_audit,
        write_abraxas_spec_stack_belief_graph_schema_audit,
        BELIEF_OUT_JSON,
        "contracts/canon/abraxas_spec_stack_belief_graph_schema_audit.v1.schema.json",
    ),
    (
        "codegen_spine",
        build_abraxas_spec_stack_codegen_spine_schema_audit,
        write_abraxas_spec_stack_codegen_spine_schema_audit,
        CODEGEN_OUT_JSON,
        "contracts/canon/abraxas_spec_stack_codegen_spine_schema_audit.v1.schema.json",
    ),
    (
        "ingest",
        build_abraxas_spec_stack_ingest_schema_audit,
        write_abraxas_spec_stack_ingest_schema_audit,
        INGEST_OUT_JSON,
        "contracts/canon/abraxas_spec_stack_ingest_schema_audit.v1.schema.json",
    ),
    (
        "binding",
        build_abraxas_spec_stack_binding_schema_audit,
        write_abraxas_spec_stack_binding_schema_audit,
        BINDING_OUT_JSON,
        "contracts/canon/abraxas_spec_stack_binding_schema_audit.v1.schema.json",
    ),
    (
        "situation_runtime",
        build_abraxas_spec_stack_situation_runtime_schema_audit,
        write_abraxas_spec_stack_situation_runtime_schema_audit,
        SITUATION_OUT_JSON,
        "contracts/canon/abraxas_spec_stack_situation_runtime_schema_audit.v1.schema.json",
    ),
)


@pytest.mark.parametrize(
    ("domain", "builder", "_writer", "_out_json", "_schema_path"),
    DOMAIN_CASES,
    ids=[case[0] for case in DOMAIN_CASES],
)
def test_domain_governance_envelope(
    domain: str,
    builder,
    _writer,
    _out_json,
    _schema_path,
) -> None:
    packet = builder(REPO_ROOT)
    envelope = spec_stack_governance_envelope()
    for key, value in envelope.items():
        assert packet[key] == value, domain


@pytest.mark.parametrize(
    ("domain", "builder", "_writer", "_out_json", "_schema_path"),
    DOMAIN_CASES,
    ids=[case[0] for case in DOMAIN_CASES],
)
def test_domain_contract_records_deterministic(
    domain: str,
    builder,
    _writer,
    _out_json,
    _schema_path,
) -> None:
    first = builder(REPO_ROOT)
    second = builder(REPO_ROOT)
    assert first["audit_hash"] == second["audit_hash"], domain


@pytest.mark.parametrize(
    ("domain", "builder", "_writer", "_out_json", "schema_path"),
    DOMAIN_CASES,
    ids=[case[0] for case in DOMAIN_CASES],
)
def test_domain_schema_validates(
    domain: str,
    builder,
    _writer,
    _out_json,
    schema_path: str,
) -> None:
    packet = builder(REPO_ROOT)
    without_hash = dict(packet)
    audit_hash = without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(without_hash), domain
    schema = json.loads((REPO_ROOT / schema_path).read_text(encoding="utf-8"))
    validate(packet, schema)


@pytest.mark.parametrize(
    ("domain", "builder", "_writer", "_out_json", "_schema_path"),
    DOMAIN_CASES,
    ids=[case[0] for case in DOMAIN_CASES],
)
def test_domain_denies_authority(
    domain: str,
    builder,
    _writer,
    _out_json,
    _schema_path,
) -> None:
    packet = builder(REPO_ROOT)
    assert all(value is False for value in packet["authority_locks"].values()), domain


@pytest.mark.parametrize(
    ("domain", "_builder", "writer", "out_json", "_schema_path"),
    DOMAIN_CASES,
    ids=[case[0] for case in DOMAIN_CASES],
)
def test_domain_runner_writes_stable_outputs(
    domain: str,
    _builder,
    writer,
    out_json: Path,
    _schema_path,
    tmp_path: Path,
) -> None:
    packet = writer(REPO_ROOT, out_root=tmp_path)
    target = tmp_path / out_json
    md_target = target.with_suffix(".md")
    first_json = target.read_text(encoding="utf-8")
    first_md = md_target.read_text(encoding="utf-8")
    second = writer(REPO_ROOT, out_root=tmp_path)
    assert second["audit_hash"] == packet["audit_hash"], domain
    assert first_json == target.read_text(encoding="utf-8")
    assert first_md == md_target.read_text(encoding="utf-8")


def test_receipt_governance_envelope() -> None:
    receipt = build_abraxas_spec_stack_schema_audit_receipt(REPO_ROOT)
    envelope = spec_stack_governance_envelope()
    for key, value in envelope.items():
        assert receipt[key] == value


def test_receipt_aggregates_five_domains() -> None:
    receipt = build_abraxas_spec_stack_schema_audit_receipt(REPO_ROOT)
    assert receipt["stack_summary"]["domain_count"] == 5
    assert len(receipt["domain_audits"]) == 5


def test_receipt_downstream_not_computable() -> None:
    receipt = build_abraxas_spec_stack_schema_audit_receipt(REPO_ROOT)
    assert receipt["downstream_status"] == "NOT_COMPUTABLE"
    assert receipt["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_receipt_schema_validates() -> None:
    receipt = build_abraxas_spec_stack_schema_audit_receipt(REPO_ROOT)
    without_hash = dict(receipt)
    receipt_hash = without_hash.pop("receipt_hash")
    assert receipt_hash == canonical_hash(without_hash)
    schema = json.loads(
        (
            REPO_ROOT / "contracts/canon/abraxas_spec_stack_schema_audit_receipt.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(receipt, schema)


def test_receipt_denies_authority() -> None:
    receipt = build_abraxas_spec_stack_schema_audit_receipt(REPO_ROOT)
    assert all(value is False for value in receipt["authority_locks"].values())
    assert all(value is False for value in authority_locks().values())


def test_receipt_runner_writes_stable_outputs(tmp_path: Path) -> None:
    receipt = write_abraxas_spec_stack_schema_audit_receipt(REPO_ROOT, out_root=tmp_path)
    target = tmp_path / RECEIPT_OUT_JSON
    first_json = target.read_text(encoding="utf-8")
    second = run_abraxas_spec_stack_schema_audit_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert second["receipt_hash"] == receipt["receipt_hash"]
    assert first_json == target.read_text(encoding="utf-8")


def test_binding_shadow_binding_gaps_documented() -> None:
    packet = build_abraxas_spec_stack_binding_schema_audit(REPO_ROOT)
    inventory = next(
        finding
        for finding in packet["findings"]
        if finding["finding_id"] == "cross_spine_shadow_binding_gap_inventory"
    )
    assert inventory["missing_binding_count"] >= 1


def test_belief_graph_shadow_binding_gap_missing() -> None:
    packet = build_abraxas_spec_stack_belief_graph_schema_audit(REPO_ROOT)
    gap = next(
        finding
        for finding in packet["findings"]
        if finding["finding_id"] == "belief_graph_engine_shadow_binding_gap"
    )
    assert gap["finding_status"] == "MISSING"
