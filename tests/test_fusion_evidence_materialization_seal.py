from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from scripts.viz import run_fusion_evidence_materialization_seal


def test_seal_receipt_fields_and_invariants() -> None:
    run_fusion_evidence_materialization_seal.main()
    payload = json.loads(
        Path("out/audit/fusion_evidence_materialization_seal_001.latest.json").read_text(encoding="utf-8")
    )

    for key in (
        "schema_version",
        "seal_id",
        "status",
        "classification",
        "run_count",
        "summary_hash",
        "artifact_hashes",
        "final_fusion_status",
        "remaining_blockers",
        "authority_invariants",
        "tests_run",
        "remaining_risks",
        "recommended_next_lane",
        "receipt_hash",
    ):
        assert key in payload

    assert payload["status"] == "SEALED"
    assert payload["remaining_blockers"] == []
    assert payload["authority_invariants"] == {
        "advisory_only": True,
        "projection_only": True,
        "authority_granted": False,
        "forecast_authority": False,
        "mutation_allowed": False,
    }


def test_seal_receipt_hash_stability_and_markdown_sidecar() -> None:
    first = run_fusion_evidence_materialization_seal.build_receipt()
    second = run_fusion_evidence_materialization_seal.build_receipt()
    assert first == second

    without_hash = {k: v for k, v in first.items() if k != "receipt_hash"}
    assert first["receipt_hash"] == canonical_hash(without_hash)

    run_fusion_evidence_materialization_seal.main()
    assert Path("out/audit/fusion_evidence_materialization_seal_001.latest.md").exists()
