"""
Elo Baseline Performance Report
================================

Generate comprehensive performance report for the Elo rating system baseline.

M2 Phase 1: Elo Baseline Performance
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from typing import Dict, List
from collections import defaultdict


def load_predictions(filename: str = 'elo_predictions_calibrated.json') -> Dict:
    """Load Elo predictions from file"""
    with open(filename, 'r') as f:
        return json.load(f)


def load_calibration_results(filename: str = 'elo_calibration_results.json') -> Dict:
    """Load calibration results from file"""
    with open(filename, 'r') as f:
        return json.load(f)


def calculate_calibration_curve(predictions: List[Dict], n_bins: int = 10) -> tuple:
    """
    Calculate calibration curve data
    
    Returns:
        (bin_centers, observed_frequencies, counts)
    """
    # Extract predicted probabilities and actual outcomes
    pred_probs = np.array([p['predicted_home_win_prob'] for p in predictions])
    actual_outcomes = np.array([p['actual_home_win'] for p in predictions])
    
    # Create bins
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(pred_probs, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    # Calculate observed frequency in each bin
    bin_centers = []
    observed_freqs = []
    counts = []
    
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            bin_centers.append(bins[i:i+2].mean())
            observed_freqs.append(actual_outcomes[mask].mean())
            counts.append(mask.sum())
    
    return np.array(bin_centers), np.array(observed_freqs), np.array(counts)


def plot_calibration_curve(predictions: List[Dict], save_path: str = 'elo_calibration_curve.png'):
    """Generate and save calibration curve plot"""
    bin_centers, observed_freqs, counts = calculate_calibration_curve(predictions, n_bins=10)
    
    plt.figure(figsize=(10, 8))
    
    # Plot perfect calibration line
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)
    
    # Plot actual calibration
    plt.plot(bin_centers, observed_freqs, 'bo-', label='Elo Model', linewidth=2, markersize=8)
    
    # Add sample size annotations
    for x, y, count in zip(bin_centers, observed_freqs, counts):
        plt.annotate(f'n={count}', (x, y), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=8)
    
    plt.xlabel('Predicted Probability', fontsize=12)
    plt.ylabel('Observed Frequency', fontsize=12)
    plt.title('Elo Model Calibration Curve', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    print(f"   📊 Calibration curve saved to: {save_path}")


def analyze_by_confidence(predictions: List[Dict]):
    """Analyze performance by confidence level"""
    print("\n📊 Performance by Confidence Level:")
    print("-" * 70)
    
    confidence_bins = [
        (0.5, 0.6, "Low (50-60%)"),
        (0.6, 0.7, "Medium (60-70%)"),
        (0.7, 0.8, "High (70-80%)"),
        (0.8, 1.0, "Very High (80-100%)")
    ]
    
    for min_conf, max_conf, label in confidence_bins:
        # Filter predictions in this confidence range
        filtered = [
            p for p in predictions
            if min_conf <= p['predicted_home_win_prob'] < max_conf or
               min_conf <= (1 - p['predicted_home_win_prob']) < max_conf
        ]
        
        if not filtered:
            continue
        
        # Calculate accuracy
        correct = sum(
            1 for p in filtered
            if (p['predicted_home_win_prob'] > 0.5 and p['actual_home_win'] == 1.0) or
               (p['predicted_home_win_prob'] <= 0.5 and p['actual_home_win'] == 0.0)
        )
        
        accuracy = correct / len(filtered) if filtered else 0
        
        print(f"   {label:20s}: {len(filtered):4d} games, Accuracy: {accuracy:.1%}")


def analyze_by_team(predictions: List[Dict]):
    """Analyze performance by team"""
    print("\n📊 Performance by Team (Top 10 Most Predicted):")
    print("-" * 70)
    
    # Count predictions per team
    team_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    
    for p in predictions:
        home_team = p['home_team']
        away_team = p['away_team']
        
        # Home team
        team_stats[home_team]['total'] += 1
        if (p['predicted_home_win_prob'] > 0.5 and p['actual_home_win'] == 1.0) or \
           (p['predicted_home_win_prob'] <= 0.5 and p['actual_home_win'] == 0.0):
            team_stats[home_team]['correct'] += 1
        
        # Away team
        team_stats[away_team]['total'] += 1
        if (p['predicted_home_win_prob'] <= 0.5 and p['actual_home_win'] == 0.0) or \
           (p['predicted_home_win_prob'] > 0.5 and p['actual_home_win'] == 1.0):
            team_stats[away_team]['correct'] += 1
    
    # Calculate accuracy and sort
    team_accuracies = [
        (team, stats['correct'] / stats['total'], stats['total'])
        for team, stats in team_stats.items()
    ]
    team_accuracies.sort(key=lambda x: x[2], reverse=True)
    
    print(f"{'Team':<30s} {'Games':<8s} {'Accuracy':<10s}")
    print("-" * 70)
    
    for team, accuracy, total in team_accuracies[:10]:
        print(f"{team:<30s} {total:<8d} {accuracy:<10.1%}")


def generate_baseline_report():
    """Generate comprehensive Elo baseline performance report"""
    print("=" * 70)
    print("📊 ELO BASELINE PERFORMANCE REPORT")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading data...")
    pred_data = load_predictions('elo_predictions_calibrated.json')
    calib_data = load_calibration_results('elo_calibration_results.json')
    
    predictions = pred_data['predictions']
    metadata = pred_data['metadata']
    performance = pred_data['performance']
    best_params = calib_data['best_params']
    
    print(f"   ✅ Loaded {len(predictions)} predictions")
    
    # Print configuration
    print("\n⚙️  Optimal Configuration:")
    print(f"   K-factor: {best_params['k_factor']}")
    print(f"   Home Advantage: {best_params['home_advantage']} Elo points")
    print(f"   Initial Rating: 1500.0")
    
    # Print overall performance
    print("\n📈 Overall Performance Metrics:")
    print(f"   Total Predictions: {performance['total_predictions']}")
    print(f"   Accuracy: {performance['accuracy']:.1%}")
    print(f"   Brier Score: {performance['brier_score']:.4f}")
    print(f"   Log Loss: {performance['log_loss']:.4f}")
    
    # Check against RFC targets
    print("\n🎯 RFC Target Comparison:")
    target_brier = 0.19
    target_accuracy = 0.60
    
    brier_status = "✅ PASS" if performance['brier_score'] <= target_brier else "❌ FAIL"
    accuracy_status = "✅ PASS" if performance['accuracy'] >= target_accuracy else "❌ FAIL"
    
    print(f"   Brier Score ≤ {target_brier}: {performance['brier_score']:.4f} {brier_status}")
    print(f"   Accuracy > {target_accuracy:.0%}: {performance['accuracy']:.1%} {accuracy_status}")
    
    # Analyze by confidence
    analyze_by_confidence(predictions)
    
    # Analyze by team
    analyze_by_team(predictions)
    
    # Generate calibration curve
    print("\n📊 Generating calibration curve...")
    plot_calibration_curve(predictions)
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 BASELINE SUMMARY")
    print("=" * 70)
    
    if performance['brier_score'] <= target_brier and performance['accuracy'] >= target_accuracy:
        print("\n✅ ELO BASELINE MEETS ALL RFC TARGETS!")
        print("   Ready to proceed to Phase 2: Logistic Regression")
    elif performance['brier_score'] <= 0.22:
        print("\n⚠️  ELO BASELINE: ACCEPTABLE PERFORMANCE")
        print("   Close to RFC targets. Can proceed with caution.")
        print("   Logistic regression should improve performance.")
    else:
        print("\n❌ ELO BASELINE: BELOW TARGETS")
        print("   Consider further calibration or feature engineering.")
    
    print("\n" + "=" * 70)
    
    # Save report
    report_data = {
        'timestamp': metadata['timestamp'],
        'configuration': {
            'k_factor': best_params['k_factor'],
            'home_advantage': best_params['home_advantage'],
            'initial_rating': 1500.0
        },
        'performance': performance,
        'rfc_targets': {
            'brier_score_target': target_brier,
            'brier_score_actual': performance['brier_score'],
            'brier_score_pass': performance['brier_score'] <= target_brier,
            'accuracy_target': target_accuracy,
            'accuracy_actual': performance['accuracy'],
            'accuracy_pass': performance['accuracy'] >= target_accuracy
        },
        'status': 'PASS' if (performance['brier_score'] <= target_brier and 
                            performance['accuracy'] >= target_accuracy) else 'ACCEPTABLE'
    }
    
    with open('elo_baseline_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print("\n💾 Baseline report saved to: elo_baseline_report.json")


def main():
    """Run baseline performance report"""
    generate_baseline_report()
    
    print("\n✅ ELO BASELINE REPORT COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

