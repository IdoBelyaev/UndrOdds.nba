"""
Regenerate Elo Ratings from 2025-26 Season Only
===============================================

This script:
1. Loads games from data/nba_game_data.json
2. Filters to only 2025-26 season games (season "22025")
3. Only processes games that have been played (scores > 0)
4. Initializes all teams at 1500
5. Processes games chronologically
6. Saves new Elo ratings to data/elo_ratings.json
"""

import json
import sys
from pathlib import Path
from archive.elo_ratings import EloRatingSystem

def load_2025_26_season_games(filename: str = 'data/nba_game_data.json'):
    """Load only 2025-26 season games that have been played"""
    print("\n📂 Loading game data...")
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found")
        sys.exit(1)
    
    games = []
    for game in data['games']:
        # Filter: Only 2025-26 season
        if game.get('season') != '22025':
            continue
        
        # Filter: Only games that have been played (scores > 0)
        if game.get('home_score', 0) == 0 and game.get('away_score', 0) == 0:
            continue
        
        games.append({
            'game_id': game['game_id'],
            'date': game['date'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'home_score': game['home_score'],
            'away_score': game['away_score']
        })
    
    print(f"   ✅ Found {len(games)} played games from 2025-26 season")
    return games


def main():
    """Regenerate Elo ratings from 2025-26 season only"""
    print("=" * 70)
    print("🔄 REGENERATING ELO RATINGS - 2025-26 SEASON ONLY")
    print("=" * 70)
    
    # Load games
    games = load_2025_26_season_games()
    
    if not games:
        print("\n⚠️  No games found! Make sure:")
        print("   - Games have been played (scores > 0)")
        print("   - Season is '22025' (2025-26)")
        print("   - data/nba_game_data.json exists and is updated")
        return
    
    # Get all unique teams
    teams = set()
    for game in games:
        teams.add(game['home_team'])
        teams.add(game['away_team'])
    
    print(f"   ✅ Found {len(teams)} unique teams")
    
    # Initialize Elo system (all teams start at 1500)
    print("\n⚙️  Initializing Elo system...")
    elo = EloRatingSystem(
        k_factor=20.0,
        home_advantage=100.0,
        initial_rating=1500.0
    )
    
    elo.initialize_teams(list(teams))
    print(f"   ✅ Initialized {len(teams)} teams at {elo.initial_rating} Elo (fresh start)")
    
    # Process all games chronologically
    print("\n📊 Processing games chronologically...")
    elo.process_season(games, store_predictions=True)
    
    # Print summary
    print("\n" + "=" * 70)
    elo.print_summary()
    print("=" * 70)
    
    # Save new ratings
    output_file = 'data/elo_ratings.json'
    print(f"\n💾 Saving ratings to {output_file}...")
    elo.save_ratings(output_file)
    
    # Verify save
    if Path(output_file).exists():
        print(f"   ✅ Ratings saved successfully!")
        print(f"\n📊 Current Team Rankings (Top 10):")
        rankings = elo.get_current_rankings(top_n=10)
        for i, (team, rating) in enumerate(rankings, 1):
            print(f"   {i:2d}. {team:25s} {rating:7.1f}")
    else:
        print(f"   ❌ Error: Failed to save ratings")
    
    print("\n" + "=" * 70)
    print("✅ ELO RATINGS REGENERATED!")
    print("=" * 70)
    print(f"\n📝 Note: Dashboard will now use these fresh 2025-26 season ratings")
    print(f"   All teams started at 1500 and updated based on {len(games)} games played")


if __name__ == "__main__":
    main()


