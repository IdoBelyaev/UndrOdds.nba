"""
Comprehensive Backtest
======================

Backtest with real historical odds:
- Multiple seasons
- Different betting strategies
- Sensitivity analysis
- Monte Carlo simulation

M3 Phase 4: Comprehensive Backtest
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List
from backtesting import BettingBacktest


class ComprehensiveBacktest:
    """Run comprehensive backtesting analysis"""
    
    def __init__(self):
        """Initialize comprehensive backtest"""
        pass
    
    def run_strategy_comparison(
        self,
        predictions: pd.DataFrame,
        strategies: List[Dict]
    ) -> Dict:
        """
        Compare different betting strategies
        
        Args:
            predictions: DataFrame with predictions
            strategies: List of strategy configurations
        
        Returns:
            Dictionary with comparison results
        """
        print("\n📊 COMPARING BETTING STRATEGIES")
        print("=" * 70)
        
        results = []
        
        for strategy in strategies:
            print(f"\n🔧 Testing: {strategy['name']}")
            
            backtest = BettingBacktest(
                starting_bankroll=strategy.get('bankroll', 1000.0),
                min_ev_threshold=strategy.get('min_ev', 0.05),
                use_kelly=strategy.get('use_kelly', False),
                kelly_fraction=strategy.get('kelly_fraction', 0.25)
            )
            
            metrics = backtest.run_backtest(predictions)
            
            results.append({
                'strategy': strategy['name'],
                'config': strategy,
                'metrics': metrics
            })
            
            print(f"   ROI: {metrics['roi']:+.1f}%")
            print(f"   Win Rate: {metrics['win_rate']:.1%}")
            print(f"   Sharpe: {metrics['sharpe_ratio']:.2f}")
        
        print("\n" + "=" * 70)
        
        return {'strategies': results}
    
    def sensitivity_analysis(
        self,
        predictions: pd.DataFrame,
        parameter: str,
        values: List[float]
    ) -> Dict:
        """
        Test sensitivity to parameter changes
        
        Args:
            predictions: DataFrame with predictions
            parameter: Parameter to test ('min_ev', 'kelly_fraction', etc.)
            values: List of values to test
        
        Returns:
            Dictionary with sensitivity results
        """
        print(f"\n📊 SENSITIVITY ANALYSIS: {parameter}")
        print("=" * 70)
        
        results = []
        
        for value in values:
            print(f"\n🔧 Testing {parameter}={value}")
            
            config = {
                'starting_bankroll': 1000.0,
                'min_ev_threshold': 0.05,
                'use_kelly': False,
                'kelly_fraction': 0.25
            }
            
            # Update parameter
            if parameter == 'min_ev':
                config['min_ev_threshold'] = value
            elif parameter == 'kelly_fraction':
                config['kelly_fraction'] = value
                config['use_kelly'] = True
            
            backtest = BettingBacktest(**config)
            metrics = backtest.run_backtest(predictions)
            
            results.append({
                'parameter_value': value,
                'roi': metrics['roi'],
                'win_rate': metrics['win_rate'],
                'total_bets': metrics['total_bets'],
                'sharpe_ratio': metrics['sharpe_ratio']
            })
            
            print(f"   ROI: {metrics['roi']:+.1f}%, Bets: {metrics['total_bets']}")
        
        print("\n" + "=" * 70)
        
        return {
            'parameter': parameter,
            'results': results
        }
    
    def monte_carlo_simulation(
        self,
        predictions: pd.DataFrame,
        n_simulations: int = 1000,
        strategy: Dict = None
    ) -> Dict:
        """
        Run Monte Carlo simulation
        
        Args:
            predictions: DataFrame with predictions
            n_simulations: Number of simulations
            strategy: Strategy configuration
        
        Returns:
            Dictionary with simulation results
        """
        print(f"\n🎲 MONTE CARLO SIMULATION ({n_simulations} runs)")
        print("=" * 70)
        
        if strategy is None:
            strategy = {
                'starting_bankroll': 1000.0,
                'min_ev_threshold': 0.05,
                'use_kelly': False,
                'kelly_fraction': 0.25
            }
        
        final_bankrolls = []
        rois = []
        
        for i in range(n_simulations):
            # Shuffle predictions to simulate different bet sequences
            shuffled = predictions.sample(frac=1.0, random_state=i)
            
            backtest = BettingBacktest(**strategy)
            metrics = backtest.run_backtest(shuffled)
            
            final_bankrolls.append(metrics['ending_bankroll'])
            rois.append(metrics['roi'])
            
            if (i + 1) % 100 == 0:
                print(f"   Completed {i + 1}/{n_simulations} simulations...")
        
        # Calculate statistics
        results = {
            'n_simulations': n_simulations,
            'mean_final_bankroll': np.mean(final_bankrolls),
            'median_final_bankroll': np.median(final_bankrolls),
            'std_final_bankroll': np.std(final_bankrolls),
            'min_final_bankroll': np.min(final_bankrolls),
            'max_final_bankroll': np.max(final_bankrolls),
            'mean_roi': np.mean(rois),
            'median_roi': np.median(rois),
            'std_roi': np.std(rois),
            'probability_profit': np.mean([r > 0 for r in rois])
        }
        
        print(f"\n📊 Simulation Results:")
        print(f"   Mean ROI: {results['mean_roi']:+.1f}%")
        print(f"   Median ROI: {results['median_roi']:+.1f}%")
        print(f"   Std Dev: {results['std_roi']:.1f}%")
        print(f"   Probability of Profit: {results['probability_profit']:.1%}")
        
        print("\n" + "=" * 70)
        
        return results


def main():
    """Run comprehensive backtest"""
    print("=" * 70)
    print("📊 COMPREHENSIVE BACKTEST")
    print("=" * 70)
    
    # Load predictions
    print("\n📂 Loading predictions...")
    df = pd.read_csv('nba_features.csv')
    
    # Load calibrated model
    import pickle
    with open('nba_model_calibrated.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    # Get predictions
    X = df[model_data['feature_names']].values
    X_scaled = model_data['scaler'].transform(X)
    df['home_win_prob'] = model_data['calibrated_model'].predict_proba(X_scaled)[:, 1]
    
    print(f"   ✅ Loaded {len(df)} games")
    
    # Initialize comprehensive backtest
    comp_backtest = ComprehensiveBacktest()
    
    # Strategy comparison
    print("\n1️⃣  Strategy Comparison...")
    strategies = [
        {'name': 'Conservative Flat', 'bankroll': 1000, 'min_ev': 0.05, 'use_kelly': False},
        {'name': 'Moderate Flat', 'bankroll': 1000, 'min_ev': 0.03, 'use_kelly': False},
        {'name': 'Quarter Kelly', 'bankroll': 1000, 'min_ev': 0.05, 'use_kelly': True, 'kelly_fraction': 0.25},
    ]
    
    strategy_results = comp_backtest.run_strategy_comparison(df, strategies)
    
    # Sensitivity analysis
    print("\n2️⃣  Sensitivity Analysis...")
    sensitivity = comp_backtest.sensitivity_analysis(
        df,
        parameter='min_ev',
        values=[0.02, 0.03, 0.05, 0.07, 0.10]
    )
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'strategy_comparison': strategy_results,
        'sensitivity_analysis': sensitivity
    }
    
    with open('comprehensive_backtest_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to: comprehensive_backtest_results.json")
    
    print("\n✅ COMPREHENSIVE BACKTEST COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

