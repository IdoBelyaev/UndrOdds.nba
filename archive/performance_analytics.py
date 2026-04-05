"""
Performance Analytics
=====================

Analyze betting performance:
- ROI calculation (daily, weekly, monthly)
- Win rate analysis
- Profit/loss charts
- Bankroll growth visualization
- Performance vs expectations

M3 Phase 2: Performance Analytics
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List
from bet_tracker import BetTracker


class PerformanceAnalytics:
    """Analyze betting performance"""
    
    def __init__(self, bet_tracker: BetTracker):
        """
        Initialize performance analytics
        
        Args:
            bet_tracker: BetTracker instance with bet history
        """
        self.tracker = bet_tracker
        self.df = self.tracker.get_bets_dataframe()
    
    def calculate_roi_by_period(self) -> Dict:
        """Calculate ROI by time period"""
        if self.df.empty:
            return {}
        
        # Filter settled bets
        settled = self.df[self.df['status'].isin(['won', 'lost'])].copy()
        
        if settled.empty:
            return {}
        
        # Convert date to datetime
        settled['date'] = pd.to_datetime(settled['date'])
        
        # Calculate daily ROI
        daily_stats = settled.groupby(settled['date'].dt.date).agg({
            'bet_amount': 'sum',
            'profit': 'sum'
        })
        daily_stats['roi'] = (daily_stats['profit'] / daily_stats['bet_amount']) * 100
        
        # Calculate weekly ROI
        settled['week'] = settled['date'].dt.to_period('W')
        weekly_stats = settled.groupby('week').agg({
            'bet_amount': 'sum',
            'profit': 'sum'
        })
        weekly_stats['roi'] = (weekly_stats['profit'] / weekly_stats['bet_amount']) * 100
        
        # Calculate monthly ROI
        settled['month'] = settled['date'].dt.to_period('M')
        monthly_stats = settled.groupby('month').agg({
            'bet_amount': 'sum',
            'profit': 'sum'
        })
        monthly_stats['roi'] = (monthly_stats['profit'] / monthly_stats['bet_amount']) * 100
        
        return {
            'daily': daily_stats.to_dict('index'),
            'weekly': weekly_stats.to_dict('index'),
            'monthly': monthly_stats.to_dict('index')
        }
    
    def calculate_win_rate_analysis(self) -> Dict:
        """Analyze win rate by different factors"""
        if self.df.empty:
            return {}
        
        settled = self.df[self.df['status'].isin(['won', 'lost'])].copy()
        
        if settled.empty:
            return {}
        
        # Overall win rate
        overall_win_rate = (settled['status'] == 'won').mean()
        
        # Win rate by odds type (favorite vs underdog)
        settled['odds_type'] = settled['moneyline'].apply(
            lambda x: 'favorite' if x < 0 else 'underdog'
        )
        win_rate_by_odds = settled.groupby('odds_type').apply(
            lambda x: (x['status'] == 'won').mean()
        ).to_dict()
        
        # Win rate by EV range
        settled['ev_range'] = pd.cut(
            settled['ev_percent'],
            bins=[0, 5, 10, 20, 100],
            labels=['0-5%', '5-10%', '10-20%', '20%+']
        )
        win_rate_by_ev = settled.groupby('ev_range', observed=True).apply(
            lambda x: (x['status'] == 'won').mean()
        ).to_dict()
        
        return {
            'overall': overall_win_rate,
            'by_odds_type': win_rate_by_odds,
            'by_ev_range': {str(k): v for k, v in win_rate_by_ev.items()}
        }
    
    def plot_bankroll_growth(self, save_path: str = 'bankroll_growth.png'):
        """Plot bankroll growth over time"""
        if not self.tracker.bankroll_history:
            print("   ⚠️  No bankroll history to plot")
            return
        
        # Extract data
        timestamps = [datetime.fromisoformat(h['timestamp']) for h in self.tracker.bankroll_history]
        bankrolls = [h['bankroll'] for h in self.tracker.bankroll_history]
        
        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, bankrolls, 'b-', linewidth=2, marker='o', markersize=4)
        plt.axhline(y=bankrolls[0], color='gray', linestyle='--', label='Starting Bankroll')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Bankroll ($)', fontsize=12)
        plt.title('Bankroll Growth Over Time', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        print(f"   📊 Bankroll growth chart saved to: {save_path}")
    
    def plot_profit_loss_distribution(self, save_path: str = 'profit_loss_dist.png'):
        """Plot profit/loss distribution"""
        if self.df.empty:
            return
        
        settled = self.df[self.df['status'].isin(['won', 'lost'])].copy()
        
        if settled.empty:
            return
        
        # Plot
        plt.figure(figsize=(10, 6))
        
        wins = settled[settled['status'] == 'won']['profit']
        losses = settled[settled['status'] == 'lost']['profit']
        
        plt.hist([wins, losses], bins=20, label=['Wins', 'Losses'], color=['green', 'red'], alpha=0.7)
        plt.xlabel('Profit/Loss ($)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Profit/Loss Distribution', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        print(f"   📊 Profit/loss distribution saved to: {save_path}")
    
    def plot_cumulative_profit(self, save_path: str = 'cumulative_profit.png'):
        """Plot cumulative profit over time"""
        if self.df.empty:
            return
        
        settled = self.df[self.df['status'].isin(['won', 'lost'])].copy()
        
        if settled.empty:
            return
        
        # Sort by timestamp
        settled = settled.sort_values('timestamp')
        settled['cumulative_profit'] = settled['profit'].cumsum()
        
        # Plot
        plt.figure(figsize=(12, 6))
        plt.plot(range(len(settled)), settled['cumulative_profit'], 'g-', linewidth=2)
        plt.axhline(y=0, color='gray', linestyle='--', label='Breakeven')
        plt.fill_between(
            range(len(settled)),
            settled['cumulative_profit'],
            0,
            where=(settled['cumulative_profit'] >= 0),
            alpha=0.3,
            color='green',
            label='Profit'
        )
        plt.fill_between(
            range(len(settled)),
            settled['cumulative_profit'],
            0,
            where=(settled['cumulative_profit'] < 0),
            alpha=0.3,
            color='red',
            label='Loss'
        )
        plt.xlabel('Bet Number', fontsize=12)
        plt.ylabel('Cumulative Profit ($)', fontsize=12)
        plt.title('Cumulative Profit Over Time', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        print(f"   📊 Cumulative profit chart saved to: {save_path}")
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        print("\n" + "=" * 70)
        print("📊 PERFORMANCE ANALYTICS REPORT")
        print("=" * 70)
        
        # Get summary stats
        stats = self.tracker.get_summary_stats()
        
        print(f"\n📈 Overall Performance:")
        print(f"   Total Bets: {stats['total_bets']}")
        print(f"   Win Rate: {stats['win_rate']:.1%}")
        print(f"   Total Wagered: ${stats['total_wagered']:,.2f}")
        print(f"   Total Profit: ${stats['total_profit']:+,.2f}")
        print(f"   ROI: {stats['roi']:+.1f}%")
        
        # ROI by period
        print(f"\n📅 ROI by Period:")
        roi_periods = self.calculate_roi_by_period()
        
        if 'daily' in roi_periods and roi_periods['daily']:
            avg_daily_roi = np.mean([v['roi'] for v in roi_periods['daily'].values()])
            print(f"   Average Daily ROI: {avg_daily_roi:+.1f}%")
        
        if 'weekly' in roi_periods and roi_periods['weekly']:
            avg_weekly_roi = np.mean([v['roi'] for v in roi_periods['weekly'].values()])
            print(f"   Average Weekly ROI: {avg_weekly_roi:+.1f}%")
        
        # Win rate analysis
        print(f"\n🎯 Win Rate Analysis:")
        win_rate_analysis = self.calculate_win_rate_analysis()
        
        if 'by_odds_type' in win_rate_analysis:
            for odds_type, wr in win_rate_analysis['by_odds_type'].items():
                print(f"   {odds_type.capitalize()}: {wr:.1%}")
        
        if 'by_ev_range' in win_rate_analysis:
            print(f"\n   By EV Range:")
            for ev_range, wr in win_rate_analysis['by_ev_range'].items():
                print(f"      {ev_range}: {wr:.1%}")
        
        # Generate charts
        print(f"\n📊 Generating visualizations...")
        self.plot_bankroll_growth()
        self.plot_profit_loss_distribution()
        self.plot_cumulative_profit()
        
        print("\n" + "=" * 70)
        
        # Save report (convert all keys to strings)
        def convert_for_json(obj):
            if isinstance(obj, dict):
                return {str(k): convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            else:
                return obj
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary_stats': convert_for_json(stats),
            'roi_by_period': convert_for_json(roi_periods),
            'win_rate_analysis': convert_for_json(win_rate_analysis)
        }
        
        with open('performance_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n💾 Performance report saved to: performance_report.json")
        
        return report


def example_usage():
    """Example usage with sample data"""
    print("=" * 70)
    print("📊 PERFORMANCE ANALYTICS - EXAMPLE")
    print("=" * 70)
    
    # Load bet tracker with example data
    tracker = BetTracker('example_bet_history.json')
    
    # Create analytics
    analytics = PerformanceAnalytics(tracker)
    
    # Generate report
    report = analytics.generate_performance_report()
    
    print("\n✅ PERFORMANCE ANALYTICS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()

