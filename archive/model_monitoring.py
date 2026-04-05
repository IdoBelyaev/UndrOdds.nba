"""
Model Performance Monitoring
=============================

Monitor model accuracy over time:
- Prediction accuracy tracking
- Brier score monitoring
- Calibration drift detection
- Model degradation alerts

M3 Phase 2: Model Performance Monitoring
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from sklearn.metrics import brier_score_loss, accuracy_score, log_loss


class ModelMonitor:
    """Monitor model performance over time"""
    
    def __init__(self, monitoring_file: str = 'model_monitoring.json'):
        """
        Initialize model monitor
        
        Args:
            monitoring_file: Path to monitoring history file
        """
        self.monitoring_file = monitoring_file
        self.monitoring_history = []
        
        # Load existing history
        self.load_history()
    
    def load_history(self):
        """Load monitoring history from file"""
        try:
            with open(self.monitoring_file, 'r') as f:
                data = json.load(f)
                self.monitoring_history = data.get('monitoring_history', [])
            print(f"📂 Loaded {len(self.monitoring_history)} monitoring records")
        except FileNotFoundError:
            print("📂 No monitoring history found, starting fresh")
    
    def log_predictions(
        self,
        predictions: List[Dict],
        period_label: str = None
    ):
        """
        Log a batch of predictions for monitoring
        
        Args:
            predictions: List of prediction dictionaries with:
                         - predicted_prob
                         - actual_outcome (if available)
            period_label: Label for this period (e.g., "Week 1", "2024-10-20")
        """
        if period_label is None:
            period_label = datetime.now().strftime("%Y-%m-%d")
        
        # Extract predictions and actuals
        y_pred = [p['predicted_prob'] for p in predictions]
        y_true = [p.get('actual_outcome') for p in predictions if 'actual_outcome' in p]
        
        # Calculate metrics if we have actuals
        metrics = {}
        if y_true and len(y_true) == len(y_pred):
            y_pred_class = [1 if p > 0.5 else 0 for p in y_pred]
            
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred_class),
                'brier_score': brier_score_loss(y_true, y_pred),
                'log_loss': log_loss(y_true, y_pred),
                'total_predictions': len(predictions)
            }
        
        # Log monitoring record
        record = {
            'timestamp': datetime.now().isoformat(),
            'period_label': period_label,
            'total_predictions': len(predictions),
            'metrics': metrics
        }
        
        self.monitoring_history.append(record)
        self.save_history()
        
        print(f"✅ Logged {len(predictions)} predictions for {period_label}")
        if metrics:
            print(f"   Accuracy: {metrics['accuracy']:.1%}, Brier: {metrics['brier_score']:.4f}")
    
    def save_history(self):
        """Save monitoring history to file"""
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_records': len(self.monitoring_history),
            'monitoring_history': self.monitoring_history
        }
        
        with open(self.monitoring_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_model_degradation(
        self,
        baseline_accuracy: float = 0.668,
        baseline_brier: float = 0.2089,
        degradation_threshold: float = 0.05
    ) -> Dict:
        """
        Check if model performance has degraded
        
        Args:
            baseline_accuracy: Expected accuracy
            baseline_brier: Expected Brier score
            degradation_threshold: Threshold for degradation alert (5% default)
        
        Returns:
            Dictionary with degradation analysis
        """
        if not self.monitoring_history:
            return {'status': 'NO_DATA'}
        
        # Get recent records with metrics
        recent_records = [
            r for r in self.monitoring_history[-10:]
            if r['metrics']
        ]
        
        if not recent_records:
            return {'status': 'NO_METRICS'}
        
        # Calculate average recent performance
        avg_accuracy = np.mean([r['metrics']['accuracy'] for r in recent_records])
        avg_brier = np.mean([r['metrics']['brier_score'] for r in recent_records])
        
        # Check for degradation
        accuracy_drop = baseline_accuracy - avg_accuracy
        brier_increase = avg_brier - baseline_brier
        
        degraded = (accuracy_drop > degradation_threshold) or (brier_increase > degradation_threshold)
        
        return {
            'status': 'DEGRADED' if degraded else 'HEALTHY',
            'baseline_accuracy': baseline_accuracy,
            'recent_accuracy': avg_accuracy,
            'accuracy_drop': accuracy_drop,
            'baseline_brier': baseline_brier,
            'recent_brier': avg_brier,
            'brier_increase': brier_increase,
            'degradation_threshold': degradation_threshold
        }
    
    def print_monitoring_summary(self):
        """Print monitoring summary"""
        print("\n" + "=" * 70)
        print("📊 MODEL MONITORING SUMMARY")
        print("=" * 70)
        
        if not self.monitoring_history:
            print("\n⚠️  No monitoring data available")
            return
        
        # Get records with metrics
        records_with_metrics = [r for r in self.monitoring_history if r['metrics']]
        
        if not records_with_metrics:
            print("\n⚠️  No completed predictions to monitor")
            return
        
        print(f"\n📈 Monitoring History:")
        print(f"   Total Records: {len(self.monitoring_history)}")
        print(f"   Records with Metrics: {len(records_with_metrics)}")
        
        # Recent performance
        if records_with_metrics:
            recent = records_with_metrics[-5:]
            
            print(f"\n📊 Recent Performance (last {len(recent)} periods):")
            for r in recent:
                m = r['metrics']
                print(f"   {r['period_label']}: Accuracy={m['accuracy']:.1%}, Brier={m['brier_score']:.4f}")
        
        # Check degradation
        degradation = self.check_model_degradation()
        
        print(f"\n🔍 Model Health Check:")
        if degradation['status'] == 'HEALTHY':
            print(f"   ✅ Model is performing as expected")
        elif degradation['status'] == 'DEGRADED':
            print(f"   ⚠️  Model performance has degraded!")
            print(f"      Accuracy drop: {degradation['accuracy_drop']:.1%}")
            print(f"      Brier increase: {degradation['brier_increase']:.4f}")
            print(f"      Recommendation: Retrain model with recent data")
        else:
            print(f"   ℹ️  Not enough data to assess model health")
        
        print("\n" + "=" * 70)


def example_usage():
    """Example usage"""
    print("=" * 70)
    print("📊 MODEL MONITORING - EXAMPLE")
    print("=" * 70)
    
    # Initialize monitor
    monitor = ModelMonitor('example_model_monitoring.json')
    
    # Simulate logging predictions
    print("\n1️⃣  Logging predictions for Week 1...")
    week1_preds = [
        {'predicted_prob': 0.65, 'actual_outcome': 1},
        {'predicted_prob': 0.55, 'actual_outcome': 0},
        {'predicted_prob': 0.72, 'actual_outcome': 1},
        {'predicted_prob': 0.48, 'actual_outcome': 0},
        {'predicted_prob': 0.81, 'actual_outcome': 1},
    ]
    monitor.log_predictions(week1_preds, "Week 1")
    
    print("\n2️⃣  Logging predictions for Week 2...")
    week2_preds = [
        {'predicted_prob': 0.68, 'actual_outcome': 1},
        {'predicted_prob': 0.52, 'actual_outcome': 1},
        {'predicted_prob': 0.75, 'actual_outcome': 1},
        {'predicted_prob': 0.45, 'actual_outcome': 0},
    ]
    monitor.log_predictions(week2_preds, "Week 2")
    
    # Print summary
    monitor.print_monitoring_summary()
    
    print("\n✅ MODEL MONITORING EXAMPLE COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()

