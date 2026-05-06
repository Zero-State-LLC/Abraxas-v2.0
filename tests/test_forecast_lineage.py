import pytest

from core.forecast.lineage import ForecastLineageNode, ForecastLineagePacket


def test_cyclic_lineage_fail_closed() -> None:
    n=[ForecastLineageNode(forecast_hash="a", generation=0), ForecastLineageNode(forecast_hash="a", generation=1)]
    with pytest.raises(ValueError):
        ForecastLineagePacket(lineage_id="l", lineage_depth=2, lineage_nodes=n, deterministic_lineage_hash=ForecastLineagePacket.compute_hash(n))
