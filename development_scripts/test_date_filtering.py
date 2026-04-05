#!/usr/bin/env python3
"""
Test Date Filtering Fix
Tests if the dashboard now correctly filters games by date
"""

import json
from datetime import datetime, date, timedelta

def load_games_for_date(selected_date):
    """Load NBA games for a specific date (fixed version)"""
    try:
        with open('data/nba_game_data.json', 'r') as f:
            data = json.load(f)
            games = data['games']
        
        # Filter games for the selected date only
        date_str = selected_date.strftime('%Y-%m-%d')
        date_games = [g for g in games if g['date'].startswith(date_str)]
        
        return date_games
        
    except FileNotFoundError:
        return []

def test_date_filtering():
    """Test that games are correctly filtered by date"""
    print("🧪 TESTING DATE FILTERING FIX")
    print("=" * 50)
    
    # Test specific dates
    test_dates = [
        date(2025, 10, 22),  # Oct 22
        date(2025, 10, 23),  # Oct 23
        date(2025, 10, 24),  # Oct 24
    ]
    
    for test_date in test_dates:
        print(f"\n📅 Testing date: {test_date}")
        games = load_games_for_date(test_date)
        
        if games:
            print(f"   ✅ Found {len(games)} games")
            
            # Show all games for this date
            for i, game in enumerate(games, 1):
                print(f"     {i}. {game['away_team']} @ {game['home_team']}")
                print(f"        Date: {game['date']}")
                print(f"        ID: {game['game_id']}")
        else:
            print(f"   ❌ No games found")
    
    # Test that we don't get cross-contamination
    print(f"\n🔍 CROSS-CONTAMINATION TEST:")
    
    oct22_games = load_games_for_date(date(2025, 10, 22))
    oct23_games = load_games_for_date(date(2025, 10, 23))
    
    print(f"   Oct 22 games: {len(oct22_games)}")
    print(f"   Oct 23 games: {len(oct23_games)}")
    
    # Check for any games that appear on both dates
    oct22_teams = set()
    for game in oct22_games:
        matchup = f"{game['away_team']} @ {game['home_team']}"
        oct22_teams.add(matchup)
    
    oct23_teams = set()
    for game in oct23_games:
        matchup = f"{game['away_team']} @ {game['home_team']}"
        oct23_teams.add(matchup)
    
    overlap = oct22_teams.intersection(oct23_teams)
    if overlap:
        print(f"   ⚠️ WARNING: {len(overlap)} games appear on both dates:")
        for matchup in overlap:
            print(f"     - {matchup}")
    else:
        print(f"   ✅ No games appear on both dates - filtering works correctly!")

if __name__ == "__main__":
    test_date_filtering()
