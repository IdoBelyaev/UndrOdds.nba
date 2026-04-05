"""
Bet Tracking System
==================

Handles bet logging, result tracking, and performance analytics.
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class BetTracker:
    """Bet tracking and management system"""
    
    def __init__(self, history_file: str = 'bet_history.json'):
        """Initialize bet tracker"""
        self.history_file = history_file
        self.bankroll_history = []
        self.load_history()
    
    def load_history(self):
        """Load bet history from file"""
        try:
            with open(self.history_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            # Initialize empty history
            self.data = {
                'last_updated': datetime.now().isoformat(),
                'total_bets': 0,
                'bets': [],
                'bankroll_history': []
            }
            self.save_history()
    
    def save_history(self):
        """Save bet history to file"""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.history_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_bet(
        self,
        date: str,
        game: str,
        team: str,
        opponent: str,
        moneyline: int,
        bet_amount: float,
        win_probability: float,
        ev_percent: float,
        bankroll_before: float
    ) -> str:
        """
        Log a new bet
        
        Args:
            date: Game date
            game: Game description
            team: Team picked
            opponent: Opposing team
            moneyline: Moneyline odds
            bet_amount: Amount bet
            win_probability: Model's win probability
            ev_percent: Expected value percentage
            bankroll_before: Bankroll before bet
        
        Returns:
            Bet ID
        """
        bet_id = str(uuid.uuid4())[:8]
        
        bet = {
            'bet_id': bet_id,
            'date': date,
            'game': game,
            'team': team,
            'opponent': opponent,
            'moneyline': moneyline,
            'bet_amount': bet_amount,
            'win_probability': win_probability,
            'ev_percent': ev_percent,
            'bankroll_before': bankroll_before,
            'status': 'pending',
            'result': None,
            'profit': None,
            'bankroll_after': None,
            'timestamp': datetime.now().isoformat()
        }
        
        self.data['bets'].append(bet)
        self.data['total_bets'] = len(self.data['bets'])
        self.save_history()
        
        return bet_id
    
    def update_bet_result(self, bet_id: str, won: bool, new_bankroll: float):
        """
        Update bet result
        
        Args:
            bet_id: Bet ID
            won: Whether the bet won
            new_bankroll: Updated bankroll
        """
        for bet in self.data['bets']:
            if bet['bet_id'] == bet_id:
                bet['result'] = 'won' if won else 'lost'
                bet['status'] = 'won' if won else 'lost'
                
                # Calculate profit
                if won:
                    if bet['moneyline'] > 0:
                        profit = bet['bet_amount'] * (bet['moneyline'] / 100)
                    else:
                        profit = bet['bet_amount'] * (100 / abs(bet['moneyline']))
                else:
                    profit = -bet['bet_amount']
                
                bet['profit'] = profit
                bet['bankroll_after'] = new_bankroll
                
                # Add to bankroll history
                self.bankroll_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'bankroll': new_bankroll,
                    'bet_id': bet_id,
                    'profit': profit
                })
                
                break
        
        self.save_history()
    
    def get_bets_dataframe(self) -> pd.DataFrame:
        """Get all bets as DataFrame"""
        if not self.data['bets']:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.data['bets'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        if not self.data['bets']:
            return {
                'total_bets': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'roi': 0.0,
                'total_wagered': 0.0
            }
        
        df = self.get_bets_dataframe()
        settled_bets = df[df['status'].isin(['won', 'lost'])]
        
        if len(settled_bets) == 0:
            return {
                'total_bets': len(df),
                'win_rate': 0.0,
                'total_profit': 0.0,
                'roi': 0.0,
                'total_wagered': 0.0
            }
        
        total_bets = len(settled_bets)
        wins = len(settled_bets[settled_bets['status'] == 'won'])
        win_rate = wins / total_bets if total_bets > 0 else 0
        
        total_wagered = settled_bets['bet_amount'].sum()
        total_profit = settled_bets['profit'].sum()
        roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
        
        return {
            'total_bets': total_bets,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'roi': roi,
            'total_wagered': total_wagered
        }
    
    def get_pending_bets(self) -> List[Dict]:
        """Get all pending bets"""
        return [bet for bet in self.data['bets'] if bet['status'] == 'pending']
    
    def get_bet_by_id(self, bet_id: str) -> Optional[Dict]:
        """Get bet by ID"""
        for bet in self.data['bets']:
            if bet['bet_id'] == bet_id:
                return bet
        return None
    
    def delete_bet(self, bet_id: str) -> bool:
        """
        Delete a bet by ID
        
        Args:
            bet_id: Bet ID to delete
            
        Returns:
            True if bet was found and deleted, False otherwise
        """
        for i, bet in enumerate(self.data['bets']):
            if bet['bet_id'] == bet_id:
                # If bet hasn't been settled, refund the bet amount to bankroll
                if bet['status'] == 'pending':
                    # Note: This doesn't automatically update bankroll, 
                    # but the bet amount is stored in bet['bet_amount']
                    pass
                
                # Remove the bet
                del self.data['bets'][i]
                self.data['total_bets'] = len(self.data['bets'])
                self.save_history()
                return True
        
        return False