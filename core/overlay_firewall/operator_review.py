from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OperatorOverlayFirewallReviewPacket(BaseModel):
    schema_version: Literal["OperatorOverlayFirewallReviewPacket.v1"] = (
        "OperatorOverlayFirewallReviewPacket.v1"
    )
    review_id: str
    overlay_hash: str
    firewall_status: str
    operator_review_required: bool
    pending_actions: list[str]
    status: Literal["approved", "rejected", "pending"]
