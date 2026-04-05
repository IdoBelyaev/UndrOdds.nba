"""
Flask API Server for NBA Betting System
Provides REST API endpoints for the macOS app
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date, timedelta
import json
import pandas as pd
import numpy as np
from pathlib import Path
import pickle

# Import existing modules
from bet_tracker import BetTracker
from ev_calculator import EVCalculator
from elo_ratings import EloSystem

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
bet_tracker = BetTracker()
ev_calc = EVCalculator()

def load_model():
    """Load the trained model and calibrator"""
    model_path = Path('models/logistic_model.pkl')
    calibrator_path = Path('models/calibrator.pkl')
    
    if not model_path.exists() or not calibrator_path.exists():
        return None
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(calibrator_path, 'rb') as f:
        calibrator = pickle.load(f)
    
    return {'model': model, 'calibrator': calibrator}

def load_elo_ratings():
    """Load current Elo ratings"""
    elo_file = Path('data/current_elo_ratings.json')
    if elo_file.exists():
        with open(elo_file, 'r') as f:
            return json.load(f)
    return {}

def load_games_for_date(date_str):
    """Load games for a specific date"""
    games_file = Path('data/nba_games.json')
    if not games_file.exists():
        return []
    
    with open(games_file, 'r') as f:
        games = json.load(f)
    
    # Filter games for the specified date
    filtered_games = [g for g in games if g.get('date') == date_str]
    return filtered_games

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/games/<date_str>', methods=['GET'])
def get_games(date_str):
    """Get games for a specific date"""
    try:
        games = load_games_for_date(date_str)
        return jsonify({
            'success': True,
            'date': date_str,
            'games': games,
            'count': len(games)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/picks', methods=['POST'])
def get_picks():
    """
    Calculate picks for games with odds
    
    Request body:
    {
        "date": "13-10-2025",
        "games": [
            {
                "home_team": "Los Angeles Lakers",
                "away_team": "Golden State Warriors",
                "home_ml": 203,
                "away_ml": -271
            }
        ],
        "min_ev": 0.05,
        "bet_amount": 20
    }
    """
    try:
        data = request.json
        games = data.get('games', [])
        min_ev = data.get('min_ev', 0.05)
        bet_amount = data.get('bet_amount', 20)
        
        model_data = load_model()
        if not model_data:
            return jsonify({
                'success': False,
                'error': 'Model not found'
            }), 500
        
        elo_ratings = load_elo_ratings()
        recommendations = []
        
        for game in games:
            home_team = game['home_team']
            away_team = game['away_team']
            home_ml = game['home_ml']
            away_ml = game['away_ml']
            
            # Get Elo ratings
            home_elo = elo_ratings.get(home_team, 1500)
            away_elo = elo_ratings.get(away_team, 1500)
            
            # Calculate win probability (simplified - using Elo)
            elo_diff = home_elo - away_elo + 50  # +50 for home court
            home_win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
            away_win_prob = 1 - home_win_prob
            
            # Calculate EV for home team
            if home_ml != 0:
                home_decimal_odds = ev_calc.moneyline_to_decimal(home_ml)
                home_ev = ev_calc.calculate_ev(home_win_prob, home_decimal_odds)
                
                if home_ev > min_ev:
                    expected_profit = bet_amount * home_ev
                    recommendations.append({
                        'game': f"{home_team} vs {away_team}",
                        'pick': home_team,
                        'odds': home_ml,
                        'win_probability': round(home_win_prob * 100, 1),
                        'ev': round(home_ev * 100, 2),
                        'bet_amount': bet_amount,
                        'expected_profit': round(expected_profit, 2),
                        'potential_return': round(bet_amount * home_decimal_odds, 2)
                    })
            
            # Calculate EV for away team
            if away_ml != 0:
                away_decimal_odds = ev_calc.moneyline_to_decimal(away_ml)
                away_ev = ev_calc.calculate_ev(away_win_prob, away_decimal_odds)
                
                if away_ev > min_ev:
                    expected_profit = bet_amount * away_ev
                    recommendations.append({
                        'game': f"{home_team} vs {away_team}",
                        'pick': away_team,
                        'odds': away_ml,
                        'win_probability': round(away_win_prob * 100, 1),
                        'ev': round(away_ev * 100, 2),
                        'bet_amount': bet_amount,
                        'expected_profit': round(expected_profit, 2),
                        'potential_return': round(bet_amount * away_decimal_odds, 2)
                    })
        
        # Sort by EV
        recommendations.sort(key=lambda x: x['ev'], reverse=True)
        
        return jsonify({
            'success': True,
            'picks': recommendations,
            'count': len(recommendations)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bets', methods=['GET'])
def get_bets():
    """Get all bets from history"""
    try:
        history_file = Path('bet_history.json')
        if not history_file.exists():
            return jsonify({
                'success': True,
                'bets': [],
                'count': 0
            })
        
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        bets = data.get('bets', [])
        
        return jsonify({
            'success': True,
            'bets': bets,
            'count': len(bets)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bets', methods=['POST'])
def save_bet():
    """Save a new bet"""
    try:
        bet_data = request.json
        
        bet_tracker.log_bet(
            game_id=bet_data.get('game_id', ''),
            date=bet_data['date'],
            home_team=bet_data['home_team'],
            away_team=bet_data['away_team'],
            pick=bet_data['pick'],
            odds=bet_data['odds'],
            bet_amount=bet_data['bet_amount']
        )
        
        return jsonify({
            'success': True,
            'message': 'Bet saved successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bets/<bet_id>/result', methods=['PUT'])
def update_bet_result(bet_id):
    """Update bet result (won/lost)"""
    try:
        result_data = request.json
        won = result_data['won']
        
        bet_tracker.update_bet_result(bet_id, won)
        
        return jsonify({
            'success': True,
            'message': 'Bet result updated'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get betting statistics"""
    try:
        history_file = Path('bet_history.json')
        if not history_file.exists():
            return jsonify({
                'success': True,
                'stats': {
                    'total_bets': 0,
                    'wins': 0,
                    'losses': 0,
                    'win_rate': 0,
                    'total_profit': 0,
                    'roi': 0,
                    'current_bankroll': 1000
                }
            })
        
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        bets = data.get('bets', [])
        total_bets = len([b for b in bets if b.get('result') is not None])
        wins = len([b for b in bets if b.get('result') == 'won'])
        losses = len([b for b in bets if b.get('result') == 'lost'])
        
        total_wagered = sum(b.get('amount', 0) for b in bets if b.get('result') is not None)
        total_return = sum(b.get('return', 0) for b in bets if b.get('result') == 'won')
        total_profit = total_return - total_wagered
        
        win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
        roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_bets': total_bets,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 1),
                'total_profit': round(total_profit, 2),
                'roi': round(roi, 1),
                'current_bankroll': data.get('bankroll', 1000)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/elo-rankings', methods=['GET'])
def get_elo_rankings():
    """Get current Elo rankings"""
    try:
        elo_ratings = load_elo_ratings()
        
        # Convert to list and sort
        rankings = [
            {'team': team, 'rating': rating}
            for team, rating in elo_ratings.items()
        ]
        rankings.sort(key=lambda x: x['rating'], reverse=True)
        
        return jsonify({
            'success': True,
            'rankings': rankings
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 80)
    print("🏀 NBA Betting API Server")
    print("=" * 80)
    print()
    print("Starting Flask API server on http://localhost:5000")
    print()
    print("Available endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/games/<date>        - Get games for date")
    print("  POST /api/picks               - Calculate picks")
    print("  GET  /api/bets                - Get all bets")
    print("  POST /api/bets                - Save new bet")
    print("  PUT  /api/bets/<id>/result    - Update bet result")
    print("  GET  /api/stats               - Get statistics")
    print("  GET  /api/elo-rankings        - Get Elo rankings")
    print()
    print("=" * 80)
    
    app.run(host='localhost', port=5000, debug=True)

