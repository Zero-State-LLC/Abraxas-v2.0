import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'skills/holler-sports/slang-emergence/scripts/slang_emergence_engine.py'
spec = importlib.util.spec_from_file_location('slang', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_unretrieved_query_is_not_computable():
    result = m.detect_memetic_patterns('unrelated query')
    assert result['status'] == 'NOT_COMPUTABLE'
    assert not result['observed']
    assert result['provenance']['brier'] is None


def test_cli_json_only_and_explicit_output(tmp_path):
    out = tmp_path / 'receipt.json'
    run = subprocess.run([sys.executable, str(SCRIPT), '--output', str(out)], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result == json.loads(out.read_text())
    assert result['status'] == 'NOT_COMPUTABLE'
