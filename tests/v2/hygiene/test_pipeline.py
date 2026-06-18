from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene import HygienePipeline, V2Output


def test_pipeline_off_is_noop() -> None:
    output = V2Output(observed={"x": 1}, inferred={}, speculative={})
    pipeline = HygienePipeline(mode=HygieneMode.OFF)
    assert pipeline.process(output) == output
