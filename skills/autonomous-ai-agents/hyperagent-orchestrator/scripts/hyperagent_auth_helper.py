#!/usr/bin/env python3
"""Local HyperAgent auth/session inspector.

This is intentionally conservative: it does not assume a specific live API.
It reports the credential sources and, if an endpoint is configured, can probe
it with a simple GET request.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


def env(name: str) -> str | None:
    value = os.getenv(name)
    return value if value else None


def inspect_session() -> dict:
    creds = {
        "HYPERAGENT_API_KEY": bool(env("HYPERAGENT_API_KEY")),
        "HYPERAGENT_OAUTH_TOKEN": bool(env("HYPERAGENT_OAUTH_TOKEN")),
        "HYPERAGENT_SESSION_TOKEN": bool(env("HYPERAGENT_SESSION_TOKEN")),
        "HYPERAGENT_SECURE_STORE": env("HYPERAGENT_SECURE_STORE"),
        "HYPERAGENT_BASE_URL": env("HYPERAGENT_BASE_URL"),
        "HYPERAGENT_AUTH_PATH": env("HYPERAGENT_AUTH_PATH"),
        "HYPERAGENT_SESSION_FILE": env("HYPERAGENT_SESSION_FILE"),
    }
    if creds["HYPERAGENT_SESSION_FILE"]:
        creds["session_file_exists"] = Path(creds["HYPERAGENT_SESSION_FILE"]).expanduser().exists()
    return {
        "status": "ok",
        "credential_sources": creds,
        "missing_required": [k for k, v in creds.items() if isinstance(v, bool) and not v],
        "notes": [
            "Prefer env vars or a secure store.",
            "Do not print tokens.",
            "Use a live endpoint only when explicitly configured.",
        ],
    }


def probe_endpoint(base_url: str, auth_path: str) -> dict:
    url = base_url.rstrip("/") + "/" + auth_path.lstrip("/")
    req = Request(url, headers={"User-Agent": "hyperagent-orchestrator-auth-helper/1.0"})
    try:
        with urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "status": "ok",
                "url": url,
                "http_status": getattr(resp, "status", 200),
                "body_preview": body[:1000],
            }
    except HTTPError as exc:
        return {"status": "http_error", "url": url, "http_status": exc.code, "reason": exc.reason}
    except URLError as exc:
        return {"status": "url_error", "url": url, "reason": str(exc.reason)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="Print deterministic credential status")
    parser.add_argument("--probe", action="store_true", help="Probe a configured auth endpoint")
    args = parser.parse_args()

    payload = inspect_session()
    if args.probe:
        base_url = env("HYPERAGENT_BASE_URL")
        auth_path = env("HYPERAGENT_AUTH_PATH") or "/api/me"
        if not base_url:
            payload["probe"] = {"status": "skipped", "reason": "HYPERAGENT_BASE_URL not set"}
        else:
            payload["probe"] = probe_endpoint(base_url, auth_path)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
