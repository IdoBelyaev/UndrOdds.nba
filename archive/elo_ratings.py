"""
Elo Rating System for NBA Teams
================================

This module implements an Elo rating system for NBA teams to predict
game outcomes and calculate win probabilities.

Elo Formula:
- Expected Score: E = 1 / (1 + 10^((Elo_opponent - Elo_team) / 400))
- Rating Update: Elo_new = Elo_old + K * (Actual - Expected)

M2 Phase 1: Elo Rating System
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class EloRatingSystem:
    """Elo rating system for NBA teams"""
    
    def __init__(
        self,
        k_factor: float = 20.0,
        home_advantage: float = 100.0,
        initial_rating: float = 1500.0,
        season_regression: float = 0.75
    ):
        """
        Initialize Elo rating system
        
        Args:
            k_factor: K-factor for rating updates (typical: 10-40)
            home_advantage: Home court advantage in Elo points (typical: 100)
            initial_rating: Starting Elo rating for all teams
            season_regression: Regression to mean between seasons (0.75 = regress 25%)
        """
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.initial_rating = initial_rating
        self.season_regression = season_regression
        
        # Team ratings: {team_name: elo_rating}
        self.ratings = {}
        
        # Rating history: {team_name: [(date, rating), ...]}
        self.rating_history = defaultdict(list)
        
        # Predictions: [(game_id, home_team, away_team, pred_home_win_prob, actual_home_win)]
        self.predictions = []
    
    def initialize_teams(self, teams: List[str]):
        """Initialize all teams with starting Elo rating"""
        for team in teams:
            self.ratings[team] = self.initial_rating
    
    def get_rating(self, team: str) -> float:
        """Get current Elo rating for a team"""
        if team not in self.ratings:
            self.ratings[team] = self.initial_rating
        return self.ratings[team]
    
    def expected_score(
        self,
        rating_a: float,
        rating_b: float,
        home_advantage: float = 0.0
    ) -> float:
        """
        Calculate expected score (win probability) for team A
        
        Args:
            rating_a: Elo rating of team A
            rating_b: Elo rating of team B
            home_advantage: Home court advantage for team A (if home)
        
        Returns:
            Expected score (probability of team A winning)
        """
        adjusted_rating_a = rating_a + home_advantage
        exponent = (rating_b - adjusted_rating_a) / 400.0
        expected = 1.0 / (1.0 + 10.0 ** exponent)
        return expected
    
    def update_ratings(
        self,
        team_a: str,
        team_b: str,
        score_a: float,
        is_team_a_home: bool = False
    ) -> Tuple[float, float]:
        """
        Update Elo ratings after a game
        
        Args:
            team_a: Name of team A
            team_b: Name of team B
            score_a: Actual score for team A (1 = win, 0 = loss)
            is_team_a_home: Whether team A is home team
        
        Returns:
            Tuple of (new_rating_a, new_rating_b)
        """
        # Get current ratings
        rating_a = self.get_rating(team_a)
        rating_b = self.get_rating(team_b)
        
        # Calculate home advantage
        home_adv = self.home_advantage if is_team_a_home else -self.home_advantage
        
        # Calculate expected scores
        expected_a = self.expected_score(rating_a, rating_b, home_adv)
        expected_b = 1.0 - expected_a
        
        # Calculate actual scores
        actual_a = score_a
        actual_b = 1.0 - score_a
        
        # Update ratings
        new_rating_a = rating_a + self.k_factor * (actual_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (actual_b - expected_b)
        
        # Store updated ratings
        self.ratings[team_a] = new_rating_a
        self.ratings[team_b] = new_rating_b
        
        return new_rating_a, new_rating_b
    
    def predict_game(
        self,
        home_team: str,
        away_team: str
    ) -> Dict[str, float]:
        """
        Predict game outcome
        
        Args:
            home_team: Name of home team
            away_team: Name of away team
        
        Returns:
            Dictionary with predictions:
            {
                'home_win_prob': float,
                'away_win_prob': float,
                'home_elo': float,
                'away_elo': float,
                'elo_diff': float
            }
        """
        home_elo = self.get_rating(home_team)
        away_elo = self.get_rating(away_team)
        
        # Calculate win probability (home team gets home advantage)
        home_win_prob = self.expected_score(home_elo, away_elo, self.home_advantage)
        away_win_prob = 1.0 - home_win_prob
        
        return {
            'home_win_prob': home_win_prob,
            'away_win_prob': away_win_prob,
            'home_elo': home_elo,
            'away_elo': away_elo,
            'elo_diff': home_elo - away_elo + self.home_advantage
        }
    
    def process_game(
        self,
        game_id: str,
        date: str,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        store_prediction: bool = True
    ):
        """
        Process a game: make prediction, then update ratings
        
        Args:
            game_id: Unique game identifier
            date: Game date
            home_team: Home team name
            away_team: Away team name
            home_score: Home team score
            away_score: Away team score
            store_prediction: Whether to store prediction for evaluation
        """
        # Make prediction before updating ratings
        prediction = self.predict_game(home_team, away_team)
        
        # Determine actual outcome
        home_won = 1.0 if home_score > away_score else 0.0
        
        # Store prediction if requested
        if store_prediction:
            self.predictions.append({
                'game_id': game_id,
                'date': date,
                'home_team': home_team,
                'away_team': away_team,
                'home_elo_before': prediction['home_elo'],
                'away_elo_before': prediction['away_elo'],
                'predicted_home_win_prob': prediction['home_win_prob'],
                'actual_home_win': home_won,
                'home_score': home_score,
                'away_score': away_score
            })
        
        # Update ratings
        new_home_elo, new_away_elo = self.update_ratings(
            home_team, away_team, home_won, is_team_a_home=True
        )
        
        # Store rating history
        self.rating_history[home_team].append((date, new_home_elo))
        self.rating_history[away_team].append((date, new_away_elo))
    
    def process_season(
        self,
        games: List[Dict],
        store_predictions: bool = True
    ):
        """
        Process an entire season of games
        
        Args:
            games: List of game dictionaries with keys:
                   game_id, date, home_team, away_team, home_score, away_score
            store_predictions: Whether to store predictions for evaluation
        """
        # Sort games by date
        sorted_games = sorted(games, key=lambda g: g['date'])
        
        print(f"\n📊 Processing {len(sorted_games)} games...")
        
        for i, game in enumerate(sorted_games):
            self.process_game(
                game_id=game['game_id'],
                date=game['date'],
                home_team=game['home_team'],
                away_team=game['away_team'],
                home_score=game['home_score'],
                away_score=game['away_score'],
                store_prediction=store_predictions
            )
            
            # Progress update
            if (i + 1) % 100 == 0:
                print(f"   Processed {i + 1}/{len(sorted_games)} games...")
        
        print(f"   ✅ Processed all {len(sorted_games)} games")
    
    def get_current_rankings(self, top_n: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        Get current team rankings by Elo rating
        
        Args:
            top_n: Number of top teams to return (None = all teams)
        
        Returns:
            List of (team_name, elo_rating) tuples, sorted by rating
        """
        rankings = sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
        
        if top_n:
            return rankings[:top_n]
        return rankings
    
    def calculate_accuracy(self) -> float:
        """
        Calculate prediction accuracy
        
        Returns:
            Accuracy (percentage of correct predictions)
        """
        if not self.predictions:
            return 0.0
        
        correct = sum(
            1 for p in self.predictions
            if (p['predicted_home_win_prob'] > 0.5 and p['actual_home_win'] == 1.0) or
               (p['predicted_home_win_prob'] <= 0.5 and p['actual_home_win'] == 0.0)
        )
        
        accuracy = correct / len(self.predictions)
        return accuracy
    
    def calculate_brier_score(self) -> float:
        """
        Calculate Brier score (lower is better, 0 = perfect)
        
        Brier Score = (1/N) * Σ(predicted_prob - actual_outcome)^2
        
        Returns:
            Brier score
        """
        if not self.predictions:
            return 1.0
        
        squared_errors = [
            (p['predicted_home_win_prob'] - p['actual_home_win']) ** 2
            for p in self.predictions
        ]
        
        brier_score = np.mean(squared_errors)
        return brier_score
    
    def calculate_log_loss(self) -> float:
        """
        Calculate log loss (lower is better)
        
        Returns:
            Log loss
        """
        if not self.predictions:
            return float('inf')
        
        epsilon = 1e-15  # Avoid log(0)
        
        log_losses = []
        for p in self.predictions:
            pred_prob = np.clip(p['predicted_home_win_prob'], epsilon, 1 - epsilon)
            actual = p['actual_home_win']
            
            log_loss = -(actual * np.log(pred_prob) + (1 - actual) * np.log(1 - pred_prob))
            log_losses.append(log_loss)
        
        return np.mean(log_losses)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get comprehensive performance metrics
        
        Returns:
            Dictionary of performance metrics
        """
        return {
            'accuracy': self.calculate_accuracy(),
            'brier_score': self.calculate_brier_score(),
            'log_loss': self.calculate_log_loss(),
            'total_predictions': len(self.predictions)
        }
    
    def save_ratings(self, filename: str = 'elo_ratings.json'):
        """Save current ratings to file"""
        data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'k_factor': self.k_factor,
                'home_advantage': self.home_advantage,
                'initial_rating': self.initial_rating,
                'total_teams': len(self.ratings)
            },
            'ratings': self.ratings,
            'performance': self.get_performance_metrics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Ratings saved to: {filename}")
    
    def save_predictions(self, filename: str = 'elo_predictions.json'):
        """Save all predictions to file"""
        data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'k_factor': self.k_factor,
                'home_advantage': self.home_advantage,
                'total_predictions': len(self.predictions)
            },
            'predictions': self.predictions,
            'performance': self.get_performance_metrics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Predictions saved to: {filename}")
    
    def print_summary(self):
        """Print summary of Elo system"""
        print("\n" + "=" * 70)
        print("📊 ELO RATING SYSTEM SUMMARY")
        print("=" * 70)
        
        print(f"\n⚙️  Configuration:")
        print(f"   K-factor: {self.k_factor}")
        print(f"   Home Advantage: {self.home_advantage} Elo points")
        print(f"   Initial Rating: {self.initial_rating}")
        
        print(f"\n📈 Current Ratings:")
        print(f"   Total Teams: {len(self.ratings)}")
        
        rankings = self.get_current_rankings(top_n=10)
        print(f"\n🏆 Top 10 Teams:")
        for i, (team, rating) in enumerate(rankings, 1):
            print(f"   {i:2d}. {team:25s} {rating:7.1f}")
        
        if self.predictions:
            metrics = self.get_performance_metrics()
            print(f"\n📊 Performance Metrics:")
            print(f"   Total Predictions: {metrics['total_predictions']}")
            print(f"   Accuracy: {metrics['accuracy']:.1%}")
            print(f"   Brier Score: {metrics['brier_score']:.4f}")
            print(f"   Log Loss: {metrics['log_loss']:.4f}")
        
        print("\n" + "=" * 70)


def load_game_data(filename: str = 'nba_game_data.json') -> List[Dict]:
    """Load game data from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    games = []
    for game in data['games']:
        games.append({
            'game_id': game['game_id'],
            'date': game['date'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'home_score': game['home_score'],
            'away_score': game['away_score']
        })
    
    return games


def main():
    """Run Elo rating system on NBA data"""
    print("=" * 70)
    print("🚀 NBA ELO RATING SYSTEM")
    print("=" * 70)
    
    # Load game data
    print("\n📂 Loading game data...")
    games = load_game_data('nba_game_data.json')
    print(f"   ✅ Loaded {len(games)} games")
    
    # Get unique teams
    teams = set()
    for game in games:
        teams.add(game['home_team'])
        teams.add(game['away_team'])
    
    print(f"   ✅ Found {len(teams)} unique teams")
    
    # Initialize Elo system
    print("\n⚙️  Initializing Elo system...")
    elo = EloRatingSystem(
        k_factor=20.0,
        home_advantage=100.0,
        initial_rating=1500.0
    )
    
    elo.initialize_teams(list(teams))
    print(f"   ✅ Initialized {len(teams)} teams at {elo.initial_rating} Elo")
    
    # Process all games
    elo.process_season(games, store_predictions=True)
    
    # Print summary
    elo.print_summary()
    
    # Save results
    elo.save_ratings('elo_ratings.json')
    elo.save_predictions('elo_predictions.json')
    
    print("\n✅ ELO RATING SYSTEM COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

