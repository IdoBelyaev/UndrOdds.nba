#!/usr/bin/env python3
"""
Quick Injury Check - Non-interactive verification tool
"""

import json

def load_injury_data():
    """Load the injury data from JSON file"""
    try:
        with open('data/nba_injury_data.json', 'r') as f:
            data = json.load(f)
        
        # Check if it's the cleaned format with team_organization
        if 'team_organization' in data:
            # Extract all players from team organization
            all_players = []
            for team_name, team_data in data['team_organization'].items():
                if 'players' in team_data:
                    all_players.extend(team_data['players'])
            return all_players
        # Check if it's the old format with injuries array
        elif 'metadata' in data and 'injuries' in data:
            return data['injuries']
        elif 'metadata' in data and 'players' in data:
            return data['players']
        else:
            # Old format - direct array
            return data
    except FileNotFoundError:
        print("❌ Error: data/nba_injury_data.json not found")
        return None

def find_player_data(injury_data, player_name):
    """Find a specific player in the injury data"""
    for player in injury_data:
        if player['player_name'].lower() == player_name.lower():
            return player
    return None

def main():
    """Main verification function"""
    print("🏀 QUICK INJURY DATA CHECK")
    print("=" * 40)
    
    # Load data
    injury_data = load_injury_data()
    if not injury_data:
        return
    
    # Key players to verify
    key_players = [
        "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo",
        "Luka Doncic", "Jayson Tatum", "Joel Embiid", "Nikola Jokic",
        "Kawhi Leonard", "Jimmy Butler", "Damian Lillard", "Anthony Davis",
        "Devin Booker", "Donovan Mitchell", "Trae Young", "Ja Morant",
        "Zion Williamson", "Paolo Banchero", "Victor Wembanyama", "Anthony Edwards"
    ]
    
    print(f"\n🎯 KEY PLAYERS STATUS:")
    print("-" * 40)
    
    found_players = []
    missing_players = []
    
    for player_name in key_players:
        player_data = find_player_data(injury_data, player_name)
        if player_data:
            status_emoji = "✅" if player_data['injury_status'] in ['Healthy', 'HEALTHY'] else "⚠️"
            print(f"{status_emoji} {player_name}")
            print(f"   Team: {player_data['team_name']}")
            print(f"   Status: {player_data['injury_status']}")
            print(f"   Injury: {player_data['injury_type']}")
            print(f"   Duration: {player_data['injury_duration']}")
            print(f"   Games Missed: {player_data['games_missed']}")
            print()
            found_players.append(player_name)
        else:
            print(f"❌ {player_name} - NOT FOUND")
            print()
            missing_players.append(player_name)
    
    # Summary
    print("📊 SUMMARY:")
    print(f"   Found: {len(found_players)}/{len(key_players)} players")
    print(f"   Missing: {len(missing_players)} players")
    
    if missing_players:
        print(f"\n❌ MISSING PLAYERS:")
        for player in missing_players:
            print(f"   - {player}")
    
    # Check for potential issues
    print(f"\n🔍 POTENTIAL ISSUES TO VERIFY:")
    print("1. LeBron James shows as 'OUT' - verify if he actually missed opening day")
    print("2. Kevin Durant is missing - he should be in the data")
    print("3. Victor Wembanyama is missing - he's a key rookie")
    print("4. Check if team assignments are correct")
    print("5. Verify injury statuses match ESPN/news sources")
    
    print(f"\n🌐 MANUAL VERIFICATION:")
    print("Visit: https://www.espn.com/nba/injuries")
    print("Compare our data with ESPN's official injury list")

if __name__ == "__main__":
    main()
