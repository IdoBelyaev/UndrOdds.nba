#!/usr/bin/env python3
"""
Injury Data Verification Tool
Helps you spot-check key NBA players against real sources
"""

import json
import webbrowser
from datetime import datetime

def load_injury_data():
    """Load the injury data from JSON file"""
    try:
        with open('data/nba_injury_data.json', 'r') as f:
            data = json.load(f)
        
        # Check if it's the new format with metadata
        if 'metadata' in data and 'injuries' in data:
            return data['injuries']
        elif 'metadata' in data and 'players' in data:
            return data['players']
        else:
            # Old format - direct array
            return data
    except FileNotFoundError:
        print("❌ Error: data/nba_injury_data.json not found")
        return None

def get_key_players():
    """Get a list of key players to verify"""
    return [
        "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo",
        "Luka Doncic", "Jayson Tatum", "Joel Embiid", "Nikola Jokic",
        "Kawhi Leonard", "Jimmy Butler", "Damian Lillard", "Anthony Davis",
        "Devin Booker", "Donovan Mitchell", "Trae Young", "Ja Morant",
        "Zion Williamson", "Paolo Banchero", "Victor Wembanyama", "Anthony Edwards"
    ]

def find_player_data(injury_data, player_name):
    """Find a specific player in the injury data"""
    for player in injury_data:
        if player['player_name'].lower() == player_name.lower():
            return player
    return None

def display_player_info(player):
    """Display player injury information in a readable format"""
    if not player:
        return "❌ Player not found"
    
    print(f"\n🏀 {player['player_name']}")
    print(f"   Team: {player['team_name']}")
    print(f"   Status: {player['injury_status']}")
    print(f"   Injury Type: {player['injury_type']}")
    print(f"   Duration: {player['injury_duration']}")
    print(f"   Games Missed: {player['games_missed']}")
    print(f"   Recent Minutes: {player['recent_minutes_avg']}")

def open_espn_injury_page():
    """Open ESPN injury page for manual verification"""
    espn_url = "https://www.espn.com/nba/injuries"
    print(f"\n🌐 Opening ESPN injury page: {espn_url}")
    webbrowser.open(espn_url)

def main():
    """Main verification interface"""
    print("🏀 NBA INJURY DATA VERIFICATION TOOL")
    print("=" * 50)
    
    # Load data
    injury_data = load_injury_data()
    if not injury_data:
        return
    
    print(f"📊 Loaded {len(injury_data)} players from injury data")
    
    # Get key players to check
    key_players = get_key_players()
    
    print(f"\n🎯 KEY PLAYERS TO VERIFY ({len(key_players)} players):")
    print("These are the most important players to spot-check:")
    
    for i, player_name in enumerate(key_players, 1):
        player_data = find_player_data(injury_data, player_name)
        if player_data:
            status_emoji = "✅" if player_data['injury_status'] == "Healthy" else "⚠️"
            print(f"{i:2d}. {status_emoji} {player_name} ({player_data['team_name']}) - {player_data['injury_status']}")
        else:
            print(f"{i:2d}. ❌ {player_name} - NOT FOUND")
    
    # Interactive verification
    print(f"\n🔍 VERIFICATION OPTIONS:")
    print("1. Check specific player details")
    print("2. Open ESPN injury page for manual verification")
    print("3. Show all injured players")
    print("4. Show all healthy players")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            player_name = input("Enter player name: ").strip()
            player_data = find_player_data(injury_data, player_name)
            display_player_info(player_data)
            
        elif choice == "2":
            open_espn_injury_page()
            print("\n📝 MANUAL VERIFICATION STEPS:")
            print("1. Compare our data with ESPN's injury list")
            print("2. Check if injury statuses match")
            print("3. Verify team assignments")
            print("4. Note any discrepancies")
            
        elif choice == "3":
            injured_players = [p for p in injury_data if p['injury_status'] != "Healthy"]
            print(f"\n⚠️ INJURED PLAYERS ({len(injured_players)} total):")
            for player in injured_players[:20]:  # Show first 20
                print(f"   {player['player_name']} ({player['team_name']}) - {player['injury_status']} - {player['injury_type']}")
            if len(injured_players) > 20:
                print(f"   ... and {len(injured_players) - 20} more")
                
        elif choice == "4":
            healthy_players = [p for p in injury_data if p['injury_status'] == "Healthy"]
            print(f"\n✅ HEALTHY PLAYERS ({len(healthy_players)} total):")
            for player in healthy_players[:20]:  # Show first 20
                print(f"   {player['player_name']} ({player['team_name']})")
            if len(healthy_players) > 20:
                print(f"   ... and {len(healthy_players) - 20} more")
                
        elif choice == "5":
            print("\n✅ Verification complete!")
            print("\n📝 NEXT STEPS:")
            print("1. Check the key players listed above against ESPN")
            print("2. Note any inaccuracies you find")
            print("3. Report back with your findings")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
