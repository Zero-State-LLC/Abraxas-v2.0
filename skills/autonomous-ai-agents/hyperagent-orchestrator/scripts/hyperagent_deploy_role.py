#!/usr/bin/env python3
"""Deterministic HyperAgent role payload builder.

Outputs a stable JSON payload suitable for review, export, or posting to a
HyperAgent deployment endpoint if one is configured.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


def load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_payload(template: dict[str, Any], name: str | None, mission: str | None, dry_run: bool) -> dict[str, Any]:
    payload = dict(template)
    if name:
        payload["name"] = name
    if mission:
        payload["mission"] = mission
    payload.setdefault("version", "0.1.0")
    payload.setdefault("tools", [])
    payload.setdefault("budget", {"max_cost_usd": 0, "max_steps": 1})
    payload["deployment_mode"] = "dry_run" if dry_run else "deploy"
    return payload


def post_payload(payload: dict[str, Any]) -> dict[str, Any]:
    endpoint = os.getenv("HYPERAGENT_DEPLOY_URL")
    token = os.getenv("HYPERAGENT_OAUTH_TOKEN") or os.getenv("HYPERAGENT_API_KEY")
    if not endpoint:
        return {"status": "skipped", "reason": "HYPERAGENT_DEPLOY_URL not set", "payload": payload}
    req = Request(
        endpoint,
        data=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "hyperagent-orchestrator-deploy-role/1.0",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return {"status": "posted", "http_status": getattr(resp, "status", 200), "body": body}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, help="Path to a JSON role template")
    parser.add_argument("--input", help="Optional input role JSON to use instead of template fields")
    parser.add_argument("--name", help="Override the role name")
    parser.add_argument("--mission", help="Override the mission text")
    parser.add_argument("--dry-run", action="store_true", help="Print payload instead of posting")
    args = parser.parse_args()

    template = load_json(args.input) if args.input else load_json(args.template)
    payload = build_payload(template, args.name, args.mission, args.dry_run)

    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    result = post_payload(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
