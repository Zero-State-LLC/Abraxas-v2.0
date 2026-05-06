from core.projections.aal_viz import build_projection_packet
from core.spine.typing_strict import emit_strict_typing_packet


def test_pyright_strict_mode_detection():
    packet = emit_strict_typing_packet(pyright_clean=True)
    assert packet["strict_mode"] is True


def test_typing_summary_projection():
    projection = build_projection_packet({"pipeline_count": 0}, [], {"queue_item_count": 0}, {}, {"strict_mode": True, "pyright_clean": True, "excluded_paths": [], "status": "passed"})
    assert projection["typing_summary"]["typing_gate_status"] == "passed"
    assert projection["projection_only"] is True
