"""LLM-powered daily intelligence report generator."""

import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select
import httpx

from src.config import settings
from src.db.session import async_sessionmaker
from src.models.subnet import Subnet
from src.models.signal import Signal
from src.models.flow_snapshot import FlowSnapshot
from src.models.report import Report

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates daily intelligence reports using LLM."""

    def __init__(self):
        self.llm_base_url = settings.LLM_BASE_URL
        self.llm_api_key = settings.LLM_API_KEY

    async def generate_daily_report(self) -> Report:
        """Generate a daily intelligence report from current data."""
        async with async_sessionmaker() as session:
            # Gather data
            subnets_result = await session.execute(
                select(Subnet)
                .where(Subnet.is_active == True)
                .order_by(Subnet.emission_share.desc())
                .limit(20)
            )
            subnets = list(subnets_result.scalars().all())

            # Get recent BUY/ACCUMULATE signals
            buy_signals_result = await session.execute(
                select(Signal)
                .where(Signal.signal_type.in_(["BUY", "ACCUMULATE"]))
                .order_by(Signal.confidence.desc())
                .limit(10)
            )
            buy_signals = list(buy_signals_result.scalars().all())

            # Get recent AVOID/REDUCE signals
            avoid_signals_result = await session.execute(
                select(Signal)
                .where(Signal.signal_type.in_(["AVOID", "REDUCE"]))
                .order_by(Signal.created_at.desc())
                .limit(10)
            )
            avoid_signals = list(avoid_signals_result.scalars().all())

            # Build data context
            data_context = self._build_data_context(subnets, buy_signals, avoid_signals)

            # Try LLM generation
            report_content = await self._call_llm(data_context)

            if not report_content:
                report_content = self._generate_template_report(
                    subnets, buy_signals, avoid_signals
                )

            # Save report
            report = Report(
                report_type="daily",
                title=f"Daily Intelligence Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                content=report_content,
                metadata_={
                    "subnets_analyzed": len(subnets),
                    "buy_signals": len(buy_signals),
                    "avoid_signals": len(avoid_signals),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            session.add(report)
            await session.commit()

            logger.info(f"Daily report generated: {report.title}")
            return report

    async def _call_llm(self, data_context: str) -> str | None:
        """Call OpenAI-compatible LLM endpoint. Returns None on failure."""
        if not self.llm_api_key and "localhost" not in self.llm_base_url:
            logger.info("No LLM API key configured, using template report")
            return None

        system_prompt = """You are a Bittensor subnet investment analyst. Generate a concise, actionable daily intelligence report in Markdown.

Structure:
# Daily Intelligence Report — [date]

## Market Overview
Brief summary of top subnets by emission, any notable movements.

## Top Opportunities
Subnets with BUY/ACCUMULATE signals. For each: name, signal, confidence, key reason.

## Risk Watch  
Subnets with REDUCE/AVOID signals. For each: name, signal, key concern.

## Flow Movers
Top 5 subnets by flow change direction (biggest increases and decreases).

## Summary
2-3 sentence actionable summary.

Keep it concise. No fluff. Data-driven analysis only."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}"
                        if self.llm_api_key
                        else "Bearer sk-placeholder",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "sonnet",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": data_context},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"LLM call failed, using template: {e}")
            return None

    def _build_data_context(
        self, subnets: list, buy_signals: list, avoid_signals: list
    ) -> str:
        """Convert data to text context for LLM."""
        lines = ["CURRENT SUBNET DATA (sorted by emission share):\n"]

        for s in subnets[:15]:
            lines.append(
                f"- SN{s.netuid} {s.name}: emission={s.emission_share:.2%}, "
                f"price={s.price:.6f} TAO, MC={s.market_cap:.0f}, "
                f"miners={s.active_miners}, validators={s.active_validators}, "
                f"fund_score={s.fundamental_score or 'N/A'}, "
                f"risk_score={s.risk_score or 'N/A'}"
            )

        if buy_signals:
            lines.append("\nBUY/ACCUMULATE SIGNALS:")
            for sig in buy_signals[:5]:
                lines.append(
                    f"- SN{sig.subnet_netuid}: {sig.signal_type} "
                    f"(confidence={sig.confidence:.1f}, score={sig.composite_score:.1f}) "
                    f"- {sig.flow_signal or ''}"
                )

        if avoid_signals:
            lines.append("\nREDUCE/AVOID SIGNALS:")
            for sig in avoid_signals[:5]:
                lines.append(
                    f"- SN{sig.subnet_netuid}: {sig.signal_type} "
                    f"(confidence={sig.confidence:.1f}, score={sig.composite_score:.1f}) "
                    f"- {sig.flow_signal or ''}"
                )

        return "\n".join(lines)

    def _generate_template_report(
        self, subnets: list, buy_signals: list, avoid_signals: list
    ) -> str:
        """Fallback template report when LLM is unavailable."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines = [
            f"# Daily Intelligence Report — {today}\n",
            "## Market Overview\n",
            f"Tracking {len(subnets)} active subnets.\n",
            "## Top Opportunities\n",
        ]

        if buy_signals:
            for sig in buy_signals[:5]:
                lines.append(
                    f"- **SN{sig.subnet_netuid}**: {sig.signal_type} "
                    f"(confidence: {sig.confidence:.1f}%, composite: {sig.composite_score:.1f}/100)"
                )
        else:
            lines.append("No BUY/ACCUMULATE signals detected.")

        lines.append("\n## Risk Watch\n")
        if avoid_signals:
            for sig in avoid_signals[:5]:
                lines.append(
                    f"- **SN{sig.subnet_netuid}**: {sig.signal_type} "
                    f"(confidence: {sig.confidence:.1f}%, composite: {sig.composite_score:.1f}/100)"
                )
        else:
            lines.append("No REDUCE/AVOID signals detected.")

        lines.append("\n## Top Subnets by Emission\n")
        for s in subnets[:10]:
            lines.append(
                f"| SN{s.netuid} | {s.name} | {s.emission_share:.2%} | {s.price:.6f} TAO |"
            )

        return "\n".join(lines)
