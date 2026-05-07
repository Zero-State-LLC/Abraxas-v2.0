import json
from pathlib import Path
from core.review_resolution.runtime import run_review_resolution_spine

if __name__ == '__main__':
    p = Path('out/review_resolution/latest.json')
    if p.exists():
        print(json.loads(p.read_text()).get('replay', {}))
    else:
        run_review_resolution_spine([], [], [], [], [])
