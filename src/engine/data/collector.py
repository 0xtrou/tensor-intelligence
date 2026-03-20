"""Data collection orchestrator for Bittensor subnet intelligence."""

import asyncio
from datetime import datetime
from typing import List
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.session import async_sessionmaker
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.engine.data.taostats_client import TaostatsClient


class DataCollector:
    """Orchestrates periodic data collection from Taostats."""

    def __init__(self):
        self.taostats = TaostatsClient()
        self.collection_interval = getattr(
            settings, "collection_interval_seconds", 900
        )  # 15 min default

    async def collect_all(self) -> None:
        """Collect data for all active subnets.

        Fetches all subnets from Taostats, upserts Subnet records,
        and creates FlowSnapshot records for each.
        """
        async with self.taostats:
            # Fetch all subnets
            subnet_data_list = await self.taostats.get_subnets()

            async with async_sessionmaker() as session:
                for subnet_data in subnet_data_list:
                    try:
                        await self._process_subnet(session, subnet_data)
                    except Exception as e:
                        # Log error but continue with other subnets
                        print(
                            f"Error processing subnet {subnet_data.get('netuid')}: {e}"
                        )
                        continue

                await session.commit()

    async def collect_subnet(self, netuid: int) -> None:
        """Collect detailed data for a single subnet.

        Args:
            netuid: Subnet unique ID to collect
        """
        async with self.taostats:
            subnet_data = await self.taostats.get_subnet_detail(netuid)
            flow_history = await self.taostats.get_flow_history(netuid)

            async with async_sessionmaker() as session:
                await self._process_subnet(session, subnet_data)

                # Create flow snapshots from history
                for flow_record in flow_history:
                    snapshot = FlowSnapshot(
                        subnet_netuid=netuid,
                        timestamp=datetime.fromisoformat(
                            flow_record["timestamp"].replace("Z", "+00:00")
                        ),
                        flow_ema=float(flow_record.get("tao_flow", 0)),
                        emission_share=float(subnet_data.get("emission", 0)),
                        # Additional fields as available
                        miners_count=int(subnet_data.get("active_miners", 0)),
                        validators_count=int(subnet_data.get("active_validators", 0)),
                        price=float(subnet_data.get("price", 0)),
                        market_cap=float(subnet_data.get("market_cap", 0)),
                        tao_volume_24h=float(subnet_data.get("tao_volume_24_hr", 0)),
                        alpha_volume_24h=float(
                            subnet_data.get("alpha_volume_24_hr", 0)
                        ),
                    )
                    session.add(snapshot)

                await session.commit()

    async def _process_subnet(self, session: AsyncSession, data: dict) -> None:
        """Process a single subnet record.

        Args:
            session: Database session
            data: Subnet data dict from Taostats
        """
        netuid = data["netuid"]

        # Check if subnet exists
        result = await session.execute(select(Subnet).where(Subnet.netuid == netuid))
        existing = result.scalar_one_or_none()

        # Prepare subnet values
        subnet_values = {
            "netuid": netuid,
            "name": data.get("name", ""),
            "symbol": data.get("symbol", ""),
            "price": float(data.get("price", 0)),
            "market_cap": float(data.get("market_cap", 0)),
            "emission": float(data.get("emission", 0)),
            "emission_share": float(data.get("emission_share", 0)),
            "active_miners": int(data.get("active_miners", 0)),
            "active_validators": int(data.get("active_validators", 0)),
            "liquidity": float(data.get("liquidity", 0)),
            "total_tao": float(data.get("total_tao", 0)),
            "total_alpha": float(data.get("total_alpha", 0)),
            "alpha_staked": float(data.get("alpha_staked", 0)),
            "tao_volume_24h": float(data.get("tao_volume_24_hr", 0)),
            "alpha_volume_24h": float(data.get("alpha_volume_24_hr", 0)),
            "updated_at": datetime.utcnow(),
        }

        if existing:
            # Update existing subnet
            stmt = update(Subnet).where(Subnet.netuid == netuid).values(**subnet_values)
            await session.execute(stmt)
        else:
            # Create new subnet
            subnet = Subnet(**subnet_values)
            session.add(subnet)

        # Create current flow snapshot
        flow_snapshot = FlowSnapshot(
            subnet_netuid=netuid,
            timestamp=datetime.utcnow(),
            flow_ema=float(data.get("tao_flow", 0)),
            emission_share=float(data.get("emission", 0)),
            miners_count=int(data.get("active_miners", 0)),
            validators_count=int(data.get("active_validators", 0)),
            price=float(data.get("price", 0)),
            market_cap=float(data.get("market_cap", 0)),
            tao_volume_24h=float(data.get("tao_volume_24_hr", 0)),
            alpha_volume_24h=float(data.get("alpha_volume_24_hr", 0)),
        )
        session.add(flow_snapshot)
