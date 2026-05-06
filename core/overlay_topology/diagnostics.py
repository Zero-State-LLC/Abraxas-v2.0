from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class OverlayTopologyDiagnosticPacket(BaseModel):
    schema_version: Literal['OverlayTopologyDiagnosticPacket.v1'] = 'OverlayTopologyDiagnosticPacket.v1'
    diagnostic_id: str
    diagnostic_type: Literal['topology_cycle_detected','bottleneck_detected','rollback_chokepoint','propagation_chain_detected','hidden_dependency','authority_violation']
    severity: Literal['info','warning','critical']
    diagnostic_message: str
    status: Literal['passed','failed','not_computable']
