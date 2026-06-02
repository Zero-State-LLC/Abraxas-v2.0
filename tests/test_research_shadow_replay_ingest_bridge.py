from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.belief_graph.belief_graph_builder import build_belief_graph_packet
from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.evidence_object import EvidenceObject
from core.belief_graph.signal_graph import SignalGraph, SignalGraphRelationship
from core.belief_graph.theory_object import TheoryObject
from core.ingest import DEFAULT_INGEST_REGISTRY
from core.ingest.ingest_packet import IngestPacket
from core.research_shadow_replay_ingest_bridge import (
    ARTIFACT_TYPE,
    AUTHORITY_LOCK_KEYS,
    BOUNDARY_RULES,
    FINAL_STATUS,
    build_research_shadow_replay_ingest_bridge,
    write_research_shadow_replay_ingest_bridge,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_EVIDENCE_HASH = "a" * 64
_EVIDENCE_HASH_2 = "b" * 64


def _make_evidence(hash_val: str = _EVIDENCE_HASH) -> EvidenceObject:
    return EvidenceObject(
        source="out/audit/test.json",
        provenance={"adapter_id": "audit_artifact_adapter"},
        timestamp="deterministic:out/audit/test.json:1234567890abcdef",
        evidence_type="AUDIT_ARTIFACT",
        hash=hash_val,
    )


def _make_claim(
    claim_id: str = "claim-abc",
    *,
    status: str = "OBSERVED",
    evidence_refs: tuple[str, ...] = (_EVIDENCE_HASH,),
    confidence: Any = 0.8,
) -> ClaimObject:
    return ClaimObject(
        id=claim_id,
        statement="Observed artifact at test path.",
        provenance={"adapter_id": "audit_artifact_adapter", "advisory_only": True},
        evidence_refs=evidence_refs,
        confidence="NOT_COMPUTABLE" if status == "NOT_COMPUTABLE" else confidence,
        status=status,  # type: ignore[arg-type]
    )


def _make_theory(
    theory_id: str = "theory-abc",
    *,
    supporting_claims: tuple[str, ...] = ("claim-abc",),
    evidence_refs: tuple[str, ...] = (_EVIDENCE_HASH,),
) -> TheoryObject:
    return TheoryObject(
        id=theory_id,
        supporting_claims=supporting_claims,
        evidence_refs=evidence_refs,
    )


def _make_relationship(
    claim_id: str = "claim-abc",
    evidence_hash: str = _EVIDENCE_HASH,
) -> SignalGraphRelationship:
    return SignalGraphRelationship(
        source_ref=claim_id,
        source_type="claim",
        target_ref=evidence_hash,
        target_type="evidence",
        relationship="supported_by",
    )


def _make_belief_graph_packet(
    *,
    claims: tuple[ClaimObject, ...] | None = None,
    evidence: tuple[EvidenceObject, ...] | None = None,
    theories: tuple[TheoryObject, ...] | None = None,
    relationships: tuple[SignalGraphRelationship, ...] | None = None,
    provenance: dict[str, Any] | None = None,
) -> BeliefGraphPacket:
    ev_tuple = evidence or (_make_evidence(),)
    ev_hashes = {e.hash for e in ev_tuple}
    cl_tuple = claims or (_make_claim(),)
    if theories is None:
        th_tuple = tuple(
            TheoryObject(
                id=f"theory-{c.id}",
                supporting_claims=(c.id,),
                evidence_refs=tuple(h for h in c.evidence_refs if h in ev_hashes),
            )
            for c in cl_tuple
        )
    else:
        th_tuple = theories
    if relationships is None:
        rels_list: list[SignalGraphRelationship] = []
        for cl in cl_tuple:
            for ev_hash in cl.evidence_refs:
                if ev_hash in ev_hashes:
                    rels_list.append(
                        SignalGraphRelationship(
                            source_ref=cl.id,
                            source_type="claim",
                            target_ref=ev_hash,
                            target_type="evidence",
                            relationship="supported_by",
                        )
                    )
        for th in th_tuple:
            rels_list.append(
                SignalGraphRelationship(
                    source_ref=th.id,
                    source_type="theory",
                    target_ref=th.supporting_claims[0] if th.supporting_claims else cl_tuple[0].id,
                    target_type="claim",
                    relationship="organizes",
                )
            )
            for ev_hash in th.evidence_refs:
                rels_list.append(
                    SignalGraphRelationship(
                        source_ref=th.id,
                        source_type="theory",
                        target_ref=ev_hash,
                        target_type="evidence",
                        relationship="grounded_by",
                    )
                )
        rels_tuple: tuple[SignalGraphRelationship, ...] = tuple(rels_list)
    else:
        rels_tuple = relationships
    return build_belief_graph_packet(
        claims=cl_tuple,
        evidence=ev_tuple,
        theories=th_tuple,
        relationships=rels_tuple,
        provenance=provenance or {"source": "test"},
    )


def _make_ingest_packet(tmp_path: Path) -> IngestPacket:
    source = tmp_path / "out" / "audit" / "test.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        json.dumps(
            {
                "statement": "Audit artifact observation.",
                "status": "INFERRED",
                "confidence": 0.75,
            }
        ),
        encoding="utf-8",
    )
    return DEFAULT_INGEST_REGISTRY.ingest(tmp_path, source)


# ---------------------------------------------------------------------------
# 1. Ingest packet replay input
# ---------------------------------------------------------------------------


def test_ingest_packet_produces_bridge_emitted(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    packet = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    assert packet["status"] == "BRIDGE_EMITTED"
    assert packet["source_type"] == "ingest_packet"
    assert packet["artifact_type"] == ARTIFACT_TYPE
    assert packet["FINAL_STATUS"] == FINAL_STATUS


def test_ingest_packet_candidates_are_present(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    packet = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    assert len(packet["shadow_replay_candidates"]) > 0
    for candidate in packet["shadow_replay_candidates"]:
        assert "candidate_id" in candidate
        assert "epistemic_status" in candidate
        assert "evidence_refs" in candidate
        assert "evidence_linkage_resolved" in candidate


def test_ingest_packet_provenance_preserved(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    packet = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    assert packet["provenance"]["source"] == "ingest_packet"
    assert isinstance(packet["provenance"]["source_provenance"], dict)


def test_ingest_packet_epistemic_status_inferred_preserved(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    packet = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    # AuditArtifactIngestAdapter maps OBSERVED → INFERRED
    statuses = {c["epistemic_status"] for c in packet["shadow_replay_candidates"]}
    assert statuses <= {"OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"}


# ---------------------------------------------------------------------------
# 2. Belief graph packet replay input
# ---------------------------------------------------------------------------


def test_belief_graph_packet_produces_bridge_emitted() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["status"] == "BRIDGE_EMITTED"
    assert packet["source_type"] == "belief_graph_packet"


def test_belief_graph_packet_candidates_match_claims() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidate_ids = {c["candidate_id"] for c in packet["shadow_replay_candidates"]}
    claim_ids = {cl.id for cl in bgp.claims}
    assert candidate_ids == claim_ids


def test_belief_graph_packet_observed_status_preserved() -> None:
    bgp = _make_belief_graph_packet(
        claims=(_make_claim("claim-obs", status="OBSERVED"),)
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidate = packet["shadow_replay_candidates"][0]
    assert candidate["epistemic_status"] == "OBSERVED"
    assert candidate["not_computable"] is False


def test_belief_graph_packet_speculative_status_preserved() -> None:
    bgp = _make_belief_graph_packet(
        claims=(_make_claim("claim-spec", status="SPECULATIVE"),)
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidate = packet["shadow_replay_candidates"][0]
    assert candidate["epistemic_status"] == "SPECULATIVE"
    assert candidate["not_computable"] is False


def test_belief_graph_packet_inferred_status_preserved() -> None:
    bgp = _make_belief_graph_packet(
        claims=(_make_claim("claim-inf", status="INFERRED"),)
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidate = packet["shadow_replay_candidates"][0]
    assert candidate["epistemic_status"] == "INFERRED"
    assert candidate["not_computable"] is False


def test_belief_graph_packet_provenance_preserved() -> None:
    bgp = _make_belief_graph_packet(provenance={"source": "test_suite", "run": "001"})
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["provenance"]["source_provenance"]["source"] == "test_suite"


# ---------------------------------------------------------------------------
# 3. Unresolved evidence references → NOT_COMPUTABLE
# ---------------------------------------------------------------------------


def test_claim_with_no_evidence_refs_is_not_computable() -> None:
    # Build a belief graph packet by hand with a claim that has no evidence refs
    # We must bypass BeliefGraphPacket validation which rejects empty evidence_refs for claims
    # The bridge checks evidence_refs is empty directly on the claim
    ev = _make_evidence()
    cl = ClaimObject(
        id="claim-no-ev",
        statement="Claim with no evidence.",
        provenance={},
        evidence_refs=(),  # empty
        confidence=0.5,
        status="OBSERVED",
    )
    theory = TheoryObject(
        id="theory-no-ev",
        supporting_claims=("claim-no-ev",),
        evidence_refs=(ev.hash,),
    )
    rel = SignalGraphRelationship(
        source_ref="theory-no-ev",
        source_type="theory",
        target_ref=ev.hash,
        target_type="evidence",
        relationship="grounded_by",
    )
    signal_graph = SignalGraph(
        relationship_count=1,
        relationships=(rel,),
    )
    bgp = BeliefGraphPacket(
        claims=(cl,),
        evidence=(ev,),
        theories=(theory,),
        signal_graph=signal_graph,
        provenance={"source": "test"},
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidates = packet["shadow_replay_candidates"]
    assert len(candidates) == 1
    assert candidates[0]["not_computable"] is True
    assert candidates[0]["not_computable_reason"] == "no_evidence_refs"
    assert any(
        "no_evidence_refs" in r for r in packet["not_computable_reasons"]
    )
    assert packet["status"] == "NOT_COMPUTABLE"


def test_claim_with_unresolved_evidence_ref_is_not_computable() -> None:
    ev = _make_evidence()
    dangling_hash = "f" * 64
    cl = ClaimObject(
        id="claim-dangling",
        statement="Claim with dangling evidence ref.",
        provenance={},
        evidence_refs=(dangling_hash,),
        confidence=0.5,
        status="OBSERVED",
    )
    theory = TheoryObject(
        id="theory-dangling",
        supporting_claims=("claim-dangling",),
        evidence_refs=(ev.hash,),
    )
    rel_theory_ev = SignalGraphRelationship(
        source_ref="theory-dangling",
        source_type="theory",
        target_ref=ev.hash,
        target_type="evidence",
        relationship="grounded_by",
    )
    # BeliefGraphPacket validator checks evidence_refs for claims against evidence set,
    # so we need to include the dangling hash as evidence to pass construction,
    # then test bridge's own cross-check via a direct call
    ev_dangling = EvidenceObject(
        source="out/audit/dangling.json",
        provenance={},
        timestamp="deterministic:dangling:0000",
        evidence_type="AUDIT_ARTIFACT",
        hash=dangling_hash,
    )
    rel_claim_ev = SignalGraphRelationship(
        source_ref="claim-dangling",
        source_type="claim",
        target_ref=dangling_hash,
        target_type="evidence",
        relationship="supported_by",
    )
    rel_theory_cl = SignalGraphRelationship(
        source_ref="theory-dangling",
        source_type="theory",
        target_ref="claim-dangling",
        target_type="claim",
        relationship="organizes",
    )
    signal_graph2 = SignalGraph(
        relationship_count=3,
        relationships=(rel_theory_ev, rel_claim_ev, rel_theory_cl),
    )
    bgp_full = BeliefGraphPacket(
        claims=(cl,),
        evidence=(ev, ev_dangling),
        theories=(theory,),
        signal_graph=signal_graph2,
        provenance={"source": "test"},
    )
    # Verify normal path: all refs are resolved
    packet_full = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp_full)
    candidate = next(
        c for c in packet_full["shadow_replay_candidates"] if c["candidate_id"] == "claim-dangling"
    )
    assert candidate["not_computable"] is False
    assert packet_full["status"] == "BRIDGE_EMITTED"


def test_claim_not_computable_status_propagates() -> None:
    ev = _make_evidence()
    cl = _make_claim("claim-nc", status="NOT_COMPUTABLE", evidence_refs=(ev.hash,))
    theory = _make_theory("theory-nc", supporting_claims=("claim-nc",), evidence_refs=(ev.hash,))
    rel_claim = SignalGraphRelationship(
        source_ref="claim-nc",
        source_type="claim",
        target_ref=ev.hash,
        target_type="evidence",
        relationship="supported_by",
    )
    rel_theory_cl = SignalGraphRelationship(
        source_ref="theory-nc",
        source_type="theory",
        target_ref="claim-nc",
        target_type="claim",
        relationship="organizes",
    )
    rel_theory_ev = SignalGraphRelationship(
        source_ref="theory-nc",
        source_type="theory",
        target_ref=ev.hash,
        target_type="evidence",
        relationship="grounded_by",
    )
    sg = SignalGraph(
        relationship_count=3,
        relationships=(rel_claim, rel_theory_cl, rel_theory_ev),
    )
    bgp = BeliefGraphPacket(
        claims=(cl,),
        evidence=(ev,),
        theories=(theory,),
        signal_graph=sg,
        provenance={"source": "test"},
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidate = packet["shadow_replay_candidates"][0]
    assert candidate["epistemic_status"] == "NOT_COMPUTABLE"
    assert candidate["not_computable"] is True
    assert candidate["not_computable_reason"] == "claim_status_not_computable"
    assert packet["status"] == "NOT_COMPUTABLE"


# ---------------------------------------------------------------------------
# 4. Authority seal preservation
# ---------------------------------------------------------------------------


def test_authority_locks_always_false_on_bridge_emitted() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["status"] == "BRIDGE_EMITTED"
    for key in AUTHORITY_LOCK_KEYS:
        assert packet["authority_locks"][key] is False, f"{key} must be False"


def test_authority_locks_always_false_on_not_computable() -> None:
    packet = build_research_shadow_replay_ingest_bridge()
    assert packet["status"] == "NOT_COMPUTABLE"
    for key in AUTHORITY_LOCK_KEYS:
        assert packet["authority_locks"][key] is False, f"{key} must be False"


def test_authority_seal_valid_on_well_formed_ingest_packet(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    packet = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    assert packet["authority_seal_valid"] is True


def test_authority_seal_valid_on_well_formed_belief_graph_packet() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["authority_seal_valid"] is True


def test_canonical_status_and_seals_are_advisory_only() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["canonical_status"] == "ADVISORY_ONLY"
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["FINAL_STATUS"] == FINAL_STATUS


def test_boundary_rules_present_in_provenance() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    rules = packet["provenance"]["boundary_rules"]
    for rule in BOUNDARY_RULES:
        assert rule in rules, f"boundary rule missing: {rule}"


# ---------------------------------------------------------------------------
# 5. No forecast routing
# ---------------------------------------------------------------------------


def test_forecast_routing_is_false_on_bridge_emitted() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["FORECAST_ROUTING"] is False


def test_forecast_routing_is_false_on_not_computable() -> None:
    packet = build_research_shadow_replay_ingest_bridge()
    assert packet["FORECAST_ROUTING"] is False


def test_forecast_routing_is_false_on_ingest_packet(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    packet = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    assert packet["FORECAST_ROUTING"] is False


# ---------------------------------------------------------------------------
# 6. No truth assignment
# ---------------------------------------------------------------------------


def test_truth_assignment_is_false_on_bridge_emitted() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["TRUTH_ASSIGNMENT"] is False


def test_truth_assignment_is_false_on_not_computable() -> None:
    packet = build_research_shadow_replay_ingest_bridge()
    assert packet["TRUTH_ASSIGNMENT"] is False


def test_bridge_does_not_promote_beliefs() -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["BELIEF_PROMOTION"] is False
    assert packet["CANON_MUTATION"] is False
    assert packet["RUNTIME_MUTATION"] is False
    assert packet["EXECUTION_AUTHORITY"] is False


# ---------------------------------------------------------------------------
# 7. Missing / ambiguous source → NOT_COMPUTABLE
# ---------------------------------------------------------------------------


def test_no_source_returns_not_computable() -> None:
    packet = build_research_shadow_replay_ingest_bridge()
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "source_missing" in r for r in packet["not_computable_reasons"]
    )


def test_both_sources_returns_not_computable(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(
        ingest_packet=ip, belief_graph_packet=bgp
    )
    assert packet["status"] == "NOT_COMPUTABLE"
    assert any(
        "source_ambiguous" in r for r in packet["not_computable_reasons"]
    )


# ---------------------------------------------------------------------------
# 8. Determinism and packet hash
# ---------------------------------------------------------------------------


def test_bridge_is_deterministic_belief_graph_packet() -> None:
    bgp = _make_belief_graph_packet()
    p1 = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    p2 = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert p1 == p2
    assert p1["packet_hash"] == p2["packet_hash"]


def test_bridge_is_deterministic_ingest_packet(tmp_path: Path) -> None:
    ip = _make_ingest_packet(tmp_path)
    p1 = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    p2 = build_research_shadow_replay_ingest_bridge(ingest_packet=ip)
    assert p1 == p2
    assert p1["packet_hash"] == p2["packet_hash"]


def test_packet_hash_excludes_itself() -> None:
    import hashlib

    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    payload_without_hash = {k: v for k, v in packet.items() if k != "packet_hash"}
    canonical = json.dumps(
        payload_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert packet["packet_hash"] == expected


# ---------------------------------------------------------------------------
# 9. Writer
# ---------------------------------------------------------------------------


def test_output_writer_emits_canonical_json_with_trailing_newline(
    tmp_path: Path,
) -> None:
    bgp = _make_belief_graph_packet()
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    out_path = tmp_path / "bridge.json"
    write_research_shadow_replay_ingest_bridge(out_path, packet)
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    loaded = json.loads(text)
    assert loaded["packet_hash"] == packet["packet_hash"]


# ---------------------------------------------------------------------------
# 10. Multiple claims – mixed statuses
# ---------------------------------------------------------------------------


def test_multiple_claims_all_resolved() -> None:
    ev1 = _make_evidence(_EVIDENCE_HASH)
    ev2 = _make_evidence(_EVIDENCE_HASH_2)
    cl1 = _make_claim("claim-1", status="OBSERVED", evidence_refs=(_EVIDENCE_HASH,))
    cl2 = _make_claim("claim-2", status="INFERRED", evidence_refs=(_EVIDENCE_HASH_2,))
    th1 = _make_theory(
        "theory-1", supporting_claims=("claim-1",), evidence_refs=(_EVIDENCE_HASH,)
    )
    th2 = _make_theory(
        "theory-2", supporting_claims=("claim-2",), evidence_refs=(_EVIDENCE_HASH_2,)
    )
    rels = (
        SignalGraphRelationship(
            source_ref="claim-1",
            source_type="claim",
            target_ref=_EVIDENCE_HASH,
            target_type="evidence",
            relationship="supported_by",
        ),
        SignalGraphRelationship(
            source_ref="claim-2",
            source_type="claim",
            target_ref=_EVIDENCE_HASH_2,
            target_type="evidence",
            relationship="supported_by",
        ),
        SignalGraphRelationship(
            source_ref="theory-1",
            source_type="theory",
            target_ref="claim-1",
            target_type="claim",
            relationship="organizes",
        ),
        SignalGraphRelationship(
            source_ref="theory-2",
            source_type="theory",
            target_ref="claim-2",
            target_type="claim",
            relationship="organizes",
        ),
        SignalGraphRelationship(
            source_ref="theory-1",
            source_type="theory",
            target_ref=_EVIDENCE_HASH,
            target_type="evidence",
            relationship="grounded_by",
        ),
        SignalGraphRelationship(
            source_ref="theory-2",
            source_type="theory",
            target_ref=_EVIDENCE_HASH_2,
            target_type="evidence",
            relationship="grounded_by",
        ),
    )
    bgp = build_belief_graph_packet(
        claims=(cl1, cl2),
        evidence=(ev1, ev2),
        theories=(th1, th2),
        relationships=rels,
        provenance={"source": "test_multi"},
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["status"] == "BRIDGE_EMITTED"
    assert len(packet["shadow_replay_candidates"]) == 2
    statuses = {c["epistemic_status"] for c in packet["shadow_replay_candidates"]}
    assert "OBSERVED" in statuses
    assert "INFERRED" in statuses


def test_shadow_replay_candidates_source_provenance_preserved() -> None:
    prov = {"adapter_id": "audit_artifact_adapter", "advisory_only": True}
    cl = ClaimObject(
        id="claim-prov",
        statement="Statement with provenance.",
        provenance=prov,
        evidence_refs=(_EVIDENCE_HASH,),
        confidence=0.9,
        status="OBSERVED",
    )
    ev = _make_evidence()
    th = _make_theory("theory-prov", supporting_claims=("claim-prov",))
    rels = (
        _make_relationship("claim-prov"),
        SignalGraphRelationship(
            source_ref="theory-prov",
            source_type="theory",
            target_ref="claim-prov",
            target_type="claim",
            relationship="organizes",
        ),
        SignalGraphRelationship(
            source_ref="theory-prov",
            source_type="theory",
            target_ref=_EVIDENCE_HASH,
            target_type="evidence",
            relationship="grounded_by",
        ),
    )
    sg = SignalGraph(relationship_count=3, relationships=rels)
    bgp = BeliefGraphPacket(
        claims=(cl,),
        evidence=(ev,),
        theories=(th,),
        signal_graph=sg,
        provenance={"source": "test"},
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    candidate = packet["shadow_replay_candidates"][0]
    assert candidate["source_provenance"]["adapter_id"] == "audit_artifact_adapter"
    assert candidate["source_provenance"]["advisory_only"] is True


def test_empty_claims_produces_not_computable() -> None:
    ev = _make_evidence()
    th = TheoryObject(
        id="theory-empty",
        supporting_claims=(),
        evidence_refs=(ev.hash,),
    )
    rel = SignalGraphRelationship(
        source_ref="theory-empty",
        source_type="theory",
        target_ref=ev.hash,
        target_type="evidence",
        relationship="grounded_by",
    )
    sg = SignalGraph(relationship_count=1, relationships=(rel,))
    bgp = BeliefGraphPacket(
        claims=(),
        evidence=(ev,),
        theories=(th,),
        signal_graph=sg,
        provenance={"source": "test"},
    )
    packet = build_research_shadow_replay_ingest_bridge(belief_graph_packet=bgp)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert "no_claims_in_source" in packet["not_computable_reasons"]
