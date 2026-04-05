"""
Elo Rating System Calibration
==============================

This module calibrates the Elo rating system by testing different
K-factors and home court advantage values to find optimal parameters.

Goal: Minimize Brier score and maximize accuracy

M2 Phase 1: Elo Calibration
"""

import json
import numpy as np
from typing import Dict, List, Tuple
from elo_ratings import EloRatingSystem, load_game_data


def calibrate_elo(
    games: List[Dict],
    k_factors: List[float] = [10, 20, 30, 40],
    home_advantages: List[float] = [50, 75, 100, 125, 150],
    verbose: bool = True
) -> Dict:
    """
    Calibrate Elo system by testing different parameters
    
    Args:
        games: List of game dictionaries
        k_factors: List of K-factors to test
        home_advantages: List of home advantage values to test
        verbose: Whether to print progress
    
    Returns:
        Dictionary with calibration results
    """
    if verbose:
        print("=" * 70)
        print("🔧 ELO CALIBRATION")
        print("=" * 70)
        print(f"\n📊 Testing {len(k_factors)} K-factors × {len(home_advantages)} home advantages")
        print(f"   Total combinations: {len(k_factors) * len(home_advantages)}")
        print()
    
    # Get unique teams
    teams = set()
    for game in games:
        teams.add(game['home_team'])
        teams.add(game['away_team'])
    
    results = []
    best_brier = float('inf')
    best_params = None
    
    total_tests = len(k_factors) * len(home_advantages)
    test_num = 0
    
    for k in k_factors:
        for ha in home_advantages:
            test_num += 1
            
            if verbose:
                print(f"Testing {test_num}/{total_tests}: K={k:4.1f}, HA={ha:5.1f}...", end=" ")
            
            # Initialize Elo system
            elo = EloRatingSystem(
                k_factor=k,
                home_advantage=ha,
                initial_rating=1500.0
            )
            
            elo.initialize_teams(list(teams))
            
            # Process all games
            elo.process_season(games, store_predictions=True)
            
            # Get metrics
            metrics = elo.get_performance_metrics()
            
            result = {
                'k_factor': k,
                'home_advantage': ha,
                'accuracy': metrics['accuracy'],
                'brier_score': metrics['brier_score'],
                'log_loss': metrics['log_loss']
            }
            
            results.append(result)
            
            if verbose:
                print(f"Accuracy: {metrics['accuracy']:.1%}, Brier: {metrics['brier_score']:.4f}")
            
            # Track best parameters
            if metrics['brier_score'] < best_brier:
                best_brier = metrics['brier_score']
                best_params = result
    
    if verbose:
        print("\n" + "=" * 70)
        print("🏆 CALIBRATION RESULTS")
        print("=" * 70)
        print(f"\n✅ Best Parameters:")
        print(f"   K-factor: {best_params['k_factor']}")
        print(f"   Home Advantage: {best_params['home_advantage']} Elo points")
        print(f"\n📊 Best Performance:")
        print(f"   Accuracy: {best_params['accuracy']:.1%}")
        print(f"   Brier Score: {best_params['brier_score']:.4f}")
        print(f"   Log Loss: {best_params['log_loss']:.4f}")
        print("\n" + "=" * 70)
    
    return {
        'best_params': best_params,
        'all_results': results
    }


def analyze_calibration_results(results: List[Dict]):
    """Analyze and visualize calibration results"""
    print("\n📊 DETAILED CALIBRATION ANALYSIS")
    print("=" * 70)
    
    # Sort by Brier score
    sorted_results = sorted(results, key=lambda x: x['brier_score'])
    
    print("\n🏆 Top 10 Parameter Combinations (by Brier Score):")
    print(f"{'Rank':<6} {'K-factor':<10} {'Home Adv':<12} {'Accuracy':<12} {'Brier':<10} {'Log Loss':<10}")
    print("-" * 70)
    
    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i:<6} {r['k_factor']:<10.1f} {r['home_advantage']:<12.1f} "
              f"{r['accuracy']:<12.1%} {r['brier_score']:<10.4f} {r['log_loss']:<10.4f}")
    
    # Analyze by K-factor
    print("\n📈 Average Performance by K-factor:")
    k_factors = sorted(set(r['k_factor'] for r in results))
    
    for k in k_factors:
        k_results = [r for r in results if r['k_factor'] == k]
        avg_accuracy = np.mean([r['accuracy'] for r in k_results])
        avg_brier = np.mean([r['brier_score'] for r in k_results])
        
        print(f"   K={k:4.1f}: Accuracy={avg_accuracy:.1%}, Brier={avg_brier:.4f}")
    
    # Analyze by Home Advantage
    print("\n🏠 Average Performance by Home Advantage:")
    home_advs = sorted(set(r['home_advantage'] for r in results))
    
    for ha in home_advs:
        ha_results = [r for r in results if r['home_advantage'] == ha]
        avg_accuracy = np.mean([r['accuracy'] for r in ha_results])
        avg_brier = np.mean([r['brier_score'] for r in ha_results])
        
        print(f"   HA={ha:5.1f}: Accuracy={avg_accuracy:.1%}, Brier={avg_brier:.4f}")
    
    print("\n" + "=" * 70)


def run_with_best_params(
    games: List[Dict],
    best_params: Dict,
    save_results: bool = True
) -> EloRatingSystem:
    """
    Run Elo system with best calibrated parameters
    
    Args:
        games: List of game dictionaries
        best_params: Best parameters from calibration
        save_results: Whether to save results to files
    
    Returns:
        Trained EloRatingSystem
    """
    print("\n🚀 RUNNING ELO WITH BEST PARAMETERS")
    print("=" * 70)
    
    # Get unique teams
    teams = set()
    for game in games:
        teams.add(game['home_team'])
        teams.add(game['away_team'])
    
    # Initialize with best parameters
    elo = EloRatingSystem(
        k_factor=best_params['k_factor'],
        home_advantage=best_params['home_advantage'],
        initial_rating=1500.0
    )
    
    elo.initialize_teams(list(teams))
    
    # Process all games
    elo.process_season(games, store_predictions=True)
    
    # Print summary
    elo.print_summary()
    
    # Save results
    if save_results:
        elo.save_ratings('elo_ratings_calibrated.json')
        elo.save_predictions('elo_predictions_calibrated.json')
    
    return elo


def save_calibration_results(calibration_data: Dict, filename: str = 'elo_calibration_results.json'):
    """Save calibration results to file"""
    with open(filename, 'w') as f:
        json.dump(calibration_data, f, indent=2)
    
    print(f"\n💾 Calibration results saved to: {filename}")


def main():
    """Run Elo calibration"""
    print("=" * 70)
    print("🔧 NBA ELO CALIBRATION SYSTEM")
    print("=" * 70)
    
    # Load game data
    print("\n📂 Loading game data...")
    games = load_game_data('nba_game_data.json')
    print(f"   ✅ Loaded {len(games)} games")
    
    # Run calibration
    calibration_results = calibrate_elo(
        games=games,
        k_factors=[10, 15, 20, 25, 30, 35, 40],
        home_advantages=[50, 75, 100, 125, 150],
        verbose=True
    )
    
    # Analyze results
    analyze_calibration_results(calibration_results['all_results'])
    
    # Save calibration results
    save_calibration_results(calibration_results)
    
    # Run with best parameters
    best_elo = run_with_best_params(
        games=games,
        best_params=calibration_results['best_params'],
        save_results=True
    )
    
    print("\n✅ ELO CALIBRATION COMPLETE!")
    print("=" * 70)
    
    return best_elo, calibration_results


if __name__ == "__main__":
    main()

