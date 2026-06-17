from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_JSON_PATH = REPO_ROOT / "operator_input/governed_authorization_phase30_live_hyperstition.json"
RECORD_MD_PATH = REPO_ROOT / "operator_input/governed_authorization_phase30_live_hyperstition.md"
EXPECTED_PHASE29_HASH = (
    "86afdeb01ac119bae4676f69f289cdd3f9846e66887a3f5e1dadf39367a18cec"
)
EXPECTED_AUTHORIZATION_HASH = (
    "5a7b3f1c94a47dfc288ad1d646d7fc210006e1021d0d172763550b126d1384d0"
)


def test_governed_authorization_phase30_record_is_stable() -> None:
    record = json.loads(RECORD_JSON_PATH.read_text(encoding="utf-8"))
    observed_hash = canonical_hash(
        {key: value for key, value in record.items() if key != "authorization_hash"}
    )

    assert record["record_id"] == "governed_authorization_phase30_live_hyperstition_001"
    assert record["advisory_only"] is True
    assert record["governed_authorization_record"] is True
    assert (
        record["hash_chain_acknowledgement"]["phase29_attestation_hash"]
        == EXPECTED_PHASE29_HASH
    )
    assert record["authorization_hash"] == EXPECTED_AUTHORIZATION_HASH
    assert observed_hash == EXPECTED_AUTHORIZATION_HASH
    assert record["operator_review_posture_requested"] == "FINAL_AUTHORITY_GRANTED"
    assert (
        record["authority_boundary_acknowledgement"][
            "live_execution_authority_granted_by_record_alone"
        ]
        is False
    )
    assert record["terminal_output_controls"]["downstream_lane_disposition"] == "NOT_COMPUTABLE"
    assert len(record["specific_authorizations_granted"]) == 9


def test_governed_authorization_phase30_markdown_references_hashes() -> None:
    markdown = RECORD_MD_PATH.read_text(encoding="utf-8")

    assert EXPECTED_PHASE29_HASH in markdown
    assert EXPECTED_AUTHORIZATION_HASH in markdown
    assert "GOVERNED AUTHORIZATION RECORD — PHASE 30 LIVE HYPERSTITION PROPAGATION" in markdown
