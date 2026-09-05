import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills/abx-hermes-skill-evolution'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SKILL))
spec = importlib.util.spec_from_file_location('decision_validator', SKILL / 'abx_skill_formal_operator_decision_validator.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def run(tmp_path, monkeypatch, **overrides):
    review = {'formal_review_id':'review-test', 'deterministic_hash':'legacy'}
    decision = {
        'formal_review_id':'review-test', 'review_packet_hash':'legacy',
        'decision_value':'HOLD_FOR_REVIEW',
        'acknowledgements':dict.fromkeys(m.REQUIRED_ACKS, True),
        'authority_boundary':dict.fromkeys(['promotion_authorized','production_activation_allowed','active_skill_replacement_allowed','automatic_transition_allowed'], False),
        'operator':{'operator_id':'synthetic-human', 'operator_display_name':'Fixture'},
        'provenance':{'source':'AGENT_SUPPLIED', 'input_method':'AUTOMATED'},
        'timestamp': datetime.now(timezone.utc).isoformat(),
        **overrides,
    }
    rp = tmp_path / 'review.json'; rp.write_text(json.dumps(review))
    dp = tmp_path / 'decision.json'; dp.write_text(json.dumps(decision))
    monkeypatch.setattr(m, 'COMPLETED_PATH', dp)
    monkeypatch.setattr(m, 'REVIEW_PACKET_PATH', rp)
    monkeypatch.setattr(m, 'OUT', tmp_path)
    return m.main()


def test_builder_requires_confirmation_and_full_review_binding():
    spec = importlib.util.spec_from_file_location('builder', SKILL / 'abx_skill_formal_operator_decision_builder.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    review = {'formal_review_id':'test', 'deterministic_hash':'old'}
    working = {'normalized_fields':{}, 'operator_confirmed':False}
    with pytest.raises(ValueError, match='CONFIRMATION_REQUIRED'):
        builder.build_final_record(builder.resolve_machine_fields(review), working, review)


def test_confirmed_builder_record_binds_full_review():
    import hashlib
    spec = importlib.util.spec_from_file_location('builder', SKILL / 'abx_skill_formal_operator_decision_builder.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    review = {'formal_review_id':'fixture', 'deterministic_hash':'old'}
    working = {'normalized_fields':dict.fromkeys(builder.HUMAN_FIELD_ORDER, True), 'operator_confirmed':True}
    result = builder.build_final_record(builder.resolve_machine_fields(review), working, review)
    expected = hashlib.sha256(json.dumps(review, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert result['confirmed_review_sha256'] == expected
    assert result['operator_confirmed'] is True


def test_builder_rejects_same_id_changed_review_before_prompt(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('builder', SKILL / 'abx_skill_formal_operator_decision_builder.py')
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    review = {'formal_review_id':'same-id', 'deterministic_hash':'new'}
    monkeypatch.setattr(builder, 'load_review_packet', lambda: review)
    monkeypatch.setattr(builder, 'load_working', lambda: {'formal_review_id':'same-id', 'review_sha256':'old', 'normalized_fields':{}})
    monkeypatch.setattr('builtins.input', lambda *args: pytest.fail('must not reuse acknowledgments after drift'))
    assert builder.interactive_collect()['builder_status'] == 'BLOCKED_BY_PACKET_DRIFT'


def test_agent_filled_acknowledgments_rejected(tmp_path, monkeypatch):
    assert run(tmp_path, monkeypatch)['status'] == 'BLOCKED_BY_VALIDATION_ERRORS'


def test_stale_decision_rejected(tmp_path, monkeypatch):
    assert run(tmp_path, monkeypatch, timestamp='2000-01-01T00:00:00+00:00', provenance={'source':'OPERATOR_SUPPLIED','input_method':'INTERACTIVE_ONE_AT_A_TIME'})['status'] == 'BLOCKED_BY_VALIDATION_ERRORS'
