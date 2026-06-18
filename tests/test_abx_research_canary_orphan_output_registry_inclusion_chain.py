from __future__ import annotations

from pathlib import Path

from core.abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt import (
    build_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt,
)
from core.abx_research_canary_orphan_output_registry_inclusion_constants import ORPHAN_OUTPUT_JSON_PATHS
from core.abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate import (
    build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate,
)
from core.abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record import (
    build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record,
)
from core.abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan import (
    build_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan,
)
from core.abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record import (
    build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record,
)
from core.abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt import (
    build_abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt,
)
from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_inclusion_authorization_record_emitted() -> None:
    packet = build_abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record(
        source_root=REPO_ROOT
    )
    assert packet["status"].endswith("_EMITTED")
    assert packet["selected_decision"] == "AUTHORIZE_ORPHAN_REGISTRY_INCLUSION_SPEC"
    assert packet["orphan_count"] == 10


def test_inclusion_spec_plan_lists_all_orphans() -> None:
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan(
        source_root=REPO_ROOT
    )
    assert packet["status"].endswith("_READY")
    assert len(packet["proposed_inclusion_steps"]) == len(ORPHAN_OUTPUT_JSON_PATHS)


def test_inclusion_chain_completes_when_registry_updated() -> None:
    gate = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate(
        source_root=REPO_ROOT
    )
    assert gate["status"].endswith("_HELD_FOR_OPERATOR")

    auth_record = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record(
        source_root=REPO_ROOT
    )
    assert auth_record["authorization_granted"] is True

    scoped = build_abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt(
        source_root=REPO_ROOT
    )
    assert scoped["status"].endswith("_EMITTED")
    assert scoped["registry_mutation_performed"] is True
    assert all(path in _DERIVED_OPTIONAL_ARTIFACTS for path in ORPHAN_OUTPUT_JSON_PATHS)

    regen = build_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt(
        source_root=REPO_ROOT
    )
    assert regen["status"].endswith("_EMITTED")
    assert regen["downstream_status"] == "ORPHAN_INCLUSION_CHAIN_COMPLETE"
    assert regen["post_regeneration_audit"]["orphan_research_output_count"] == 0
