"""Tests for skills/abx-esoteric-intelligence/alife_adapter.py (TEST candidate 20ddfc88df1a2df4)"""

import sys
sys.path.insert(0, "skills/abx-esoteric-intelligence")
import alife_adapter as a

def test_build_organism_candidate_governance():
    pkt = a.build_organism_candidate("test input with hyperstition", {"request_id": "r1", "synthetic_fixture": True})
    assert pkt["schema_version"] == "ABX.SymbolicOrganismCandidate.v1"
    gov = pkt["governance"]
    assert gov["lane"] == "SHADOW"
    assert gov["entity_assertion"] is False
    assert gov["execution_authority"] is False
    assert "candidate_id" in pkt
    assert pkt["organism_class"] == "HYPERSTITION"

def test_build_archetype_lineage():
    pkt = a.build_archetype_lineage("Hermes archetype", {"synthetic_fixture": True})
    assert pkt["schema_version"] == "ABX.ArchetypeLineage.v1"
    assert "stable_motif_genes" in pkt
    assert pkt["governance"]["entity_assertion"] is False

def test_build_sigil_and_population():
    sig = a.build_sigil_genotype("some text", {"synthetic_fixture": True})
    assert sig["schema_version"] == "ABX.SigilGenotype.v1"
    assert sig["governance"]["entity_assertion"] is False

    pop = a.build_population_model("population input", {"synthetic_fixture": True})
    assert pop["schema_version"] == "ABX.DistributedSymbolicPopulation.v1"
    assert pop["entity_assertion"] is False

def test_build_metabolism_and_synchronicity():
    met = a.build_metabolism_packet("metabolism input", {"synthetic_fixture": True})
    assert met["schema_version"] == "ABX.SymbolicMetabolismPacket.v1"
    assert met["execution_claimed"] is False

    syn = a.build_synchronicity_ecology("syn input", {"synthetic_fixture": True})
    assert syn["schema_version"] == "ABX.SynchronicityAnalysisPacket.v1"
    assert syn["governance"]["forecast_authority"] is False

def test_dispatcher_and_modes():
    assert "organismize" in a.ALIFE_MODE_BUILDERS
    pkt = a.build_alife_packet("organismize", "door water hyperstition", {"request_id": "r2", "synthetic_fixture": True})
    assert "candidate_id" in pkt
    try:
        a.build_alife_packet("unknown_mode", "x", {"synthetic_fixture": True})
        assert False
    except KeyError:
        pass

def test_deterministic_hashes():
    p1 = a.build_organism_candidate("same input", {"synthetic_fixture": True})
    p2 = a.build_organism_candidate("same input", {"synthetic_fixture": True})
    assert p1["genotype"]["provenance_hash"] == p2["genotype"]["provenance_hash"]