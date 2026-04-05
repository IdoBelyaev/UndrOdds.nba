"""
Logistic Regression Model Training
===================================

Train logistic regression model for NBA game prediction using:
- Elo ratings
- Rest days
- Recent form
- Injury impact
- Home court advantage

M2 Phase 2: Model Training
"""

import json
import numpy as np
import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, cross_val_predict, TimeSeriesSplit
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from typing import Dict, List, Tuple


class NBAGamePredictor:
    """Logistic regression model for NBA game prediction"""
    
    def __init__(self):
        """Initialize model"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.training_history = []
    
    def load_features(self, filename: str = 'nba_features.csv') -> pd.DataFrame:
        """Load feature dataset"""
        df = pd.read_csv(filename)
        print(f"\n📂 Loaded {len(df)} games with {len(df.columns)} columns")
        return df
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        feature_cols: List[str] = None
    ) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Prepare data for training
        
        Args:
            df: Feature dataframe
            feature_cols: List of feature column names (None = use all numeric)
        
        Returns:
            (X, y, df_clean)
        """
        # Default feature columns
        if feature_cols is None:
            feature_cols = [
                'elo_diff',
                'rest_diff',
                'form_diff',
                'injury_diff',
                'home_court'
            ]
        
        self.feature_names = feature_cols
        
        # Extract features and target
        X = df[feature_cols].values
        y = df['home_win'].values
        
        print(f"\n📊 Using {len(feature_cols)} features:")
        for feat in feature_cols:
            print(f"   • {feat}")
        
        return X, y, df
    
    def train_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        C: float = 1.0,
        use_scaling: bool = True
    ):
        """
        Train logistic regression model
        
        Args:
            X: Feature matrix
            y: Target vector
            C: Regularization strength (smaller = more regularization)
            use_scaling: Whether to scale features
        """
        print(f"\n🔧 Training logistic regression (C={C})...")
        
        # Scale features if requested
        if use_scaling:
            X_scaled = self.scaler.fit_transform(X)
            print("   ✅ Features scaled (StandardScaler)")
        else:
            X_scaled = X
        
        # Train model
        self.model = LogisticRegression(
            C=C,
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
        
        self.model.fit(X_scaled, y)
        print("   ✅ Model trained")
        
        # Print feature importance (coefficients)
        print("\n📊 Feature Coefficients:")
        for feat, coef in zip(self.feature_names, self.model.coef_[0]):
            print(f"   {feat:20s}: {coef:7.4f}")
    
    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cv: int = 5,
        use_time_series: bool = True
    ) -> Dict:
        """
        Perform cross-validation
        
        Args:
            X: Feature matrix
            y: Target vector
            cv: Number of folds
            use_time_series: Use TimeSeriesSplit (respects temporal order)
        
        Returns:
            Dictionary of CV results
        """
        print(f"\n🔄 Running {cv}-fold cross-validation...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Choose CV strategy
        if use_time_series:
            cv_splitter = TimeSeriesSplit(n_splits=cv)
            print(f"   Using TimeSeriesSplit (respects temporal order)")
        else:
            cv_splitter = cv
        
        # Calculate metrics
        accuracy_scores = cross_val_score(
            self.model, X_scaled, y,
            cv=cv_splitter,
            scoring='accuracy'
        )
        
        # Get predictions for all folds
        # Note: cross_val_predict doesn't work with TimeSeriesSplit for predict_proba
        # So we'll manually collect predictions
        y_pred_proba = np.zeros(len(y))
        
        for train_idx, test_idx in cv_splitter.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train = y[train_idx]
            
            # Train on this fold
            fold_model = LogisticRegression(C=self.model.C, max_iter=1000, random_state=42, solver='lbfgs')
            fold_model.fit(X_train, y_train)
            
            # Predict on test fold
            y_pred_proba[test_idx] = fold_model.predict_proba(X_test)[:, 1]
        
        # Calculate Brier score
        brier = brier_score_loss(y, y_pred_proba)
        
        # Calculate log loss
        logloss = log_loss(y, y_pred_proba)
        
        # Calculate AUC
        auc = roc_auc_score(y, y_pred_proba)
        
        results = {
            'accuracy_mean': accuracy_scores.mean(),
            'accuracy_std': accuracy_scores.std(),
            'accuracy_scores': accuracy_scores.tolist(),
            'brier_score': brier,
            'log_loss': logloss,
            'auc': auc
        }
        
        print(f"\n📊 Cross-Validation Results:")
        print(f"   Accuracy: {results['accuracy_mean']:.1%} ± {results['accuracy_std']:.1%}")
        print(f"   Brier Score: {results['brier_score']:.4f}")
        print(f"   Log Loss: {results['log_loss']:.4f}")
        print(f"   AUC: {results['auc']:.4f}")
        
        return results
    
    def evaluate_on_test(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict:
        """
        Evaluate model on test set
        
        Args:
            X: Feature matrix
            y: Target vector
        
        Returns:
            Dictionary of evaluation metrics
        """
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predictions
        y_pred = self.model.predict(X_scaled)
        y_pred_proba = self.model.predict_proba(X_scaled)[:, 1]
        
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
        
        return results
    
    def save_model(self, filename: str = 'nba_model.pkl'):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'training_date': datetime.now().isoformat()
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved to: {filename}")
    
    def load_model(self, filename: str = 'nba_model.pkl'):
        """Load trained model"""
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        
        print(f"\n📂 Model loaded from: {filename}")
    
    def predict_game(self, features: Dict) -> Dict:
        """
        Predict outcome for a single game
        
        Args:
            features: Dictionary of features
        
        Returns:
            Dictionary with predictions
        """
        # Convert features to array
        X = np.array([[features[feat] for feat in self.feature_names]])
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        home_win_prob = self.model.predict_proba(X_scaled)[0, 1]
        away_win_prob = 1.0 - home_win_prob
        
        return {
            'home_win_prob': home_win_prob,
            'away_win_prob': away_win_prob
        }


def compare_with_elo_baseline(model_results: Dict, elo_results: Dict):
    """Compare model performance with Elo baseline"""
    print("\n" + "=" * 70)
    print("📊 MODEL vs ELO BASELINE COMPARISON")
    print("=" * 70)
    
    print(f"\n{'Metric':<20s} {'Elo Baseline':<15s} {'Logistic Model':<15s} {'Improvement':<15s}")
    print("-" * 70)
    
    # Accuracy
    elo_acc = elo_results['accuracy']
    model_acc = model_results['accuracy_mean']
    acc_diff = model_acc - elo_acc
    acc_symbol = "✅" if acc_diff > 0 else "⚠️"
    print(f"{'Accuracy':<20s} {elo_acc:<15.1%} {model_acc:<15.1%} {acc_symbol} {acc_diff:+.1%}")
    
    # Brier Score
    elo_brier = elo_results['brier_score']
    model_brier = model_results['brier_score']
    brier_diff = elo_brier - model_brier  # Lower is better, so flip sign
    brier_symbol = "✅" if brier_diff > 0 else "⚠️"
    print(f"{'Brier Score':<20s} {elo_brier:<15.4f} {model_brier:<15.4f} {brier_symbol} {brier_diff:+.4f}")
    
    # Log Loss
    elo_logloss = elo_results['log_loss']
    model_logloss = model_results['log_loss']
    logloss_diff = elo_logloss - model_logloss  # Lower is better
    logloss_symbol = "✅" if logloss_diff > 0 else "⚠️"
    print(f"{'Log Loss':<20s} {elo_logloss:<15.4f} {model_logloss:<15.4f} {logloss_symbol} {logloss_diff:+.4f}")
    
    print("\n" + "=" * 70)
    
    # Check RFC target
    rfc_brier_target = 0.19
    if model_brier <= rfc_brier_target:
        print(f"🎉 SUCCESS! Brier score {model_brier:.4f} ≤ {rfc_brier_target} (RFC target)")
    else:
        print(f"⚠️  Close! Brier score {model_brier:.4f} > {rfc_brier_target} (RFC target)")
        print(f"   Need to improve by {model_brier - rfc_brier_target:.4f}")
    
    print("=" * 70)


def main():
    """Run model training pipeline"""
    print("=" * 70)
    print("🤖 NBA LOGISTIC REGRESSION MODEL TRAINING")
    print("=" * 70)
    
    # Initialize predictor
    predictor = NBAGamePredictor()
    
    # Load features
    df = predictor.load_features('nba_features.csv')
    
    # Prepare data
    X, y, df_clean = predictor.prepare_data(df)
    
    # Train model
    predictor.train_model(X, y, C=1.0, use_scaling=True)
    
    # Cross-validate
    cv_results = predictor.cross_validate(X, y, cv=5, use_time_series=True)
    
    # Load Elo baseline results for comparison
    with open('elo_baseline_report.json', 'r') as f:
        elo_baseline = json.load(f)
    
    # Compare with Elo baseline
    compare_with_elo_baseline(cv_results, elo_baseline['performance'])
    
    # Save model
    predictor.save_model('nba_model.pkl')
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'model_type': 'LogisticRegression',
        'features': predictor.feature_names,
        'cross_validation': cv_results,
        'comparison_with_elo': {
            'elo_accuracy': elo_baseline['performance']['accuracy'],
            'model_accuracy': cv_results['accuracy_mean'],
            'accuracy_improvement': cv_results['accuracy_mean'] - elo_baseline['performance']['accuracy'],
            'elo_brier': elo_baseline['performance']['brier_score'],
            'model_brier': cv_results['brier_score'],
            'brier_improvement': elo_baseline['performance']['brier_score'] - cv_results['brier_score']
        }
    }
    
    with open('model_training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to: model_training_results.json")
    
    print("\n✅ MODEL TRAINING COMPLETE!")
    print("=" * 70)
    
    return predictor, cv_results


if __name__ == "__main__":
    main()

