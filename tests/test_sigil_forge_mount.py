"""Sigil-Forge stack mount: genotype honesty, ingest envelope, specialist slots.

These tests lock the Abraxas-side adapter. They must fail if the genotype
falls back to hardcoded primitives or grants forecast/canon/execution.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "abx-esoteric-intelligence"))

import alife_adapter as a  # noqa: E402
import forge_ingest  # noqa: E402
import sigil_forge_bridge as bridge  # noqa: E402

CALM_FOCUS = "I maintain calm focus while shipping Sigil-Forge"
# Spare letter_monogram of the golden fixture (examples/intents/calm_focus.json)
CALM_FOCUS_PRIMITIVES = list("mntclfswhpgr")
# Pinned replay of Zero-State-LLC/Sigil-Forge forge_core outputs (see PROVENANCE.md).
PINNED_FORGE_HOME = ROOT / "tests" / "fixtures" / "sigil_forge_pinned"
PINNED_OUTPUTS = json.loads(
    (PINNED_FORGE_HOME / "forge_core_outputs.v1.json").read_text(encoding="utf-8")
)
REQUIRE_LIVE_ENV = "ABRAXAS_REQUIRE_SIGIL_FORGE"
FEATURES_GOLD = (
    ROOT
    / "skills"
    / "abx-esoteric-intelligence"
    / "fixtures"
    / "specialist_features.calm_focus.v1.jsonl"
)


def _use_forge_home(monkeypatch, home: Path) -> None:
    """Point discovery at one engine root only; drop cached engine modules."""
    monkeypatch.delenv("HERMES_HOME", raising=False)
    monkeypatch.delenv("HERMES_SKILL_DIR", raising=False)
    for key in bridge._NATIVE_ROOT_ENV:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("SIGIL_FORGE_HOME", str(home))
    monkeypatch.setattr(sys, "path", list(sys.path))
    for name in ("forge_core", "commitment", "artifact_root"):
        if name in sys.modules:
            monkeypatch.delitem(sys.modules, name)


@pytest.fixture
def pinned_forge(monkeypatch, tmp_path):
    """Contract lane: always runs against the pinned replay fixture."""
    monkeypatch.setenv("HOME", str(tmp_path))  # hide ~/Sigil-Forge, ~/.hermes
    _use_forge_home(monkeypatch, PINNED_FORGE_HOME)
    yield PINNED_FORGE_HOME
    sys.modules.pop("forge_core", None)


@pytest.fixture
def live_forge(monkeypatch):
    """Live lane: a real checkout. Missing -> SKIPPED, or FAIL when required."""
    home = Path(
        os.environ.get("SIGIL_FORGE_HOME") or Path.home() / "Sigil-Forge"
    ).expanduser()
    if not (home / "scripts" / "forge_core.py").is_file():
        msg = f"Sigil-Forge checkout not found at {home} (set SIGIL_FORGE_HOME)"
        if os.environ.get(REQUIRE_LIVE_ENV) == "1":
            pytest.fail(f"{REQUIRE_LIVE_ENV}=1: {msg}", pytrace=False)
        pytest.skip(msg)
    _use_forge_home(monkeypatch, home)
    yield home
    for name in ("forge_core", "commitment", "artifact_root"):
        sys.modules.pop(name, None)




def test_sigil_genotype_never_hardcodes_hm():
    sig = a.build_sigil_genotype("some text", {})
    assert sig["schema_version"] == "ABX.SigilGenotype.v1"
    assert sig["genotype"]["primitives"] != ["H", "M"]
    assert sig["governance"]["entity_assertion"] is False
    assert sig.get("synthetic") is not True
    assert sig.get("evidence_status") != "SYNTHETIC"


def test_canned_alife_builders_still_require_synthetic_opt_in():
    try:
        a.build_organism_candidate("x", {})
        raise AssertionError("canned organismize must stay synthetic-only")
    except ValueError as exc:
        assert "NOT_COMPUTABLE" in str(exc)
    try:
        a.build_population_model("x", {})
        raise AssertionError("canned population_model must stay synthetic-only")
    except ValueError as exc:
        assert "NOT_COMPUTABLE" in str(exc)


def test_sigil_genotype_derives_spare_primitives_from_intent():
    sig = a.build_sigil_genotype(CALM_FOCUS, {"request_id": "golden-calm-focus"})
    assert sig["genotype"]["construction"] == "spare.letter_monogram"
    assert sig["genotype"]["primitives"] == CALM_FOCUS_PRIMITIVES
    assert sig["variant_classification"] in (
        "FORGE_CORE",
        "LOCAL_SPARE_REDUCTION",
    )
    digest = sig["genotype"]["intent_digest"]
    assert isinstance(digest, str) and len(digest) == 64
    assert sig["governance"]["lane"] == "SHADOW"
    assert sig["governance"]["forecast_authority"] is False


def test_sigil_genotype_is_deterministic():
    a1 = a.build_sigil_genotype(CALM_FOCUS, {})
    a2 = a.build_sigil_genotype(CALM_FOCUS, {})
    assert a1["genotype"]["primitives"] == a2["genotype"]["primitives"]
    assert a1["genotype"]["intent_digest"] == a2["genotype"]["intent_digest"]
    assert a1["genotype"]["provenance_hash"] == a2["genotype"]["provenance_hash"]


def test_sigil_genotype_all_vowel_is_not_computable():
    sig = a.build_sigil_genotype("aeiou y", {})
    assert sig["genotype"]["construction"] == "NOT_COMPUTABLE"
    assert sig["genotype"]["primitives"] == []
    assert sig["claim_class"] == "NOT_COMPUTABLE"


def test_bridge_letter_sequence_matches_spare_golden():
    assert bridge.letter_sequence(bridge.normalize_intent(CALM_FOCUS)) == CALM_FOCUS_PRIMITIVES


def test_forge_ingest_envelope_is_shadow_and_digest_only():
    env = forge_ingest.from_intent(CALM_FOCUS, request_id="golden-calm-focus")
    assert env["schema_version"] == "ForgeIngestEnvelope.v1"
    assert env["specialist_id"] == "sigil-forge"
    assert env["lane"] == "SHADOW"
    assert env["authority"]["forecast_authority"] is False
    assert env["authority"]["canon_authority"] is False
    assert env["authority"]["execution_authority"] is False
    assert env["plaintext_intent_in_public"] is False
    assert "normalized_intent" not in env
    assert len(env["intent_digest"]) == 64
    pack = env["evidence_pack"]
    assert pack["schema_version"] == "EvidencePack.v0"
    assert pack["intent"] == "other"
    registers = {c["register"] for c in pack["claims"]}
    assert "OBSERVED" not in registers or all(
        c["register"] != "OBSERVED" or "efficacy" not in c["text"].lower()
        for c in pack["claims"]
    )
    assert any(c["register"] == "COMPUTED" or c["register"] == "INFERRED" for c in pack["claims"])


def _assert_frozen_feature_identity() -> dict:
    import forge_kernel

    gold = json.loads(FEATURES_GOLD.read_text(encoding="utf-8").splitlines()[0])
    run = forge_kernel.run_shadow_kernel(CALM_FOCUS, request_id="features-calm-focus")
    rec = forge_kernel.public_feature_record(run["envelope"])
    assert rec["schema_version"] == "SpecialistFeatureRecord.v1"
    assert rec["plaintext_intent"] is False
    assert rec["intent_digest"] == gold["intent_digest"]
    assert rec["construction"] == gold["construction"]
    assert rec["engine"] == gold["engine"]
    assert rec["primitives_len"] == gold["primitives_len"]
    dumped = json.dumps(rec)
    assert '"nonce"' not in dumped
    assert CALM_FOCUS.lower() not in dumped.lower()
    return run


def test_public_feature_record_matches_frozen_identity(pinned_forge):
    _assert_frozen_feature_identity()
    assert bridge.discovery_source() == "env:SIGIL_FORGE_HOME"


def test_pinned_fixture_records_its_source():
    assert PINNED_OUTPUTS["source_repo"] == "Zero-State-LLC/Sigil-Forge"
    assert len(PINNED_OUTPUTS["source_commit"]) == 40
    for row in PINNED_OUTPUTS["outputs"]:
        assert row["intent_digest"] == bridge.intent_digest(row["normalized"])


def test_specialist_stack_contract_lists_sigil_forge_and_siblings():
    path = ROOT / "contracts" / "specialist_models" / "stack.v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "SpecialistModelStack.v1"
    assert data["lane"] == "SHADOW"
    ids = [row["id"] for row in data["specialists"]]
    assert ids == ["hyperlex", "sigil-forge", "athanor", "semion", "trutina"]
    sf = next(row for row in data["specialists"] if row["id"] == "sigil-forge")
    assert sf["role"] == "intent_compression"
    assert sf["live_catalog_mutation"] is False
    assert data["source"]["unshared_owner_pages"] == []
    observed = {row["id"]: row for row in data["specialists"]}
    assert observed["athanor"]["role"] == "tradition_retrieve"
    assert "athanor.packet.v0" in observed["athanor"]["packet"]
    assert observed["athanor"]["claim_class_on_job"] == "OBSERVED_OWNER_PAGE"
    assert observed["semion"]["packet"] == "semion.frame.v0"
    assert observed["trutina"]["packet"] == "brier.score.v0"
    for sid in ("athanor", "semion", "trutina"):
        assert observed[sid]["status"] == "SLOT_RESERVED"
        assert observed[sid]["abraxas_mount"] is False
    dumped = json.dumps(data)
    assert "UNSHARED_OWNER_PAGE" not in dumped
    assert "refinement_furnace" not in dumped
    assert "v1" in data["evolution"]
    assert "v2" in data["evolution"]
    assert "v3" in data["evolution"]


def test_bridge_prefers_native_home_over_hermes(monkeypatch, tmp_path):
    scripts = tmp_path / "Sigil-Forge" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "forge_core.py").write_text(
        "class ForgeConfig:\n"
        "    def __init__(self, **kwargs): pass\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HERMES_HOME", raising=False)
    monkeypatch.delenv("HERMES_SKILL_DIR", raising=False)
    monkeypatch.setenv("SIGIL_FORGE_HOME", str(tmp_path / "Sigil-Forge"))
    monkeypatch.setenv("HERMES_SKILL_DIR", str(tmp_path / "hermes-decoy"))
    dirs = bridge.engine_script_dirs()
    assert dirs[0] == scripts.resolve()
    assert dirs[0] != (tmp_path / "hermes-decoy" / "scripts")
    source = bridge.configured_discovery_label()
    assert source.startswith("env:SIGIL_FORGE_")
    assert "HERMES" not in source


def test_bridge_discovers_without_any_hermes_env(pinned_forge):
    core = bridge.load_forge_core()
    assert core is not None
    assert bridge.discovery_source().startswith("env:SIGIL_FORGE_")


@pytest.mark.sigil_forge_live
@pytest.mark.integration
def test_live_bridge_discovers_checkout(live_forge):
    core = bridge.load_forge_core()
    assert core is not None
    assert bridge.discovery_source().startswith("env:SIGIL_FORGE_")
    assert Path(core.__file__).resolve().parent == (live_forge / "scripts").resolve()


@pytest.mark.sigil_forge_live
@pytest.mark.integration
def test_live_public_feature_record_matches_frozen_identity(live_forge):
    run = _assert_frozen_feature_identity()
    assert run["envelope"]["zk_provenance"]["status"] == "commitment"


@pytest.mark.sigil_forge_live
@pytest.mark.integration
def test_live_forge_matches_pinned_outputs(live_forge):
    """Drift alarm: if this fails, re-pin (tests/fixtures/sigil_forge_pinned/PROVENANCE.md)."""
    forge = bridge.load_forge_core()
    cfg = forge.ForgeConfig(**PINNED_OUTPUTS["config"])
    for row in PINNED_OUTPUTS["outputs"]:
        r = forge.compute_forge(row["normalized"], cfg)
        assert r.intent_digest == row["intent_digest"]
        assert r.spare_letters == row["spare_letters"]
        assert (r.square_name, r.square_order) == (row["square_name"], row["square_order"])


def test_mount_contract_is_agent_agnostic():
    doc = (ROOT / "docs" / "architecture" / "SIGIL_FORGE_STACK_MOUNT_001.md").read_text(
        encoding="utf-8"
    )
    assert "agent-agnostic" in doc.lower()
    assert "→ Hermes (sigil-forge skill" not in doc
    stack = json.loads(
        (ROOT / "contracts" / "specialist_models" / "stack.v1.json").read_text(
            encoding="utf-8"
        )
    )
    sf = next(row for row in stack["specialists"] if row["id"] == "sigil-forge")
    assert sf.get("runtime") == "standalone-cli"
    assert "hermes-skill" not in json.dumps(sf).lower()
    routing = json.loads(
        (ROOT / "contracts" / "specialist_models" / "notion_routing.v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert routing["mints_spine_owner"] is False
    ids = [row["system_id"] for row in routing["aal_viz_systems"]]
    assert ids == [
        "familiar",
        "hyperlex",
        "sigil_forge",
        "athanor",
        "semion",
        "trutina",
    ]


def test_ingest_poi_is_public_only_and_not_efficacy():
    env = forge_ingest.from_intent(CALM_FOCUS, request_id="golden-calm-focus")
    dumped = json.dumps(env)
    assert '"nonce"' not in dumped
    assert env["plaintext_intent_in_public"] is False
    poi = env["zk_provenance"]
    assert poi["schema_version"] == "ABX_ZK_PROVENANCE_V1"
    assert poi["status"] in ("commitment", "skipped")
    assert poi["proof"] is None
    assert poi["authority"]["forecast_authority"] is False
    assert poi["note"]
    assert "not efficacy" in poi["note"].lower()
    if env["engine"] == "sigil-forge":
        assert poi["status"] == "commitment"
        assert isinstance(env["sigil_root"], str) and len(env["sigil_root"]) == 64
        assert env["intent_commitment"]["value"]
        assert "nonce" not in env["intent_commitment"]
        assert env["sigil_root_scope"] == "public_genotype_leaves"
        feats = env["specialist_features"]
        assert feats["intent_digest"] == env["intent_digest"]
        assert feats["sigil_root"] == env["sigil_root"]
        assert feats["primitives_len"] == 12
    proj = forge_ingest.inspect_projection(env)
    assert proj["schema_version"] == "ForgeInspectProjection.v1"
    assert proj["lane"] == "SHADOW"
    assert proj["chips"]["proof"] in ("commitment", "skipped")
    assert proj["authority_visible"] is True


def test_shadow_kernel_ingests_and_bridges_without_mutation():
    import forge_kernel

    from core.signal.evidence_pack import validate_evidence_pack

    run = forge_kernel.run_shadow_kernel(CALM_FOCUS, request_id="golden-calm-focus")
    assert run["schema_version"] == "ForgeKernelRun.v1"
    assert run["lane"] == "SHADOW"
    assert run["authority"]["forecast_routing_authorized"] is False
    pack = run["envelope"]["evidence_pack"]
    assert validate_evidence_pack(pack, repo_root=ROOT) == []
    assert pack["provenance"]["skill_id"] == "abx-esoteric-intelligence"
    receipt = run["ingestion_receipt"]
    assert receipt["status"] == "INGESTED_SHADOW"
    assert receipt["lane"] == "SHADOW"
    assert receipt["advisory_only"] is True
    assert run["spine_touchpoint"]["route"] == "ORACLE_SHADOW_CANDIDATE"
    bridge_pkt = run["oracle_belief_bridge"]
    assert bridge_pkt["status"] == "BRIDGED_SHADOW"
    assert bridge_pkt["oracle_shadow_intake"]["queue_write_authorized"] is False
    assert bridge_pkt["oracle_shadow_intake"]["runtime_invoke_authorized"] is False
    for seed in bridge_pkt["belief_candidate_seeds"]:
        assert seed["truth_assignment"] is False
        assert seed["belief_promotion"] is False
    dumped = json.dumps(run)
    assert '"nonce"' not in dumped
    assert run["inspect_projection"]["chips"]["authority"] == "SHADOW"


def test_shadow_adapter_is_not_on_live_registry():
    from core.alembic.adapters import DEFAULT_ADAPTERS
    from core.alembic.models import ExecutionContext, TaskEnvelope
    from core.alembic.registry import default_registry

    import alembic_sigil_forge as sf_ad

    live_ids = [a.descriptor().architecture_id for a in DEFAULT_ADAPTERS]
    assert "arch.sigil_forge.intent_compression.v1" not in live_ids
    snap = default_registry().snapshot()
    assert snap["count"] == 8
    adapter = sf_ad.SigilForgeShadowAdapter()
    desc = adapter.descriptor()
    assert desc.status == "SHADOW_ONLY"
    assert desc.is_stub is False
    task = TaskEnvelope(
        task_id="sf-t1",
        run_id="sf-r1",
        goal="I maintain calm focus while shipping Sigil-Forge",
        task_type="transform",
        input_modalities=("text",),
        input_artifacts=({"intent": CALM_FOCUS},),
        required_output_contract="ForgeIngestEnvelope.v1",
        required_determinism="BOUNDED_DETERMINISTIC",
        allowed_architecture_families=("deterministic_tool",),
        lane="SHADOW",
    )
    assert adapter.validate_task(task).ok is True
    blocked = adapter.validate_task(task.model_copy(update={"lane": "FORECAST"}))
    assert blocked.ok is False
    ctx = ExecutionContext(run_id="sf-r1", lane="SHADOW")
    raw = adapter.invoke(task, ctx)
    assert raw.is_stub is False
    assert raw.status == "OK"
    payload = raw.payload
    assert payload["plaintext_intent_in_public"] is False
    assert '"nonce"' not in json.dumps(payload)
    assert payload["zk_provenance"]["status"] in ("commitment", "skipped")
    contrib = adapter.normalize_with_task(raw, task, ctx)
    assert contrib.lane == "SHADOW"
    assert contrib.is_stub is False
    packets = payload["inspect_projection"]["chips"]
    assert packets["authority"] == "SHADOW"


def test_alembic_sigil_forge_descriptor_is_shadow_not_live():
    desc_path = ROOT / "contracts" / "sigil_forge" / "architecture_descriptor.v1.json"
    desc = json.loads(desc_path.read_text(encoding="utf-8"))
    assert desc["schema_version"] == "ArchitectureDescriptor.v1"
    assert desc["architecture_family"] == "deterministic_tool"
    assert desc["status"] == "SHADOW_ONLY"
    assert desc["is_stub"] is False
    assert desc["authority_class"] == "SHADOW_ONLY"
    registry = json.loads(
        (ROOT / "contracts" / "alembic" / "architecture_registry.json").read_text(
            encoding="utf-8"
        )
    )
    live_ids = [row["architecture_id"] for row in registry["architectures"]]
    assert desc["architecture_id"] not in live_ids


def test_sigil_forge_rune_proposals_are_advisory_only():
    path = ROOT / "contracts" / "sigil_forge" / "rune_proposals.v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["live_catalog_mutation"] is False
    assert "RUNE.SIGIL.FORGE" in data["proposed_rune_ids"]
    assert "RUNE.SIGIL.CLASSIFY" in data["proposed_rune_ids"]
    assert "RUNE.SIGIL.GENOTYPE" in data["proposed_rune_ids"]
    assert data["status"] == "ADVISORY_PROPOSALS_ONLY"
