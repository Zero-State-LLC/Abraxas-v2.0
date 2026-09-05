import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_artifact_verifier_rejects_missing_invalid_and_authority(tmp_path):
    script = ROOT / 'skills/verify_artifact.py'
    assert script.exists(), 'missing fail-closed artifact validator'
    schema = tmp_path / 'schema.json'
    schema.write_text('{"type":"object","required":["authority"]}')
    bad = tmp_path / 'bad.json'
    for body in ['{}', '{"authority":{"execution_authority":true}}', 'not json']:
        bad.write_text(body)
        run = subprocess.run([sys.executable, str(script), '--schema', str(schema), str(bad)], capture_output=True)
        assert run.returncode != 0
    run = subprocess.run([sys.executable, str(script), '--schema', str(schema), str(tmp_path / 'missing')], capture_output=True)
    assert run.returncode != 0


def test_artifact_verifier_accepts_schema_valid_advisory(tmp_path):
    script = ROOT / 'skills/verify_artifact.py'
    assert script.exists()
    schema = tmp_path / 'schema.json'; schema.write_text('{"type":"object","required":["authority"]}')
    packet = tmp_path / 'packet.json'; packet.write_text('{"authority":{"execution_authority":false}}')
    run = subprocess.run([sys.executable, str(script), '--schema', str(schema), str(packet)], capture_output=True)
    assert run.returncode == 0, run.stderr
