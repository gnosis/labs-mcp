from eth_typing import HexAddress, HexStr
from fastapi import FastAPI
from fastapi_mcp import add_mcp_server
from prediction_market_agent.agents.prophet_agent.deploy import (
    DeployablePredictionProphetGPT4ominiAgent,
)
from prediction_market_agent_tooling.markets.agent_market import FilterBy, SortBy
from prediction_market_agent_tooling.markets.data_models import ProbabilisticAnswer
from prediction_market_agent_tooling.markets.omen.data_models import OmenMarket
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    OmenSubgraphHandler,
)

from server.market import MarketFetcher, MarketPrediction

app = FastAPI()

mcp_server = add_mcp_server(
    app,  # Your FastAPI app
    mount_path="/mcp",
    name="Gnosis AI MCP",
    describe_all_responses=True,
    describe_full_response_schema=True,
)


@mcp_server.tool()
def fetch_open_omen_markets(limit: int = 1) -> list[OmenMarket]:
    """Fetches Omen prediction markets on Gnosis that are still open for trading"""
    s = OmenSubgraphHandler()
    open_markets = s.get_omen_binary_markets_simple(
        limit=limit, filter_by=FilterBy.OPEN, sort_by=SortBy.NEWEST
    )
    return open_markets


@mcp_server.tool()
async def fetch_predictions_by_market_id(market_id: str) -> list[MarketPrediction]:
    """Fetches predictions from multiple agents for a specific market ID"""
    predictions = await MarketFetcher().fetch_predictions(
        market_id=HexAddress(HexStr(market_id))
    )
    return predictions


@mcp_server.tool()
def answer_binary_question(question: str) -> ProbabilisticAnswer | None:
    """
    Answers a binary question using a DeployablePredictionProphetGPT4ominiAgent.

    Args:
        question (str): The binary question to be answered.

    Returns:
        ProbabilisticAnswer | None: The probabilistic answer to the question, or None if an error occurs.
    """
    # We could make this agent selectable via argument, similar to what we do on PMA's `run_agent`.
    # We select gpt-4o-mini for cost-efficiency.
    agent = DeployablePredictionProphetGPT4ominiAgent()
    probabilistic_answer: ProbabilisticAnswer | None = agent.agent.predict(
        question
    ).outcome_prediction
    return probabilistic_answer
