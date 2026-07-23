"""YggdrasilScanReceipt.v1 — advisory Soft Facade for YGGDRASIL Scan runes.

Does not replace individual scan runes. Completely optional.
execution_authority is hard-coded False. net_catalog_delta = 0.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
import hashlib
import json

SCANS = (
    "DEPENDENCY_SCAN",
    "LANE_BOUNDARY_SCAN",
    "EDGE_VALIDATION",
    "UNKNOWN_NODE_GATE",
)
Outcome = Literal["PASS", "FAIL", "SKIPPED", "NOT_APPLICABLE"]


@dataclass
class YggdrasilScanReceipt:
    """Advisory composite. Does not replace individual scan runes."""

    receipt_type: str = "YggdrasilScanReceipt.v1"
    schema_version: str = "YggdrasilScanReceipt.v1"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    producer_system: str = "GROK"
    execution_authority: bool = False
    net_catalog_delta: int = 0
    applied_scans: Dict[str, bool] = field(default_factory=dict)
    scan_outcomes: Dict[str, Outcome] = field(default_factory=dict)
    residual_nodes_detected: List[str] = field(default_factory=list)
    source_receipts: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    provenance_hash: str = ""
    recommended_next: str = "OPERATOR_REVIEW"
    provenance: Dict = field(default_factory=dict)

    def finalize(self) -> "YggdrasilScanReceipt":
        payload = {
            "receipt_type": self.receipt_type,
            "schema_version": self.schema_version,
            "producer_system": self.producer_system,
            "execution_authority": self.execution_authority,
            "net_catalog_delta": self.net_catalog_delta,
            "applied_scans": self.applied_scans,
            "scan_outcomes": self.scan_outcomes,
            "residual_nodes_detected": sorted(self.residual_nodes_detected),
            "source_receipts": sorted(self.source_receipts),
            "notes": self.notes,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.provenance_hash = hashlib.sha256(raw).hexdigest()
        self.provenance = {
            "generator": "YggdrasilScanReceipt.v1-hygiene-0.2",
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


def emit_yggdrasil_scan_receipt(
    applied: List[str],
    outcomes: Optional[Dict[str, Outcome]] = None,
    residual_nodes_detected: Optional[List[str]] = None,
    source_receipts: Optional[List[str]] = None,
    notes: Optional[str] = None,
    producer_system: str = "GROK",
) -> YggdrasilScanReceipt:
    """Thin advisory helper. Individual scan runes remain authoritative."""
    applied_set = {s.upper() for s in applied}
    applied_map = {s: (s in applied_set) for s in SCANS}
    final_outcomes: Dict[str, Outcome] = {}
    for s in SCANS:
        if outcomes and s in outcomes:
            final_outcomes[s] = outcomes[s]
        else:
            final_outcomes[s] = "SKIPPED" if applied_map[s] else "NOT_APPLICABLE"
    receipt = YggdrasilScanReceipt(
        producer_system=producer_system,
        applied_scans=applied_map,
        scan_outcomes=final_outcomes,
        residual_nodes_detected=residual_nodes_detected or [],
        source_receipts=source_receipts or [],
        notes=notes,
    )
    return receipt.finalize()
