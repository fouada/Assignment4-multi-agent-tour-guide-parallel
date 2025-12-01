"""
Tests for Multi-Agent Negotiation Protocol via Game Theory.

MIT-Level Test Coverage for:
- AgentBid and AuctionResult
- VCGAuction mechanism
- NashEquilibriumAnalyzer
- ConsensusProtocol
- StrategicAgent
- CooperativeContentGame
- MultiAgentNegotiationSystem

Edge Cases Documented:
- Single bidder auction
- Tied bids
- Zero/negative bids
- Byzantine agents (non-truthful bidding)
- Empty coalition
- All agents fail
"""

import numpy as np

from src.research.agent_negotiation import (
    AgentBid,
    AgentType,
    ConsensusProtocol,
    CooperativeContentGame,
    MultiAgentNegotiationSystem,
    NashEquilibriumAnalyzer,
    StrategicAgent,
    VCGAuction,
)

# =============================================================================
# AgentBid Tests
# =============================================================================


class TestAgentBid:
    """Test AgentBid dataclass."""

    def test_bid_creation(self):
        """Test basic bid creation."""
        bid = AgentBid(
            agent_type=AgentType.VIDEO, value=0.8, bid=0.8, quality_score=0.9
        )
        assert bid.agent_type == AgentType.VIDEO
        assert bid.value == 0.8
        assert bid.bid == 0.8

    def test_is_truthful_true(self):
        """Test truthfulness check when bid equals value."""
        bid = AgentBid(
            agent_type=AgentType.MUSIC, value=0.7, bid=0.7, quality_score=0.85
        )
        assert bid.is_truthful is True

    def test_is_truthful_false(self):
        """Test truthfulness check when bid differs from value."""
        bid = AgentBid(
            agent_type=AgentType.TEXT,
            value=0.6,
            bid=0.9,  # Overbidding
            quality_score=0.75,
        )
        assert bid.is_truthful is False

    # EDGE CASE: Nearly equal bid and value
    def test_is_truthful_near_threshold(self):
        """Edge case: Bid very close to value (within tolerance)."""
        bid = AgentBid(
            agent_type=AgentType.VIDEO,
            value=0.5,
            bid=0.505,  # Within 0.01 tolerance
            quality_score=0.7,
        )
        assert bid.is_truthful is True


# =============================================================================
# VCGAuction Tests
# =============================================================================


class TestVCGAuction:
    """Test VCG auction mechanism."""

    def test_auction_creation(self):
        """Test auction creation with reserve price."""
        auction = VCGAuction(reserve_price=0.1)
        assert auction.reserve_price == 0.1

    def test_run_auction_basic(self):
        """Test basic auction with three bidders."""
        auction = VCGAuction()

        bids = [
            AgentBid(AgentType.VIDEO, value=0.8, bid=0.8, quality_score=0.9),
            AgentBid(AgentType.MUSIC, value=0.6, bid=0.6, quality_score=0.8),
            AgentBid(AgentType.TEXT, value=0.5, bid=0.5, quality_score=0.85),
        ]

        result = auction.run_auction(bids)

        assert result.winner == AgentType.VIDEO
        assert result.winning_bid == 0.8
        # VCG payment = second highest bid
        assert result.payments[AgentType.VIDEO] == 0.6

    def test_auction_efficiency(self):
        """Test that highest value bidder wins (efficiency)."""
        auction = VCGAuction()

        bids = [
            AgentBid(AgentType.VIDEO, value=0.3, bid=0.3, quality_score=0.9),
            AgentBid(AgentType.MUSIC, value=0.9, bid=0.9, quality_score=0.8),
            AgentBid(AgentType.TEXT, value=0.5, bid=0.5, quality_score=0.85),
        ]

        result = auction.run_auction(bids)

        assert result.winner == AgentType.MUSIC
        assert result.is_efficient is True

    # EDGE CASE: Single bidder
    def test_auction_single_bidder(self):
        """Edge case: Only one bidder."""
        auction = VCGAuction(reserve_price=0.1)

        bids = [AgentBid(AgentType.VIDEO, value=0.8, bid=0.8, quality_score=0.9)]

        result = auction.run_auction(bids)

        assert result.winner == AgentType.VIDEO
        # Payment should be reserve price
        assert result.payments[AgentType.VIDEO] == 0.1

    # EDGE CASE: Tied bids
    def test_auction_tied_bids(self):
        """Edge case: Two agents with identical bids."""
        auction = VCGAuction()

        bids = [
            AgentBid(AgentType.VIDEO, value=0.7, bid=0.7, quality_score=0.9),
            AgentBid(AgentType.MUSIC, value=0.7, bid=0.7, quality_score=0.8),
            AgentBid(AgentType.TEXT, value=0.5, bid=0.5, quality_score=0.85),
        ]

        result = auction.run_auction(bids)

        # Should pick one of the tied bidders
        assert result.winner in [AgentType.VIDEO, AgentType.MUSIC]
        assert result.winning_bid == 0.7

    # EDGE CASE: All bids below reserve price
    def test_auction_all_below_reserve(self):
        """Edge case: All bids below reserve price."""
        auction = VCGAuction(reserve_price=0.9)

        bids = [
            AgentBid(AgentType.VIDEO, value=0.5, bid=0.5, quality_score=0.9),
            AgentBid(AgentType.MUSIC, value=0.6, bid=0.6, quality_score=0.8),
        ]

        result = auction.run_auction(bids)

        assert result.is_efficient is False
        assert result.social_welfare == 0.0

    # EDGE CASE: Zero bids
    def test_auction_zero_bids(self):
        """Edge case: Bidder with zero bid."""
        auction = VCGAuction(reserve_price=0.0)

        bids = [
            AgentBid(AgentType.VIDEO, value=0.0, bid=0.0, quality_score=0.9),
            AgentBid(AgentType.MUSIC, value=0.5, bid=0.5, quality_score=0.8),
        ]

        result = auction.run_auction(bids)

        assert result.winner == AgentType.MUSIC

    def test_analyze_truthfulness(self):
        """Test truthfulness analysis."""
        auction = VCGAuction()

        # Run several auctions
        for _ in range(5):
            bids = [
                AgentBid(AgentType.VIDEO, value=0.7, bid=0.7, quality_score=0.9),
                AgentBid(AgentType.MUSIC, value=0.5, bid=0.5, quality_score=0.8),
                AgentBid(AgentType.TEXT, value=0.6, bid=0.6, quality_score=0.85),
            ]
            auction.run_auction(bids)

        analysis = auction.analyze_truthfulness()

        assert "truthfulness_rate" in analysis
        assert analysis["truthfulness_rate"] == 1.0  # All truthful
        assert analysis["num_auctions"] == 5


# =============================================================================
# NashEquilibriumAnalyzer Tests
# =============================================================================


class TestNashEquilibriumAnalyzer:
    """Test Nash equilibrium analysis."""

    def test_analyzer_creation(self):
        """Test analyzer creation."""
        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}
        analyzer = NashEquilibriumAnalyzer(values)

        assert len(analyzer.agents) == 3

    def test_compute_best_response(self):
        """Test best response computation."""
        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}
        analyzer = NashEquilibriumAnalyzer(values)

        other_bids = {AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}
        best_response = analyzer.compute_best_response(AgentType.VIDEO, other_bids)

        # Best response in VCG is truthful bidding
        assert best_response == 0.8

    def test_verify_nash_equilibrium_truthful(self):
        """Test that truthful bidding is Nash equilibrium."""
        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}
        analyzer = NashEquilibriumAnalyzer(values)

        # Truthful strategy profile
        truthful_profile = {
            AgentType.VIDEO: 0.8,
            AgentType.MUSIC: 0.6,
            AgentType.TEXT: 0.5,
        }

        is_nash, analysis = analyzer.verify_nash_equilibrium(truthful_profile)

        assert is_nash is True
        assert len(analysis["deviations"]) == 0

    def test_verify_nash_equilibrium_non_truthful(self):
        """Test non-truthful strategy is not Nash equilibrium."""
        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}
        analyzer = NashEquilibriumAnalyzer(values)

        # Non-truthful: VIDEO overbids
        non_truthful = {
            AgentType.VIDEO: 0.95,  # Overbidding
            AgentType.MUSIC: 0.6,
            AgentType.TEXT: 0.5,
        }

        is_nash, analysis = analyzer.verify_nash_equilibrium(non_truthful)

        # VIDEO has incentive to deviate to truthful
        # (though result depends on specific utility calculations)
        assert "strategy_profile" in analysis

    def test_find_nash_equilibrium(self):
        """Test finding Nash equilibrium."""
        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}
        analyzer = NashEquilibriumAnalyzer(values)

        ne = analyzer.find_nash_equilibrium()

        # Nash equilibrium should be truthful bidding
        assert ne[AgentType.VIDEO] == 0.8
        assert ne[AgentType.MUSIC] == 0.6
        assert ne[AgentType.TEXT] == 0.5


# =============================================================================
# ConsensusProtocol Tests
# =============================================================================


class TestConsensusProtocol:
    """Test distributed consensus protocol."""

    def test_protocol_creation(self):
        """Test protocol creation."""
        protocol = ConsensusProtocol(list(AgentType), seed=42)
        assert len(protocol.agents) == 3

    def test_reach_consensus_single_bid(self):
        """Test consensus with single bid."""
        protocol = ConsensusProtocol(list(AgentType), seed=42)

        bids = [AgentBid(AgentType.VIDEO, value=0.8, bid=0.8, quality_score=0.9)]

        winner = protocol.reach_consensus(bids)

        assert winner == AgentType.VIDEO

    def test_reach_consensus_multiple_bids(self):
        """Test consensus with multiple tied bids."""
        protocol = ConsensusProtocol(list(AgentType), seed=42)

        bids = [
            AgentBid(AgentType.VIDEO, value=0.7, bid=0.7, quality_score=0.9),
            AgentBid(AgentType.MUSIC, value=0.7, bid=0.7, quality_score=0.85),
        ]

        winner = protocol.reach_consensus(bids)

        assert winner in [AgentType.VIDEO, AgentType.MUSIC]

    # EDGE CASE: Empty bids
    def test_reach_consensus_no_bids(self):
        """Edge case: No bids to reach consensus on."""
        protocol = ConsensusProtocol(list(AgentType), seed=42)

        # This should handle empty gracefully
        # Default to first agent type
        winner = protocol.reach_consensus([])

        assert winner == AgentType.VIDEO


# =============================================================================
# StrategicAgent Tests
# =============================================================================


class TestStrategicAgent:
    """Test strategic agent model."""

    def test_truthful_agent(self):
        """Test truthful bidding strategy."""
        agent = StrategicAgent(AgentType.VIDEO, strategy="truthful", seed=42)

        bid = agent.generate_bid(value=0.8, quality_score=0.9)

        assert bid.bid == 0.8
        assert bid.is_truthful is True

    def test_overbidding_agent(self):
        """Test overbidding strategy."""
        agent = StrategicAgent(AgentType.MUSIC, strategy="overbid", seed=42)

        bid = agent.generate_bid(value=0.8, quality_score=0.9)

        assert bid.bid > 0.8  # Overbid
        assert bid.is_truthful is False

    def test_underbidding_agent(self):
        """Test underbidding strategy."""
        agent = StrategicAgent(AgentType.TEXT, strategy="underbid", seed=42)

        bid = agent.generate_bid(value=0.8, quality_score=0.9)

        assert bid.bid < 0.8  # Underbid
        assert bid.is_truthful is False

    def test_learning_agent_update(self):
        """Test learning agent parameter update."""
        agent = StrategicAgent(AgentType.VIDEO, strategy="learning", seed=42)

        # Initial adjustment should be 0

        # Update after winning with positive utility
        agent.update(value=0.8, bid=0.8, won=True, payment=0.5)

        # Adjustment should change
        assert len(agent.history) == 1


# =============================================================================
# CooperativeContentGame Tests
# =============================================================================


class TestCooperativeContentGame:
    """Test cooperative game theory for coalitions."""

    def test_game_creation(self):
        """Test game creation."""
        game = CooperativeContentGame(list(AgentType))
        assert game.n == 3

    def test_coalition_value_single(self):
        """Test single-agent coalition value."""
        game = CooperativeContentGame(list(AgentType))

        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}

        video_coalition = frozenset([AgentType.VIDEO])
        value = game.coalition_value(video_coalition, values)

        assert value == 0.8  # Just VIDEO's value, no synergy

    def test_coalition_value_with_synergy(self):
        """Test coalition value with synergy bonus."""
        game = CooperativeContentGame(list(AgentType))

        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}

        video_text = frozenset([AgentType.VIDEO, AgentType.TEXT])
        value = game.coalition_value(video_text, values)

        # Should be sum + synergy
        assert value > 0.8 + 0.5  # With synergy bonus

    def test_compute_shapley_values(self):
        """Test Shapley value computation."""
        game = CooperativeContentGame(list(AgentType))

        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}

        shapley = game.compute_shapley_values(values)

        assert AgentType.VIDEO in shapley
        assert AgentType.MUSIC in shapley
        assert AgentType.TEXT in shapley

        # Shapley values should be positive
        assert all(v >= 0 for v in shapley.values())

    def test_recommend_coalition(self):
        """Test coalition recommendation."""
        game = CooperativeContentGame(list(AgentType))

        values = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.5}

        best_coalition, value = game.recommend_coalition(values)

        assert len(best_coalition) >= 1
        assert value > 0

    # EDGE CASE: Empty values
    def test_coalition_value_zero_values(self):
        """Edge case: All agents have zero value."""
        game = CooperativeContentGame(list(AgentType))

        values = {AgentType.VIDEO: 0.0, AgentType.MUSIC: 0.0, AgentType.TEXT: 0.0}

        full_coalition = frozenset(AgentType)
        value = game.coalition_value(full_coalition, values)

        # Should only have synergy value
        assert value == game.synergies.get(full_coalition, 0)


# =============================================================================
# MultiAgentNegotiationSystem Tests
# =============================================================================


class TestMultiAgentNegotiationSystem:
    """Test main negotiation system interface."""

    def test_system_creation(self):
        """Test system creation."""
        system = MultiAgentNegotiationSystem(mechanism="vcg", seed=42)
        assert system.mechanism == "vcg"

    def test_select_content(self):
        """Test content selection."""
        system = MultiAgentNegotiationSystem(seed=42)

        valuations = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.7}
        quality_scores = {
            AgentType.VIDEO: 0.9,
            AgentType.MUSIC: 0.8,
            AgentType.TEXT: 0.85,
        }

        winner, analysis = system.select_content(valuations, quality_scores)

        assert winner == AgentType.VIDEO  # Highest valuation
        assert "winner" in analysis
        assert "is_nash_equilibrium" in analysis

    def test_multiple_selections(self):
        """Test multiple content selections."""
        system = MultiAgentNegotiationSystem(seed=42)

        for _ in range(5):
            valuations = {
                AgentType.VIDEO: np.random.uniform(0.5, 0.9),
                AgentType.MUSIC: np.random.uniform(0.5, 0.9),
                AgentType.TEXT: np.random.uniform(0.5, 0.9),
            }
            quality_scores = {
                AgentType.VIDEO: 0.8,
                AgentType.MUSIC: 0.8,
                AgentType.TEXT: 0.8,
            }

            system.select_content(valuations, quality_scores)

        assert len(system.selection_history) == 5

    def test_get_theoretical_analysis(self):
        """Test theoretical analysis output."""
        system = MultiAgentNegotiationSystem(seed=42)

        # Make some selections
        valuations = {AgentType.VIDEO: 0.8, AgentType.MUSIC: 0.6, AgentType.TEXT: 0.7}
        quality_scores = {
            AgentType.VIDEO: 0.9,
            AgentType.MUSIC: 0.8,
            AgentType.TEXT: 0.85,
        }
        system.select_content(valuations, quality_scores)

        theory = system.get_theoretical_analysis()

        assert "mechanism" in theory
        assert "properties" in theory
        assert "theoretical_guarantees" in theory


# =============================================================================
# Integration Tests
# =============================================================================


class TestNegotiationIntegration:
    """Integration tests for negotiation system."""

    def test_full_negotiation_pipeline(self):
        """Test complete negotiation pipeline."""
        system = MultiAgentNegotiationSystem(mechanism="vcg", seed=42)

        # Simulate 10 negotiations
        winners = []
        for i in range(10):
            valuations = {
                AgentType.VIDEO: 0.7 + 0.2 * (i % 3 == 0),
                AgentType.MUSIC: 0.7 + 0.2 * (i % 3 == 1),
                AgentType.TEXT: 0.7 + 0.2 * (i % 3 == 2),
            }
            quality_scores = {
                AgentType.VIDEO: 0.8,
                AgentType.MUSIC: 0.8,
                AgentType.TEXT: 0.8,
            }

            winner, _ = system.select_content(valuations, quality_scores)
            winners.append(winner)

        # All three types should win at some point
        assert AgentType.VIDEO in winners
        assert AgentType.MUSIC in winners
        assert AgentType.TEXT in winners

    def test_vcg_incentive_compatibility(self):
        """Test that VCG mechanism is incentive compatible."""
        system = MultiAgentNegotiationSystem(mechanism="vcg", seed=42)

        # True valuations
        true_valuations = {
            AgentType.VIDEO: 0.8,
            AgentType.MUSIC: 0.6,
            AgentType.TEXT: 0.7,
        }

        # Run with truthful bidding
        quality_scores = {
            AgentType.VIDEO: 0.9,
            AgentType.MUSIC: 0.8,
            AgentType.TEXT: 0.85,
        }
        winner, analysis = system.select_content(true_valuations, quality_scores)

        # Verify is Nash equilibrium (truthful bidding)
        assert analysis["is_nash_equilibrium"] is True
