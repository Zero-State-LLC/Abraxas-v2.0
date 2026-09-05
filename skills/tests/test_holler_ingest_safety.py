"""Offline audit regressions: injected HTTP responses, never live requests."""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ingest', ROOT / 'skills/holler-sports/holler-ingest/scripts/holler_ingest_client.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def client(tmp_path, data=None, error=None, cached=False):
    c = m.HollerIngestClient(str(tmp_path))
    def get(*args, **kwargs):
        if error:
            raise error
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: data, from_cache=cached)
    c.session = SimpleNamespace(get=get)
    return c


@pytest.mark.parametrize('error', [requests.HTTPError('401'), requests.Timeout('timeout'), ValueError('bad JSON')])
def test_fetch_failure_never_becomes_observed(tmp_path, error):
    with pytest.raises(Exception, match='FETCH_FAILED'):
        client(tmp_path, error=error).fetch('test', 'https://example.invalid')


@pytest.mark.parametrize('data', [{}, {'data': 'wrong'}, {'data': [1]}, {'data':[{}]}, {'error':'denied','data':[]}, {'fallback':True,'data':[]}])
def test_schema_rejects_invalid_payload(tmp_path, data):
    with pytest.raises(Exception, match='SCHEMA_INVALID'):
        client(tmp_path, data=data).fetch('test', 'https://example.invalid')


def test_observed_hash_cache_and_absent_brier(tmp_path):
    data = {'data': [{'id': 1}]}
    result = client(tmp_path, data).fetch('test', 'https://example.invalid')
    assert result['observed'] == data
    assert result['provenance']['canonical_hash'] == hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    assert result['inferred']['cached'] is False
    assert result['provenance']['brier'] is None
    assert client(tmp_path, data, cached=True).fetch('test', 'https://example.invalid')['inferred']['cached'] is True


def test_failure_traceback_does_not_expose_service_secret(tmp_path):
    import traceback
    c = client(tmp_path, error=requests.HTTPError('SECRET-BEARER'))
    try:
        c.fetch('test', 'https://example.invalid')
    except Exception:
        assert 'SECRET-BEARER' not in traceback.format_exc()


def test_response_cache_timing_is_preserved(tmp_path):
    c = client(tmp_path)
    created = __import__('datetime').datetime(2024, 1, 1, tzinfo=__import__('datetime').timezone.utc)
    response = SimpleNamespace(raise_for_status=lambda: None, json=lambda: {'data': []}, from_cache=True, created_at=created, expires=created, is_expired=True, headers={'Date':'source date', 'Last-Modified':'source modification'})
    c.session = SimpleNamespace(get=lambda *a, **kw: response)
    p = c.fetch('test', 'https://example.invalid')['provenance']
    assert p['cache_created_at'] == created.isoformat()
    assert p['cache_expires_at'] == created.isoformat()
    assert p['cache_expired'] is True
    assert p['source_date'] == 'source date'
    assert p['source_last_modified'] == 'source modification'


def test_duplicate_provider_jobs_preserved(tmp_path):
    result = client(tmp_path, {'data': []}).batch_ingest([{'provider':'test', 'url':'https://example.invalid/a'}, {'provider':'test', 'url':'https://example.invalid/b'}])
    assert len(result['results']) == 2
    assert len({r['job_id'] for r in result['results']}) == 2
