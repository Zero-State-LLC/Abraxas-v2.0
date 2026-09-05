"""Operational documentation contracts for the fourteen audited entrypoints."""
from pathlib import Path
import re
import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = sorted((ROOT / 'skills').rglob('SKILL.md'))


@pytest.mark.parametrize('path', SKILLS, ids=lambda p: p.parent.name)
def test_entrypoint_declares_checkout_and_current_evidence(path):
    text = path.read_text()
    assert 'full checkout' in text.lower()
    assert 'skills/OPERATING.md' in text
    for stale in ['/Users/appliedalchemylabs', '| tail -5', 'acks forced', 'Activated for ALL', 'Self-enforcement', '36 collection', 'abc123']:
        assert stale not in text


def test_evolution_operational_body_is_bounded_and_authority_safe():
    text = (ROOT / 'skills/abx-hermes-skill-evolution/SKILL.md').read_text()
    assert len(text) < 10000
    assert 'immutable' in text
    assert 'scripts/codegen/run_abx_hermes_skill_evolution_cycle.py' in text
    assert 'scripts/codegen/run_unattended_abx_continuation.py' in text
    assert 'historical-notes.md' in text


def test_no_missing_local_references():
    missing = []
    for path in SKILLS:
        for ref in re.findall(r'references/[\w./-]+\.(?:md|json)', path.read_text()):
            if not (path.parent / ref).is_file():
                missing.append(str(path.relative_to(ROOT)) + ':' + ref)
    assert not missing, missing


def test_calibration_is_explicit_design_not_fabricated_algorithm():
    text = (ROOT / 'skills/holler-sports/holler-calibrate/SKILL.md').read_text()
    assert 'DESIGN_ONLY' in text
    assert 'calibrated_brier' not in text
    assert '0.95' not in text
