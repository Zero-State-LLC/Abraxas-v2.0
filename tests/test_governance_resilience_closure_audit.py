from scripts.governance import run_governance_resilience_closure_audit as closure


def test_closure_hash_deterministic_across_runs() -> None:
    first, _, _ = closure.build_closure_payload()
    second, _, _ = closure.build_closure_payload()
    assert first["closure_hash"] == second["closure_hash"]


def test_failed_source_audit_produces_failed_closure() -> None:
    source_audits = [{"name": "artifact_contract_inventory", "status": "failed", "critical_gap_count": 1}]
    status = closure._compute_status(
        source_audits=source_audits,
        mutation_gaps_empty=True,
        projection_only=True,
        inference_authority=False,
        authority_leak_detected=False,
        missing_gates=[],
        missing_summaries=[],
        readable=True,
    )
    assert status == "failed"


def test_non_empty_mutation_gaps_fail_closure() -> None:
    source_audits = [{"name": "artifact_contract_inventory", "status": "passed", "critical_gap_count": 0}]
    status = closure._compute_status(
        source_audits=source_audits,
        mutation_gaps_empty=False,
        projection_only=True,
        inference_authority=False,
        authority_leak_detected=False,
        missing_gates=[],
        missing_summaries=[],
        readable=True,
    )
    assert status == "failed"


def test_missing_gate_fails_closure() -> None:
    source_audits = [{"name": "artifact_contract_inventory", "status": "passed", "critical_gap_count": 0}]
    status = closure._compute_status(
        source_audits=source_audits,
        mutation_gaps_empty=True,
        projection_only=True,
        inference_authority=False,
        authority_leak_detected=False,
        missing_gates=["external_action_proposal_gate"],
        missing_summaries=[],
        readable=True,
    )
    assert status == "failed"


def test_missing_summary_fails_closure() -> None:
    source_audits = [{"name": "artifact_contract_inventory", "status": "passed", "critical_gap_count": 0}]
    status = closure._compute_status(
        source_audits=source_audits,
        mutation_gaps_empty=True,
        projection_only=True,
        inference_authority=False,
        authority_leak_detected=False,
        missing_gates=[],
        missing_summaries=["external_action_proposal_summary"],
        readable=True,
    )
    assert status == "failed"


def test_projection_invariant_failure_fails_closure() -> None:
    source_audits = [{"name": "artifact_contract_inventory", "status": "passed", "critical_gap_count": 0}]
    status = closure._compute_status(
        source_audits=source_audits,
        mutation_gaps_empty=True,
        projection_only=False,
        inference_authority=False,
        authority_leak_detected=False,
        missing_gates=[],
        missing_summaries=[],
        readable=True,
    )
    assert status == "failed"


def test_authority_fields_locked() -> None:
    payload, _, _ = closure.build_closure_payload()
    assert payload["authority"]["mutation_authority"] is False
    assert payload["authority"]["execution_authority"] is False
