"""Durbin Framework fundamental scoring for Bittensor subnets."""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List
from src.models.subnet import Subnet
from src.models.flow_snapshot import FlowSnapshot


@dataclass
class FundamentalScore:
    """Result of fundamental analysis."""

    total: float  # 0-100
    breakdown: Dict[str, float]  # per-dimension scores
    notes: List[str]  # explanations


class FundamentalScorer:
    """Scores subnet fundamentals using the Durbin Framework."""

    WEIGHTS = {
        "team_quality": 0.20,
        "use_case_clarity": 0.15,
        "technical_execution": 0.20,
        "network_effects": 0.15,
        "community_sentiment": 0.10,
        "tokenomics_health": 0.10,
        "competitive_moat": 0.10,
    }

    # Known subnet metadata (hardcoded for MVP, later from scraping)
    KNOWN_SUBNETS = {
        1: {
            "name": "Apex",
            "team": "Macrocosmos",
            "category": "ai_inference",
            "has_doxed_team": True,
            "competitiveness": "high",
            "experience_years": 3,
        },
        3: {
            "name": "Templar",
            "team": "Rayon Labs",
            "category": "training",
            "has_doxed_team": True,
            "competitiveness": "medium",
            "experience_years": 2,
        },
        4: {
            "name": "Targon",
            "team": "Targon Labs",
            "category": "ai_inference",
            "has_doxed_team": True,
            "competitiveness": "high",
            "nvidia_inception": True,
            "experience_years": 2,
        },
        5: {
            "name": "OpenKaito",
            "team": "Kaito AI",
            "category": "search",
            "has_doxed_team": True,
            "competitiveness": "medium",
            "experience_years": 2,
        },
        8: {
            "name": "Trading Network",
            "team": "Unknown",
            "category": "finance",
            "has_doxed_team": False,
            "competitiveness": "medium",
            "experience_years": 1,
        },
        9: {
            "name": "Pretraining",
            "team": "Unknown",
            "category": "research",
            "has_doxed_team": False,
            "competitiveness": "medium",
            "experience_years": 1,
        },
        13: {
            "name": "Data Universe",
            "team": "Macrocosmos",
            "category": "data",
            "has_doxed_team": True,
            "competitiveness": "high",
            "experience_years": 3,
        },
        17: {
            "name": "404gen",
            "team": "Unknown",
            "category": "3d_gen",
            "has_doxed_team": False,
            "competitiveness": "medium",
            "experience_years": 1,
        },
        19: {
            "name": "Nineteen",
            "team": "Unknown",
            "category": "vision",
            "has_doxed_team": False,
            "competitiveness": "medium",
            "experience_years": 1,
        },
        34: {
            "name": "BitMind",
            "team": "Unknown",
            "category": "safety",
            "has_doxed_team": False,
            "competitiveness": "medium",
            "experience_years": 1,
        },
        56: {
            "name": "Gradients",
            "team": "Unknown",
            "category": "training",
            "has_doxed_team": False,
            "competitiveness": "medium",
            "experience_years": 1,
        },
        64: {
            "name": "Chutes",
            "team": "Chutes AI",
            "category": "ai_compute",
            "has_doxed_team": True,
            "competitiveness": "high",
            "first_100m_mc": True,
            "experience_years": 2,
        },
        120: {
            "name": "Affine",
            "team": "Affine Labs",
            "category": "ai_inference",
            "has_doxed_team": True,
            "competitiveness": "high",
            "experience_years": 2,
        },
    }

    def score(
        self, subnet: Subnet, recent_snapshots: List[FlowSnapshot]
    ) -> FundamentalScore:
        """Score a subnet's fundamentals 0-100.

        Args:
            subnet: Subnet model instance
            recent_snapshots: Recent flow snapshots (last 30 days ideally)

        Returns:
            FundamentalScore with total score, breakdown, and notes
        """
        metadata = self.KNOWN_SUBNETS.get(
            subnet.netuid,
            {
                "name": subnet.name,
                "team": "Unknown",
                "category": "unknown",
                "has_doxed_team": False,
                "competitiveness": "low",
                "experience_years": 0,
            },
        )

        breakdown = {}
        notes = []

        # Score each dimension
        breakdown["team_quality"] = self._score_team(subnet, metadata)
        breakdown["use_case_clarity"] = self._score_use_case(subnet, metadata)
        breakdown["technical_execution"] = self._score_execution(
            subnet, recent_snapshots
        )
        breakdown["network_effects"] = self._score_network(subnet, recent_snapshots)
        breakdown["community_sentiment"] = self._score_community(subnet)
        breakdown["tokenomics_health"] = self._score_tokenomics(
            subnet, recent_snapshots
        )
        breakdown["competitive_moat"] = self._score_moat(subnet, metadata)

        # Calculate weighted total
        total = sum(breakdown[dim] * self.WEIGHTS[dim] for dim in self.WEIGHTS)

        # Generate notes
        notes = self._generate_notes(breakdown, metadata)

        return FundamentalScore(total=total, breakdown=breakdown, notes=notes)

    def _score_team(self, subnet: Subnet, metadata: dict) -> float:
        """Score team quality 0-100."""
        score = 0.0

        # Doxxed team
        if metadata.get("has_doxed_team"):
            score += 30.0
        else:
            score += 0.0
            # Note: anonymous teams are common in crypto but risky

        # Experience
        exp_years = metadata.get("experience_years", 0)
        if exp_years >= 3:
            score += 30.0
        elif exp_years >= 2:
            score += 20.0
        elif exp_years >= 1:
            score += 10.0

        # Track record (based on known successful projects)
        if metadata.get("team") in ["Macrocosmos", "Chutes AI", "Affine Labs"]:
            score += 20.0

        # Team size (inferred from subnet activity)
        if subnet.active_miners > 50:
            score += 10.0
        elif subnet.active_miners > 20:
            score += 5.0

        # Funding status (if known)
        if metadata.get("vc_funded"):
            score += 10.0

        return min(100.0, score)

    def _score_use_case(self, subnet: Subnet, metadata: dict) -> float:
        """Score use case clarity 0-100."""
        score = 0.0
        category = metadata.get("category", "unknown")

        # Service-oriented categories score higher than pure research
        service_categories = [
            "ai_inference",
            "search",
            "finance",
            "ai_compute",
            "data",
            "3d_gen",
            "vision",
            "safety",
        ]
        research_categories = ["training", "research"]

        if category in service_categories:
            score += 40.0
        elif category in research_categories:
            score += 20.0

        # Clear problem statement (inferred from category)
        if category in ["ai_inference", "search", "finance"]:
            score += 20.0  # Clear commercial applications

        # Market demand (based on emission share and market cap)
        if subnet.emission_share and subnet.emission_share > 0.01:  # >1% emission share
            score += 20.0

        # Active development (GitHub activity would be ideal, but we use miner count)
        if subnet.active_miners > 30:
            score += 20.0

        return min(100.0, score)

    def _score_execution(self, subnet: Subnet, snapshots: List[FlowSnapshot]) -> float:
        """Score technical execution 0-100."""
        if len(snapshots) < 10:
            return 50.0  # Neutral if insufficient data

        score = 0.0

        # Uptime proxy: consistent snapshots
        # Count snapshots in last 30 days (should be ~2880 at 15min intervals)
        expected_snapshots = 2880
        actual_snapshots = len(snapshots)
        completeness = min(1.0, actual_snapshots / expected_snapshots)
        score += completeness * 30.0

        # Stable miner/validator counts (low volatility)
        miner_counts = [s.miners_count for s in snapshots]
        if miner_counts:
            volatility = (
                np.std(miner_counts) / np.mean(miner_counts)
                if np.mean(miner_counts) > 0
                else 0
            )
            if volatility < 0.1:
                score += 30.0  # Very stable
            elif volatility < 0.3:
                score += 20.0
            elif volatility < 0.5:
                score += 10.0
            else:
                score += 0.0

        # Incentive stability (flow consistency)
        flows = [s.flow_ema for s in snapshots]
        if flows:
            # Count positive flow days
            positive_days = sum(1 for f in flows if f > 0)
            positive_ratio = positive_days / len(flows)
            score += positive_ratio * 40.0

        return min(100.0, score)

    def _score_network(self, subnet: Subnet, snapshots: List[FlowSnapshot]) -> float:
        """Score network effects 0-100."""
        if len(snapshots) < 10:
            return 50.0

        score = 0.0
        miner_counts = [s.miners_count for s in snapshots]
        validator_counts = [s.validators_count for s in snapshots]

        # Growing miner count
        if len(miner_counts) >= 2:
            start_miners = miner_counts[0]
            end_miners = miner_counts[-1]
            if start_miners > 0:
                growth_rate = (end_miners - start_miners) / start_miners
                if growth_rate > 0.2:
                    score += 30.0  # >20% growth
                elif growth_rate > 0.1:
                    score += 20.0
                elif growth_rate > 0:
                    score += 10.0
                else:
                    score += 0.0

        # Growing validator count
        if len(validator_counts) >= 2:
            start_validators = validator_counts[0]
            end_validators = validator_counts[-1]
            if start_validators > 0:
                growth_rate = (end_validators - start_validators) / start_validators
                if growth_rate > 0.2:
                    score += 30.0
                elif growth_rate > 0.1:
                    score += 20.0
                elif growth_rate > 0:
                    score += 10.0

        # Active participation rate
        if subnet.active_miners and subnet.active_validators:
            # Assuming max meaningful values
            max_miners = 100
            max_validators = 50
            miner_score = min(1.0, subnet.active_miners / max_miners) * 20.0
            validator_score = min(1.0, subnet.active_validators / max_validators) * 20.0
            score += miner_score + validator_score

        return min(100.0, score)

    def _score_community(self, subnet: Subnet) -> float:
        """Score community sentiment 0-100."""
        # For MVP, use SSI if available, otherwise neutral
        # SSI (Subnet Sentiment Index) is 0-100 composite score from Taostats
        # This would ideally come from social scraping in later phases

        # Placeholder: return neutral score
        # In production, this would integrate:
        # - Discord activity metrics
        # - Twitter engagement
        # - SSI from Taostats if available
        return 50.0

    def _score_tokenomics(self, subnet: Subnet, snapshots: List[FlowSnapshot]) -> float:
        """Score tokenomics health 0-100."""
        score = 0.0

        # Liquidity depth (liquidity / market_cap ratio)
        if subnet.liquidity and subnet.market_cap and subnet.market_cap > 0:
            liquidity_ratio = subnet.liquidity / subnet.market_cap
            if liquidity_ratio > 0.1:  # >10% liquidity depth
                score += 30.0
            elif liquidity_ratio > 0.05:
                score += 20.0
            elif liquidity_ratio > 0.02:
                score += 10.0

        # Staking ratio (alpha_staked / total_alpha)
        if subnet.total_alpha and subnet.total_alpha > 0:
            staking_ratio = subnet.alpha_staked / subnet.total_alpha
            if staking_ratio > 0.5:
                score += 30.0  # >50% staked is healthy
            elif staking_ratio > 0.3:
                score += 20.0
            elif staking_ratio > 0.1:
                score += 10.0

        # Emission sustainability (emission share vs market cap)
        # Higher emission with reasonable market cap suggests sustainable rewards
        if subnet.emission_share and subnet.market_cap:
            # Rough heuristic: emission share should be proportional to market cap rank
            # For now, neutral
            pass

        # Volume activity (24h volume indicates liquidity)
        if subnet.tao_volume_24h:
            if subnet.tao_volume_24h > 1e12:  # >1T TAO daily volume
                score += 20.0
            elif subnet.tao_volume_24h > 1e11:
                score += 10.0

        # Flow stability (from snapshots)
        if len(snapshots) >= 10:
            flows = [s.flow_ema for s in snapshots]
            positive_ratio = sum(1 for f in flows if f > 0) / len(flows)
            if positive_ratio > 0.8:
                score += 20.0
            elif positive_ratio > 0.6:
                score += 10.0

        return min(100.0, score)

    def _score_moat(self, subnet: Subnet, metadata: dict) -> float:
        """Score competitive moat 0-100."""
        score = 0.0
        competitiveness = metadata.get("competitiveness", "low")

        # Base competitiveness
        if competitiveness == "high":
            score += 30.0
        elif competitiveness == "medium":
            score += 15.0

        # Proprietary data/model
        if metadata.get("has_proprietary_data"):
            score += 20.0

        # First-mover advantage
        if metadata.get("first_100m_mc"):
            score += 20.0

        # Network effects (already scored in _score_network, but moat bonus)
        if subnet.active_miners > 50:
            score += 15.0

        # Category leadership (inferred from emission share)
        if subnet.emission_share and subnet.emission_share > 0.05:  # >5% emission share
            score += 15.0

        # Team reputation (already in team score, but moat bonus)
        if metadata.get("team") in ["Macrocosmos", "Chutes AI"]:
            score += 10.0

        return min(100.0, score)

    def _generate_notes(self, breakdown: Dict[str, float], metadata: dict) -> List[str]:
        """Generate explanatory notes for the score."""
        notes = []

        # Team notes
        if breakdown["team_quality"] > 80:
            notes.append("Strong, experienced team with public track record")
        elif breakdown["team_quality"] < 40:
            notes.append("Anonymous or inexperienced team - higher risk")

        # Use case notes
        if breakdown["use_case_clarity"] > 70:
            notes.append(
                f"Clear service-oriented use case in {metadata.get('category', 'unknown')}"
            )
        elif breakdown["use_case_clarity"] < 40:
            notes.append("Unclear or research-focused use case")

        # Execution notes
        if breakdown["technical_execution"] > 70:
            notes.append("Consistent technical execution and uptime")
        elif breakdown["technical_execution"] < 40:
            notes.append("Inconsistent operation or high volatility")

        # Network effects notes
        if breakdown["network_effects"] > 70:
            notes.append("Strong network growth and participation")
        elif breakdown["network_effects"] < 40:
            notes.append("Stagnant or declining network participation")

        # Tokenomics notes
        if breakdown["tokenomics_health"] > 70:
            notes.append("Healthy tokenomics with good liquidity")
        elif breakdown["tokenomics_health"] < 40:
            notes.append("Poor tokenomics or shallow liquidity")

        # Moat notes
        if breakdown["competitive_moat"] > 70:
            notes.append("Strong competitive moat and defensibility")
        elif breakdown["competitive_moat"] < 40:
            notes.append("Weak moat - high competition risk")

        return notes
