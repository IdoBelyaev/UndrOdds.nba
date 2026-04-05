#!/usr/bin/env python3
"""
Fix Team Assignments for NBA Injury Data
Manually assigns correct teams to players based on known rosters
"""

import json
from datetime import datetime

def fix_team_assignments():
    """Fix team assignments for all players"""
    print("🏀 FIXING TEAM ASSIGNMENTS FOR NBA INJURY DATA")
    print("=" * 60)
    
    # Load current injury data
    with open('data/nba_injury_data.json', 'r') as f:
        injury_data = json.load(f)
    
    injuries = injury_data.get('injuries', [])
    print(f"📊 Total players to fix: {len(injuries)}")
    
    # Player to team mapping (based on 2025-26 rosters)
    player_team_mapping = {
        # Boston Celtics
        'Jayson Tatum': 'Boston Celtics',
        'Danny Wolf': 'Boston Celtics',
        
        # Miami Heat
        'Haywood Highsmith': 'Miami Heat',
        'Tyler Herro': 'Miami Heat',
        'Kasparas Jakucionis': 'Miami Heat',
        'Jordan Miller': 'Miami Heat',
        
        # Chicago Bulls
        'Coby White': 'Chicago Bulls',
        'Zach Collins': 'Chicago Bulls',
        
        # Atlanta Hawks
        'De\'Andre Hunter': 'Atlanta Hawks',
        
        # Cleveland Cavaliers
        'Darius Garland': 'Cleveland Cavaliers',
        'Max Strus': 'Cleveland Cavaliers',
        
        # Dallas Mavericks
        'Daniel Gafford': 'Dallas Mavericks',
        'Dante Exum': 'Dallas Mavericks',
        'Kyrie Irving': 'Dallas Mavericks',
        'Luka Doncic': 'Dallas Mavericks',
        'Maxi Kleber': 'Dallas Mavericks',
        
        # Denver Nuggets
        'Aaron Gordon': 'Denver Nuggets',
        'Jamal Murray': 'Denver Nuggets',
        'Nikola Jokic': 'Denver Nuggets',
        
        # Detroit Pistons
        'Marcus Sasser': 'Detroit Pistons',
        'Jaden Ivey': 'Detroit Pistons',
        
        # Golden State Warriors
        'Moses Moody': 'Golden State Warriors',
        'Alex Toohey': 'Golden State Warriors',
        'De\'Anthony Melton': 'Golden State Warriors',
        
        # Houston Rockets
        'Amen Thompson': 'Houston Rockets',
        'Isaiah Crawford': 'Houston Rockets',
        'Dorian Finney-Smith': 'Houston Rockets',
        'Jae\'Sean Tate': 'Houston Rockets',
        'Fred VanVleet': 'Houston Rockets',
        
        # Indiana Pacers
        'Quenton Jackson': 'Indiana Pacers',
        'Kam Jones': 'Indiana Pacers',
        'T.J. McConnell': 'Indiana Pacers',
        'Tyrese Haliburton': 'Indiana Pacers',
        
        # Los Angeles Lakers
        'LeBron James': 'Los Angeles Lakers',
        'Adou Thiero': 'Los Angeles Lakers',
        
        # Memphis Grizzlies
        'Vince Williams Jr.': 'Memphis Grizzlies',
        'Ty Jerome': 'Memphis Grizzlies',
        'Scotty Pippen Jr.': 'Memphis Grizzlies',
        'Brandon Clarke': 'Memphis Grizzlies',
        'Zach Edey': 'Memphis Grizzlies',
        
        # Milwaukee Bucks
        'Kevin Porter Jr.': 'Milwaukee Bucks',
        
        # Minnesota Timberwolves
        'Anthony Edwards': 'Minnesota Timberwolves',
        
        # New Orleans Pelicans
        'Karlo Matkovic': 'New Orleans Pelicans',
        'Kevon Looney': 'New Orleans Pelicans',
        'Dejounte Murray': 'New Orleans Pelicans',
        
        # New York Knicks
        'Mitchell Robinson': 'New York Knicks',
        'Josh Hart': 'New York Knicks',
        
        # Oklahoma City Thunder
        'Jalen Williams': 'Oklahoma City Thunder',
        'Cason Wallace': 'Oklahoma City Thunder',
        'Luguentz Dort': 'Oklahoma City Thunder',
        'Isaiah Joe': 'Oklahoma City Thunder',
        'Alex Caruso': 'Oklahoma City Thunder',
        'Nikola Topic': 'Oklahoma City Thunder',
        'Kenrich Williams': 'Oklahoma City Thunder',
        'Thomas Sorber': 'Oklahoma City Thunder',
        
        # Orlando Magic
        'Moritz Wagner': 'Orlando Magic',
        
        # Portland Trail Blazers
        'Trendon Watford': 'Portland Trail Blazers',
        'Robert Williams III': 'Portland Trail Blazers',
        'Scoot Henderson': 'Portland Trail Blazers',
        'Damian Lillard': 'Portland Trail Blazers',
        
        # Philadelphia 76ers
        'Paul George': 'Philadelphia 76ers',
        'Jared McCain': 'Philadelphia 76ers',
        
        # Phoenix Suns
        'Jalen Green': 'Phoenix Suns',
        
        # Sacramento Kings
        'Isaac Jones': 'Sacramento Kings',
        'Domantas Sabonis': 'Sacramento Kings',
        'Keegan Murray': 'Sacramento Kings',
        'De\'Aaron Fox': 'Sacramento Kings',
        
        # San Antonio Spurs
        'Kelly Olynyk': 'San Antonio Spurs',
        'Lindy Waters III': 'San Antonio Spurs',
        'Jeremy Sochan': 'San Antonio Spurs',
        'Collin Murray-Boyles': 'San Antonio Spurs',
        'Ja\'Kobe Walter': 'San Antonio Spurs',
        'Keaton Wallace': 'San Antonio Spurs',
        
        # Utah Jazz
        'Isaiah Collier': 'Utah Jazz',
        'Georges Niang': 'Utah Jazz',
        
        # Washington Wizards
        'Bilal Coulibaly': 'Washington Wizards'
    }
    
    # Fix team assignments
    fixed_injuries = []
    fixed_count = 0
    
    for injury in injuries:
        player_name = injury['player_name']
        
        # Skip header rows
        if player_name == 'NAME':
            continue
        
        # Get correct team
        correct_team = player_team_mapping.get(player_name, 'Unknown')
        
        # Update injury record
        fixed_injury = injury.copy()
        fixed_injury['team_name'] = correct_team
        fixed_injury['team_id'] = hash(correct_team)
        
        if correct_team != 'Unknown':
            fixed_count += 1
            print(f"   ✅ {player_name} → {correct_team}")
        else:
            print(f"   ❓ {player_name} → Unknown (not in mapping)")
        
        fixed_injuries.append(fixed_injury)
    
    print(f"\n📊 Team Assignment Summary:")
    print(f"   Total players: {len(fixed_injuries)}")
    print(f"   Successfully assigned: {fixed_count}")
    print(f"   Unknown teams: {len(fixed_injuries) - fixed_count}")
    
    # Organize by teams
    team_organization = {}
    for injury in fixed_injuries:
        team_name = injury['team_name']
        
        if team_name not in team_organization:
            team_organization[team_name] = {
                'team_name': team_name,
                'total_players': 0,
                'injured_players': 0,
                'out_players': 0,
                'questionable_players': 0,
                'players': []
            }
        
        team_organization[team_name]['total_players'] += 1
        team_organization[team_name]['players'].append(injury)
        
        if injury['injury_status'] != 'UNKNOWN':
            team_organization[team_name]['injured_players'] += 1
            
            if injury['injury_status'] == 'OUT':
                team_organization[team_name]['out_players'] += 1
            elif injury['injury_status'] == 'QUESTIONABLE':
                team_organization[team_name]['questionable_players'] += 1
    
    # Save fixed data
    fixed_data = {
        "metadata": {
            "data_source": "ESPN Web Scraping - Team Assignments Fixed",
            "season": "2025-26",
            "export_date": datetime.now().isoformat(),
            "total_players": len(fixed_injuries),
            "data_quality": "Team assignments fixed with correct NBA teams",
            "update_frequency": "Daily",
            "method": "ESPN Web Scraping - Team Assignments Fixed"
        },
        "injuries": fixed_injuries,
        "team_organization": team_organization
    }
    
    with open('data/nba_injury_data.json', 'w') as f:
        json.dump(fixed_data, f, indent=2)
    
    print(f"\n💾 Saved fixed injury data to data/nba_injury_data.json")
    
    # Show team breakdown
    print(f"\n🏀 TEAM BREAKDOWN:")
    for team_name, data in sorted(team_organization.items()):
        if data['injured_players'] > 0:
            print(f"\n{team_name}: {data['injured_players']} injured players")
            for player in data['players']:
                if player['injury_status'] != 'UNKNOWN':
                    status_emoji = {
                        'OUT': '❌',
                        'QUESTIONABLE': '🟠',
                        'PROBABLE': '🟡',
                        'DOUBTFUL': '🔴'
                    }.get(player['injury_status'], '❓')
                    
                    print(f"   {status_emoji} {player['player_name']} - {player['injury_status']} ({player['injury_type']})")
    
    print(f"\n✅ SUCCESS! Team assignments fixed!")
    print(f"📁 Data saved to: data/nba_injury_data.json")
    print(f"🎯 Ready for model building with correct team assignments!")

if __name__ == "__main__":
    fix_team_assignments()
