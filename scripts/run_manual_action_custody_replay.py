import json
from pathlib import Path
from core.manual_action_custody.runtime import run_manual_action_custody
if __name__=='__main__':
    if not Path('out/manual_action_custody/latest.json').exists():
        run_manual_action_custody([],[],[],[])
    print(json.loads(Path('out/manual_action_custody_replay/latest.json').read_text()))
