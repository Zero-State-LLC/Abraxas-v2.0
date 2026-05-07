import json
from pathlib import Path
from core.manual_execution.runtime import run_manual_execution_authorization

if __name__=='__main__':
    p=Path('out/manual_execution/latest.json')
    if not p.exists():
        run_manual_execution_authorization([],[],[],[],[])
    print(json.loads(Path('out/manual_execution_replay/latest.json').read_text()))
