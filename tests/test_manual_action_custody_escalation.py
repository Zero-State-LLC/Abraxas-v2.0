from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.canonical.json import canonical_dumps
from core.manual_action_custody.escalation import ManualActionEscalationPacket


def _escalation_kwargs(
    *,
    custody_hash: str = "custody-prev-hash",
    escalation_type: str = "operator_review_required",
    escalation_reason: str = "operator review gate required",
    escalation_required: bool = True,
) -> dict[str, object]:
    return {
        "escalation_id": "mae-test-1",
        "custody_hash": custody_hash,
        "escalation_type": escalation_type,
        "escalation_reason": escalation_reason,
        "escalation_required": escalation_required,
        "deterministic_escalation_hash": ManualActionEscalationPacket.compute_hash(
            custody_hash,
            escalation_type,
            escalation_reason,
            escalation_required,
        ),
        "status": "passed",
    }


def test_escalation_authority_is_locked_by_default() -> None:
    packet = ManualActionEscalationPacket(**_escalation_kwargs())
    assert all(value is False for value in packet.authority.model_dump().values())


def test_escalation_requires_predecessor_chain_reference() -> None:
    with pytest.raises(ValidationError, match="custody hash required"):
        ManualActionEscalationPacket(**_escalation_kwargs(custody_hash=""))


def test_invalid_custody_transition_is_blocked() -> None:
    with pytest.raises(ValidationError, match="forbidden escalation type"):
        ManualActionEscalationPacket(**_escalation_kwargs(escalation_type="auto_execute"))


def test_escalation_cannot_skip_stages() -> None:
    with pytest.raises(ValidationError, match="invalid escalation transition"):
        ManualActionEscalationPacket(
            **_escalation_kwargs(escalation_type="none", escalation_required=True)
        )


def test_escalation_transition_requires_explicit_required_flag() -> None:
    with pytest.raises(ValidationError, match="invalid escalation transition"):
        ManualActionEscalationPacket(
            **_escalation_kwargs(
                escalation_type="governance_review_required", escalation_required=False
            )
        )


def test_malformed_lineage_hash_is_blocked() -> None:
    payload = _escalation_kwargs()
    payload["deterministic_escalation_hash"] = "tampered"
    with pytest.raises(ValidationError, match="escalation hash"):
        ManualActionEscalationPacket(**payload)


def test_escalation_lineage_hash_is_deterministic() -> None:
    payload = _escalation_kwargs()
    packet_a = ManualActionEscalationPacket(**payload)
    packet_b = ManualActionEscalationPacket(**payload)
    assert (
        packet_a.deterministic_escalation_hash
        == packet_b.deterministic_escalation_hash
        == ManualActionEscalationPacket.compute_hash(
            "custody-prev-hash",
            "operator_review_required",
            "operator review gate required",
            True,
        )
    )
    assert canonical_dumps(packet_a.model_dump()) == canonical_dumps(packet_b.model_dump())
