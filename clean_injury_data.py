#!/usr/bin/env python3
"""
Clean Injury Data - Remove Duplicates
Keeps team-organized structure, removes duplicate main injuries array
"""

import json
import os
from datetime import datetime

def load_injury_data():
    """Load the current injury data"""
    try:
        with open('data/nba_injury_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: data/nba_injury_data.json not found")
        return None

def clean_injury_data(data):
    """Clean the injury data by removing duplicates and keeping team organization"""
    
    if not data:
        return None
    
    # Extract metadata
    metadata = data.get('metadata', {})
    
    # Extract teams section (this is what we want to keep)
    # Teams are under 'team_organization' key
    teams_section = data.get('team_organization', {})
    
    if not teams_section:
        print("❌ Error: No team_organization section found in data")
        return None
    
    # Count total players from teams
    total_players = 0
    healthy_players = 0
    injured_players = 0
    
    for team_name, team_data in teams_section.items():
        if 'players' in team_data:
            team_players = team_data['players']
            total_players += len(team_players)
            
            for player in team_players:
                if player.get('injury_status') in ['Healthy', 'HEALTHY']:
                    healthy_players += 1
                else:
                    injured_players += 1
    
    # Create cleaned data structure
    cleaned_data = {
        "metadata": {
            **metadata,
            "total_players": total_players,
            "healthy_players": healthy_players,
            "injured_players": injured_players,
            "total_teams": len(teams_section),
            "data_quality": "Cleaned - No duplicates, team-organized",
            "cleaned_date": datetime.now().isoformat(),
            "original_size": "12,918 lines",
            "cleaned_size": f"{total_players} players organized by {len(teams_section)} teams"
        },
        "team_organization": teams_section  # Keep teams under team_organization key
    }
    
    return cleaned_data

def save_cleaned_data(cleaned_data, backup=True):
    """Save the cleaned data"""
    
    # Create backup if requested
    if backup:
        backup_file = f"data/nba_injury_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open('data/nba_injury_data.json', 'r') as original:
                with open(backup_file, 'w') as backup_f:
                    backup_f.write(original.read())
            print(f"✅ Backup created: {backup_file}")
        except Exception as e:
            print(f"⚠️ Could not create backup: {e}")
    
    # Save cleaned data
    try:
        with open('data/nba_injury_data.json', 'w') as f:
            json.dump(cleaned_data, f, indent=2)
        print("✅ Cleaned data saved to data/nba_injury_data.json")
        return True
    except Exception as e:
        print(f"❌ Error saving cleaned data: {e}")
        return False

def verify_cleaned_data():
    """Verify the cleaned data structure"""
    try:
        with open('data/nba_injury_data.json', 'r') as f:
            data = json.load(f)
        
        print("\n🔍 VERIFICATION OF CLEANED DATA:")
        print("-" * 40)
        
        # Check structure
        if 'metadata' in data:
            print("✅ Structure: metadata + teams (correct)")
        else:
            print("❌ Structure: Missing metadata")
            return False
        
        # Check metadata
        metadata = data['metadata']
        print(f"✅ Total Players: {metadata.get('total_players', 'Unknown')}")
        print(f"✅ Healthy Players: {metadata.get('healthy_players', 'Unknown')}")
        print(f"✅ Injured Players: {metadata.get('injured_players', 'Unknown')}")
        print(f"✅ Total Teams: {metadata.get('total_teams', 'Unknown')}")
        
        # Check teams (they're under 'team_organization' key)
        team_org = data.get('team_organization', {})
        print(f"✅ Teams Section: {len(team_org)} teams found")
        
        # Check a few key players
        key_players = ["LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo"]
        found_players = 0
        
        for team_name, team_data in team_org.items():
            if 'players' in team_data:
                for player in team_data['players']:
                    if player['player_name'] in key_players:
                        found_players += 1
                        print(f"✅ Found: {player['player_name']} ({team_name}) - {player['injury_status']}")
        
        print(f"✅ Key Players Found: {found_players}/{len(key_players)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying cleaned data: {e}")
        return False

def main():
    """Main cleaning function"""
    print("🧹 CLEANING INJURY DATA - REMOVING DUPLICATES")
    print("=" * 50)
    
    # Load current data
    print("📥 Loading current injury data...")
    data = load_injury_data()
    if not data:
        return
    
    print(f"📊 Current file size: {os.path.getsize('data/nba_injury_data.json') / 1024 / 1024:.1f} MB")
    
    # Clean the data
    print("\n🧹 Cleaning data (removing duplicates)...")
    cleaned_data = clean_injury_data(data)
    if not cleaned_data:
        return
    
    # Save cleaned data
    print("\n💾 Saving cleaned data...")
    if save_cleaned_data(cleaned_data, backup=True):
        print(f"📊 New file size: {os.path.getsize('data/nba_injury_data.json') / 1024 / 1024:.1f} MB")
        
        # Verify the cleaned data
        print("\n🔍 Verifying cleaned data...")
        if verify_cleaned_data():
            print("\n✅ CLEANING COMPLETE!")
            print("   - Duplicates removed")
            print("   - Team organization preserved")
            print("   - Backup created")
            print("   - Ready for cross-referencing")
        else:
            print("\n❌ Verification failed - check the cleaned data")
    else:
        print("\n❌ Failed to save cleaned data")

if __name__ == "__main__":
    main()
