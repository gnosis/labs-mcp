from server.app import fetch_predictions_by_market_id
from prediction_market_agent_tooling.gtypes import HexStr, HexAddress


def test_market_predictions() -> None:
    market_id = HexAddress(HexStr("0x1e7989d53162e0a63c33f89e7a2666fefe89c1ee"))
    predictions = fetch_predictions_by_market_id(market_id)
    assert len(predictions) > 0
