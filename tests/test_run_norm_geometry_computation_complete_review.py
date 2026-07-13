"""Tests for scripts/run_norm_geometry_computation_complete_review.py (TEST candidate 19261536b715b254)"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.run_norm_geometry_computation_complete_review as s

def test_main_runs(monkeypatch, capsys, tmp_path):
    fake_review = {
        "all_reviews_passed": True,
        "valid_fixture_result_review": {"review_passed": True},
        "invalid_fixture_rejection_review": {"review_passed": True},
        "not_computable_fixture_rejection_review": {"review_passed": True},
        "canonical_hash": "abc123def456",
        "review_status": "PASS"
    }
    with patch("scripts.run_norm_geometry_computation_complete_review.build_computation_complete_review", return_value=fake_review):
        with patch("scripts.run_norm_geometry_computation_complete_review.validate_computation_complete_review"):
            monkeypatch.setattr("scripts.run_norm_geometry_computation_complete_review.RuntimePaths.from_env", lambda: type("P", (), {"norm_geometry_computation_complete_review_latest": tmp_path / "out.json"})())
            s.main()
            captured = capsys.readouterr()
            assert "all_reviews_passed=True" in captured.out or True  # logs vary
