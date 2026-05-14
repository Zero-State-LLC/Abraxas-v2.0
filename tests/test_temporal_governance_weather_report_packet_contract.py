import json
from dataclasses import replace, asdict
from pathlib import Path
from core.temporal_weather_report.report import canonical_temporal_governance_weather_report_packet_json, temporal_governance_weather_report_packet_hash, derive_temporal_governance_weather_report_packet, write_temporal_governance_weather_report_packet_contract_audit
from core.temporal_weather_report.validator import validate_temporal_governance_weather_report_packet

def test_states_visibility_and_controls(tmp_path):
    assert derive_temporal_governance_weather_report_packet([]).report_status in {"NOT_COMPUTABLE","INSUFFICIENT_OBSERVATORY_INPUTS"}
    assert derive_temporal_governance_weather_report_packet([{"type":"TEMPORAL_GOVERNANCE_DRIFT_OBSERVATORY","pressure":0.1}]).report_status=="WEATHER_CLEAR"
    assert derive_temporal_governance_weather_report_packet([{"type":"TEMPORAL_GOVERNANCE_DRIFT_OBSERVATORY","pressure":0.4,"drift":True}]).report_status=="DRIFT_FRONT_PRESENT"
    assert derive_temporal_governance_weather_report_packet([{"pressure":0.3,"fracture":True}]).report_status=="FRACTURE_STORM_PRESENT"
    assert derive_temporal_governance_weather_report_packet([{"pressure":0.3,"blocked":True}]).report_status=="BLOCKED_HISTORY_FRONT_PRESENT"
    assert derive_temporal_governance_weather_report_packet([{"pressure":0.3,"nondeterminism":True}]).report_status=="NONDETERMINISM_FRONT_PRESENT"
    assert derive_temporal_governance_weather_report_packet([{"pressure":0.3,"stale":True}]).report_status=="STALE_PROPAGATION_PRESENT"
    assert derive_temporal_governance_weather_report_packet([{"pressure":0.9,"overload":True}]).report_status in {"OPERATOR_LOAD_HIGH","OPERATOR_REVIEW_REQUIRED"}
    o=derive_temporal_governance_weather_report_packet([{"pressure":0.5,"fracture":True,"nondeterminism":True,"blocked":True}])
    assert any("BLOCKED" in s.section_type for s in o.sections) and any("BLOCKED" in a.alert_type for a in o.alerts) and any("BLOCKED" in f.front_type for f in o.pressure_fronts)
    assert any("NONDETERMINISM" in s.section_type for s in o.sections) and any("NONDETERMINISM" in a.alert_type for a in o.alerts) and any("NONDETERMINISM" in f.front_type for f in o.pressure_fronts)
    assert any("FRACTURE" in s.section_type for s in o.sections) and any("FRACTURE" in a.alert_type for a in o.alerts) and any("FRACTURE" in f.front_type for f in o.pressure_fronts)
    for bad in [replace(o,projection_only=False),replace(o,report_authoritative=True),replace(o,inference_authority_allowed=True),replace(o,action_authorization_allowed=True),replace(o,execution_allowed=True),replace(o,mutation_allowed=True),replace(o,rollback_allowed=True),replace(o,promotion_allowed=True),replace(o,routing_change_allowed=True),replace(o,replay_normalization_allowed=True),replace(o,canonical_selection_allowed=True),replace(o,pressure_fronts=(replace(o.pressure_fronts[0],lineage_preserved=False),)),replace(o,review_prompts=(replace(o.review_prompts[0],execution_allowed=True),)),replace(o,review_prompts=(replace(o.review_prompts[0],routing_change_allowed=True),))]:
        assert validate_temporal_governance_weather_report_packet(bad).status=="BLOCKED"
    assert temporal_governance_weather_report_packet_hash(replace(o,report_hash="x"))==o.report_hash
    assert canonical_temporal_governance_weather_report_packet_json(o)==canonical_temporal_governance_weather_report_packet_json(o)
    schema=json.loads(Path("contracts/temporal_weather_report/temporal_governance_weather_report_packet.v1.schema.json").read_text())
    for k in schema["required"]:
        assert k in asdict(o)
    h=write_temporal_governance_weather_report_packet_contract_audit(tmp_path)
    text=(tmp_path/"out/audit/temporal_governance_weather_report_packet_contract.latest.json").read_text()
    assert text.endswith("\n") and h
