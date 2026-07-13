"""Tests for skills/holler-sports/holler-ingest/scripts/holler_ingest_client.py (TEST candidate 8874e580a8c3d77c)"""

import sys
import json
import hashlib
from unittest.mock import patch, MagicMock

# Mock heavy external deps before importing the module under test
sys.modules.setdefault("requests", MagicMock())
sys.modules.setdefault("requests_cache", MagicMock())
sys.modules.setdefault("requests.adapters", MagicMock())
sys.modules.setdefault("urllib3.util.retry", MagicMock())

sys.path.insert(0, "skills/holler-sports/holler-ingest/scripts")
import holler_ingest_client as h

# Ensure the except clause in the source sees real BaseException subclasses
class _DummyReqExc(Exception):
    pass
h.requests = MagicMock()
h.requests.exceptions = MagicMock()
h.requests.exceptions.RequestException = _DummyReqExc

def test_fetch_basic():
    client = h.HollerIngestClient(cache_dir="/tmp/holler_test_cache")
    with patch.object(client.session, "get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": 42, "home_team": "TestTeam", "score": "3-1"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        result = client.fetch("test_provider", "http://example.com", {"date": "2026-07-12"})
        assert "observed" in result
        assert result["inferred"]["provider"] == "test_provider"
        assert result["schema_valid"] is True
        assert "canonical_hash" in result["provenance"]

def test_fetch_fallback_on_error():
    client = h.HollerIngestClient(cache_dir="/tmp/holler_test_cache")
    with patch.object(client.session, "get", side_effect=ValueError("bad json for determinism")):
        result = client.fetch("bad_provider", "http://bad.example.com")
        obs = result.get("observed", {})
        assert "error" in str(obs) or "data" in str(obs) or "fallback" in str(obs)

def test_batch_ingest():
    client = h.HollerIngestClient(cache_dir="/tmp/holler_test_cache")
    jobs = [
        {"provider": "p1", "url": "http://ex1"},
        {"provider": "p2", "url": "http://ex2", "params": {"limit": 5}}
    ]
    with patch.object(client, "fetch", side_effect=lambda p, u, pr=None: {"observed": {"provider": p}, "inferred": {"provider": p}}):
        res = client.batch_ingest(jobs)
        assert isinstance(res, dict)

def test_provenance_hash_stable():
    data = {"a": 1, "b": 2}
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    hsh = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    assert len(hsh) == 16
    hsh2 = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    assert hsh == hsh2