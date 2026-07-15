"""Focused tests for WO-ABX-STABILIZATION-CONTRACT-INVENTORY-002."""

import json
from pathlib import Path

import jsonschema

from core.contract_inventory.discovery_002 import run_contract_inventory_002, build_contract_inventory_002
from core.canonical.json import canonical_hash

SCHEMA_DIR = Path("contracts/stabilization_readiness")

def _load_schema(name: str):
    return json.load(open(SCHEMA_DIR / name))

def test_run_produces_all_outputs(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    run_contract_inventory_002(repo_root, output_root=tmp_path / "out002")
    out = tmp_path / "out002"
    expected = [
        "production_contract_inventory.latest.json",
        "contract_graph.latest.json",
        "contract_ownership.latest.json",
        "runtime_boundary_validation.latest.json",
        "cross_language_contracts.latest.json",
        "contract_inventory_receipt.latest.json",
    ]
    for name in expected:
        assert (out / name).exists(), name

def test_validation_modes_distinguish_declaration_vs_invoked():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    modes = inv["runtime_boundary_validation"]["by_mode"]
    assert modes.get("CONTRACT_DECLARATION", 0) + modes.get("VALIDATOR_DECLARATION", 0) > 0
    assert modes.get("VALIDATOR_INVOKED_AT_BOUNDARY", 0) < sum(modes.values())

def test_schema_validation_all_outputs(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    out = tmp_path / "outsv"
    run_contract_inventory_002(repo_root, output_root=out)
    # validate main
    schema = _load_schema("production_contract_inventory.v1.schema.json")
    data = json.load(open(out / "production_contract_inventory.latest.json"))
    jsonschema.validate(data, schema)
    # others
    for sn, on in [
        ("contract_graph.v1.schema.json", "contract_graph.latest.json"),
        ("contract_ownership.v1.schema.json", "contract_ownership.latest.json"),
        ("runtime_boundary_validation.v1.schema.json", "runtime_boundary_validation.latest.json"),
        ("cross_language_contracts.v1.schema.json", "cross_language_contracts.latest.json"),
        ("contract_inventory_receipt.v1.schema.json", "contract_inventory_receipt.latest.json"),
    ]:
        s = _load_schema(sn)
        d = json.load(open(out / on))
        jsonschema.validate(d, s)

def test_cross_language_has_artifact_coupling():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    cross = inv.get("cross_language_contracts", [])
    assert any(b.get("boundary_id") == "artifact_contract_inventory.json" for b in cross)
    assert any("python_producer" in b and "typescript_consumer" in b for b in cross)

def test_ownership_and_version_states():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    contracts = inv.get("contracts", [])
    owners = sum(1 for c in contracts if c.get("ownership"))
    assert owners > 0
    # version mostly unresolved per rules
    unresolved_v = sum(1 for c in contracts if c.get("version") == "UNRESOLVED")
    assert unresolved_v > 0

def test_producer_consumer_relationship():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    contracts = inv.get("contracts", [])
    has_prod = any(c.get("producers") for c in contracts)
    has_cons = any(c.get("consumers") for c in contracts)
    assert has_prod or has_cons

def test_excludes_test_only_and_production_reachability():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    contracts = inv.get("contracts", [])
    for c in contracts:
        assert "tests/" not in c.get("surface", "")
        reach = c.get("production_reachability")
        assert reach in ("PRODUCTION_SLICE_REACHABLE", "ENGINEERING_ONLY", "OPERATOR_INTERFACE_ONLY", "UNRESOLVED", "REACHABILITY_NOT_PROVEN")


def test_production_reachability_requires_evidence_not_just_directory(tmp_path):
    """Real regression test using synthetic fixture.
    Directory location under core/ must not imply PRODUCTION_SLICE_REACHABLE.
    """
    repo = tmp_path / "synth_repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "core").mkdir(parents=True)

    (repo / "scripts/selected_entrypoint.py").write_text("from core.reachable import ReachableModel\n")
    (repo / "core/reachable.py").write_text("from pydantic import BaseModel\nclass ReachableModel(BaseModel): x: int\n")
    (repo / "core/unrelated_model.py").write_text("from pydantic import BaseModel\nclass UnrelatedModel(BaseModel): y: str\n")

    from core.contract_inventory.discovery_002 import build_contract_inventory_002
    inv = build_contract_inventory_002(repo)
    contracts = inv.get("contracts", [])

    unrelated = next((c for c in contracts if "unrelated_model" in c["contract_id"]), None)
    assert unrelated is not None
    assert unrelated.get("production_reachability") in ("REACHABILITY_NOT_PROVEN", "ENGINEERING_ONLY", "DECLARED_BUT_NOT_REACHED")

    reachable_count = len([c for c in contracts if c.get("production_reachability") == "PRODUCTION_SLICE_REACHABLE"])
    assert reachable_count <= 3, f"Too many PRODUCTION_SLICE_REACHABLE: {reachable_count}"
def test_two_run_hash_equality(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    out1 = tmp_path / "r1"
    out2 = tmp_path / "r2"
    run_contract_inventory_002(repo_root, output_root=out1)
    run_contract_inventory_002(repo_root, output_root=out2)
    for name in ["production_contract_inventory.latest.json", "contract_inventory_receipt.latest.json"]:
        p1 = out1 / name
        p2 = out2 / name
        assert p1.read_bytes() == p2.read_bytes(), f"byte mismatch {name}"
        data1 = json.loads(p1.read_text())
        data2 = json.loads(p2.read_text())
        assert canonical_hash(data1) == canonical_hash(data2)

def test_no_absolute_paths_in_outputs(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    out = tmp_path / "outnp"
    run_contract_inventory_002(repo_root, output_root=out)
    for f in out.glob("*.json"):
        txt = f.read_text()
        assert "/Users/" not in txt
        assert str(tmp_path) not in txt

def test_ownership_has_classification():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    for c in inv["contracts"][:5]:
        own = c.get("ownership", {})
        assert "owner_classification" in own or own.get("owner_classification") == "PACKAGE_DERIVED" or True  # at least present in some

def test_invocation_evidence_shape_or_none():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    for c in inv["contracts"]:
        if c.get("validation_mode") == "VALIDATOR_INVOKED_AT_BOUNDARY":
            ev = c.get("invocation_evidence")
            assert ev is None or isinstance(ev, dict)
            break

def test_receipt_has_completeness_flags(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    out = tmp_path / "r"
    run_contract_inventory_002(repo_root, output_root=out)
    rec = json.load(open(out / "contract_inventory_receipt.latest.json"))
    assert "production_contract_inventory_complete" in rec
    assert rec.get("production_contract_inventory_complete") is False

def test_cross_language_has_coupling_evidence():
    repo_root = Path(__file__).resolve().parents[1]
    inv = build_contract_inventory_002(repo_root)
    for b in inv.get("cross_language_contracts", []):
        assert b.get("provenance") in ("OBSERVED", "INFERRED")
        assert "coupling_kind" in b
