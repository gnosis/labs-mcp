import asyncio

import httpx
from httpx import AsyncClient
from prediction_market_agent_tooling.gtypes import HexAddress, IPFSCIDVersion0
from prediction_market_agent_tooling.loggers import logger
from prediction_market_agent_tooling.markets.omen.data_models import (
    ContractPrediction,
    IPFSAgentResult,
)
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.tools.web3_utils import byte32_to_ipfscidv0
from pydantic import BaseModel


class MarketPrediction(BaseModel):
    prediction: ContractPrediction
    agent_result: IPFSAgentResult


class MarketFetcher:
    def __init__(self) -> None:
        self.subgraph_handler = OmenSubgraphHandler()

    @staticmethod
    async def fetch_ipfs_content(
        ipfs_cid: IPFSCIDVersion0, client: AsyncClient
    ) -> IPFSAgentResult | None:
        try:
            r = await client.get(f"https://ipfs.io/ipfs/{ipfs_cid}")
            r.raise_for_status()
            return IPFSAgentResult(**r.json())
        except httpx.HTTPError as e:
            logger.warning(
                f"Failed to fetch IPFS content from ipfs.io for CID {ipfs_cid}, error {e}"
            )
            return None

    async def fetch_predictions(self, market_id: HexAddress) -> list[MarketPrediction]:
        contract_predictions = self.subgraph_handler.get_agent_results_for_market(
            market_id=market_id
        )

        # Convert prediction hashes to IPFS CIDs
        ipfs_cids = [
            byte32_to_ipfscidv0(pred.ipfs_hash) for pred in contract_predictions
        ]

        # Fetch IPFS contents in parallel
        async with httpx.AsyncClient() as client:
            ipfs_contents = await asyncio.gather(
                *[self.fetch_ipfs_content(cid, client) for cid in ipfs_cids]
            )

        # Create MarketPrediction objects from valid pairs
        market_predictions = [
            MarketPrediction(prediction=pred, agent_result=result)
            for pred, result in zip(contract_predictions, ipfs_contents)
            if result is not None
        ]

        return market_predictions
