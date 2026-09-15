#!/usr/bin/env python3
"""Fail-closed ingestion of normalized provider envelopes (not provider adapters)."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from jsonschema import Draft202012Validator
from requests.adapters import HTTPAdapter
from requests_cache import CachedSession
from urllib3.util.retry import Retry

# Only this narrow normalized envelope is supported. Provider-specific schemas
# must be supplied explicitly; this is not HollerSportsBatch validation.
SCHEMA_VERSION = "HollerNormalizedEnvelope.v1"
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "required": ["data"],
    "not": {"anyOf": [{"required": [key]} for key in ("error", "errors", "fallback")]},
    "properties": {"data": {"type": "array", "items": {"type": "object", "minProperties": 1}}},
}


class IngestError(ValueError):
    """An ingestion failure; no observation or success receipt was produced."""


class HollerIngestClient:
    def __init__(self, cache_dir="~/.holler/cache", timeout=10):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = CachedSession(str(self.cache_dir / "ingest_cache"), expire_after=300, allowable_methods=('GET',))
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        self.timeout = timeout

    def fetch(self, provider, url, params=None, schema_version=SCHEMA_VERSION):
        if schema_version != SCHEMA_VERSION:
            raise IngestError("UNSUPPORTED_SCHEMA")
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            # Do not expose bearer tokens, signed URLs, or raw service responses.
            raise IngestError("FETCH_FAILED: " + type(exc).__name__) from None
        try:
            Draft202012Validator(SCHEMA).validate(data)
            canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False)
        except (ValueError, TypeError) as exc:
            raise IngestError("SCHEMA_INVALID") from None
        except Exception as exc:
            from jsonschema import ValidationError
            if isinstance(exc, ValidationError):
                raise IngestError("SCHEMA_INVALID") from None
            raise
        return {
            "observed": data,
            "inferred": {"provider": provider, "status": "ingested", "cached": bool(getattr(response, 'from_cache', False))},
            "speculative": {},
            "provenance": {"canonical_hash": hashlib.sha256(canonical.encode()).hexdigest(),
                           "timestamp": datetime.now(timezone.utc).isoformat(),
                           "source_date": getattr(response, 'headers', {}).get('Date'),
                           "source_last_modified": getattr(response, 'headers', {}).get('Last-Modified'),
                           "cache_created_at": response.created_at.isoformat() if getattr(response, 'created_at', None) else None,
                           "cache_expires_at": response.expires.isoformat() if getattr(response, 'expires', None) else None,
                           "cache_expired": getattr(response, 'is_expired', None),
                           "version": schema_version, "brier": None},
            "schema_valid": True, "schema_version": schema_version,
        }

    def batch_ingest(self, jobs):
        results = []
        for index, job in enumerate(jobs):
            results.append({"job_id": str(index), "provider": job['provider'],
                            "receipt": self.fetch(job['provider'], job['url'], job.get('params'))})
        return {"results": results, "total_jobs": len(results)}


if __name__ == '__main__':
    raise SystemExit('No implicit live request. Import HollerIngestClient and supply an approved provider URL.')
