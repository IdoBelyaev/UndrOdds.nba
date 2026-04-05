"""
Real-time Updates
=================

Update predictions with latest data:
- Refresh injury data before games
- Update Elo ratings after each game
- Recalculate predictions if odds change
- Live game status tracking

M3 Phase 3: Real-time Updates
"""

import json
import pickle
import numpy as np
from datetime import datetime, date
from typing import Dict, List
from feature_engineering import FeatureEngineer


class RealtimeUpdater:
    """Handle real-time updates for predictions"""
    
    def __init__(self):
        """Initialize real-time updater"""
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load calibrated model"""
        try:
            with open('nba_model_calibrated.pkl', 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['calibrated_model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
            print("✅ Model loaded")
        except FileNotFoundError:
            print("❌ Model not found")
    
    def refresh_injury_data(self) -> bool:
        """
        Refresh injury data before games
        
        Returns:
            True if successful
        """
        print("\n🏥 Refreshing injury data...")
        
        try:
            import subprocess
            result = subprocess.run(
                ['python', 'injury_data_fetch.py'],
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Injury data refreshed")
                return True
            else:
                print("⚠️ Injury data refresh had issues")
                return False
        except Exception as e:
            print(f"❌ Error refreshing injury data: {e}")
            return False
    
    def update_elo_for_game(
        self,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int
    ) -> Dict:
        """
        Update Elo ratings after a game completes
        
        Args:
            home_team: Home team name
            away_team: Away team name
            home_score: Home team score
            away_score: Away team score
        
        Returns:
            Dictionary with updated ratings
        """
        print(f"\n🔄 Updating Elo for {home_team} vs {away_team}...")
        
        # Load current Elo ratings
        try:
            with open('elo_ratings_calibrated.json', 'r') as f:
                data = json.load(f)
                ratings = data['ratings']
        except FileNotFoundError:
            print("❌ Elo ratings not found")
            return {}
        
        # Get current ratings
        home_elo = ratings.get(home_team, 1500.0)
        away_elo = ratings.get(away_team, 1500.0)
        
        # Calculate expected scores (K=30, HA=50)
        k_factor = 30.0
        home_advantage = 50.0
        
        expected_home = 1.0 / (1.0 + 10.0 ** ((away_elo - (home_elo + home_advantage)) / 400.0))
        
        # Actual score
        actual_home = 1.0 if home_score > away_score else 0.0
        
        # Update ratings
        new_home_elo = home_elo + k_factor * (actual_home - expected_home)
        new_away_elo = away_elo + k_factor * ((1.0 - actual_home) - (1.0 - expected_home))
        
        # Update in memory
        ratings[home_team] = new_home_elo
        ratings[away_team] = new_away_elo
        
        # Save updated ratings
        data['ratings'] = ratings
        data['last_updated'] = datetime.now().isoformat()
        
        with open('elo_ratings_calibrated.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Elo updated:")
        print(f"   {home_team}: {home_elo:.1f} → {new_home_elo:.1f}")
        print(f"   {away_team}: {away_elo:.1f} → {new_away_elo:.1f}")
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_elo_old': home_elo,
            'home_elo_new': new_home_elo,
            'away_elo_old': away_elo,
            'away_elo_new': new_away_elo
        }
    
    def recalculate_predictions(
        self,
        games: List[Dict]
    ) -> List[Dict]:
        """
        Recalculate predictions for games
        
        Args:
            games: List of game dictionaries with features
        
        Returns:
            List of updated predictions
        """
        print(f"\n🔄 Recalculating predictions for {len(games)} games...")
        
        if not self.model:
            print("❌ Model not loaded")
            return []
        
        predictions = []
        
        for game in games:
            # Extract features
            X = np.array([[game[feat] for feat in self.feature_names]])
            X_scaled = self.scaler.transform(X)
            
            # Predict
            home_win_prob = self.model.predict_proba(X_scaled)[0, 1]
            
            predictions.append({
                'game': f"{game['home_team']} vs {game['away_team']}",
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'home_win_prob': home_win_prob,
                'away_win_prob': 1.0 - home_win_prob,
                'timestamp': datetime.now().isoformat()
            })
        
        print(f"✅ Predictions recalculated")
        
        return predictions
    
    def check_game_status(self, game_date: str) -> List[Dict]:
        """
        Check status of games for a given date
        
        Args:
            game_date: Date in YYYY-MM-DD format
        
        Returns:
            List of games with status
        """
        print(f"\n🔍 Checking game status for {game_date}...")
        
        # Load game data
        try:
            with open('nba_game_data.json', 'r') as f:
                data = json.load(f)
                games = data['games']
        except FileNotFoundError:
            print("❌ Game data not found")
            return []
        
        # Filter games for date
        date_games = [
            g for g in games
            if g['date'].startswith(game_date)
        ]
        
        print(f"✅ Found {len(date_games)} games for {game_date}")
        
        return date_games


def main():
    """Run real-time updates example"""
    print("=" * 70)
    print("🔄 REAL-TIME UPDATES")
    print("=" * 70)
    
    # Initialize updater
    updater = RealtimeUpdater()
    
    # Example: Refresh injury data
    updater.refresh_injury_data()
    
    # Example: Update Elo after a game
    print("\n📊 Example: Update Elo after game...")
    updater.update_elo_for_game(
        home_team='Lakers',
        away_team='Warriors',
        home_score=112,
        away_score=108
    )
    
    # Example: Check game status
    updater.check_game_status('2024-10-22')
    
    print("\n✅ REAL-TIME UPDATES COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

