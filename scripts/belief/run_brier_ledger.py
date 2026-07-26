from __future__ import annotations

import json
from pathlib import Path

from core.brier.runtime import build_brier_ledger
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path('out')

def main() -> None:
    forecast = json.loads(Path('out/forecast/latest.json').read_text(encoding='utf-8'))
    outcome = forecast['outcome_binding']
    out = build_brier_ledger(forecast, outcome)
    write_classified_json(Path('out/brier/latest.json'), out, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/brier_lineage/latest.json'), out['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/brier_reliability/latest.json'), out['reliability'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/brier_replay/latest.json'), out['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    print('brier ledger artifacts emitted')
if __name__ == '__main__':
    main()
