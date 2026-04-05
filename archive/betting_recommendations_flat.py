"""
Betting Recommendations System - FLAT BETTING
==============================================

Generate betting recommendations with FLAT BETTING:
- Bet the same amount on every game
- No Kelly Criterion (simpler, safer)
- More predictable bankroll management

M2 Phase 3: Betting Recommendations (Flat Betting Version)
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List
from ev_calculator import EVCalculator


class FlatBettingRecommendationSystem:
    """Generate betting recommendations with flat betting"""
    
    def __init__(
        self,
        model_path: str = 'nba_model_calibrated.pkl',
        min_ev_threshold: float = 0.05,
        flat_bet_amount: float = 20.0
    ):
        """
        Initialize flat betting recommendation system
        
        Args:
            model_path: Path to calibrated model
            min_ev_threshold: Minimum EV to recommend (default 5%)
            flat_bet_amount: Fixed bet amount per game (default $20)
        """
        self.model_path = model_path
        self.min_ev_threshold = min_ev_threshold
        self.flat_bet_amount = flat_bet_amount
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.ev_calc = EVCalculator()
        
        # Load model
        self.load_model()
    
    def load_model(self):
        """Load calibrated model"""
        print(f"\n📂 Loading model from {self.model_path}...")
        
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['calibrated_model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        
        print(f"   ✅ Model loaded successfully")
    
    def predict_game(self, features: Dict) -> Dict:
        """Predict outcome for a single game"""
        X = np.array([[features[feat] for feat in self.feature_names]])
        X_scaled = self.scaler.transform(X)
        home_win_prob = self.model.predict_proba(X_scaled)[0, 1]
        
        return {
            'home_win_prob': home_win_prob,
            'away_win_prob': 1.0 - home_win_prob
        }
    
    def evaluate_bet_flat(
        self,
        team: str,
        true_probability: float,
        moneyline: int
    ) -> Dict:
        """
        Evaluate a bet with flat betting
        
        Args:
            team: Team name
            true_probability: Our estimated win probability
            moneyline: Sportsbook odds
        
        Returns:
            Dictionary with bet evaluation
        """
        # Calculate EV
        ev_calc = self.ev_calc.calculate_ev(true_probability, moneyline)
        
        # Determine if bet is recommended
        is_positive_ev = ev_calc['ev'] > 0
        meets_threshold = ev_calc['ev_percent'] >= (self.min_ev_threshold * 100)
        recommended = is_positive_ev and meets_threshold
        
        # Calculate expected profit with flat betting
        expected_profit = self.flat_bet_amount * ev_calc['ev']
        
        return {
            'team': team,
            'moneyline': moneyline,
            'true_probability': true_probability,
            'implied_probability': ev_calc['implied_probability'],
            'ev': ev_calc['ev'],
            'ev_percent': ev_calc['ev_percent'],
            'edge_percent': ev_calc['edge_percent'],
            'bet_amount': self.flat_bet_amount,
            'expected_profit': expected_profit,
            'recommended': recommended,
            'decimal_odds': ev_calc['decimal_odds']
        }
    
    def generate_recommendations(
        self,
        games: List[Dict],
        odds_data: List[Dict]
    ) -> List[Dict]:
        """Generate betting recommendations for multiple games"""
        print(f"\n🔍 Analyzing {len(games)} games...")
        print(f"   Flat Bet Amount: ${self.flat_bet_amount:.2f} per game")
        print()
        
        recommendations = []
        
        for game in games:
            # Find odds for this game
            game_odds = None
            for odds in odds_data:
                if (odds['home_team'] == game['home_team'] and 
                    odds['away_team'] == game['away_team']):
                    game_odds = odds
                    break
            
            if not game_odds:
                continue
            
            # Get prediction
            prediction = self.predict_game(game)
            
            # Evaluate both sides
            home_bet = self.evaluate_bet_flat(
                game['home_team'],
                prediction['home_win_prob'],
                game_odds['home_moneyline']
            )
            
            away_bet = self.evaluate_bet_flat(
                game['away_team'],
                prediction['away_win_prob'],
                game_odds['away_moneyline']
            )
            
            # Determine best bet
            best_bet = None
            if home_bet['recommended'] and away_bet['recommended']:
                best_bet = 'home' if home_bet['ev_percent'] > away_bet['ev_percent'] else 'away'
            elif home_bet['recommended']:
                best_bet = 'home'
            elif away_bet['recommended']:
                best_bet = 'away'
            
            if best_bet:
                game_rec = {
                    'game_date': game.get('date', 'Unknown'),
                    'game_id': game.get('game_id', 'Unknown'),
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'home_bet': home_bet,
                    'away_bet': away_bet,
                    'best_bet': best_bet,
                    'has_positive_ev': True
                }
                recommendations.append(game_rec)
        
        print(f"   ✅ Found {len(recommendations)} positive EV opportunities")
        
        # Sort by EV
        recommendations.sort(
            key=lambda x: x[f"{x['best_bet']}_bet"]['ev_percent'],
            reverse=True
        )
        
        return recommendations
    
    def print_recommendations(self, recommendations: List[Dict]):
        """Print formatted betting recommendations"""
        print("\n" + "=" * 80)
        print("💰 FLAT BETTING RECOMMENDATIONS")
        print("=" * 80)
        
        if not recommendations:
            print("\n⚠️  No positive EV bets found")
            return
        
        print(f"\n🎯 Found {len(recommendations)} Positive EV Bets")
        print(f"   Flat Bet Amount: ${self.flat_bet_amount:.2f} per game")
        print(f"   Min EV Threshold: {self.min_ev_threshold * 100:.0f}%")
        print()
        
        total_wagered = 0
        total_expected_profit = 0
        
        for i, rec in enumerate(recommendations, 1):
            best_side = rec['best_bet']
            bet = rec[f'{best_side}_bet']
            
            total_wagered += bet['bet_amount']
            total_expected_profit += bet['expected_profit']
            
            print(f"{'=' * 80}")
            print(f"BET #{i}")
            print(f"{'=' * 80}")
            print(f"🏀 Game: {rec['home_team']} vs {rec['away_team']}")
            print(f"📅 Date: {rec['game_date']}")
            print()
            print(f"🎯 RECOMMENDED BET: {bet['team']} ({bet['moneyline']:+d})")
            print(f"   Bet Amount: ${bet['bet_amount']:.2f} (FLAT)")
            print(f"   Win Probability: {bet['true_probability']:.1%}")
            print(f"   Expected Value: {bet['ev_percent']:+.1f}%")
            print(f"   Expected Profit: ${bet['expected_profit']:+.2f}")
            print()
        
        print("=" * 80)
        
        # Summary
        avg_ev = np.mean([
            rec[f"{rec['best_bet']}_bet"]['ev_percent'] 
            for rec in recommendations
        ])
        
        print(f"\n📈 FLAT BETTING SUMMARY")
        print(f"   Total Bets: {len(recommendations)}")
        print(f"   Total Wagered: ${total_wagered:.2f}")
        print(f"   Expected Profit: ${total_expected_profit:+.2f}")
        print(f"   Expected ROI: {(total_expected_profit/total_wagered)*100:+.1f}%")
        print(f"   Average EV per Bet: {avg_ev:.1f}%")
        print()
        print("=" * 80)
    
    def save_recommendations(
        self,
        recommendations: List[Dict],
        filename: str = 'flat_betting_recommendations.json'
    ):
        """Save recommendations to JSON file"""
        
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'betting_strategy': 'FLAT',
            'flat_bet_amount': float(self.flat_bet_amount),
            'min_ev_threshold': float(self.min_ev_threshold),
            'total_recommendations': int(len(recommendations)),
            'recommendations': convert_types(recommendations)
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Recommendations saved to: {filename}")


def example_usage():
    """Example usage with sample data"""
    print("=" * 80)
    print("🎯 FLAT BETTING RECOMMENDATIONS - EXAMPLE")
    print("=" * 80)
    
    # Initialize system with $20 flat bets
    system = FlatBettingRecommendationSystem(
        model_path='nba_model_calibrated.pkl',
        min_ev_threshold=0.05,
        flat_bet_amount=20.0
    )
    
    # Sample games
    sample_games = [
        {
            'game_id': 'sample_001',
            'date': '2025-10-20',
            'home_team': 'Lakers',
            'away_team': 'Warriors',
            'elo_diff': 50.0,
            'rest_diff': 0.0,
            'form_diff': 0.1,
            'injury_diff': 0.0,
            'home_court': 1.0
        },
        {
            'game_id': 'sample_002',
            'date': '2025-10-20',
            'home_team': 'Celtics',
            'away_team': 'Heat',
            'elo_diff': 100.0,
            'rest_diff': 1.0,
            'form_diff': 0.2,
            'injury_diff': 0.5,
            'home_court': 1.0
        }
    ]
    
    # Sample odds
    sample_odds = [
        {
            'home_team': 'Lakers',
            'away_team': 'Warriors',
            'home_moneyline': +120,
            'away_moneyline': -140
        },
        {
            'home_team': 'Celtics',
            'away_team': 'Heat',
            'home_moneyline': -180,
            'away_moneyline': +155
        }
    ]
    
    # Generate recommendations
    recommendations = system.generate_recommendations(sample_games, sample_odds)
    
    # Print recommendations
    system.print_recommendations(recommendations)
    
    # Save recommendations
    system.save_recommendations(recommendations)
    
    print("\n✅ FLAT BETTING EXAMPLE COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    example_usage()

