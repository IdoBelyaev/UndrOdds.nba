#!/usr/bin/env python3
"""
Quick Data Check
Fast way to verify your data is correct before using the dashboard
"""

import json
from datetime import datetime, date

def quick_check():
    """Quick check of all data"""
    print("🔍 QUICK DATA CHECK")
    print("=" * 30)
    
    # Check game data
    try:
        with open('data/nba_game_data.json', 'r') as f:
            game_data = json.load(f)
        games = game_data.get('games', [])
        print(f"✅ Games: {len(games)} total")
        
        # Check today's games
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        today_games = [g for g in games if g['date'].startswith(today_str)]
        print(f"✅ Today ({today_str}): {len(today_games)} games")
        
    except Exception as e:
        print(f"❌ Game data error: {e}")
    
    # Check team data
    try:
        with open('data/nba_team_data.json', 'r') as f:
            team_data = json.load(f)
        teams = team_data.get('teams', [])
        print(f"✅ Teams: {len(teams)}/30")
    except Exception as e:
        print(f"❌ Team data error: {e}")
    
    # Check injury data
    try:
        with open('data/nba_injury_data.json', 'r') as f:
            injury_data = json.load(f)
        injuries = injury_data.get('injuries', [])
        status_summary = injury_data.get('metadata', {}).get('injury_status_summary', {})
        print(f"✅ Injuries: {len(injuries)} players")
        print(f"   Status: {status_summary}")
    except Exception as e:
        print(f"❌ Injury data error: {e}")
    
    print(f"\n🎯 Ready to use dashboard!")

if __name__ == "__main__":
    quick_check()
