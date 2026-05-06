from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.canonical.json import write_canonical_json

if __name__ == '__main__':
    data = json.loads(Path('out/canary_promotion/latest.json').read_text())
    write_canonical_json('out/canary_promotion_replay/latest.json', data['replay'])
    print('run_canary_promotion_replay complete')
