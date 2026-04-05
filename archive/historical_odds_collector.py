"""
Historical Odds Collector
==========================

Collect real historical sportsbook odds:
- Manual historical odds database
- Odds data validation
- Historical odds storage

M3 Phase 4: Historical Odds Collection
"""

import json
from datetime import datetime
from typing import Dict, List


class HistoricalOddsCollector:
    """Collect and manage historical sportsbook odds"""
    
    def __init__(self, odds_file: str = 'historical_odds.json'):
        """Initialize historical odds collector"""
        self.odds_file = odds_file
        self.historical_odds = []
        self.load_odds()
    
    def load_odds(self):
        """Load historical odds from file"""
        try:
            with open(self.odds_file, 'r') as f:
                data = json.load(f)
                self.historical_odds = data.get('odds', [])
            print(f"📂 Loaded {len(self.historical_odds)} historical odds records")
        except FileNotFoundError:
            print("📂 No historical odds found, starting fresh")
    
    def add_odds(
        self,
        date: str,
        home_team: str,
        away_team: str,
        home_moneyline: int,
        away_moneyline: int,
        sportsbook: str = 'Underdog Fantasy'
    ):
        """
        Add historical odds record
        
        Args:
            date: Game date (YYYY-MM-DD)
            home_team: Home team name
            away_team: Away team name
            home_moneyline: Home team odds
            away_moneyline: Away team odds
            sportsbook: Sportsbook name
        """
        odds_record = {
            'date': date,
            'home_team': home_team,
            'away_team': away_team,
            'home_moneyline': home_moneyline,
            'away_moneyline': away_moneyline,
            'sportsbook': sportsbook,
            'added_timestamp': datetime.now().isoformat()
        }
        
        self.historical_odds.append(odds_record)
        self.save_odds()
        
        print(f"✅ Added odds: {home_team} vs {away_team} on {date}")
    
    def save_odds(self):
        """Save historical odds to file"""
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_records': len(self.historical_odds),
            'sportsbook': 'Underdog Fantasy',
            'odds': self.historical_odds
        }
        
        with open(self.odds_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_odds_for_date(self, date: str) -> List[Dict]:
        """Get all odds for a specific date"""
        return [o for o in self.historical_odds if o['date'] == date]
    
    def print_summary(self):
        """Print summary of historical odds"""
        print("\n" + "=" * 70)
        print("📊 HISTORICAL ODDS SUMMARY")
        print("=" * 70)
        
        print(f"\n📈 Total Records: {len(self.historical_odds)}")
        
        if self.historical_odds:
            # Get date range
            dates = [o['date'] for o in self.historical_odds]
            print(f"   Date Range: {min(dates)} to {max(dates)}")
            
            # Count by sportsbook
            sportsbooks = {}
            for o in self.historical_odds:
                sb = o.get('sportsbook', 'Unknown')
                sportsbooks[sb] = sportsbooks.get(sb, 0) + 1
            
            print(f"\n📊 By Sportsbook:")
            for sb, count in sportsbooks.items():
                print(f"   {sb}: {count} records")
        
        print("\n" + "=" * 70)


def main():
    """Example usage"""
    print("=" * 70)
    print("📊 HISTORICAL ODDS COLLECTOR")
    print("=" * 70)
    
    collector = HistoricalOddsCollector()
    
    print("\n💡 NOTE: Historical odds must be collected manually")
    print("   Options:")
    print("   1. Input past odds you tracked")
    print("   2. Use odds from underdog_moneylines.json")
    print("   3. Scrape historical odds (if available)")
    print()
    print("   For now, this provides the infrastructure.")
    print("   Add real odds as you collect them!")
    
    collector.print_summary()
    
    print("\n✅ HISTORICAL ODDS COLLECTOR READY!")
    print("=" * 70)


if __name__ == "__main__":
    main()

