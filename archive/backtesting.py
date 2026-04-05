"""
Backtesting Framework
=====================

Simulate historical betting performance:
- Historical bet simulation
- ROI calculation
- Win rate analysis
- Drawdown analysis
- Sharpe ratio
- Kelly Criterion performance

M2 Phase 4: Backtesting
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List
from ev_calculator import EVCalculator


class BettingBacktest:
    """Backtest betting strategy on historical data"""
    
    def __init__(
        self,
        starting_bankroll: float = 10000.0,
        min_ev_threshold: float = 0.05,
        use_kelly: bool = True,
        kelly_fraction: float = 0.25
    ):
        """
        Initialize backtesting system
        
        Args:
            starting_bankroll: Starting bankroll in dollars
            min_ev_threshold: Minimum EV to place bet (5% default)
            use_kelly: Whether to use Kelly Criterion sizing
            kelly_fraction: Fraction of Kelly to use (0.25 = quarter Kelly)
        """
        self.starting_bankroll = starting_bankroll
        self.min_ev_threshold = min_ev_threshold
        self.use_kelly = use_kelly
        self.kelly_fraction = kelly_fraction
        
        self.ev_calc = EVCalculator()
        
        # Track results
        self.bets = []
        self.bankroll_history = [starting_bankroll]
        self.current_bankroll = starting_bankroll
    
    def simulate_bet(
        self,
        team: str,
        true_probability: float,
        moneyline: int,
        actual_win: bool
    ) -> Dict:
        """
        Simulate a single bet
        
        Args:
            team: Team name
            true_probability: Our estimated win probability
            moneyline: Sportsbook odds
            actual_win: Whether the team actually won
        
        Returns:
            Dictionary with bet results
        """
        # Calculate EV
        ev_result = self.ev_calc.calculate_ev(true_probability, moneyline)
        
        # Check if bet meets threshold
        if ev_result['ev_percent'] < (self.min_ev_threshold * 100):
            return None  # Skip bet
        
        # Determine bet size
        if self.use_kelly:
            kelly_size = self.ev_calc.kelly_criterion(
                true_probability,
                ev_result['decimal_odds'],
                fraction=self.kelly_fraction
            )
            bet_amount = self.current_bankroll * kelly_size
        else:
            # Flat betting (1% of bankroll)
            bet_amount = self.current_bankroll * 0.01
        
        # Calculate profit/loss
        if actual_win:
            # Win: profit = bet_amount * (decimal_odds - 1)
            profit = bet_amount * ev_result['profit_multiplier']
        else:
            # Loss: lose the bet amount
            profit = -bet_amount
        
        # Update bankroll
        self.current_bankroll += profit
        self.bankroll_history.append(self.current_bankroll)
        
        # Record bet
        bet_record = {
            'team': team,
            'moneyline': moneyline,
            'true_probability': true_probability,
            'implied_probability': ev_result['implied_probability'],
            'ev_percent': ev_result['ev_percent'],
            'bet_amount': bet_amount,
            'actual_win': actual_win,
            'profit': profit,
            'bankroll_after': self.current_bankroll
        }
        
        self.bets.append(bet_record)
        
        return bet_record
    
    def run_backtest(
        self,
        predictions: pd.DataFrame,
        odds_data: pd.DataFrame = None
    ) -> Dict:
        """
        Run backtest on historical predictions
        
        Args:
            predictions: DataFrame with predictions and actual outcomes
            odds_data: DataFrame with historical odds (if None, use synthetic)
        
        Returns:
            Dictionary with backtest results
        """
        print(f"\n🔄 Running backtest...")
        print(f"   Starting Bankroll: ${self.starting_bankroll:,.2f}")
        print(f"   Min EV Threshold: {self.min_ev_threshold * 100:.0f}%")
        print(f"   Kelly Sizing: {'Yes' if self.use_kelly else 'No'} ({self.kelly_fraction * 100:.0f}% Kelly)")
        print()
        
        # For this backtest, we'll use synthetic odds based on Elo predictions
        # In production, you'd use actual historical odds
        print("   ⚠️  Using synthetic odds (Elo-based) for backtest")
        print("   💡 In production, use actual historical sportsbook odds")
        print()
        
        bet_count = 0
        
        for idx, row in predictions.iterrows():
            # Generate synthetic odds (slightly worse than true probability)
            # This simulates the sportsbook vig
            home_prob = row['home_win_prob']
            
            # Sportsbook typically prices with 5-10% vig
            # We'll make synthetic odds slightly unfavorable
            if home_prob > 0.5:
                # Home team is favorite
                # Make odds slightly worse (higher implied prob)
                synthetic_implied = home_prob + 0.05
                synthetic_implied = min(synthetic_implied, 0.95)
                
                # Convert to moneyline
                synthetic_ml = -int(synthetic_implied / (1 - synthetic_implied) * 100)
            else:
                # Home team is underdog
                synthetic_implied = home_prob - 0.05
                synthetic_implied = max(synthetic_implied, 0.05)
                
                synthetic_ml = int((1 - synthetic_implied) / synthetic_implied * 100)
            
            # Simulate bet
            actual_win = row['home_win'] == 1
            
            bet_result = self.simulate_bet(
                team=row['home_team'],
                true_probability=home_prob,
                moneyline=synthetic_ml,
                actual_win=actual_win
            )
            
            if bet_result:
                bet_count += 1
                
                if bet_count % 50 == 0:
                    print(f"   Processed {bet_count} bets, Bankroll: ${self.current_bankroll:,.2f}")
        
        print(f"\n   ✅ Backtest complete: {bet_count} bets placed")
        
        return self.calculate_performance_metrics()
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.bets:
            return {}
        
        # Basic metrics
        total_bets = len(self.bets)
        wins = sum(1 for bet in self.bets if bet['actual_win'])
        losses = total_bets - wins
        win_rate = wins / total_bets
        
        # Profit metrics
        total_profit = self.current_bankroll - self.starting_bankroll
        roi = (total_profit / self.starting_bankroll) * 100
        
        # Average bet metrics
        avg_bet_size = np.mean([bet['bet_amount'] for bet in self.bets])
        avg_profit_per_bet = np.mean([bet['profit'] for bet in self.bets])
        
        # Drawdown analysis
        bankroll_array = np.array(self.bankroll_history)
        running_max = np.maximum.accumulate(bankroll_array)
        drawdown = (bankroll_array - running_max) / running_max
        max_drawdown = abs(drawdown.min()) * 100
        
        # Sharpe ratio (simplified)
        returns = np.diff(self.bankroll_history) / self.bankroll_history[:-1]
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = 0.0
        
        metrics = {
            'total_bets': total_bets,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'starting_bankroll': self.starting_bankroll,
            'ending_bankroll': self.current_bankroll,
            'total_profit': total_profit,
            'roi': roi,
            'avg_bet_size': avg_bet_size,
            'avg_profit_per_bet': avg_profit_per_bet,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
        
        return metrics
    
    def print_backtest_results(self, metrics: Dict):
        """Print formatted backtest results"""
        print("\n" + "=" * 70)
        print("📊 BACKTEST RESULTS")
        print("=" * 70)
        
        print(f"\n💰 Bankroll Performance:")
        print(f"   Starting: ${metrics['starting_bankroll']:,.2f}")
        print(f"   Ending: ${metrics['ending_bankroll']:,.2f}")
        print(f"   Profit: ${metrics['total_profit']:,.2f}")
        print(f"   ROI: {metrics['roi']:+.1f}%")
        
        print(f"\n📊 Betting Statistics:")
        print(f"   Total Bets: {metrics['total_bets']}")
        print(f"   Wins: {metrics['wins']} ({metrics['win_rate']:.1%})")
        print(f"   Losses: {metrics['losses']} ({1-metrics['win_rate']:.1%})")
        print(f"   Avg Bet Size: ${metrics['avg_bet_size']:,.2f}")
        print(f"   Avg Profit/Bet: ${metrics['avg_profit_per_bet']:,.2f}")
        
        print(f"\n📉 Risk Metrics:")
        print(f"   Max Drawdown: {metrics['max_drawdown']:.1f}%")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        
        # Check RFC targets
        print(f"\n🎯 RFC Target Comparison:")
        print(f"   ROI > 5%: {metrics['roi']:.1f}% {'✅' if metrics['roi'] > 5 else '❌'}")
        print(f"   Win Rate > 52.4%: {metrics['win_rate']:.1%} {'✅' if metrics['win_rate'] > 0.524 else '❌'}")
        print(f"   Sharpe > 1.0: {metrics['sharpe_ratio']:.2f} {'✅' if metrics['sharpe_ratio'] > 1.0 else '❌'}")
        print(f"   Max DD < 20%: {metrics['max_drawdown']:.1f}% {'✅' if metrics['max_drawdown'] < 20 else '❌'}")
        
        print("\n" + "=" * 70)
    
    def save_backtest_results(self, metrics: Dict, filename: str = 'backtest_results.json'):
        """Save backtest results to file"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'starting_bankroll': self.starting_bankroll,
                'min_ev_threshold': self.min_ev_threshold,
                'use_kelly': self.use_kelly,
                'kelly_fraction': self.kelly_fraction
            },
            'metrics': metrics,
            'bets': self.bets[:100],  # Save first 100 bets as sample
            'bankroll_history': self.bankroll_history
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Backtest results saved to: {filename}")


def main():
    """Run backtesting"""
    print("=" * 70)
    print("🔄 NBA BETTING BACKTEST")
    print("=" * 70)
    
    # Load predictions
    print("\n📂 Loading predictions...")
    df = pd.read_csv('nba_features.csv')
    
    # Load calibrated model
    with open('nba_model_calibrated.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    # Get predictions
    X = df[model_data['feature_names']].values
    X_scaled = model_data['scaler'].transform(X)
    y_pred_proba = model_data['calibrated_model'].predict_proba(X_scaled)[:, 1]
    
    # Add predictions to dataframe
    df['home_win_prob'] = y_pred_proba
    
    print(f"   ✅ Loaded {len(df)} games with predictions")
    
    # Initialize backtest
    backtest = BettingBacktest(
        starting_bankroll=1000.0,
        min_ev_threshold=0.05,
        use_kelly=True,
        kelly_fraction=0.25
    )
    
    # Run backtest
    metrics = backtest.run_backtest(df)
    
    # Print results
    backtest.print_backtest_results(metrics)
    
    # Save results
    backtest.save_backtest_results(metrics)
    
    print("\n✅ BACKTESTING COMPLETE!")
    print("=" * 70)
    
    return backtest, metrics


if __name__ == "__main__":
    import pickle
    main()

