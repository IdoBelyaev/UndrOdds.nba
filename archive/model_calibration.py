"""
Model Calibration
=================

Calibrate logistic regression probabilities using:
- Isotonic Regression (non-parametric)
- Platt Scaling (parametric)

Goal: Improve Brier score by making probabilities more accurate

M2 Phase 2: Model Calibration
"""

import json
import numpy as np
import pandas as pd
import pickle
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import brier_score_loss, log_loss, accuracy_score, roc_auc_score
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_model_and_data():
    """Load trained model and feature data"""
    print("\n📂 Loading model and data...")
    
    # Load model
    with open('nba_model.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    # Load features
    df = pd.read_csv('nba_features.csv')
    
    # Prepare data
    feature_cols = model_data['feature_names']
    X = df[feature_cols].values
    y = df['home_win'].values
    
    print(f"   ✅ Loaded model and {len(df)} games")
    
    return model_data, X, y, df


def calibrate_model(model_data, X, y, method='isotonic', cv=5):
    """
    Calibrate model using cross-validation
    
    Args:
        model_data: Dictionary with model, scaler, feature_names
        X: Feature matrix
        y: Target vector
        method: 'isotonic' or 'sigmoid' (Platt scaling)
        cv: Number of CV folds
    
    Returns:
        Calibrated model
    """
    print(f"\n🔧 Calibrating model using {method} regression...")
    
    # Get base model and scaler
    base_model = model_data['model']
    scaler = model_data['scaler']
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Create calibrated classifier
    # Use TimeSeriesSplit to respect temporal order
    cv_splitter = TimeSeriesSplit(n_splits=cv)
    
    calibrated_model = CalibratedClassifierCV(
        base_model,
        method=method,
        cv=cv_splitter
    )
    
    # Fit calibrated model
    calibrated_model.fit(X_scaled, y)
    
    print(f"   ✅ Model calibrated with {method}")
    
    return calibrated_model


def evaluate_calibrated_model(calibrated_model, scaler, X, y):
    """Evaluate calibrated model"""
    print("\n📊 Evaluating calibrated model...")
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Get predictions
    y_pred_proba = calibrated_model.predict_proba(X_scaled)[:, 1]
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    # Calculate metrics
    accuracy = accuracy_score(y, y_pred)
    brier = brier_score_loss(y, y_pred_proba)
    logloss = log_loss(y, y_pred_proba)
    auc = roc_auc_score(y, y_pred_proba)
    
    results = {
        'accuracy': accuracy,
        'brier_score': brier,
        'log_loss': logloss,
        'auc': auc
    }
    
    print(f"   Accuracy: {accuracy:.1%}")
    print(f"   Brier Score: {brier:.4f}")
    print(f"   Log Loss: {logloss:.4f}")
    print(f"   AUC: {auc:.4f}")
    
    return results, y_pred_proba


def plot_calibration_curve(y_true, y_pred_proba_uncal, y_pred_proba_cal, save_path='model_calibration_curve.png'):
    """Plot calibration curves before and after calibration"""
    
    def get_calibration_data(y_true, y_pred, n_bins=10):
        """Calculate calibration curve data"""
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(y_pred, bins) - 1
        bin_indices = np.clip(bin_indices, 0, n_bins - 1)
        
        bin_centers = []
        observed_freqs = []
        counts = []
        
        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_centers.append(bins[i:i+2].mean())
                observed_freqs.append(y_true[mask].mean())
                counts.append(mask.sum())
        
        return np.array(bin_centers), np.array(observed_freqs), np.array(counts)
    
    # Get calibration data
    uncal_centers, uncal_freqs, uncal_counts = get_calibration_data(y_true, y_pred_proba_uncal)
    cal_centers, cal_freqs, cal_counts = get_calibration_data(y_true, y_pred_proba_cal)
    
    # Plot
    plt.figure(figsize=(10, 8))
    
    # Perfect calibration line
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)
    
    # Uncalibrated model
    plt.plot(uncal_centers, uncal_freqs, 'ro-', label='Uncalibrated Model', linewidth=2, markersize=8)
    
    # Calibrated model
    plt.plot(cal_centers, cal_freqs, 'go-', label='Calibrated Model', linewidth=2, markersize=8)
    
    plt.xlabel('Predicted Probability', fontsize=12)
    plt.ylabel('Observed Frequency', fontsize=12)
    plt.title('Model Calibration: Before vs After', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    print(f"\n   📊 Calibration curve saved to: {save_path}")


def compare_models(elo_results, uncal_results, cal_results):
    """Compare Elo baseline, uncalibrated, and calibrated models"""
    print("\n" + "=" * 70)
    print("📊 MODEL COMPARISON: ELO vs UNCALIBRATED vs CALIBRATED")
    print("=" * 70)
    
    print(f"\n{'Metric':<20s} {'Elo':<15s} {'Uncalibrated':<15s} {'Calibrated':<15s} {'Best':<10s}")
    print("-" * 70)
    
    # Accuracy
    elo_acc = elo_results['accuracy']
    uncal_acc = uncal_results['accuracy']
    cal_acc = cal_results['accuracy']
    best_acc = max(elo_acc, uncal_acc, cal_acc)
    best_acc_symbol = "🏆" if cal_acc == best_acc else ""
    print(f"{'Accuracy':<20s} {elo_acc:<15.1%} {uncal_acc:<15.1%} {cal_acc:<15.1%} {best_acc_symbol:<10s}")
    
    # Brier Score (lower is better)
    elo_brier = elo_results['brier_score']
    uncal_brier = uncal_results['brier_score']
    cal_brier = cal_results['brier_score']
    best_brier = min(elo_brier, uncal_brier, cal_brier)
    best_brier_symbol = "🏆" if cal_brier == best_brier else ""
    print(f"{'Brier Score':<20s} {elo_brier:<15.4f} {uncal_brier:<15.4f} {cal_brier:<15.4f} {best_brier_symbol:<10s}")
    
    # Log Loss (lower is better)
    elo_logloss = elo_results['log_loss']
    uncal_logloss = uncal_results['log_loss']
    cal_logloss = cal_results['log_loss']
    best_logloss = min(elo_logloss, uncal_logloss, cal_logloss)
    best_logloss_symbol = "🏆" if cal_logloss == best_logloss else ""
    print(f"{'Log Loss':<20s} {elo_logloss:<15.4f} {uncal_logloss:<15.4f} {cal_logloss:<15.4f} {best_logloss_symbol:<10s}")
    
    print("\n" + "=" * 70)
    
    # Check RFC target
    rfc_brier_target = 0.19
    if cal_brier <= rfc_brier_target:
        print(f"🎉 SUCCESS! Calibrated Brier score {cal_brier:.4f} ≤ {rfc_brier_target} (RFC target)")
    else:
        print(f"⚠️  Close! Calibrated Brier score {cal_brier:.4f} > {rfc_brier_target} (RFC target)")
        print(f"   Need to improve by {cal_brier - rfc_brier_target:.4f}")
        
        # Check if we improved from Elo
        if cal_brier < elo_brier:
            improvement = elo_brier - cal_brier
            print(f"   ✅ But we improved from Elo baseline by {improvement:.4f}!")
    
    print("=" * 70)


def main():
    """Run model calibration"""
    print("=" * 70)
    print("🔧 NBA MODEL CALIBRATION")
    print("=" * 70)
    
    # Load model and data
    model_data, X, y, df = load_model_and_data()
    
    # Get uncalibrated predictions for comparison
    print("\n📊 Getting uncalibrated predictions...")
    X_scaled = model_data['scaler'].transform(X)
    y_pred_proba_uncal = model_data['model'].predict_proba(X_scaled)[:, 1]
    y_pred_uncal = (y_pred_proba_uncal > 0.5).astype(int)
    
    uncal_results = {
        'accuracy': accuracy_score(y, y_pred_uncal),
        'brier_score': brier_score_loss(y, y_pred_proba_uncal),
        'log_loss': log_loss(y, y_pred_proba_uncal),
        'auc': roc_auc_score(y, y_pred_proba_uncal)
    }
    
    print(f"   Uncalibrated Brier: {uncal_results['brier_score']:.4f}")
    
    # Calibrate model with isotonic regression
    calibrated_model = calibrate_model(model_data, X, y, method='isotonic', cv=5)
    
    # Evaluate calibrated model
    cal_results, y_pred_proba_cal = evaluate_calibrated_model(
        calibrated_model, model_data['scaler'], X, y
    )
    
    # Plot calibration curves
    print("\n📊 Generating calibration curves...")
    plot_calibration_curve(y, y_pred_proba_uncal, y_pred_proba_cal)
    
    # Load Elo baseline for comparison
    with open('elo_baseline_report.json', 'r') as f:
        elo_baseline = json.load(f)
    
    # Compare all models
    compare_models(elo_baseline['performance'], uncal_results, cal_results)
    
    # Save calibrated model
    print("\n💾 Saving calibrated model...")
    calibrated_model_data = {
        'calibrated_model': calibrated_model,
        'scaler': model_data['scaler'],
        'feature_names': model_data['feature_names'],
        'calibration_method': 'isotonic',
        'training_date': datetime.now().isoformat()
    }
    
    with open('nba_model_calibrated.pkl', 'wb') as f:
        pickle.dump(calibrated_model_data, f)
    
    print("   ✅ Calibrated model saved to: nba_model_calibrated.pkl")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'calibration_method': 'isotonic',
        'uncalibrated': uncal_results,
        'calibrated': cal_results,
        'improvement': {
            'brier_improvement': uncal_results['brier_score'] - cal_results['brier_score'],
            'logloss_improvement': uncal_results['log_loss'] - cal_results['log_loss']
        },
        'comparison_with_elo': {
            'elo_brier': elo_baseline['performance']['brier_score'],
            'calibrated_brier': cal_results['brier_score'],
            'improvement_vs_elo': elo_baseline['performance']['brier_score'] - cal_results['brier_score']
        }
    }
    
    with open('model_calibration_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to: model_calibration_results.json")
    
    print("\n✅ MODEL CALIBRATION COMPLETE!")
    print("=" * 70)
    
    return calibrated_model, cal_results


if __name__ == "__main__":
    main()

