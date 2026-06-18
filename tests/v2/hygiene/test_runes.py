from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene import HygienePipeline, V2Output
from abraxas.v2.hygiene.runes.adversarial_audit import AdversarialAuditRune


def test_loop_awareness_adds_dynamics_in_advisory() -> None:
    output = V2Output(observed={"x": 1}, inferred={}, speculative={})
    pipeline = HygienePipeline(mode=HygieneMode.ADVISORY)
    result = pipeline.process(output, {"retrocausal_risk": 0.2})
    assert result.loop_dynamics is not None
    assert result.provenance.get("loop_awareness")


def test_adversarial_audit_strict_blocks_with_findings() -> None:
    rune = AdversarialAuditRune()
    output = V2Output(observed={"x": 1}, inferred={}, speculative={})
    try:
        rune.apply(output, {"adversarial_findings": ["issue"]}, HygieneMode.STRICT)
        blocked = False
    except ValueError:
        blocked = True
    assert blocked
