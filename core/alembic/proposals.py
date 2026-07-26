"""Meta-optimization proposals — never auto-applied."""

from __future__ import annotations

from typing import Any

from core.alembic.config import RouterPolicy
from core.alembic.models import Provenance, RouterChangeProposal
from core.alembic.util import det_timestamp, hash_model, make_id


def propose_router_update(
    current: RouterPolicy,
    *,
    proposed_weights: dict[str, float] | None = None,
    evidence: tuple[str, ...] = (),
    expected_benefit: str = "Improve routing fit under advisory evaluation",
    risk: str = "Mis-tuned weights may increase abstention or reduce verification compatibility",
    affected_tasks: tuple[str, ...] = (),
    affected_architectures: tuple[str, ...] = (),
    backtest_result: dict[str, Any] | None = None,
    shadow_result: dict[str, Any] | None = None,
) -> RouterChangeProposal:
    proposed_config = current.model_dump(mode="python")
    if proposed_weights is not None:
        proposed_config["score_weights"] = dict(proposed_weights)
        # Validate proposed weights via RouterPolicy construction.
        RouterPolicy.model_validate(proposed_config)

    proposal = RouterChangeProposal(
        proposal_id=make_id("proposal", current.policy_id, proposed_config.get("score_weight_version")),
        current_configuration=current.model_dump(mode="python"),
        proposed_configuration=proposed_config,
        evidence=evidence,
        expected_benefit=expected_benefit,
        uncertainty=0.5,
        risk=risk,
        affected_tasks=affected_tasks,
        affected_architectures=affected_architectures,
        backtest_result=backtest_result or {"status": "NOT_COMPUTABLE"},
        shadow_result=shadow_result or {"status": "NOT_COMPUTABLE"},
        rollback_plan="Retain current_configuration; do not mutate live router policy without operator gate.",
        status="DRAFT",
        provenance=Provenance(classification="INFERRED", producer="core.alembic.proposals"),
    )
    digest = hash_model(proposal)
    return proposal.model_copy(
        update={
            "provenance": proposal.provenance.model_copy(
                update={"content_hash": digest, "notes": det_timestamp(digest)}
            )
        }
    )
