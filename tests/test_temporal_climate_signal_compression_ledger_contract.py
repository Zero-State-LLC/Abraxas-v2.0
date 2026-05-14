import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_signal_compression.ledger import canonical_temporal_signal_compression_ledger_json, derive_temporal_signal_compression_ledger, temporal_signal_compression_ledger_hash, write_temporal_signal_compression_ledger_contract_audit
from core.temporal_signal_compression.validator import validate_temporal_signal_compression_ledger


def _queue(items=()):
    return {"queue_items": items}


def test_signal_compression_derivation_rules():
    assert derive_temporal_signal_compression_ledger([]).ledger_status in {"NOT_COMPUTABLE", "INSUFFICIENT_SIGNAL_INPUTS"}
    stable = derive_temporal_signal_compression_ledger([_queue()])
    assert stable.ledger_status in {"COMPRESSED", "COMPRESSED_STABLE"}
    pressure = derive_temporal_signal_compression_ledger([_queue(({"item_type": "PRESSURE_SPIKE", "source_ref_ids": ()},))])
    assert pressure.ledger_status == "COMPRESSED_PRESSURE"
    regime = derive_temporal_signal_compression_ledger([_queue(({"item_type": "REGIME_SHIFT", "source_ref_ids": ()},))])
    assert regime.ledger_status == "COMPRESSED_REGIME_RISK"
    fracture = derive_temporal_signal_compression_ledger([_queue(({"item_type": "FRACTURE_CLUSTER", "source_ref_ids": ()},))])
    assert fracture.ledger_status == "COMPRESSED_FRACTURE_RISK"
    nondet = derive_temporal_signal_compression_ledger([_queue(({"item_type": "NONDETERMINISM_CLUSTER", "source_ref_ids": ()},))])
    assert nondet.ledger_status == "COMPRESSED_NONDETERMINISM"
    overload = derive_temporal_signal_compression_ledger([_queue(({"item_type": "PRESSURE_SPIKE", "source_ref_ids": ()}, {"item_type": "REGIME_SHIFT", "source_ref_ids": ()}, {"item_type": "FRACTURE_CLUSTER", "source_ref_ids": ()}, {"item_type": "NONDETERMINISM_CLUSTER", "source_ref_ids": ()}))])
    assert overload.ledger_status in {"SIGNAL_OVERLOAD", "BLOCKED_HISTORY_VISIBLE", "COMPRESSED_NONDETERMINISM"}
    blocked = derive_temporal_signal_compression_ledger([_queue(({"item_type": "BLOCKED_HISTORY", "source_ref_ids": ()},))])
    assert any(c.cluster_type == "BLOCKED_HISTORY_CLUSTER" for c in blocked.compression_clusters)
    assert any(c.cluster_type == "NONDETERMINISM_CLUSTER" for c in nondet.compression_clusters)


def test_signal_compression_validator_hash_schema_and_audit():
    base = derive_temporal_signal_compression_ledger([_queue(({"item_type": "PRESSURE_SPIKE", "source_ref_ids": ()},))])
    bad_cluster = replace(base, compression_clusters=(replace(base.compression_clusters[0], lineage_preserved=False),))
    assert validate_temporal_signal_compression_ledger(bad_cluster).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_cluster2 = replace(base, compression_clusters=(replace(base.compression_clusters[0], replay_normalization_allowed=True),))
    assert validate_temporal_signal_compression_ledger(bad_cluster2).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_cluster3 = replace(base, compression_clusters=(replace(base.compression_clusters[0], canonical_selection_allowed=True),))
    assert validate_temporal_signal_compression_ledger(bad_cluster3).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_signal_compression_ledger(replace(base, execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_signal_compression_ledger(replace(base, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_signal_compression_ledger(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_signal_compression_ledger(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_signal_compression_ledger(replace(base, adapter_activation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_rec = replace(base, recommendations=(replace(base.recommendations[0], execution_allowed=True),))
    assert validate_temporal_signal_compression_ledger(bad_rec).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_rec2 = replace(base, recommendations=(replace(base.recommendations[0], routing_change_allowed=True),))
    assert validate_temporal_signal_compression_ledger(bad_rec2).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["ledger_hash"] = "x"
    assert temporal_signal_compression_ledger_hash(base) == temporal_signal_compression_ledger_hash(alt)
    assert canonical_temporal_signal_compression_ledger_json(base) == canonical_temporal_signal_compression_ledger_json(base)
    s = json.loads(open("contracts/temporal_signal_compression/temporal_climate_signal_compression_ledger.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))

    h = write_temporal_signal_compression_ledger_contract_audit(".")
    t = open("out/audit/temporal_climate_signal_compression_ledger_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
