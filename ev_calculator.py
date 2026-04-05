"""
Expected Value (EV) Calculator
===============================

Calculate Expected Value for NBA moneyline bets:
- Convert moneyline odds to decimal odds
- Calculate EV: p*b - (1-p)
- Kelly Criterion bet sizing
- Filter for positive EV bets

M2 Phase 3: EV Calculation
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime


class EVCalculator:
    """Expected Value calculator for sports betting"""
    
    def __init__(self):
        """Initialize EV calculator"""
        pass
    
    @staticmethod
    def moneyline_to_decimal(moneyline: int) -> float:
        """
        Convert American moneyline odds to decimal odds
        
        Args:
            moneyline: American odds (e.g., +150, -200)
        
        Returns:
            Decimal odds (e.g., 2.50, 1.50)
        
        Examples:
            +150 → 2.50 (win $150 on $100 bet)
            -200 → 1.50 (bet $200 to win $100)
        """
        if moneyline > 0:
            # Positive odds: decimal = (moneyline / 100) + 1
            return (moneyline / 100.0) + 1.0
        else:
            # Negative odds: decimal = (100 / |moneyline|) + 1
            return (100.0 / abs(moneyline)) + 1.0
    
    @staticmethod
    def decimal_to_moneyline(decimal: float) -> int:
        """
        Convert decimal odds to American moneyline
        
        Args:
            decimal: Decimal odds (e.g., 2.50)
        
        Returns:
            American moneyline (e.g., +150)
        """
        if decimal >= 2.0:
            # Underdog: moneyline = (decimal - 1) * 100
            return int((decimal - 1.0) * 100)
        else:
            # Favorite: moneyline = -100 / (decimal - 1)
            return int(-100.0 / (decimal - 1.0))
    
    @staticmethod
    def implied_probability(moneyline: int) -> float:
        """
        Calculate implied probability from moneyline odds
        
        Args:
            moneyline: American odds
        
        Returns:
            Implied probability (0-1)
        """
        if moneyline > 0:
            # Positive odds
            return 100.0 / (moneyline + 100.0)
        else:
            # Negative odds
            return abs(moneyline) / (abs(moneyline) + 100.0)
    
    def calculate_ev(
        self,
        true_probability: float,
        moneyline: int
    ) -> Dict[str, float]:
        """
        Calculate Expected Value for a bet
        
        Args:
            true_probability: Our estimated win probability (0-1)
            moneyline: Sportsbook odds
        
        Returns:
            Dictionary with EV calculations
        
        Formula:
            EV = (p × profit) - ((1-p) × stake)
            EV = (p × (decimal_odds - 1)) - (1-p)
        """
        # Convert to decimal odds
        decimal_odds = self.moneyline_to_decimal(moneyline)
        
        # Calculate profit multiplier (how much you win per $1 bet)
        profit_multiplier = decimal_odds - 1.0
        
        # Calculate EV
        # EV = (probability of win × profit) - (probability of loss × stake)
        ev = (true_probability * profit_multiplier) - ((1 - true_probability) * 1.0)
        
        # Calculate EV percentage
        ev_percent = ev * 100.0
        
        # Calculate implied probability from odds
        implied_prob = self.implied_probability(moneyline)
        
        # Calculate edge (our probability - implied probability)
        edge = true_probability - implied_prob
        edge_percent = edge * 100.0
        
        return {
            'ev': ev,
            'ev_percent': ev_percent,
            'decimal_odds': decimal_odds,
            'profit_multiplier': profit_multiplier,
            'implied_probability': implied_prob,
            'true_probability': true_probability,
            'edge': edge,
            'edge_percent': edge_percent
        }
    
    def kelly_criterion(
        self,
        true_probability: float,
        decimal_odds: float,
        fraction: float = 0.25
    ) -> float:
        """
        Calculate Kelly Criterion bet size
        
        Args:
            true_probability: Our estimated win probability
            decimal_odds: Decimal odds
            fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
        
        Returns:
            Fraction of bankroll to bet (0-1)
        
        Formula:
            Kelly % = (p × (b+1) - 1) / b
            where b = decimal_odds - 1
        """
        b = decimal_odds - 1.0  # Profit multiplier
        p = true_probability
        
        # Full Kelly
        kelly = (p * (b + 1.0) - 1.0) / b
        
        # Apply fraction (quarter Kelly is common for risk management)
        kelly_fractional = kelly * fraction
        
        # Ensure non-negative
        kelly_fractional = max(0.0, kelly_fractional)
        
        # Cap at reasonable maximum (e.g., 10% of bankroll)
        kelly_fractional = min(kelly_fractional, 0.10)
        
        return kelly_fractional
    
    def evaluate_bet(
        self,
        team: str,
        true_probability: float,
        moneyline: int,
        min_ev_threshold: float = 0.05
    ) -> Dict:
        """
        Evaluate a single bet opportunity
        
        Args:
            team: Team name
            true_probability: Our estimated win probability
            moneyline: Sportsbook odds
            min_ev_threshold: Minimum EV to recommend (default 5%)
        
        Returns:
            Dictionary with bet evaluation
        """
        # Calculate EV
        ev_calc = self.calculate_ev(true_probability, moneyline)
        
        # Calculate Kelly bet size
        kelly_size = self.kelly_criterion(
            true_probability,
            ev_calc['decimal_odds'],
            fraction=0.25  # Quarter Kelly
        )
        
        # Determine if bet is recommended
        is_positive_ev = ev_calc['ev'] > 0
        meets_threshold = ev_calc['ev_percent'] >= (min_ev_threshold * 100)
        recommended = is_positive_ev and meets_threshold
        
        return {
            'team': team,
            'moneyline': moneyline,
            'true_probability': true_probability,
            'implied_probability': ev_calc['implied_probability'],
            'ev': ev_calc['ev'],
            'ev_percent': ev_calc['ev_percent'],
            'edge_percent': ev_calc['edge_percent'],
            'kelly_fraction': kelly_size,
            'recommended': recommended,
            'decimal_odds': ev_calc['decimal_odds']
        }
    
    def evaluate_game(
        self,
        home_team: str,
        away_team: str,
        home_win_prob: float,
        home_moneyline: int,
        away_moneyline: int,
        min_ev_threshold: float = 0.05
    ) -> Dict:
        """
        Evaluate both sides of a game
        
        Args:
            home_team: Home team name
            away_team: Away team name
            home_win_prob: Predicted home win probability
            home_moneyline: Home team odds
            away_moneyline: Away team odds
            min_ev_threshold: Minimum EV threshold
        
        Returns:
            Dictionary with both bets evaluated
        """
        away_win_prob = 1.0 - home_win_prob
        
        # Evaluate home bet
        home_bet = self.evaluate_bet(
            home_team,
            home_win_prob,
            home_moneyline,
            min_ev_threshold
        )
        
        # Evaluate away bet
        away_bet = self.evaluate_bet(
            away_team,
            away_win_prob,
            away_moneyline,
            min_ev_threshold
        )
        
        # Determine best bet
        best_bet = None
        if home_bet['recommended'] and away_bet['recommended']:
            # Both positive EV, pick higher EV
            best_bet = 'home' if home_bet['ev_percent'] > away_bet['ev_percent'] else 'away'
        elif home_bet['recommended']:
            best_bet = 'home'
        elif away_bet['recommended']:
            best_bet = 'away'
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_bet': home_bet,
            'away_bet': away_bet,
            'best_bet': best_bet,
            'has_positive_ev': best_bet is not None
        }


def example_usage():
    """Example usage of EV calculator"""
    print("=" * 70)
    print("💰 EV CALCULATOR - EXAMPLE USAGE")
    print("=" * 70)
    
    calc = EVCalculator()
    
    # Example 1: Underdog bet with positive EV
    print("\n📊 Example 1: Lakers +150 (Underdog)")
    print("-" * 70)
    
    lakers_prob = 0.50  # Our model says 50% chance
    lakers_odds = +150  # Sportsbook odds
    
    result = calc.evaluate_bet("Lakers", lakers_prob, lakers_odds)
    
    print(f"True Probability: {result['true_probability']:.1%}")
    print(f"Implied Probability: {result['implied_probability']:.1%}")
    print(f"Edge: {result['edge_percent']:+.1f}%")
    print(f"Expected Value: {result['ev_percent']:+.1f}%")
    print(f"Kelly Bet Size: {result['kelly_fraction']:.1%} of bankroll")
    print(f"Recommended: {'✅ YES' if result['recommended'] else '❌ NO'}")
    
    # Example 2: Favorite bet with negative EV
    print("\n📊 Example 2: Warriors -200 (Favorite)")
    print("-" * 70)
    
    warriors_prob = 0.65  # Our model says 65% chance
    warriors_odds = -200  # Sportsbook odds
    
    result = calc.evaluate_bet("Warriors", warriors_prob, warriors_odds)
    
    print(f"True Probability: {result['true_probability']:.1%}")
    print(f"Implied Probability: {result['implied_probability']:.1%}")
    print(f"Edge: {result['edge_percent']:+.1f}%")
    print(f"Expected Value: {result['ev_percent']:+.1f}%")
    print(f"Kelly Bet Size: {result['kelly_fraction']:.1%} of bankroll")
    print(f"Recommended: {'✅ YES' if result['recommended'] else '❌ NO'}")
    
    # Example 3: Full game evaluation
    print("\n📊 Example 3: Full Game - Celtics vs Heat")
    print("-" * 70)
    
    game_result = calc.evaluate_game(
        home_team="Celtics",
        away_team="Heat",
        home_win_prob=0.68,
        home_moneyline=-180,
        away_moneyline=+155,
        min_ev_threshold=0.05
    )
    
    print(f"\nHome: {game_result['home_team']} ({game_result['home_bet']['moneyline']:+d})")
    print(f"  EV: {game_result['home_bet']['ev_percent']:+.1f}%")
    print(f"  Recommended: {'✅' if game_result['home_bet']['recommended'] else '❌'}")
    
    print(f"\nAway: {game_result['away_team']} ({game_result['away_bet']['moneyline']:+d})")
    print(f"  EV: {game_result['away_bet']['ev_percent']:+.1f}%")
    print(f"  Recommended: {'✅' if game_result['away_bet']['recommended'] else '❌'}")
    
    if game_result['best_bet']:
        best_side = game_result['best_bet']
        best_bet_data = game_result[f'{best_side}_bet']
        print(f"\n🎯 Best Bet: {best_bet_data['team']} ({best_bet_data['moneyline']:+d})")
        print(f"   EV: {best_bet_data['ev_percent']:+.1f}%")
        print(f"   Kelly Size: {best_bet_data['kelly_fraction']:.1%}")
    else:
        print("\n⚠️  No positive EV bets found")
    
    print("\n" + "=" * 70)
    print("✅ EV CALCULATOR READY!")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()


