import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
NEON = ROOT / 'skills/abx-neon-genie/neon_genie_router.py'
NOCTIS = ROOT / 'scripts/research/run_noctis_dream.py'


def invoke(script, *args, cwd):
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, env={**os.environ, 'PYTHONPATH':str(ROOT)}, capture_output=True, text=True)


def test_neon_explicit_input_emits_complete_json(tmp_path):
    p = tmp_path / 'input.json'; p.write_text('{"mode":"SYMBOLIC_LED","seed":"synthetic test"}')
    run = invoke(NEON, '--input', str(p), cwd=tmp_path)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result['authority']['execution_authority'] is False


def test_noctis_missing_input_does_not_fabricate_dream(tmp_path):
    run = invoke(NOCTIS, '--input', str(tmp_path / 'missing.json'), '--output', str(tmp_path / 'out.json'), cwd=tmp_path)
    assert run.returncode != 0
    assert not (tmp_path / 'out.json').exists()


def test_noctis_requires_explicit_input_or_fixture(tmp_path):
    run = invoke(NOCTIS, '--output', str(tmp_path / 'out.json'), cwd=tmp_path)
    assert run.returncode != 0


def test_noctis_explicit_fixture_json_and_boundaries(tmp_path):
    out = tmp_path / 'out.json'
    run = invoke(NOCTIS, '--synthetic-fixture', '--output', str(out), cwd=tmp_path)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result == json.loads(out.read_text())
    assert result['status']['validation_status'] == 'NOT_RUN'
    assert result['source'] == 'SYSTEM'
    assert result['privacy_tier'] == 'PUBLIC_SYNTHETIC'
    assert result['authority']['forecast_authority'] is False


def load_alife():
    spec = importlib.util.spec_from_file_location('alife', ROOT / 'skills/abx-esoteric-intelligence/alife_adapter.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize('mode', ['organismize','archetype_lineage','sigil_genotype','population_model','metabolism','synchronicity_ecology'])
def test_alife_canned_builders_require_opt_in_fixture(mode):
    with pytest.raises(ValueError, match='NOT_COMPUTABLE'):
        load_alife().build_alife_packet(mode, 'unrelated input', {})


def test_alife_opt_in_is_labeled_synthetic():
    result = load_alife().build_alife_packet('organismize', 'fixture', {'synthetic_fixture':True})
    assert result['synthetic'] is True
    assert result['evidence_status'] == 'SYNTHETIC'
