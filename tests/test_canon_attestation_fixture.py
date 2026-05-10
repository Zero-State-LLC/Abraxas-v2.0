import hashlib
import json
from pathlib import Path

from core.canon.attestation_fixture import (
    build_fixture_attestation_report,
    load_canon_attestation_fixture,
    validate_canon_attestation_fixture,
    write_canon_attestation_fixture_audit,
)
from core.runtime_spine.models import RuntimeInvocation, RuntimePosture, RuntimeRoute
from core.runtime_spine.router import route_runtime_invocation


def test_fixture_loads_deterministically() -> None:
    p = Path("fixtures/canon/canon_attestation_fixture.v1.json")
    f1 = load_canon_attestation_fixture(p)
    f2 = load_canon_attestation_fixture(p)
    assert f1 == f2


def test_fixture_validation_pass() -> None:
    fixture = load_canon_attestation_fixture("fixtures/canon/canon_attestation_fixture.v1.json")
    report = validate_canon_attestation_fixture(fixture)
    assert report.status == "PASS"


def test_missing_required_notion_ref_not_computable(tmp_path: Path) -> None:
    payload = json.loads(Path("fixtures/canon/canon_attestation_fixture.v1.json").read_text(encoding="utf-8"))
    payload["source_refs"] = [r for r in payload["source_refs"] if r["source_id"] != "73460b50-4dfd-4cc3-93e7-906559678624"]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    fixture = load_canon_attestation_fixture(bad)
    assert validate_canon_attestation_fixture(fixture).status == "NOT_COMPUTABLE"


def test_invalid_authority_mode_blocked(tmp_path: Path) -> None:
    payload = json.loads(Path("fixtures/canon/canon_attestation_fixture.v1.json").read_text(encoding="utf-8"))
    payload["authority_mode"] = "LIVE_CANON"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    fixture = load_canon_attestation_fixture(bad)
    assert validate_canon_attestation_fixture(fixture).status == "BLOCKED"


def test_attestation_hash_stable_across_loads() -> None:
    p = Path("fixtures/canon/canon_attestation_fixture.v1.json")
    assert load_canon_attestation_fixture(p).attestation_hash == load_canon_attestation_fixture(p).attestation_hash


def test_runtime_spine_passes_with_fixture_attestation_test_path() -> None:
    fixture = load_canon_attestation_fixture("fixtures/canon/canon_attestation_fixture.v1.json")
    report = build_fixture_attestation_report(fixture)
    invocation = RuntimeInvocation(route=RuntimeRoute(subsystem_id="canon.subsystem", lane="CANON", promotion_state="CANON_ACTIVE", authority_scope="CANON"), payload={"k": 1}, canon_attestation=report.attestation_hash, outcome_binding="bound")
    assert route_runtime_invocation(invocation).posture == RuntimePosture.PASS


def test_runtime_spine_without_attestation_not_computable() -> None:
    invocation = RuntimeInvocation(route=RuntimeRoute(subsystem_id="canon.subsystem", lane="CANON", promotion_state="CANON_ACTIVE", authority_scope="CANON"), payload={"k": 1}, canon_attestation=None, outcome_binding="bound")
    assert route_runtime_invocation(invocation).posture == RuntimePosture.NOT_COMPUTABLE


def test_fixture_audit_artifact_stable_sha_and_newline(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures/canon"
    fixture_dir.mkdir(parents=True)
    fixture_dir.joinpath("canon_attestation_fixture.v1.json").write_text(Path("fixtures/canon/canon_attestation_fixture.v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    h1 = write_canon_attestation_fixture_audit(tmp_path)
    text1 = (tmp_path / "out/audit/canon_attestation_fixture.latest.json").read_text(encoding="utf-8")
    h2 = write_canon_attestation_fixture_audit(tmp_path)
    text2 = (tmp_path / "out/audit/canon_attestation_fixture.latest.json").read_text(encoding="utf-8")
    assert text1.endswith("\n")
    assert h1 == h2
    assert hashlib.sha256(text1.encode("utf-8")).hexdigest() == hashlib.sha256(text2.encode("utf-8")).hexdigest()


def test_no_network_calls_required() -> None:
    fixture = load_canon_attestation_fixture("fixtures/canon/canon_attestation_fixture.v1.json")
    assert all(not str(ref.source_id).startswith(("http://", "https://")) for ref in fixture.source_refs)
