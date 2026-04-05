"""
Feature Engineering for NBA Game Prediction
============================================

This module creates features for logistic regression model including:
- Elo rating difference
- Recent form (last 10 games)
- Rest days difference
- Injury impact
- Home court advantage

M2 Phase 2: Feature Engineering
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict


class FeatureEngineer:
    """Feature engineering for NBA game prediction"""
    
    def __init__(self):
        """Initialize feature engineer"""
        self.games_data = None
        self.team_data = None
        self.injury_data = None
        self.elo_data = None
        
        # Track recent games for each team
        self.team_recent_games = defaultdict(list)
        
        # Track last game date for rest calculation
        self.team_last_game = {}
    
    def load_data(self):
        """Load all necessary data"""
        print("\n📂 Loading data...")
        
        # Load game data
        with open('nba_game_data.json', 'r') as f:
            self.games_data = json.load(f)
        print(f"   ✅ Loaded {len(self.games_data['games'])} games")
        
        # Load team data
        with open('nba_team_data.json', 'r') as f:
            self.team_data = json.load(f)
        print(f"   ✅ Loaded {len(self.team_data['teams'])} teams")
        
        # Load injury data
        with open('nba_injury_data.json', 'r') as f:
            self.injury_data = json.load(f)
        print(f"   ✅ Loaded {len(self.injury_data['injuries'])} player injury records")
        
        # Load Elo predictions (has Elo ratings before each game)
        with open('elo_predictions_calibrated.json', 'r') as f:
            self.elo_data = json.load(f)
        print(f"   ✅ Loaded {len(self.elo_data['predictions'])} Elo predictions")
    
    def calculate_rest_days(self, team: str, game_date: str) -> int:
        """
        Calculate days of rest since last game
        
        Args:
            team: Team name
            game_date: Current game date (YYYY-MM-DD HH:MM:SS)
        
        Returns:
            Number of rest days (0 = back-to-back)
        """
        current_date = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S').date()
        
        if team not in self.team_last_game:
            # First game of season
            return 3  # Assume well-rested
        
        last_game_date = self.team_last_game[team]
        rest_days = (current_date - last_game_date).days - 1
        
        return max(0, rest_days)  # 0 = back-to-back, 1 = 1 day rest, etc.
    
    def calculate_recent_form(self, team: str, n_games: int = 10) -> float:
        """
        Calculate recent win percentage for last N games
        
        Args:
            team: Team name
            n_games: Number of recent games to consider
        
        Returns:
            Win percentage (0.0 to 1.0)
        """
        if team not in self.team_recent_games:
            return 0.5  # No history, assume average
        
        recent_games = self.team_recent_games[team][-n_games:]
        
        if not recent_games:
            return 0.5
        
        wins = sum(recent_games)
        win_pct = wins / len(recent_games)
        
        return win_pct
    
    def calculate_injury_impact(self, team: str) -> float:
        """
        Calculate injury impact score for a team
        
        Higher score = more injuries = worse for team
        
        Args:
            team: Team name
        
        Returns:
            Injury impact score (0.0 = healthy, higher = more injuries)
        """
        # Get injuries for this team
        team_injuries = [
            inj for inj in self.injury_data['injuries']
            if inj['team_name'] == team or inj['team_name'] in team
        ]
        
        if not team_injuries:
            return 0.0  # No injuries
        
        # Count players by injury status
        injury_counts = {
            'OUT': 0,
            'DOUBTFUL': 0,
            'QUESTIONABLE': 0,
            'PROBABLE': 0
        }
        
        for inj in team_injuries:
            status = inj.get('injury_status', 'HEALTHY')
            if status in injury_counts:
                injury_counts[status] += 1
        
        # Weight different injury statuses
        # OUT = most impactful, PROBABLE = least impactful
        impact_score = (
            injury_counts['OUT'] * 1.0 +
            injury_counts['DOUBTFUL'] * 0.7 +
            injury_counts['QUESTIONABLE'] * 0.4 +
            injury_counts['PROBABLE'] * 0.1
        )
        
        return impact_score
    
    def get_elo_ratings(self, game_id: str) -> Tuple[float, float]:
        """
        Get Elo ratings before a specific game
        
        Args:
            game_id: Game ID
        
        Returns:
            (home_elo, away_elo)
        """
        # Find the Elo prediction for this game
        for pred in self.elo_data['predictions']:
            if pred['game_id'] == game_id:
                return pred['home_elo_before'], pred['away_elo_before']
        
        # Default to average if not found
        return 1500.0, 1500.0
    
    def create_features_for_game(
        self,
        game: Dict,
        include_target: bool = True
    ) -> Dict:
        """
        Create features for a single game
        
        Args:
            game: Game dictionary
            include_target: Whether to include target variable (for training)
        
        Returns:
            Dictionary of features
        """
        game_id = game['game_id']
        game_date = game['date']
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Get Elo ratings
        home_elo, away_elo = self.get_elo_ratings(game_id)
        
        # Calculate rest days
        home_rest = self.calculate_rest_days(home_team, game_date)
        away_rest = self.calculate_rest_days(away_team, game_date)
        
        # Calculate recent form
        home_form = self.calculate_recent_form(home_team, n_games=10)
        away_form = self.calculate_recent_form(away_team, n_games=10)
        
        # Calculate injury impact
        home_injuries = self.calculate_injury_impact(home_team)
        away_injuries = self.calculate_injury_impact(away_team)
        
        # Create features
        features = {
            'game_id': game_id,
            'date': game_date,
            'home_team': home_team,
            'away_team': away_team,
            
            # Elo features
            'home_elo': home_elo,
            'away_elo': away_elo,
            'elo_diff': home_elo - away_elo,  # Positive = home team stronger
            
            # Rest features
            'home_rest_days': home_rest,
            'away_rest_days': away_rest,
            'rest_diff': home_rest - away_rest,  # Positive = home team more rested
            
            # Form features
            'home_recent_win_pct': home_form,
            'away_recent_win_pct': away_form,
            'form_diff': home_form - away_form,  # Positive = home team better form
            
            # Injury features
            'home_injury_impact': home_injuries,
            'away_injury_impact': away_injuries,
            'injury_diff': away_injuries - home_injuries,  # Positive = away team more injured
            
            # Home court advantage (constant)
            'home_court': 1.0
        }
        
        # Add target variable if requested
        if include_target:
            features['home_win'] = 1 if game['home_score'] > game['away_score'] else 0
            features['home_score'] = game['home_score']
            features['away_score'] = game['away_score']
        
        # Update tracking for next games
        current_date = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S').date()
        self.team_last_game[home_team] = current_date
        self.team_last_game[away_team] = current_date
        
        # Update recent games
        home_won = 1 if game['home_score'] > game['away_score'] else 0
        self.team_recent_games[home_team].append(home_won)
        self.team_recent_games[away_team].append(1 - home_won)
        
        return features
    
    def create_feature_dataset(self) -> pd.DataFrame:
        """
        Create feature dataset for all games
        
        Returns:
            DataFrame with features for all games
        """
        print("\n🔧 Creating feature dataset...")
        
        # Sort games by date
        games = sorted(self.games_data['games'], key=lambda g: g['date'])
        
        # Create features for each game
        all_features = []
        
        for i, game in enumerate(games):
            features = self.create_features_for_game(game, include_target=True)
            all_features.append(features)
            
            if (i + 1) % 200 == 0:
                print(f"   Processed {i + 1}/{len(games)} games...")
        
        print(f"   ✅ Created features for {len(all_features)} games")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_features)
        
        return df
    
    def save_features(self, df: pd.DataFrame, filename: str = 'nba_features.csv'):
        """Save features to CSV"""
        df.to_csv(filename, index=False)
        print(f"\n💾 Features saved to: {filename}")
    
    def print_feature_summary(self, df: pd.DataFrame):
        """Print summary of features"""
        print("\n" + "=" * 70)
        print("📊 FEATURE SUMMARY")
        print("=" * 70)
        
        print(f"\n📈 Dataset Shape: {df.shape[0]} games × {df.shape[1]} features")
        
        print("\n📋 Feature List:")
        feature_cols = [col for col in df.columns if col not in 
                       ['game_id', 'date', 'home_team', 'away_team', 'home_win', 
                        'home_score', 'away_score']]
        
        for col in feature_cols:
            print(f"   • {col}")
        
        print(f"\n🎯 Target Variable: home_win")
        print(f"   Home wins: {df['home_win'].sum()} ({df['home_win'].mean():.1%})")
        print(f"   Away wins: {len(df) - df['home_win'].sum()} ({(1-df['home_win'].mean()):.1%})")
        
        print("\n📊 Feature Statistics:")
        numeric_features = ['elo_diff', 'rest_diff', 'form_diff', 'injury_diff']
        
        for feat in numeric_features:
            if feat in df.columns:
                print(f"\n   {feat}:")
                print(f"      Mean: {df[feat].mean():.3f}")
                print(f"      Std:  {df[feat].std():.3f}")
                print(f"      Min:  {df[feat].min():.3f}")
                print(f"      Max:  {df[feat].max():.3f}")
        
        print("\n" + "=" * 70)


def main():
    """Run feature engineering"""
    print("=" * 70)
    print("🔧 NBA FEATURE ENGINEERING")
    print("=" * 70)
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    
    # Load data
    engineer.load_data()
    
    # Create features
    df = engineer.create_feature_dataset()
    
    # Print summary
    engineer.print_feature_summary(df)
    
    # Save features
    engineer.save_features(df, 'nba_features.csv')
    
    print("\n✅ FEATURE ENGINEERING COMPLETE!")
    print("=" * 70)
    
    return df


if __name__ == "__main__":
    main()

