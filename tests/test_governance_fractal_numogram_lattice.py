"""Tests for core/governance/fractal_numogram_lattice.py (GOVERNANCE candidate 20b6853fc23d95cd)"""

from core.governance.fractal_numogram_lattice import NUMOGRAM_ZONE_BINDINGS
from core.status_result import STATUS_NOT_COMPUTABLE


def test_numogram_bindings_present():
    assert isinstance(NUMOGRAM_ZONE_BINDINGS, (list, tuple))
    assert len(NUMOGRAM_ZONE_BINDINGS) >= 7
    zone_ids = [z["zone_id"] for z in NUMOGRAM_ZONE_BINDINGS]
    assert "zone_01_observe" in zone_ids
    assert "zone_08_signal_forage" in zone_ids


def test_not_computable_constant():
    assert STATUS_NOT_COMPUTABLE == "NOT_COMPUTABLE"
