from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.forecast.runtime import run_forecast_candidates

_OUT_ROOT = Path('out')

def main() -> None:
    oracle = json.loads(Path('out/oracle/latest.json').read_text(encoding='utf-8'))
    sandbox = json.loads(Path('out/sandbox/latest.json').read_text(encoding='utf-8'))
    observability = json.loads(Path('out/observability/latest.json').read_text(encoding='utf-8'))
    out = run_forecast_candidates(oracle, sandbox, observability)
    write_classified_json(Path('out/forecast/latest.json'), out, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/forecast_lineage/latest.json'), out['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/forecast_calibration/latest.json'), out['calibration'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json(Path('out/forecast_replay/latest.json'), out['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    print('forecast candidate artifacts emitted')
if __name__ == '__main__':
    main()
