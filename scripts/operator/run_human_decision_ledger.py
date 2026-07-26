from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.human_decision_ledger.runtime import run_human_decision_ledger

_OUT_ROOT = Path('out')
if __name__ == '__main__':
    packet = run_human_decision_ledger(load_required_upstream_packet('out/proposal_decision_bridge/latest.json'), load_required_upstream_packet('out/proposal_sandbox_evaluation/latest.json'), load_required_upstream_packet('out/operator_queue/latest.json'), load_required_upstream_packet('out/proposal_decision_bridge_replay/latest.json'))
    write_classified_json('out/human_decision_ledger/latest.json', packet, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/human_decision_ledger_replay/latest.json', packet['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/human_decision_ledger_lineage/latest.json', packet['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/human_decision_ledger_diagnostics/latest.json', packet['diagnostics'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
