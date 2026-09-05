import importlib.util
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('hyper', ROOT / 'skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_deploy_role.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

@pytest.mark.parametrize('flags', [[], ['--dry-run']])
def test_input_is_standalone_and_default_never_posts(tmp_path, monkeypatch, capsys, flags):
    p = tmp_path / 'role.json'
    p.write_text('{"name":"review-only"}')
    monkeypatch.setattr(sys, 'argv', ['hyper', '--input', str(p), *flags])
    monkeypatch.setattr(m, 'post_payload', lambda *a: pytest.fail('unexpected post'))
    assert m.main() == 0
    assert json.loads(capsys.readouterr().out)['deployment_mode'] == 'dry_run'


def test_unverified_deploy_is_disabled(monkeypatch):
    monkeypatch.setenv('HYPERAGENT_DEPLOY_URL', 'http://example.invalid')
    monkeypatch.setenv('HYPERAGENT_API_KEY', 'synthetic-test-token')
    if hasattr(m, 'urlopen'):
        monkeypatch.setattr(m, 'urlopen', lambda *a, **kw: pytest.fail('network forbidden'))
    with pytest.raises(ValueError, match='DEPLOYMENT_DISABLED'):
        m.post_payload({'name':'test'})
