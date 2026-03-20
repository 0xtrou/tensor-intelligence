"""Discord webhook notifier for signals and reports."""

import logging
import httpx
from src.config import settings
from src.models.subnet import Subnet
from src.models.signal import Signal
from src.models.report import Report

logger = logging.getLogger(__name__)

SIGNAL_COLORS = {
    "BUY": 0x00FF00,  # Green
    "ACCUMULATE": 0xFFFF00,  # Yellow
    "HOLD": 0x808080,  # Gray
    "REDUCE": 0xFFA500,  # Orange
    "AVOID": 0xFF0000,  # Red
}


class DiscordNotifier:
    """Sends alerts to Discord via webhook."""

    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or settings.DISCORD_WEBHOOK_URL

    def _enabled(self) -> bool:
        return bool(self.webhook_url)

    async def send_signal_alert(self, subnet: Subnet, signal: Signal):
        """Send a signal alert to Discord as an embed."""
        if not self._enabled():
            logger.info(
                f"Discord not configured. Signal: {signal.signal_type} for {subnet.name}"
            )
            return

        color = SIGNAL_COLORS.get(signal.signal_type, 0x808080)

        embed = {
            "title": f"{signal.signal_type}: {subnet.name} (SN{subnet.netuid})",
            "description": signal.reasoning[:500]
            if signal.reasoning
            else "No reasoning available",
            "color": color,
            "fields": [
                {
                    "name": "Confidence",
                    "value": f"{signal.confidence:.1f}%",
                    "inline": True,
                },
                {
                    "name": "Composite Score",
                    "value": f"{signal.composite_score:.1f}/100",
                    "inline": True,
                },
                {
                    "name": "Flow Score",
                    "value": f"{signal.flow_score:.1f}/100",
                    "inline": True,
                },
                {
                    "name": "Fundamental Score",
                    "value": f"{signal.fundamental_score:.1f}/100",
                    "inline": True,
                },
                {
                    "name": "Risk Score",
                    "value": f"{signal.risk_score:.1f}/100",
                    "inline": True,
                },
                {
                    "name": "Flow Signal",
                    "value": signal.flow_signal or "N/A",
                    "inline": True,
                },
                {"name": "Price", "value": f"{subnet.price:.6f} TAO", "inline": True},
                {
                    "name": "Emission",
                    "value": f"{subnet.emission_share:.2%}",
                    "inline": True,
                },
            ],
            "footer": {
                "text": f"Subnet {subnet.netuid} | Score: {signal.composite_score:.1f}"
            },
        }

        payload = {
            "username": "Bittensor Intel",
            "embeds": [embed],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(self.webhook_url, json=payload)
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")

    async def send_flow_alert(self, subnet: Subnet, flow_signal: str, details: dict):
        """Send a flow change alert."""
        if not self._enabled():
            return

        color = (
            0x00FF00 if "SURGE" in flow_signal or "STEADY" in flow_signal else 0xFFA500
        )

        embed = {
            "title": f"Flow Alert: {subnet.name} (SN{subnet.netuid})",
            "description": f"**{flow_signal}** detected",
            "color": color,
            "fields": [
                {
                    "name": "Current Flow",
                    "value": f"{details.get('current_flow', 0):.2e}",
                    "inline": True,
                },
                {
                    "name": "Momentum",
                    "value": f"{details.get('momentum', 0):.1f}",
                    "inline": True,
                },
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(self.webhook_url, json={"embeds": [embed]})
        except Exception as e:
            logger.error(f"Failed to send flow alert: {e}")

    async def send_daily_summary(self, report: Report):
        """Send daily report summary to Discord."""
        if not self._enabled():
            return

        # Truncate content for Discord (2000 char limit)
        content = (
            report.content[:1900] + "..."
            if len(report.content) > 1900
            else report.content
        )

        payload = {
            "username": "Bittensor Intel",
            "content": f"## {report.title}\n\n{content}",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                await client.post(self.webhook_url, json=payload)
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
