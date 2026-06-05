from core.ingest.auto_ingest_validation_pack import load_current_stack, validate_viz_projection_only


def test_auto_ingest_viz_projection_only() -> None:
    result = validate_viz_projection_only(load_current_stack())
    assert result["status"] == "PASS_PROJECTION_ONLY"
    assert result["authority"] == "PROJECTION_ONLY"
