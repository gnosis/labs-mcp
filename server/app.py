from mcp.server.fastmcp.server import FastMCP

from prediction_market_agent_tooling.markets.agent_market import FilterBy, SortBy
from prediction_market_agent_tooling.markets.omen.data_models import OmenMarket
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    OmenSubgraphHandler,
)

mcp = FastMCP("Demo")


@mcp.tool()
def fetch_open_omen_markets(limit: int | None = None) -> list[OmenMarket]:
    """Fetches Omen prediction markets on Gnosis that are still open for trading"""
    s = OmenSubgraphHandler()
    open_markets = s.get_omen_binary_markets_simple(
        limit=limit, filter_by=FilterBy.OPEN,
        sort_by=SortBy.NEWEST
    )
    return open_markets