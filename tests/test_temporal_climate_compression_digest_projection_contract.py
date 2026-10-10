import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_compression_digest.digest import canonical_temporal_compression_digest_projection_json, derive_temporal_compression_digest_projection, temporal_compression_digest_projection_hash, write_temporal_compression_digest_projection_contract_audit
from core.temporal_compression_digest.validator import validate_temporal_compression_digest_projection


def _ledger(posture="STABLE", clusters=(), motifs=()):
    return {"ledger_posture": posture, "compression_clusters": clusters, "compression_motifs": motifs}


def test_digest_derivation_rules():
    assert derive_temporal_compression_digest_projection([]).digest_status in {"NOT_COMPUTABLE", "INSUFFICIENT_COMPRESSION_INPUTS"}
    stable = derive_temporal_compression_digest_projection([_ledger()])
    assert stable.digest_status in {"DIGEST_STABLE", "DIGEST_READY"}
    pressure = derive_temporal_compression_digest_projection([_ledger("PRESSURE", ({"cluster_type":"PRESSURE_CLUSTER","cluster_posture":"WATCH","signal_count":1,"source_ref_ids":()},), ({"motif_type":"RECURSIVE_PRESSURE","motif_weight":0.6,"motif_visibility":"MEDIUM"},))])
    assert pressure.digest_status == "DIGEST_PRESSURE"
    regime = derive_temporal_compression_digest_projection([_ledger("REGIME_RISK", ({"cluster_type":"REGIME_CLUSTER","cluster_posture":"WARN","signal_count":1,"source_ref_ids":()},), ({"motif_type":"RECURRING_REGIME_SHIFT","motif_weight":0.7,"motif_visibility":"HIGH"},))])
    assert regime.digest_status == "DIGEST_REGIME_RISK"
    fracture = derive_temporal_compression_digest_projection([_ledger("FRACTURE_RISK", ({"cluster_type":"FRACTURE_CLUSTER","cluster_posture":"WARN","signal_count":1,"source_ref_ids":()},), ({"motif_type":"FRACTURE_PROPAGATION","motif_weight":0.8,"motif_visibility":"HIGH"},))])
    assert fracture.digest_status == "DIGEST_FRACTURE_RISK"
    nondet = derive_temporal_compression_digest_projection([_ledger("NONDETERMINISM", ({"cluster_type":"NONDETERMINISM_CLUSTER","cluster_posture":"BLOCKED","signal_count":1,"source_ref_ids":()},), ({"motif_type":"NONDETERMINISM_RECURSION","motif_weight":0.9,"motif_visibility":"BLOCKED"},))])
    assert nondet.digest_status == "DIGEST_NONDETERMINISM"
    blocked = derive_temporal_compression_digest_projection([_ledger("BLOCKED", ({"cluster_type":"BLOCKED_HISTORY_CLUSTER","cluster_posture":"BLOCKED","signal_count":1,"source_ref_ids":()},), ({"motif_type":"BLOCKED_HISTORY_RECURSION","motif_weight":0.9,"motif_visibility":"BLOCKED"},))])
    assert blocked.digest_status == "DIGEST_BLOCKED_HISTORY"


def test_digest_validation_hash_schema_and_audit(tmp_path):
    base = derive_temporal_compression_digest_projection([_ledger("PRESSURE", ({"cluster_type":"PRESSURE_CLUSTER","cluster_posture":"WATCH","signal_count":1,"source_ref_ids":()},), ({"motif_type":"RECURSIVE_PRESSURE","motif_weight":0.6,"motif_visibility":"MEDIUM"},))])
    assert validate_temporal_compression_digest_projection(replace(base, digest_authoritative=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, rollback_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, promotion_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_compression_digest_projection(replace(base, replay_normalization_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_card = replace(base, signal_cards=(replace(base.signal_cards[0], lineage_preserved=False),) + base.signal_cards[1:])
    assert validate_temporal_compression_digest_projection(bad_card).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_rec = replace(base, recommendations=(replace(base.recommendations[0], execution_allowed=True),))
    assert validate_temporal_compression_digest_projection(bad_rec).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["digest_hash"] = "x"
    assert temporal_compression_digest_projection_hash(base) == temporal_compression_digest_projection_hash(alt)
    assert canonical_temporal_compression_digest_projection_json(base) == canonical_temporal_compression_digest_projection_json(base)
    s = json.loads(open("contracts/temporal_compression_digest/temporal_climate_compression_digest_projection.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))

    h = write_temporal_compression_digest_projection_contract_audit(tmp_path)
    t = open(tmp_path / "out/audit/temporal_climate_compression_digest_projection_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
