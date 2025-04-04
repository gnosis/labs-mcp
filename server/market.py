from prediction_market_agent_tooling.markets.omen.data_models import (
    IPFSAgentResult,
    ContractPrediction,
)
from prediction_market_agent_tooling.markets.omen.omen_subgraph_handler import (
    OmenSubgraphHandler,
)
from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.tools.web3_utils import byte32_to_ipfscidv0
from prediction_market_agent_tooling.tools.parallelism import par_map
from prediction_market_agent_tooling.loggers import logger
import httpx


class MarketPrediction(ContractPrediction, IPFSAgentResult):
    pass


class MarketFetcher:
    def __init__(self):
        self.subgraph_handler = OmenSubgraphHandler()

    @staticmethod
    def fetch_ipfs_content(ipfs_cid: str) -> IPFSAgentResult | None:
        try:
            r = httpx.get(f"https://ipfs.io/ipfs/{ipfs_cid}")
            r.raise_for_status()
            return IPFSAgentResult(**r.json())
        except httpx.HTTPError as e:
            logger.warning(
                f"Failed to fetch IPFS content from gateway.ipfs.io for CID {ipfs_cid}, error {e}"
            )

    def fetch_predictions(self, market_id: HexAddress) -> list[MarketPrediction]:
        predictions = self.subgraph_handler.get_agent_results_for_market(
            market_id=market_id
        )

        ipfs_cids = [byte32_to_ipfscidv0(p.ipfs_hash) for p in predictions]
        # We retrieve the IPFS contents in parallel
        ipfs_contents: list[IPFSAgentResult] = par_map(
            ipfs_cids, self.fetch_ipfs_content
        )
        items: list[MarketPrediction] = []
        for a, b in zip(predictions, ipfs_contents):
            if b is None:
                continue
            d = a.model_dump(exclude={"publisher_checksummed"})
            d.update(b.model_dump())
            items.append(MarketPrediction(**d))

        return items
