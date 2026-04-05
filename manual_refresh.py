#!/usr/bin/env python3
"""
Manual Data Refresh - Get Latest NBA Data
"""

import json
from datetime import datetime
from game_data_fetch import main as fetch_games

def main():
    print("🔄 MANUAL NBA DATA REFRESH")
    print("=" * 40)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch latest game data
    print("\n📡 Fetching latest game data...")
    try:
        fetch_games()
        success = True
    except Exception as e:
        print(f"❌ Error fetching games: {e}")
        success = False
    
    if success:
        print("✅ Game data refresh completed successfully")
        
        # Check the updated data
        try:
            with open('data/nba_game_data.json', 'r') as f:
                data = json.load(f)
            
            print(f"\n📊 Updated Data Summary:")
            print(f"   Export Date: {data['metadata']['export_date']}")
            print(f"   Total Games: {data['metadata']['total_games']}")
            print(f"   Date Range: {data['metadata']['date_range']['start']} to {data['metadata']['date_range']['end']}")
            
            # Check for recent games with scores
            games = data['games']
            recent_games = [g for g in games if '2025-10-22' in g['date']]
            completed_games = [g for g in recent_games if g.get('away_score', 0) > 0 and g.get('home_score', 0) > 0]
            
            print(f"\n🎮 Today's Games (Oct 22):")
            print(f"   Total: {len(recent_games)}")
            print(f"   Completed: {len(completed_games)}")
            
            if completed_games:
                print(f"\n🏀 Sample Completed Games:")
                for game in completed_games[:3]:
                    print(f"   {game['away_team']} @ {game['home_team']}: {game['away_score']}-{game['home_score']}")
            
        except Exception as e:
            print(f"❌ Error reading updated data: {e}")
    else:
        print("❌ Game data refresh failed")

if __name__ == "__main__":
    main()
