import json
from dataclasses import replace, asdict
from pathlib import Path
from core.temporal_governance_drift.observatory import *
from core.temporal_governance_drift.validator import validate_temporal_governance_drift_observatory


def test_observatory_states_and_rules(tmp_path):
    assert derive_temporal_governance_drift_observatory([]).observatory_status in {"INSUFFICIENT_OBSERVATORY_INPUTS","NOT_COMPUTABLE"}
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_CONTINUITY_INDEX","pressure":0.1}]).observatory_status=="STABLE"
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_CONTINUITY_INDEX","pressure":0.4}]).observatory_status=="DRIFT_OBSERVED"
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_GOVERNANCE_TOPOLOGY_INDEX","pressure":0.3,"fracture":True}]).observatory_status=="FRACTURE_CONCENTRATION"
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_SIGNAL_COMPRESSION_LEDGER","pressure":0.3,"blocked":True}]).observatory_status=="BLOCKED_HISTORY_ACCUMULATION"
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_SIGNAL_COMPRESSION_LEDGER","pressure":0.3,"nondeterminism":True}]).observatory_status=="NONDETERMINISM_CLUSTER"
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_CONTRACT_RECONCILIATION_MANIFEST","pressure":0.3,"stale":True}]).observatory_status=="STALE_PROPAGATION"
    assert derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_OPERATOR_REVIEW_QUEUE","pressure":0.9,"overload":True}]).observatory_status in {"SIGNAL_OVERLOAD","OPERATOR_REVIEW_REQUIRED"}


def test_visibility_and_validation_and_hash_schema_audit(tmp_path):
    o=derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_SIGNAL_COMPRESSION_LEDGER","pressure":0.5,"fracture":True,"nondeterminism":True,"blocked":True}])
    assert all(p.blocked_visibility_preserved for p in o.pressure_bands)
    assert all(p.nondeterminism_visibility_preserved for p in o.pressure_bands)
    assert any(z.zone_type=="FRACTURE_ZONE" for z in o.drift_zones)
    for bad in [replace(o,projection_only=False),replace(o,observatory_authoritative=True),replace(o,execution_allowed=True),replace(o,mutation_allowed=True),replace(o,rollback_allowed=True),replace(o,promotion_allowed=True),replace(o,routing_change_allowed=True),replace(o,replay_normalization_allowed=True),replace(o,canonical_selection_allowed=True)]:
        assert validate_temporal_governance_drift_observatory(bad).status=="BLOCKED"
    assert temporal_governance_drift_observatory_hash(replace(o,observatory_hash="x"))==o.observatory_hash
    assert canonical_temporal_governance_drift_observatory_json(o)==canonical_temporal_governance_drift_observatory_json(o)
    schema=json.loads(Path("contracts/temporal_governance_drift/temporal_governance_drift_observatory.v1.schema.json").read_text())
    for k in schema["required"]: assert k in asdict(o)
    h=write_temporal_governance_drift_observatory_contract_audit(tmp_path)
    text=(tmp_path/"out/audit/temporal_governance_drift_observatory_contract.latest.json").read_text()
    assert text.endswith("\n") and h
