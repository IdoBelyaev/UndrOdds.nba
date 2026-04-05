#!/usr/bin/env python3
"""
Remove Sample Games Script
Removes the test games added for 2025-26 Opening Night
"""

import json

def remove_sample_games():
    """Remove sample games from the database"""
    
    # Load current data
    with open('data/nba_game_data.json', 'r') as f:
        data = json.load(f)
    
    # Count games before removal
    total_before = len(data['games'])
    
    # Remove sample games (they have game_id starting with "00225")
    original_games = [g for g in data['games'] if not g['game_id'].startswith('00225')]
    
    # Count games after removal
    total_after = len(original_games)
    removed_count = total_before - total_after
    
    # Update the data
    data['games'] = original_games
    
    # Update metadata
    data['metadata']['total_games'] = total_after
    data['metadata']['export_date'] = '2025-10-12T22:50:00'
    data['metadata']['data_source'] = 'NBA Stats API - LeagueGameFinder'
    
    # Save updated data
    with open('data/nba_game_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Removed {removed_count} sample games")
    print(f"📊 Total games now: {total_after}")
    print("🗑️  Sample games deleted successfully!")

if __name__ == "__main__":
    remove_sample_games()


