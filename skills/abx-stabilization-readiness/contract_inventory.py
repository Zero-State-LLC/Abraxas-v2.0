"""Evidence-bounded contract inventory classification."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.canonical.json import canonical_hash

from .contracts import validate_contract_record
from .models import ContractClassification, ContractRecord


def observed_seed_contracts() -> tuple[ContractRecord, ...]:
    """Return only contracts directly observed on the implementation baseline."""
    return (
        ContractRecord(
            contract_id="python.status_result.not_computable",
            language="python",
            surface="core.status_result.STATUS_NOT_COMPUTABLE",
            classification=ContractClassification.CONTROLLED.value,
            consumers=("tests/test_status_result.py",),
            validators=("tests/test_status_result.py",),
            compatibility_policy="shared sentinel compatibility",
            evidence_complete=True,
        ),
        ContractRecord(
            contract_id="python.canonical_json.writer",
            language="python",
            surface="core.canonical.json.write_canonical_json",
            classification=ContractClassification.CONTROLLED.value,
            consumers=("tests/test_canonical_json.py",),
            validators=("tests/test_canonical_json.py",),
            compatibility_policy="canonical bytes and atomic publication",
            evidence_complete=True,
        ),
        ContractRecord(
            contract_id="schema.campaign_director.state.v1",
            language="schema",
            surface=(
                "contracts/campaign_director/"
                "campaign_director_state.v1.schema.json"
            ),
            classification=ContractClassification.VERSIONED.value,
            validators=("tests/test_campaign_director_state_recovery.py",),
            schemas=(
                "contracts/campaign_director/"
                "campaign_director_state.v1.schema.json",
            ),
            compatibility_policy="versioned schema",
            evidence_complete=True,
        ),
        ContractRecord(
            contract_id="typescript.aal_viz.exports",
            language="typescript",
            surface="apps/aal-viz-live-console/src",
            classification=ContractClassification.NOT_COMPUTABLE.value,
            compatibility_policy="NOT_COMPUTABLE",
            evidence_complete=False,
            provenance="NOT_COMPUTABLE",
        ),
    )


def build_contract_inventory(
    records: Iterable[ContractRecord] | None = None,
) -> dict[str, Any]:
    selected = tuple(records) if records is not None else observed_seed_contracts()
    payloads = sorted(
        (record.to_dict() for record in selected),
        key=lambda item: item["contract_id"],
    )
    for payload in payloads:
        validate_contract_record(payload)
    complete = bool(payloads) and all(item["evidence_complete"] for item in payloads)
    result: dict[str, Any] = {
        "schema_version": "StabilizationContractInventory.v1",
        "inventory_status": "COMPLETE" if complete else "INCOMPLETE",
        "contract_count": len(payloads),
        "contracts": payloads,
        "advisory_only": True,
    }
    result["canonical_hash"] = canonical_hash(result)
    return result
