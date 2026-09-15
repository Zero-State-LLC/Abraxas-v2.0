#!/usr/bin/env python3
"""Offline role-payload planner. No verified platform deployment adapter is shipped."""
import argparse
import json
from pathlib import Path


def load_json(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('ROLE_MUST_BE_OBJECT')
    return value


def build_payload(template, name=None, mission=None, dry_run=True):
    if not dry_run:
        raise ValueError('DEPLOYMENT_DISABLED: verified platform adapter required')
    payload = dict(template)
    if name:
        payload['name'] = name
    if mission:
        payload['mission'] = mission
    payload.setdefault('version', '0.1.0')
    payload.setdefault('tools', [])
    payload.setdefault('budget', {'max_cost_usd': 0, 'max_steps': 1})
    payload['deployment_mode'] = 'dry_run'
    return payload


def post_payload(payload):
    raise ValueError('DEPLOYMENT_DISABLED: no verified endpoint, consent binding, or read-back adapter')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--template')
    source.add_argument('--input')
    parser.add_argument('--name')
    parser.add_argument('--mission')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='Default; render local review JSON only')
    mode.add_argument('--deploy', action='store_true', help='Reserved: fails closed until verified adapter exists')
    args = parser.parse_args()
    if args.deploy:
        parser.error('DEPLOYMENT_DISABLED: no verified platform adapter; no credentials read or sent')
    try:
        payload = build_payload(load_json(args.input or args.template), args.name, args.mission)
        text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(type(exc).__name__ + ': invalid role input')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
