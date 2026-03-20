"""Scheduler entry point for the Bittensor Intel worker."""

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from src.config import settings
from src.db.session import async_sessionmaker
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot
from src.models.signal import Signal
from src.engine.data.collector import DataCollector
from src.engine.analysis.flow_detector import FlowDetector
from src.engine.analysis.fundamental_scorer import FundamentalScorer
from src.engine.analysis.signal_generator import SignalGenerator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class IntelScheduler:
    """Orchestrates periodic data collection and analysis."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.collector = DataCollector()
        self.flow_detector = FlowDetector()
        self.fundamental_scorer = FundamentalScorer()
        self.signal_generator = SignalGenerator()
        self.interval = settings.POLL_INTERVAL_MINUTES

    def start(self):
        """Start all scheduled jobs."""
        self.scheduler.add_job(
            self._collect_and_analyze,
            trigger="interval",
            minutes=self.interval,
            id="collect_and_analyze",
            replace_existing=True,
        )
        # Run once immediately on startup
        self.scheduler.add_job(
            self._collect_and_analyze,
            id="initial_run",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info(f"Scheduler started. Polling every {self.interval} minutes.")
        logger.info("Initial data collection running...")

    async def _collect_and_analyze(self):
        """Single run: collect data, analyze, generate signals."""
        try:
            logger.info("Starting data collection...")
            await self.collector.collect_all()
            logger.info("Data collection complete. Running analysis...")

            # Run analysis on each subnet
            async with async_sessionmaker() as session:
                result = await session.execute(
                    select(Subnet).where(Subnet.is_active == True)
                )
                subnets = result.scalars().all()

                for subnet in subnets:
                    try:
                        # Get recent snapshots
                        snap_result = await session.execute(
                            select(FlowSnapshot)
                            .where(FlowSnapshot.subnet_netuid == subnet.netuid)
                            .order_by(FlowSnapshot.timestamp.desc())
                            .limit(672)  # ~7 days at 15min intervals
                        )
                        snapshots = list(snap_result.scalars().all())
                        snapshots.reverse()  # Ascending order for analysis

                        if len(snapshots) < 3:
                            continue

                        # Generate signal
                        signal_result = self.signal_generator.generate(
                            subnet, snapshots
                        )

                        # Save signal
                        signal = Signal(
                            subnet_netuid=subnet.netuid,
                            signal_type=signal_result.signal_type,
                            flow_signal=signal_result.flow_signal,
                            confidence=signal_result.confidence,
                            composite_score=signal_result.composite_score,
                            flow_score=signal_result.flow_score,
                            fundamental_score=signal_result.fundamental_score,
                            risk_score=signal_result.risk_score,
                            evidence=signal_result.evidence,
                            reasoning=signal_result.reasoning,
                        )
                        session.add(signal)

                        # Update subnet scores
                        subnet.fundamental_score = signal_result.fundamental_score
                        subnet.risk_score = signal_result.risk_score

                    except Exception as e:
                        logger.error(f"Error analyzing subnet {subnet.netuid}: {e}")
                        continue

                await session.commit()
                logger.info(f"Analysis complete. Processed {len(subnets)} subnets.")

        except Exception as e:
            logger.error(f"Error in collect_and_analyze: {e}")


async def main():
    """Entry point for `python -m src.engine.scheduler`."""
    scheduler = IntelScheduler()
    scheduler.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
