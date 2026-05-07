import json
from pathlib import Path
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger
if __name__=='__main__':
    if not Path('out/manual_execution_receipts/latest.json').exists():
        run_manual_execution_receipt_ledger([],[],[],[],[])
    print(json.loads(Path('out/manual_execution_receipts_replay/latest.json').read_text()))
