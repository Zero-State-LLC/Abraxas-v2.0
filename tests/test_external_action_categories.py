import pytest
from core.external_action_proposals.categories import ProposalCategoryPacket

def test_forbidden_category_rejection() -> None:
    with pytest.raises(ValueError):
        ProposalCategoryPacket(proposal_hash="a", category="deployment", deterministic_category_hash="x", status="failed")
