import pytest
from prediction_market_agent_tooling.gtypes import HexAddress, HexStr

from server.app import fetch_predictions_by_market_id


@pytest.mark.asyncio
async def test_market_predictions() -> None:
    market_id = HexAddress(HexStr("0x1e7989d53162e0a63c33f89e7a2666fefe89c1ee"))
    predictions = await fetch_predictions_by_market_id(market_id)
    assert len(predictions) > 0
