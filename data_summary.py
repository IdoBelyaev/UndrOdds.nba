#!/usr/bin/env python3
"""
Data Summary Tool
Quick overview of all data files for verification
"""

import json
import os
from datetime import datetime

def get_file_info(filepath):
    """Get basic file information"""
    if not os.path.exists(filepath):
        return None
    
    stat = os.stat(filepath)
    size_mb = stat.st_size / (1024 * 1024)
    modified = datetime.fromtimestamp(stat.st_mtime)
    
    return {
        'size_mb': round(size_mb, 2),
        'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
        'exists': True
    }

def analyze_injury_data():
    """Analyze injury data structure"""
    try:
        with open('data/nba_injury_data.json', 'r') as f:
            data = json.load(f)
        
        # Check if it's the cleaned format with team_organization
        if 'team_organization' in data:
            # Extract all players from team organization
            players = []
            for team_name, team_data in data['team_organization'].items():
                if 'players' in team_data:
                    players.extend(team_data['players'])
            metadata = data.get('metadata', {})
        # Check if it's the old format with injuries array
        elif 'metadata' in data and 'injuries' in data:
            players = data['injuries']
            metadata = data['metadata']
        elif 'metadata' in data and 'players' in data:
            players = data['players']
            metadata = data['metadata']
        else:
            # Old format - direct array
            players = data
            metadata = {}
        
        total_players = len(players)
        healthy = len([p for p in players if p['injury_status'] in ['Healthy', 'HEALTHY']])
        injured = total_players - healthy
        
        # Get injury types
        injury_types = {}
        for player in players:
            if player['injury_status'] not in ['Healthy', 'HEALTHY']:
                injury_type = player['injury_type']
                injury_types[injury_type] = injury_types.get(injury_type, 0) + 1
        
        # Get teams
        teams = set(p['team_name'] for p in players)
        
        return {
            'total_players': total_players,
            'healthy': healthy,
            'injured': injured,
            'injury_types': injury_types,
            'teams': len(teams),
            'team_list': sorted(list(teams)),
            'metadata': metadata
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_game_data():
    """Analyze game data structure"""
    try:
        with open('data/nba_game_data.json', 'r') as f:
            data = json.load(f)
        
        # Check if it's the new format with metadata
        if 'metadata' in data and 'games' in data:
            games = data['games']
            metadata = data['metadata']
        else:
            # Old format - direct array
            games = data
            metadata = {}
        
        total_games = len(games)
        
        # Get date range
        dates = [game['date'] for game in games]
        dates.sort()
        date_range = f"{dates[0]} to {dates[-1]}" if dates else "No dates"
        
        # Get seasons
        seasons = set(game.get('season', 'Unknown') for game in games)
        
        return {
            'total_games': total_games,
            'date_range': date_range,
            'seasons': list(seasons),
            'metadata': metadata
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_team_data():
    """Analyze team data structure"""
    try:
        with open('data/nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        # Check if it's the new format with metadata
        if 'metadata' in data and 'teams' in data:
            teams_data = data['teams']
            metadata = data['metadata']
        else:
            # Old format - direct array
            teams_data = data
            metadata = {}
        
        total_teams = len(teams_data)
        teams = [team['team_name'] for team in teams_data]
        
        return {
            'total_teams': total_teams,
            'teams': sorted(teams),
            'metadata': metadata
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    """Main summary function"""
    print("📊 NBA DATA SUMMARY - VERIFICATION OVERVIEW")
    print("=" * 60)
    
    # File information
    files_to_check = [
        'data/nba_injury_data.json',
        'data/nba_game_data.json', 
        'data/nba_team_data.json',
        'data/bet_history.json'
    ]
    
    print("\n📁 FILE STATUS:")
    for filepath in files_to_check:
        info = get_file_info(filepath)
        if info:
            print(f"   ✅ {filepath}")
            print(f"      Size: {info['size_mb']} MB")
            print(f"      Modified: {info['modified']}")
        else:
            print(f"   ❌ {filepath} - NOT FOUND")
    
    # Injury data analysis
    print(f"\n🏥 INJURY DATA ANALYSIS:")
    injury_analysis = analyze_injury_data()
    if 'error' in injury_analysis:
        print(f"   ❌ Error: {injury_analysis['error']}")
    else:
        print(f"   Total Players: {injury_analysis['total_players']}")
        print(f"   Healthy: {injury_analysis['healthy']}")
        print(f"   Injured: {injury_analysis['injured']}")
        print(f"   Teams: {injury_analysis['teams']}")
        
        if injury_analysis['injury_types']:
            print(f"   Top Injury Types:")
            for injury_type, count in sorted(injury_analysis['injury_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      {injury_type}: {count} players")
    
    # Game data analysis
    print(f"\n🏀 GAME DATA ANALYSIS:")
    game_analysis = analyze_game_data()
    if 'error' in game_analysis:
        print(f"   ❌ Error: {game_analysis['error']}")
    else:
        print(f"   Total Games: {game_analysis['total_games']}")
        print(f"   Date Range: {game_analysis['date_range']}")
        print(f"   Seasons: {', '.join(game_analysis['seasons'])}")
    
    # Team data analysis
    print(f"\n🏆 TEAM DATA ANALYSIS:")
    team_analysis = analyze_team_data()
    if 'error' in team_analysis:
        print(f"   ❌ Error: {team_analysis['error']}")
    else:
        print(f"   Total Teams: {team_analysis['total_teams']}")
        print(f"   Teams: {', '.join(team_analysis['teams'])}")
    
    # Verification checklist
    print(f"\n✅ VERIFICATION CHECKLIST:")
    print("1. Run: python injury_data_verification.py")
    print("2. Check key players against ESPN")
    print("3. Verify team assignments are correct")
    print("4. Check injury statuses match reality")
    print("5. Note any discrepancies")
    
    print(f"\n🎯 KEY PLAYERS TO VERIFY:")
    key_players = [
        "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo",
        "Luka Doncic", "Jayson Tatum", "Joel Embiid", "Nikola Jokic"
    ]
    for player in key_players:
        print(f"   - {player}")

if __name__ == "__main__":
    main()
