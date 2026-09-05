"""Synthetic, local-only regressions for independent review blockers."""
import copy
import hashlib
import importlib.util
import json
import sys

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills/abx-hermes-skill-evolution'
sys.path[:0] = [str(ROOT), str(SKILL)]


def module(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / f'abx_skill_formal_operator_decision_{name}.py')
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


b = module('builder')
v = module('validator')


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def review():
    return {'formal_review_id': 'synthetic-review', 'deterministic_hash': 'legacy', 'evidence': 'old'}


def working(packet):
    fields: dict = dict.fromkeys(b.HUMAN_FIELD_ORDER, True)
    fields.update({'operator.operator_id': 'synthetic-human', 'operator.operator_display_name': 'Fixture', 'decision_value': 'HOLD_FOR_REVIEW', 'operator_notes': ''})
    return {'formal_review_id': packet['formal_review_id'], 'review_sha256': digest(packet), 'confirmed_review_sha256': digest(packet), 'normalized_fields': fields, 'operator_confirmed': True, 'original_responses': [], 'invalid_fields': []}


def test_direct_builder_cannot_rebind_stale_confirmation():
    packet = review()
    state = working(packet)
    control = b.build_final_record(b.resolve_machine_fields(packet), state, packet)
    assert control['confirmed_review_sha256'] == digest(packet)
    packet['evidence'] = 'changed'
    with pytest.raises(ValueError, match='IMMUTABLE_REVIEW_BINDING_MISMATCH'):
        b.build_final_record(b.resolve_machine_fields(packet), state, packet)


def setup_builder(tmp_path, monkeypatch, packet, state):
    monkeypatch.setattr(b, 'WORKING_PATH', tmp_path / 'working.json')
    monkeypatch.setattr(b, 'COMPLETED_PATH', tmp_path / 'completed.json')
    monkeypatch.setattr(b, 'load_review_packet', lambda: copy.deepcopy(packet))
    b.save_working(state)


def test_same_id_content_resume_clears_answers_then_recollects(tmp_path, monkeypatch, capsys):
    packet = review()
    state = working(packet)
    packet['evidence'] = 'changed'
    setup_builder(tmp_path, monkeypatch, packet, state)
    monkeypatch.setattr('builtins.input', lambda _: pytest.fail('drift must block this invocation'))
    assert b.interactive_collect()['builder_status'] == 'BLOCKED_BY_PACKET_DRIFT'
    saved = json.loads(b.WORKING_PATH.read_text())
    assert saved['normalized_fields'] == {}
    assert saved['operator_confirmed'] is False
    assert saved.get('confirmed_review_sha256') is None
    answers = iter(['synthetic-human', 'Fixture', 'hold', 'y', 'y', 'y', 'y', 'y', '', 'y', 'CONFIRM'])
    prompts = []
    def respond(prompt):
        prompts.append(prompt)
        assert json.loads(b.WORKING_PATH.read_text())['review_sha256'] == digest(packet)
        return next(answers)
    monkeypatch.setattr('builtins.input', respond)
    result = b.interactive_collect()
    assert len(prompts) == len(b.HUMAN_FIELD_ORDER) + 1
    assert result['confirmed_review_sha256'] == digest(packet)
    displayed = capsys.readouterr().out
    assert digest(packet) in displayed and 'changed' in displayed


@pytest.mark.parametrize('change_at', ['before_confirmation', 'during_confirmation', 'before_write'])
def test_source_drift_never_persists(tmp_path, monkeypatch, change_at):
    packet = review()
    state = working(packet)
    state['operator_confirmed'] = False
    setup_builder(tmp_path, monkeypatch, packet, state)
    calls = 0
    def load():
        nonlocal calls
        calls += 1
        if change_at == 'before_confirmation' and calls > 1:
            packet['evidence'] = 'changed'
        return copy.deepcopy(packet)
    monkeypatch.setattr(b, 'load_review_packet', load)
    original_build = b.build_final_record
    def build(*args):
        result = original_build(*args)
        if change_at == 'before_write':
            packet['evidence'] = 'changed'
        return result
    monkeypatch.setattr(b, 'build_final_record', build)
    def respond(_):
        if change_at == 'before_confirmation':
            pytest.fail('changed source must block before confirmation prompt')
        if change_at == 'during_confirmation':
            packet['evidence'] = 'changed'
        return 'CONFIRM'
    monkeypatch.setattr('builtins.input', respond)
    assert b.interactive_collect()['builder_status'] == 'BLOCKED_BY_PACKET_DRIFT'
    assert not b.COMPLETED_PATH.exists()


def setup_validator(tmp_path, monkeypatch):
    packet = review()
    decision = b.build_final_record(b.resolve_machine_fields(packet), working(packet), packet)
    monkeypatch.setattr(v, 'OUT', tmp_path)
    monkeypatch.setattr(v, 'COMPLETED_PATH', tmp_path / 'decision.json')
    monkeypatch.setattr(v, 'REVIEW_PACKET_PATH', tmp_path / 'review.json')
    v.COMPLETED_PATH.write_text(json.dumps(decision))
    v.REVIEW_PACKET_PATH.write_text(json.dumps(packet))
    receipt = tmp_path / 'abx_hermes_formal_operator_decision_validation_v2_8.latest.json'
    assert v.main()['status'] == 'VALIDATED'
    assert json.loads(receipt.read_text())['status'] == 'VALIDATED'
    return packet, decision, receipt


@pytest.mark.parametrize('target,value,error', [
    ('decision', [], 'INVALID_OBJECT:decision'),
    ('review', [], 'INVALID_OBJECT:review'),
    ('decision', None, 'INVALID_OBJECT:decision'),
    ('review', 'bad', 'INVALID_OBJECT:review'),
    *[(field, bad, 'INVALID_OBJECT:decision.' + field)
      for field in ['provenance', 'acknowledgements', 'authority_boundary', 'operator']
      for bad in [None, []]],
    ('decision_value', [], 'INVALID_STRING:decision.decision_value'),
    ('formal_review_id', {}, 'INVALID_STRING:decision.formal_review_id'),
    ('operator.operator_id', [], 'INVALID_STRING:decision.operator.operator_id'),
    *[(target, bad, 'INVALID_JSON:' + target) for target in ['decision', 'review']
      for bad in [float('nan'), float('inf'), float('-inf')]],
])
def test_malformed_input_replaces_prior_success(tmp_path, monkeypatch, target, value, error):
    _, decision, receipt = setup_validator(tmp_path, monkeypatch)
    path = v.COMPLETED_PATH
    if target in ['decision', 'review']:
        path = v.COMPLETED_PATH if target == 'decision' else v.REVIEW_PACKET_PATH
        payload = value
    else:
        payload = decision
        if '.' in target:
            parent, key = target.split('.')
            payload[parent][key] = value
        else:
            payload[target] = value
    path.write_text(json.dumps(payload))
    result = v.main()
    assert result['status'] == 'BLOCKED_BY_VALIDATION_ERRORS'
    assert error in result['errors']
    saved = json.loads(receipt.read_text())
    assert saved['status'] == result['status']
    assert saved['binding_verified'] is False
    assert saved['input_sha256']['decision'] == hashlib.sha256(v.COMPLETED_PATH.read_bytes()).hexdigest()
    assert saved['input_sha256']['review'] == hashlib.sha256(v.REVIEW_PACKET_PATH.read_bytes()).hexdigest()


@pytest.mark.parametrize('field,value,error', [
    ('timestamp', '2000-01-01T00:00:00+00:00', 'STALE_OR_FUTURE_DECISION'),
    ('provenance', {'source': 'AGENT_SUPPLIED', 'input_method': 'AUTOMATED'}, 'HUMAN_INPUT_REQUIRED'),
])
def test_targeted_invalid_decision_from_valid_control(tmp_path, monkeypatch, field, value, error):
    _, decision, _ = setup_validator(tmp_path, monkeypatch)
    decision[field] = value
    v.COMPLETED_PATH.write_text(json.dumps(decision))
    assert v.main()['errors'] == [error]


@pytest.mark.parametrize('raw', ['null', '[]', '{"provenance":null}', '{"extra":[NaN]}', '{"extra":[Infinity]}', '{"extra":1e999}', '{'])
def test_nested_nonfinite_or_invalid_json_replaces_success(tmp_path, monkeypatch, raw):
    _, _, receipt = setup_validator(tmp_path, monkeypatch)
    v.REVIEW_PACKET_PATH.write_text(raw)
    result = v.main()
    assert result['status'] == 'BLOCKED_BY_VALIDATION_ERRORS'
    assert json.loads(receipt.read_text())['status'] == result['status']
    if 'extra' in raw or raw == '{':
        assert 'INVALID_JSON:review' in result['errors']


@pytest.mark.parametrize('raw', [None, 'null', '[]', '{"provenance":null}', '{"extra":[NaN]}', '{'])
def test_validator_cli_invalid_input_is_nonzero(tmp_path, monkeypatch, raw):
    import os
    import subprocess
    packet, decision, _ = setup_validator(tmp_path, monkeypatch)
    audit = tmp_path / 'out/audit'
    audit.mkdir(parents=True)
    receipt = audit / 'abx_hermes_formal_operator_decision_validation_v2_8.latest.json'

    # Use the CLI's exact fixed filenames, not monkeypatched module paths.
    (audit / 'abx_hermes_formal_operator_review_packet_v2_6.latest.json').write_text(json.dumps(packet))
    operator = tmp_path / 'out/operator_input'
    operator.mkdir()
    decision_path = operator / 'abx_hermes_formal_operator_decision_v2_7.input.json'
    decision_path.write_text(json.dumps(decision))
    command = [sys.executable, str(SKILL / 'abx_skill_formal_operator_decision_validator.py')]
    env = {**os.environ, 'PYTHONPATH': str(ROOT)}
    control = subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True)
    assert control.returncode == 0
    assert json.loads(receipt.read_text())['status'] == 'VALIDATED'
    if raw is not None:
        decision_path.write_text(raw)
    else:
        decision_path.unlink()
    result = subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Traceback' not in result.stderr
    assert json.loads(receipt.read_text())['status'] != 'VALIDATED'
