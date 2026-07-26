from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.operator_queue.runtime import run_operator_approval_queue

_OUT_ROOT = Path('out')
if __name__ == '__main__':
    packet = run_operator_approval_queue(load_required_upstream_packet('out/overlay_firewall/latest.json'), load_required_upstream_packet('out/overlay_readiness/latest.json'), load_required_upstream_packet('out/overlay_governance/latest.json'), load_required_upstream_packet('out/overlay_containment/latest.json'), load_required_upstream_packet('out/overlay_firewall_replay/latest.json'))
    write_classified_json('out/operator_queue/latest.json', packet, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/operator_queue_replay/latest.json', packet['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/operator_queue_lineage/latest.json', packet['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/operator_queue_diagnostics/latest.json', packet['diagnostics'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
