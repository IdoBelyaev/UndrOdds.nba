"""
Strategy Optimization
=====================

Optimize betting strategy parameters:
- Test different EV thresholds
- Test different confidence filters
- Test different bet sizing methods
- Find optimal risk/reward balance

M3 Phase 4: Strategy Optimization
"""

import json
import numpy as np
import pandas as pd
import pickle
from typing import Dict, List, Tuple
from backtesting import BettingBacktest


class StrategyOptimizer:
    """Optimize betting strategy parameters"""
    
    def __init__(self):
        """Initialize strategy optimizer"""
        pass
    
    def optimize_ev_threshold(
        self,
        predictions: pd.DataFrame,
        thresholds: List[float] = None
    ) -> Dict:
        """
        Find optimal EV threshold
        
        Args:
            predictions: DataFrame with predictions
            thresholds: List of EV thresholds to test
        
        Returns:
            Dictionary with optimization results
        """
        if thresholds is None:
            thresholds = [0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15]
        
        print("\n🔧 OPTIMIZING EV THRESHOLD")
        print("=" * 70)
        
        results = []
        
        for threshold in thresholds:
            backtest = BettingBacktest(
                starting_bankroll=1000.0,
                min_ev_threshold=threshold,
                use_kelly=False
            )
            
            metrics = backtest.run_backtest(predictions)
            
            results.append({
                'ev_threshold': threshold,
                'roi': metrics['roi'],
                'total_bets': metrics['total_bets'],
                'win_rate': metrics['win_rate'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown']
            })
            
            print(f"   EV={threshold*100:4.0f}%: ROI={metrics['roi']:+6.1f}%, "
                  f"Bets={metrics['total_bets']:3d}, WR={metrics['win_rate']:.1%}")
        
        # Find best by ROI
        best_by_roi = max(results, key=lambda x: x['roi'])
        
        # Find best by Sharpe (risk-adjusted)
        best_by_sharpe = max(results, key=lambda x: x['sharpe_ratio'])
        
        print(f"\n🏆 Best by ROI: EV={best_by_roi['ev_threshold']*100:.0f}% "
              f"(ROI={best_by_roi['roi']:+.1f}%)")
        print(f"🏆 Best by Sharpe: EV={best_by_sharpe['ev_threshold']*100:.0f}% "
              f"(Sharpe={best_by_sharpe['sharpe_ratio']:.2f})")
        
        print("=" * 70)
        
        return {
            'results': results,
            'best_by_roi': best_by_roi,
            'best_by_sharpe': best_by_sharpe
        }
    
    def optimize_confidence_filter(
        self,
        predictions: pd.DataFrame,
        confidence_levels: List[float] = None
    ) -> Dict:
        """
        Find optimal confidence filter
        
        Args:
            predictions: DataFrame with predictions
            confidence_levels: List of confidence thresholds
        
        Returns:
            Dictionary with optimization results
        """
        if confidence_levels is None:
            confidence_levels = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
        
        print("\n🔧 OPTIMIZING CONFIDENCE FILTER")
        print("=" * 70)
        
        results = []
        
        for conf in confidence_levels:
            # Filter predictions by confidence
            filtered = predictions[
                (predictions['home_win_prob'] >= conf) |
                (predictions['home_win_prob'] <= (1 - conf))
            ].copy()
            
            if len(filtered) < 10:
                print(f"   Conf={conf:.0%}: Too few bets, skipping")
                continue
            
            backtest = BettingBacktest(
                starting_bankroll=1000.0,
                min_ev_threshold=0.05,
                use_kelly=False
            )
            
            metrics = backtest.run_backtest(filtered)
            
            results.append({
                'confidence_threshold': conf,
                'roi': metrics['roi'],
                'total_bets': metrics['total_bets'],
                'win_rate': metrics['win_rate'],
                'sharpe_ratio': metrics['sharpe_ratio']
            })
            
            print(f"   Conf={conf:.0%}: ROI={metrics['roi']:+6.1f}%, "
                  f"Bets={metrics['total_bets']:3d}, WR={metrics['win_rate']:.1%}")
        
        if results:
            best = max(results, key=lambda x: x['sharpe_ratio'])
            print(f"\n🏆 Best: Confidence={best['confidence_threshold']:.0%} "
                  f"(Sharpe={best['sharpe_ratio']:.2f})")
        
        print("=" * 70)
        
        return {'results': results}
    
    def find_optimal_strategy(
        self,
        predictions: pd.DataFrame
    ) -> Dict:
        """
        Find optimal overall strategy
        
        Args:
            predictions: DataFrame with predictions
        
        Returns:
            Dictionary with optimal strategy
        """
        print("\n🎯 FINDING OPTIMAL STRATEGY")
        print("=" * 70)
        
        # Test EV thresholds
        ev_results = self.optimize_ev_threshold(predictions)
        
        # Test confidence filters
        conf_results = self.optimize_confidence_filter(predictions)
        
        # Recommend optimal strategy
        optimal = {
            'ev_threshold': ev_results['best_by_sharpe']['ev_threshold'],
            'confidence_filter': 0.60,  # Default safe value
            'bet_sizing': 'flat',
            'flat_bet_amount': 20.0,
            'bankroll': 1000.0
        }
        
        print("\n🏆 RECOMMENDED OPTIMAL STRATEGY:")
        print(f"   EV Threshold: {optimal['ev_threshold']*100:.0f}%")
        print(f"   Confidence Filter: {optimal['confidence_filter']:.0%}")
        print(f"   Bet Sizing: {optimal['bet_sizing']} (${optimal['flat_bet_amount']:.0f})")
        print(f"   Bankroll: ${optimal['bankroll']:.0f}")
        
        print("\n" + "=" * 70)
        
        return optimal


def main():
    """Run strategy optimization"""
    print("=" * 70)
    print("🎯 STRATEGY OPTIMIZATION")
    print("=" * 70)
    
    # Load predictions
    print("\n📂 Loading predictions...")
    df = pd.read_csv('nba_features.csv')
    
    with open('nba_model_calibrated.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    X = df[model_data['feature_names']].values
    X_scaled = model_data['scaler'].transform(X)
    df['home_win_prob'] = model_data['calibrated_model'].predict_proba(X_scaled)[:, 1]
    
    print(f"   ✅ Loaded {len(df)} games")
    
    # Initialize optimizer
    optimizer = StrategyOptimizer()
    
    # Find optimal strategy
    optimal = optimizer.find_optimal_strategy(df)
    
    # Save results
    with open('strategy_optimization_results.json', 'w') as f:
        json.dump(optimal, f, indent=2)
    
    print("\n💾 Results saved to: strategy_optimization_results.json")
    
    print("\n✅ STRATEGY OPTIMIZATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

