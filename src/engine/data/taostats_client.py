"""Taostats API client with fallback web scraping."""

import asyncio
from typing import Any
import httpx
from bs4 import BeautifulSoup
from src.config import settings


class TaostatsAPIError(Exception):
    """Raised when Taostats API fails and scraping fallback also fails."""

    pass


class TaostatsClient:
    """Async HTTP client for Taostats API with web scraping fallback."""

    BASE_URL = "https://api.taostats.io"
    # Fallback to main site for scraping
    SCRAPE_URL = "https://taostats.io"

    def __init__(self, api_key: str | None = None):
        """Initialize client with optional API key."""
        self.api_key = api_key or getattr(settings, "taostats_api_key", None)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            headers = {"Accept": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=headers,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    async def aclose(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request with error handling."""
        client = await self._ensure_client()
        try:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            if e.response and e.response.status_code in (429, 502, 503, 504):
                # Rate limit or server error - try scraping fallback
                raise TaostatsAPIError(f"API error: {e}")
            raise

    async def get_subnets(self) -> list[dict]:
        """Fetch all subnet data from Taostats.

        Returns:
            List of subnet dicts with keys: netuid, name, symbol, market_cap,
                price, emission, active_miners, active_validators, etc.
        """
        try:
            # Try the pools endpoint which has comprehensive subnet data
            data = await self._request("GET", "/api/subnet/pools/v1")
            return data.get("data", [])
        except (httpx.HTTPError, TaostatsAPIError):
            # Fallback to scraping the main website
            return await self._scrape_subnets()

    async def get_subnet_detail(self, netuid: int) -> dict:
        """Fetch detailed subnet data including flow history.

        Args:
            netuid: Subnet unique ID

        Returns:
            Dict with subnet details including flow, emission, price history, etc.
        """
        try:
            # Get current pool data
            pools = await self._request(
                "GET", "/api/subnet/pools/v1", params={"netuid": netuid}
            )
            pool_data = pools.get("data", {})

            # Get flow data
            flow = await self._request(
                "GET", "/api/dtao/tao_flow/v1", params={"netuid": netuid}
            )
            flow_data = flow.get("data", [])

            # Merge data
            detail = {**pool_data, "flow_data": flow_data}
            return detail
        except (httpx.HTTPError, TaostatsAPIError):
            # Fallback to scraping
            return await self._scrape_subnet_detail(netuid)

    async def get_flow_history(self, netuid: int, days: int = 30) -> list[dict]:
        """Fetch historical flow data for a subnet.

        Args:
            netuid: Subnet unique ID
            days: Number of days of history (default 30)

        Returns:
            List of flow records with timestamp and tao_flow values
        """
        try:
            # Calculate block range based on days (approximate 7200 blocks/day)
            # Note: Taostats API may use block numbers instead of dates
            # For now, fetch recent flow data
            flow = await self._request(
                "GET",
                "/api/dtao/tao_flow/v1",
                params={"netuid": netuid, "limit": days * 96},  # ~96 blocks per day
            )
            return flow.get("data", [])
        except (httpx.HTTPError, TaostatsAPIError):
            # Fallback to scraping
            return await self._scrape_flow_history(netuid, days)

    async def _scrape_subnets(self) -> list[dict]:
        """Scrape subnet data from taostats.io website."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.SCRAPE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            subnets = []

            # Parse the subnet table (implementation depends on actual HTML structure)
            # This is a placeholder - actual selectors need to be determined
            table = soup.find("table", {"class": "subnet-table"})
            if table:
                for row in table.find_all("tr")[1:]:  # Skip header
                    cells = row.find_all("td")
                    if len(cells) >= 6:
                        subnet = {
                            "netuid": int(cells[0].text.strip()),
                            "name": cells[1].text.strip(),
                            "symbol": cells[2].text.strip(),
                            "market_cap": float(cells[3].text.strip().replace(",", "")),
                            "price": float(cells[4].text.strip()),
                            "emission": float(cells[5].text.strip()),
                            "active_miners": int(cells[6].text.strip())
                            if len(cells) > 6
                            else 0,
                            "active_validators": int(cells[7].text.strip())
                            if len(cells) > 7
                            else 0,
                        }
                        subnets.append(subnet)

            return subnets

    async def _scrape_subnet_detail(self, netuid: int) -> dict:
        """Scrape detailed subnet data from website."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.SCRAPE_URL}/subnet/{netuid}"
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            # Placeholder parsing - needs actual HTML structure
            detail = {"netuid": netuid}

            # Extract flow data from charts or tables
            # Implementation depends on actual page structure

            return detail

    async def _scrape_flow_history(self, netuid: int, days: int) -> list[dict]:
        """Scrape flow history from website charts."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.SCRAPE_URL}/subnet/{netuid}"
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            history = []

            # Look for flow chart data (often in JavaScript variables or data attributes)
            # This is a placeholder - actual implementation needs page analysis

            return history
