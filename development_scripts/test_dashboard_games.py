#!/usr/bin/env python3
"""
Test Dashboard Game Loading
Tests if the dashboard can correctly load games for different dates
"""

import json
from datetime import datetime, timedelta, date

def load_games_for_date(selected_date):
    """Load NBA games for a specific date (copied from dashboard.py)"""
    try:
        with open('data/nba_game_data.json', 'r') as f:
            data = json.load(f)
            games = data['games']
        
        # Filter games for the selected date
        date_str = selected_date.strftime('%Y-%m-%d')
        today = datetime.now().date()
        
        if selected_date == today:
            # For today, show all games regardless of exact date (handles timezone differences)
            # Games might be on 2025-10-22 or 2025-10-23 due to timezone differences
            date_games = []
            for game in games:
                game_date = game['date'][:10]  # Get just the date part
                # Include games from today or tomorrow (for late games)
                if game_date == date_str or game_date == (selected_date + timedelta(days=1)).strftime('%Y-%m-%d'):
                    date_games.append(game)
        else:
            # For other dates, filter normally
            date_games = [g for g in games if g['date'].startswith(date_str)]
        
        return date_games
        
    except FileNotFoundError:
        return []

def test_dashboard_games():
    """Test dashboard game loading for different dates"""
    print("🧪 TESTING DASHBOARD GAME LOADING")
    print("=" * 50)
    
    # Test different dates
    test_dates = [
        date.today(),  # Today
        date.today() + timedelta(days=1),  # Tomorrow
        date.today() + timedelta(days=7),  # Next week
        date.today() + timedelta(days=14),  # Two weeks
        date.today() + timedelta(days=30),  # One month
    ]
    
    for test_date in test_dates:
        print(f"\n📅 Testing date: {test_date}")
        games = load_games_for_date(test_date)
        
        if games:
            print(f"   ✅ Found {len(games)} games")
            
            # Show first few games
            for i, game in enumerate(games[:3]):
                print(f"     {i+1}. {game['away_team']} @ {game['home_team']}")
                print(f"        Score: {game['away_score']} - {game['home_score']}")
                print(f"        Status: {game['status']}")
            
            if len(games) > 3:
                print(f"     ... and {len(games) - 3} more games")
        else:
            print(f"   ❌ No games found")
    
    # Test the data file
    print(f"\n📊 DATA FILE SUMMARY:")
    try:
        with open('data/nba_game_data.json', 'r') as f:
            data = json.load(f)
            metadata = data['metadata']
            games = data['games']
            
            print(f"   Total games: {metadata['total_games']}")
            print(f"   Date range: {metadata['date_range']['start']} to {metadata['date_range']['end']}")
            print(f"   Data source: {metadata['data_source']}")
            print(f"   Export date: {metadata['export_date']}")
            
            # Show games by date
            games_by_date = {}
            for game in games:
                game_date = game['date'][:10]
                if game_date not in games_by_date:
                    games_by_date[game_date] = 0
                games_by_date[game_date] += 1
            
            print(f"\n   Games by date (first 10):")
            for date_key in sorted(games_by_date.keys())[:10]:
                print(f"     {date_key}: {games_by_date[date_key]} games")
            
            if len(games_by_date) > 10:
                print(f"     ... and {len(games_by_date) - 10} more dates")
                
    except Exception as e:
        print(f"   ❌ Error reading data file: {e}")

if __name__ == "__main__":
    test_dashboard_games()
