"""
Comprehensive Model Evaluation
===============================

Evaluate model performance with:
- Accuracy metrics
- Brier score and log loss
- Calibration analysis
- Confusion matrix
- ROC/AUC curves
- Performance by confidence level

M2 Phase 4: Model Evaluation
"""

import json
import numpy as np
import pandas as pd
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, brier_score_loss, log_loss, roc_auc_score,
    confusion_matrix, roc_curve, classification_report
)
from datetime import datetime


def load_model_and_predictions():
    """Load calibrated model and predictions"""
    print("\n📂 Loading model and data...")
    
    # Load calibrated model
    with open('nba_model_calibrated.pkl', 'rb') as f:
        model_data = pickle.load(f)
    
    # Load features
    df = pd.read_csv('nba_features.csv')
    
    # Get predictions
    X = df[model_data['feature_names']].values
    X_scaled = model_data['scaler'].transform(X)
    y_true = df['home_win'].values
    y_pred_proba = model_data['calibrated_model'].predict_proba(X_scaled)[:, 1]
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    print(f"   ✅ Loaded model and {len(df)} predictions")
    
    return model_data, df, y_true, y_pred, y_pred_proba


def calculate_comprehensive_metrics(y_true, y_pred, y_pred_proba):
    """Calculate all evaluation metrics"""
    print("\n📊 Calculating comprehensive metrics...")
    
    metrics = {
        # Classification metrics
        'accuracy': accuracy_score(y_true, y_pred),
        'brier_score': brier_score_loss(y_true, y_pred_proba),
        'log_loss': log_loss(y_true, y_pred_proba),
        'auc': roc_auc_score(y_true, y_pred_proba),
        
        # Confusion matrix
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
        
        # Classification report
        'classification_report': classification_report(
            y_true, y_pred,
            target_names=['Away Win', 'Home Win'],
            output_dict=True
        )
    }
    
    print(f"   ✅ Calculated {len(metrics)} metric categories")
    
    return metrics


def plot_confusion_matrix(y_true, y_pred, save_path='confusion_matrix.png'):
    """Generate confusion matrix plot"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    
    # Create heatmap manually
    plt.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.colorbar()
    
    # Add text annotations
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]),
                    ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black",
                    fontsize=20, fontweight='bold')
    
    # Labels
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ['Away Win', 'Home Win'])
    plt.yticks(tick_marks, ['Away Win', 'Home Win'])
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    print(f"   📊 Confusion matrix saved to: {save_path}")


def plot_roc_curve(y_true, y_pred_proba, save_path='roc_curve.png'):
    """Generate ROC curve plot"""
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    auc = roc_auc_score(y_true, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, 'b-', linewidth=2, label=f'Model (AUC = {auc:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random (AUC = 0.500)')
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    
    print(f"   📊 ROC curve saved to: {save_path}")


def analyze_by_confidence(y_true, y_pred_proba):
    """Analyze performance by confidence level"""
    print("\n📊 Performance by Confidence Level:")
    print("-" * 70)
    
    confidence_bins = [
        (0.5, 0.6, "Low (50-60%)"),
        (0.6, 0.7, "Medium (60-70%)"),
        (0.7, 0.8, "High (70-80%)"),
        (0.8, 1.0, "Very High (80-100%)")
    ]
    
    results = []
    
    for min_conf, max_conf, label in confidence_bins:
        # Filter predictions in this confidence range
        mask = ((y_pred_proba >= min_conf) & (y_pred_proba < max_conf)) | \
               ((1 - y_pred_proba >= min_conf) & (1 - y_pred_proba < max_conf))
        
        if mask.sum() == 0:
            continue
        
        # Get predictions and actuals for this bin
        y_true_bin = y_true[mask]
        y_pred_proba_bin = y_pred_proba[mask]
        
        # Determine predicted class
        y_pred_bin = (y_pred_proba_bin > 0.5).astype(int)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_true_bin, y_pred_bin)
        
        # Calculate Brier score
        brier = brier_score_loss(y_true_bin, y_pred_proba_bin)
        
        results.append({
            'label': label,
            'count': mask.sum(),
            'accuracy': accuracy,
            'brier_score': brier
        })
        
        print(f"   {label:20s}: {mask.sum():4d} games, Accuracy: {accuracy:.1%}, Brier: {brier:.4f}")
    
    return results


def print_evaluation_summary(metrics):
    """Print comprehensive evaluation summary"""
    print("\n" + "=" * 70)
    print("📊 MODEL EVALUATION SUMMARY")
    print("=" * 70)
    
    print(f"\n📈 Overall Performance:")
    print(f"   Accuracy: {metrics['accuracy']:.1%}")
    print(f"   Brier Score: {metrics['brier_score']:.4f}")
    print(f"   Log Loss: {metrics['log_loss']:.4f}")
    print(f"   AUC: {metrics['auc']:.4f}")
    
    print(f"\n📊 Confusion Matrix:")
    cm = np.array(metrics['confusion_matrix'])
    print(f"   True Away Wins, Predicted Away: {cm[0, 0]}")
    print(f"   True Away Wins, Predicted Home: {cm[0, 1]}")
    print(f"   True Home Wins, Predicted Away: {cm[1, 0]}")
    print(f"   True Home Wins, Predicted Home: {cm[1, 1]}")
    
    print(f"\n📋 Classification Report:")
    cr = metrics['classification_report']
    print(f"   Away Win - Precision: {cr['Away Win']['precision']:.1%}, Recall: {cr['Away Win']['recall']:.1%}")
    print(f"   Home Win - Precision: {cr['Home Win']['precision']:.1%}, Recall: {cr['Home Win']['recall']:.1%}")
    
    # Check RFC targets
    print(f"\n🎯 RFC Target Comparison:")
    print(f"   Accuracy > 60%: {metrics['accuracy']:.1%} {'✅' if metrics['accuracy'] > 0.60 else '❌'}")
    print(f"   Brier ≤ 0.19: {metrics['brier_score']:.4f} {'✅' if metrics['brier_score'] <= 0.19 else '⚠️'}")
    print(f"   Log Loss < 0.65: {metrics['log_loss']:.4f} {'✅' if metrics['log_loss'] < 0.65 else '❌'}")
    
    print("\n" + "=" * 70)


def main():
    """Run comprehensive model evaluation"""
    print("=" * 70)
    print("📊 COMPREHENSIVE MODEL EVALUATION")
    print("=" * 70)
    
    # Load model and predictions
    model_data, df, y_true, y_pred, y_pred_proba = load_model_and_predictions()
    
    # Calculate metrics
    metrics = calculate_comprehensive_metrics(y_true, y_pred, y_pred_proba)
    
    # Print summary
    print_evaluation_summary(metrics)
    
    # Analyze by confidence
    confidence_results = analyze_by_confidence(y_true, y_pred_proba)
    
    # Generate visualizations
    print("\n📊 Generating visualizations...")
    plot_confusion_matrix(y_true, y_pred)
    plot_roc_curve(y_true, y_pred_proba)
    
    # Save results
    # Convert numpy types to Python types
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    evaluation_report = {
        'timestamp': datetime.now().isoformat(),
        'metrics': convert_types(metrics),
        'confidence_analysis': convert_types(confidence_results)
    }
    
    with open('model_evaluation_report.json', 'w') as f:
        json.dump(evaluation_report, f, indent=2)
    
    print("\n💾 Evaluation report saved to: model_evaluation_report.json")
    
    print("\n✅ MODEL EVALUATION COMPLETE!")
    print("=" * 70)
    
    return metrics


if __name__ == "__main__":
    main()

