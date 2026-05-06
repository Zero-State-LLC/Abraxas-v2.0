from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class OverlayTopologyReplayPacket(BaseModel):
    schema_version: Literal['OverlayTopologyReplayPacket.v1'] = 'OverlayTopologyReplayPacket.v1'
    replay_id: str
    source_graph_hash: str
    replay_graph_hash: str
    deterministic_match: bool
    mismatched_components: list[str]
    status: Literal['passed','failed','not_computable']
