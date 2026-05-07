from __future__ import annotations

from pathlib import Path

from core.audit_artifact_contract_inventory import build_inventory
from core.canonical.json import write_canonical_json


def test_inventory_hash_deterministic() -> None:
    a = build_inventory(Path('.'))
    b = build_inventory(Path('.'))
    assert a['inventory_hash'] == b['inventory_hash']


def test_bindings_sorted_and_authority_locked() -> None:
    inv = build_inventory(Path('.'))
    packages = [b['package'] for b in inv['contract_bindings']]
    assert packages == sorted(packages)
    assert inv['authority'] == {
        'projection_only': True,
        'inference_authority': False,
        'mutation_authority': False,
        'execution_authority': False,
    }


def test_non_pass_when_missing_artifacts_or_orphan_gates() -> None:
    inv = build_inventory(Path('.'))
    statuses = {g['gap_type'] for g in inv['gaps']}
    if 'orphan_gate' in statuses or 'missing_producer' in statuses or 'missing_replay' in statuses:
        assert inv['status'] != 'passed'


def test_canonical_json_newline(tmp_path: Path) -> None:
    target = tmp_path / 'inventory.json'
    write_canonical_json(target, {'a': 1})
    assert target.read_text(encoding='utf-8').endswith('\n')
