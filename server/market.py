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


class MarketPrediction(ContractPrediction, IPFSAgentResult):
    pass


class MarketFetcher:
    def __init__(self) -> None:
        self.subgraph_handler = OmenSubgraphHandler()

    @staticmethod
    def fetch_ipfs_content(
        ipfs_cid: IPFSCIDVersion0, client: httpx.Client
    ) -> IPFSAgentResult | None:
        try:
            r = client.get(f"https://ipfs.io/ipfs/{ipfs_cid}")
            r.raise_for_status()
            return IPFSAgentResult(**r.json())
        except httpx.HTTPError as e:
            logger.warning(
                f"Failed to fetch IPFS content from ipfs.io for CID {ipfs_cid}, error {e}"
            )
            return None

    def fetch_predictions(self, market_id: HexAddress) -> list[MarketPrediction]:
        contract_predictions = self.subgraph_handler.get_agent_results_for_market(
            market_id=market_id
        )

        # Convert prediction hashes to IPFS CIDs
        ipfs_cids = [
            byte32_to_ipfscidv0(pred.ipfs_hash) for pred in contract_predictions
        ]

        with httpx.Client() as client:
            logger.info(f"Fetching IPFS contents from CIDs {ipfs_cids}")
            ipfs_contents = [self.fetch_ipfs_content(cid, client) for cid in ipfs_cids]

        # Merge contract and IPFS data
        market_predictions = []
        for contract_pred, ipfs_content in zip(contract_predictions, ipfs_contents):
            if ipfs_content is None:
                continue

            # Combine data from both sources
            prediction_data = {
                **contract_pred.model_dump(exclude={"publisher_checksummed"}),
                **ipfs_content.model_dump(),
            }

            market_predictions.append(MarketPrediction(**prediction_data))

        return market_predictions
