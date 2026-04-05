"""
Betting Recommendations System
===============================

Generate betting recommendations by:
- Loading calibrated model
- Predicting game outcomes
- Calculating EV for all bets
- Filtering and ranking opportunities
- Generating bet slips

M2 Phase 3: Betting Recommendations
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from ev_calculator import EVCalculator
from feature_engineering import FeatureEngineer


class BettingRecommendationSystem:
    """Generate betting recommendations from model predictions"""
    
    def __init__(
        self,
        model_path: str = 'nba_model_calibrated.pkl',
        min_ev_threshold: float = 0.05
    ):
        """
        Initialize betting recommendation system
        
        Args:
            model_path: Path to calibrated model
            min_ev_threshold: Minimum EV to recommend (default 5%)
        """
        self.model_path = model_path
        self.min_ev_threshold = min_ev_threshold
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
        print(f"   Features: {', '.join(self.feature_names)}")
    
    def predict_game(self, features: Dict) -> Dict:
        """
        Predict outcome for a single game
        
        Args:
            features: Dictionary of features
        
        Returns:
            Dictionary with predictions
        """
        # Convert features to array
        X = np.array([[features[feat] for feat in self.feature_names]])
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        home_win_prob = self.model.predict_proba(X_scaled)[0, 1]
        away_win_prob = 1.0 - home_win_prob
        
        return {
            'home_win_prob': home_win_prob,
            'away_win_prob': away_win_prob
        }
    
    def generate_recommendations(
        self,
        games: List[Dict],
        odds_data: List[Dict]
    ) -> List[Dict]:
        """
        Generate betting recommendations for multiple games
        
        Args:
            games: List of game dictionaries with features
            odds_data: List of odds dictionaries with moneylines
        
        Returns:
            List of recommendations sorted by EV
        """
        print(f"\n🔍 Analyzing {len(games)} games...")
        
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
                print(f"   ⚠️  No odds found for {game['home_team']} vs {game['away_team']}")
                continue
            
            # Get prediction
            prediction = self.predict_game(game)
            
            # Evaluate game
            game_eval = self.ev_calc.evaluate_game(
                home_team=game['home_team'],
                away_team=game['away_team'],
                home_win_prob=prediction['home_win_prob'],
                home_moneyline=game_odds['home_moneyline'],
                away_moneyline=game_odds['away_moneyline'],
                min_ev_threshold=self.min_ev_threshold
            )
            
            # Add game info
            game_eval['game_date'] = game.get('date', 'Unknown')
            game_eval['game_id'] = game.get('game_id', 'Unknown')
            
            recommendations.append(game_eval)
        
        # Filter for positive EV
        positive_ev_recs = [r for r in recommendations if r['has_positive_ev']]
        
        print(f"   ✅ Found {len(positive_ev_recs)} positive EV opportunities")
        
        # Sort by EV (descending)
        positive_ev_recs.sort(
            key=lambda x: x[f"{x['best_bet']}_bet"]['ev_percent'] if x['best_bet'] else 0,
            reverse=True
        )
        
        return positive_ev_recs
    
    def print_recommendations(self, recommendations: List[Dict]):
        """Print formatted betting recommendations"""
        print("\n" + "=" * 80)
        print("💰 BETTING RECOMMENDATIONS")
        print("=" * 80)
        
        if not recommendations:
            print("\n⚠️  No positive EV bets found")
            print("   Try lowering the minimum EV threshold or wait for better opportunities.")
            return
        
        print(f"\n🎯 Found {len(recommendations)} Positive EV Bets")
        print(f"   Minimum EV Threshold: {self.min_ev_threshold * 100:.0f}%")
        print()
        
        for i, rec in enumerate(recommendations, 1):
            best_side = rec['best_bet']
            bet = rec[f'{best_side}_bet']
            
            print(f"{'=' * 80}")
            print(f"BET #{i}")
            print(f"{'=' * 80}")
            print(f"🏀 Game: {rec['home_team']} vs {rec['away_team']}")
            print(f"📅 Date: {rec['game_date']}")
            print()
            print(f"🎯 RECOMMENDED BET: {bet['team']} ({bet['moneyline']:+d})")
            print(f"   Win Probability (Our Model): {bet['true_probability']:.1%}")
            print(f"   Implied Probability (Odds): {bet['implied_probability']:.1%}")
            print(f"   Edge: {bet['edge_percent']:+.1f}%")
            print(f"   Expected Value: {bet['ev_percent']:+.1f}%")
            print(f"   Kelly Bet Size: {bet['kelly_fraction']:.1%} of bankroll")
            print()
            
            # Show both sides for comparison
            home_bet = rec['home_bet']
            away_bet = rec['away_bet']
            
            print(f"📊 Full Game Analysis:")
            print(f"   Home: {rec['home_team']} ({home_bet['moneyline']:+d})")
            print(f"      Win Prob: {home_bet['true_probability']:.1%} | EV: {home_bet['ev_percent']:+.1f}%")
            print(f"   Away: {rec['away_team']} ({away_bet['moneyline']:+d})")
            print(f"      Win Prob: {away_bet['true_probability']:.1%} | EV: {away_bet['ev_percent']:+.1f}%")
            print()
        
        print("=" * 80)
        
        # Summary
        total_ev = sum(
            rec[f"{rec['best_bet']}_bet"]['ev_percent'] 
            for rec in recommendations
        )
        avg_ev = total_ev / len(recommendations)
        
        print(f"\n📈 SUMMARY")
        print(f"   Total Bets: {len(recommendations)}")
        print(f"   Average EV: {avg_ev:.1f}%")
        print(f"   Total EV: {total_ev:.1f}%")
        print()
        print("=" * 80)
    
    def save_recommendations(
        self,
        recommendations: List[Dict],
        filename: str = 'betting_recommendations.json'
    ):
        """Save recommendations to JSON file"""
        
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        output = {
            'timestamp': datetime.now().isoformat(),
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
    print("🎯 BETTING RECOMMENDATIONS - EXAMPLE")
    print("=" * 80)
    
    # Initialize system
    system = BettingRecommendationSystem(
        model_path='nba_model_calibrated.pkl',
        min_ev_threshold=0.05  # 5% minimum EV
    )
    
    # Sample games (with features)
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
    system.save_recommendations(recommendations, 'sample_recommendations.json')
    
    print("\n✅ EXAMPLE COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    example_usage()

