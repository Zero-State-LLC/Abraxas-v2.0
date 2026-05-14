from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.canonical.json import canonical_dumps
from core.manual_execution.authorization import ManualExecutionAuthorizationPacket


def _authorization_kwargs(
    *,
    authorization_status: str = "not_authorized",
    authorization_reason: str = "manual review not yet granted",
) -> dict[str, object]:
    return {
        "authorization_id": "mea-test-1",
        "review_resolution_hash": "rr-hash",
        "operator_queue_hash": "oq-hash",
        "firewall_hash": "fw-hash",
        "readiness_hash": "rd-hash",
        "authorization_status": authorization_status,
        "authorization_reason": authorization_reason,
        "deterministic_authorization_hash": ManualExecutionAuthorizationPacket.compute_hash(
            "rr-hash",
            "oq-hash",
            "fw-hash",
            "rd-hash",
            authorization_status,
            authorization_reason,
        ),
        "status": "passed",
    }


def test_authority_granted_false_by_default() -> None:
    packet = ManualExecutionAuthorizationPacket(
        **_authorization_kwargs(
            authorization_status="authorized_for_manual_execution_review",
            authorization_reason="manual review approval granted by operator",
        )
    )
    assert all(value is False for value in packet.authority.model_dump().values())


def test_unauthorized_execution_status_is_blocked() -> None:
    with pytest.raises(ValidationError, match="forbidden authorization status"):
        ManualExecutionAuthorizationPacket(
            **_authorization_kwargs(
                authorization_status="executed",
                authorization_reason="attempted execution without review",
            )
        )


def test_explicit_approval_required_for_authorized_status() -> None:
    with pytest.raises(ValidationError, match="explicit approval required"):
        ManualExecutionAuthorizationPacket(
            **_authorization_kwargs(
                authorization_status="authorized_for_manual_execution_review",
                authorization_reason="approved",
            )
        )


def test_missing_approval_reason_is_blocked() -> None:
    with pytest.raises(ValidationError, match="authorization reason required"):
        ManualExecutionAuthorizationPacket(**_authorization_kwargs(authorization_reason=""))


def test_whitespace_only_approval_reason_is_blocked() -> None:
    with pytest.raises(ValidationError, match="authorization reason required"):
        ManualExecutionAuthorizationPacket(
            **_authorization_kwargs(authorization_reason="   ")
        )


def test_inconsistent_predecessor_hash_is_blocked() -> None:
    payload = _authorization_kwargs(
        authorization_status="authorized_for_manual_execution_review",
        authorization_reason="manual review approval granted by operator",
    )
    payload["deterministic_authorization_hash"] = "tampered"
    with pytest.raises(ValidationError, match="authorization hash"):
        ManualExecutionAuthorizationPacket(**payload)


def test_authorization_hash_and_canonical_state_are_deterministic() -> None:
    payload = _authorization_kwargs(
        authorization_status="authorized_for_manual_execution_review",
        authorization_reason="manual review approval granted by operator",
    )
    packet_a = ManualExecutionAuthorizationPacket(**payload)
    packet_b = ManualExecutionAuthorizationPacket(**payload)
    assert (
        packet_a.deterministic_authorization_hash
        == packet_b.deterministic_authorization_hash
        == ManualExecutionAuthorizationPacket.compute_hash(
            "rr-hash",
            "oq-hash",
            "fw-hash",
            "rd-hash",
            "authorized_for_manual_execution_review",
            "manual review approval granted by operator",
        )
    )
    assert canonical_dumps(packet_a.model_dump()) == canonical_dumps(packet_b.model_dump())
