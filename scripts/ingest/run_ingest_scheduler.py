#!/usr/bin/env python3
"""WP-D4-C2 sole-writer: controlled ingest scheduler decisions + manifest + receipt.

Pure builders live in core.ingest.scheduler; this runner owns out/ publication.
Advisory/shadow scheduling only — no execution authority.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.ingest.scheduler import (
    build_scheduled_manifest,
    build_scheduler_markdown,
    build_scheduler_receipt,
    decide_ingest_windows,
)


def _utc_now() -> str:
    return datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

def _default_policy() -> dict:
    return {'schema_version': 'IngestWindowPolicy.v1', 'policy_id': 'abx_controlled_ingest_scheduler_v1', 'timezone': 'UTC', 'global': {'min_seconds_between_runs': 300, 'max_concurrent_adapters': 1, 'quiet_window_enabled': True, 'quiet_window': {'start_hour': 2, 'end_hour': 5, 'cadence_multiplier': 4.0}}, 'domain_policies': {'finance': {'base_cadence_seconds': 900, 'min_cadence_seconds': 300, 'max_cadence_seconds': 3600, 'operator_window_required': False}, 'geopolitics': {'base_cadence_seconds': 3600, 'min_cadence_seconds': 1800, 'max_cadence_seconds': 21600, 'operator_window_required': True}}, 'volatility_policy': {'enabled': True, 'compression_thresholds': [{'metric': 'z_score', 'gte': 2.5, 'cadence_multiplier': 0.5}], 'expansion_thresholds': [{'metric': 'z_score', 'lt': 1.0, 'cadence_multiplier': 2.0}]}}

def _default_adapters() -> dict:
    return {'adapters': [{'adapter_id': 'abx_market_feed_v1', 'domain': 'finance', 'enabled': True}, {'adapter_id': 'abx_geo_feed_v1', 'domain': 'geopolitics', 'enabled': True}]}

def _default_state() -> dict:
    return {'last_run_by_adapter': {}, 'active_operator_windows': [], 'blocked_adapters': []}

def _default_anomaly() -> dict:
    return {'domain_scores': {'finance': {'z_score': 1.2}, 'geopolitics': {'z_score': 0.4}}}

def _load_json(path: Path | None, default: dict) -> dict:
    if path is None or not path.is_file():
        return default
    return json.loads(path.read_text(encoding='utf-8'))

def run(*, out_dir: Path, adapter_config: dict | None=None, window_policy: dict | None=None, scheduler_state: dict | None=None, anomaly_state: dict | None=None, now_iso: str | None=None) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    adapters = adapter_config or _default_adapters()
    policy = window_policy or _default_policy()
    state = scheduler_state or _default_state()
    anomaly = anomaly_state or _default_anomaly()
    now = now_iso or _utc_now()
    decision_set = decide_ingest_windows(adapter_config_set=adapters, window_policy=policy, scheduler_state=state, anomaly_state=anomaly, now_iso=now)
    max_concurrent = int(policy.get('global', {}).get('max_concurrent_adapters', 1))
    oracle_present = (REPO_ROOT / 'core/oracle_signal.py').exists()
    manifest = build_scheduled_manifest(decision_set, max_concurrent_adapters=max_concurrent, oracle_signal_module_present=oracle_present)
    receipt = build_scheduler_receipt(decision_set, manifest)
    write_classified_json(out_dir / 'scheduler_decisions.latest.json', decision_set, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=out_dir)
    write_classified_json(out_dir / 'scheduled_ingest_run_manifest.latest.json', manifest, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=out_dir)
    write_classified_json(out_dir / 'scheduler_receipt.latest.json', receipt, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=out_dir)
    (out_dir / 'scheduler_receipt.latest.md').write_text(build_scheduler_markdown(decision_set, manifest, receipt), encoding='utf-8')
    return {'decision_set': decision_set, 'manifest': manifest, 'receipt': receipt, 'out_dir': str(out_dir)}

def main(argv: list[str] | None=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', default='out/ingest/scheduler', help='Directory for scheduler_decisions / manifest / receipt')
    parser.add_argument('--adapters-json', type=Path, default=None)
    parser.add_argument('--policy-json', type=Path, default=None)
    parser.add_argument('--state-json', type=Path, default=None)
    parser.add_argument('--anomaly-json', type=Path, default=None)
    parser.add_argument('--now-iso', default=None)
    args = parser.parse_args(argv)
    result = run(out_dir=Path(args.out_dir), adapter_config=_load_json(args.adapters_json, _default_adapters()), window_policy=_load_json(args.policy_json, _default_policy()), scheduler_state=_load_json(args.state_json, _default_state()), anomaly_state=_load_json(args.anomaly_json, _default_anomaly()), now_iso=args.now_iso)
    print(json.dumps({'out_dir': result['out_dir'], 'decision_hash': result['decision_set'].get('decision_hash'), 'run_id': result['manifest'].get('run_id'), 'receipt_hash': result['receipt'].get('receipt_hash'), 'eligible': len(result['manifest'].get('eligible_adapters') or []), 'authority': 'SHADOW_SCHEDULING_ONLY'}, indent=2, sort_keys=True))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
