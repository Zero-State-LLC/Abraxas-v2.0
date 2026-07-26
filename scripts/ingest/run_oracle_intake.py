from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.oracle.runtime import run_oracle_intake

_OUT_ROOT = Path('out')

def main() -> None:
    source_payloads = [{'source_id': 'fixture:001', 'source_type': 'document', 'payload': 'Deterministic Oracle Intake Evidence'}]
    packet = run_oracle_intake(source_payloads)
    write_classified_json(Path('out/oracle/latest.json'), packet, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/oracle_lineage/latest.json'), packet['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/oracle_conflicts/latest.json'), {'conflicts': packet['conflicts']}, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/oracle_replay/latest.json'), packet['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    print('oracle intake artifacts emitted')
if __name__ == '__main__':
    main()
