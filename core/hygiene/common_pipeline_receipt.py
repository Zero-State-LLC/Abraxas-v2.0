"""CommonPipelineReceipt.v1 — advisory Soft Facade for the PARSE	oIR_BUILD	oVALIDATE	oRECEIPT spine.

Does not replace individual pipeline runes. Completely optional.
execution_authority is hard-coded False. net_catalog_delta = 0.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json


@dataclass
class CommonPipelineReceipt:
    """Advisory composite for the Common Pipeline Sub-Graph.
    Does not replace any individual rune or route."""

    receipt_type: str = "CommonPipelineReceipt.v1"
    schema_version: str = "CommonPipelineReceipt.v1"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    producer_system: str = "GROK"
    execution_authority: bool = False
    net_catalog_delta: int = 0
    pipeline_id: str = ""
    applied_stages: Dict[str, bool] = field(default_factory=dict)
    stage_outcomes: Dict[str, str] = field(default_factory=dict)
    hygiene_receipt: Optional[Dict[str, Any]] = None
    scan_receipt: Optional[Dict[str, Any]] = None
    source_receipts: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    provenance_hash: str = ""
    recommended_next: str = "OPERATOR_REVIEW"
    provenance: Dict = field(default_factory=dict)

    def finalize(self) -> "CommonPipelineReceipt":
        payload = {
            "receipt_type": self.receipt_type,
            "schema_version": self.schema_version,
            "producer_system": self.producer_system,
            "execution_authority": self.execution_authority,
            "net_catalog_delta": self.net_catalog_delta,
            "pipeline_id": self.pipeline_id,
            "applied_stages": self.applied_stages,
            "stage_outcomes": self.stage_outcomes,
            "source_receipts": sorted(self.source_receipts),
            "notes": self.notes,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.provenance_hash = hashlib.sha256(raw).hexdigest()
        self.provenance = {
            "generator": "CommonPipelineReceipt.v1-advisory-0.1",
            "producer_system": self.producer_system,
            "registers": {"classification": "OBSERVED"},
            "loop_dynamics": {
                "assessment_complete": True,
                "retrocausal_risk": "NONE",
            },
            "hash": self.provenance_hash,
        }
        return self

    def to_dict(self) -> dict:
        return asdict(self)


def emit_common_pipeline_receipt(
    pipeline_id: str,
    applied_stages: Optional[List[str]] = None,
    stage_outcomes: Optional[Dict[str, str]] = None,
    hygiene_applied: Optional[List[str]] = None,
    scan_applied: Optional[List[str]] = None,
    scan_outcomes: Optional[Dict[str, str]] = None,
    source_receipts: Optional[List[str]] = None,
    notes: Optional[str] = None,
    producer_system: str = "GROK",
) -> CommonPipelineReceipt:
    """Thin advisory helper for the Common Pipeline Sub-Graph.

    Callers must still invoke the individual runes for actual work and gating.
    """
    stages = applied_stages or ["PARSE", "IR_BUILD", "VALIDATE", "RECEIPT"]
    stage_map = {s: True for s in stages}
    outcomes = stage_outcomes or {s: "APPLIED" for s in stages}

    hygiene = None
    if hygiene_applied is not None:
        hygiene = {
            "receipt_type": "OutputHygieneReceipt.v1",
            "applied_enforcers": {e: True for e in hygiene_applied},
            "producer_system": producer_system,
            "execution_authority": False,
            "net_catalog_delta": 0,
        }

    scan = None
    if scan_applied is not None:
        scan = {
            "receipt_type": "YggdrasilScanReceipt.v1",
            "applied_scans": {s: True for s in scan_applied},
            "scan_outcomes": scan_outcomes or {},
            "producer_system": producer_system,
            "execution_authority": False,
            "net_catalog_delta": 0,
        }

    receipt = CommonPipelineReceipt(
        producer_system=producer_system,
        pipeline_id=pipeline_id,
        applied_stages=stage_map,
        stage_outcomes=outcomes,
        hygiene_receipt=hygiene,
        scan_receipt=scan,
        source_receipts=source_receipts or [],
        notes=notes,
    )
    return receipt.finalize()
