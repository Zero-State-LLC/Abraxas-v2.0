from __future__ import annotations

import hashlib
import json

from scripts.operator import run_operator_platform_stabilization_audit as audit


def test_dependency_receipt_classifies_all_findings_as_non_production() -> None:
    receipt = audit.build_dependency_receipt()
    assert receipt["production_runtime_vulnerability_count"] == 0
    assert len(receipt["findings"]) == 5
    assert all(
        finding["runtime_reachability"] != "PRODUCTION_RUNTIME_REACHABLE"
        for finding in receipt["findings"]
    )


def test_cross_language_parity_is_confirmed() -> None:
    receipt = audit.build_parity_receipt()
    assert receipt["status"] == "PARITY_CONFIRMED"
    assert all(check["status"] == "MATCH" for check in receipt["checks"])


def test_receipt_hash_is_canonical(tmp_path) -> None:
    payload = audit.build_parity_receipt()
    output = tmp_path / "receipt.json"
    audit._write_receipt(output, payload)
    receipt = json.loads(output.read_text())
    canonical_hash = receipt.pop("canonical_hash")
    expected = hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()
    assert canonical_hash == expected
