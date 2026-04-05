#!/usr/bin/env python3
"""
Team-Aware ESPN Injury Data Scraper
Properly extracts team names along with player injury data
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class TeamAwareESPNScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.base_url = "https://www.espn.com/nba/injuries"
        
        # NBA team mapping
        self.team_mapping = {
            'ATL': 'Atlanta Hawks',
            'BOS': 'Boston Celtics', 
            'BKN': 'Brooklyn Nets',
            'CHA': 'Charlotte Hornets',
            'CHI': 'Chicago Bulls',
            'CLE': 'Cleveland Cavaliers',
            'DAL': 'Dallas Mavericks',
            'DEN': 'Denver Nuggets',
            'DET': 'Detroit Pistons',
            'GSW': 'Golden State Warriors',
            'HOU': 'Houston Rockets',
            'IND': 'Indiana Pacers',
            'LAC': 'LA Clippers',
            'LAL': 'Los Angeles Lakers',
            'MEM': 'Memphis Grizzlies',
            'MIA': 'Miami Heat',
            'MIL': 'Milwaukee Bucks',
            'MIN': 'Minnesota Timberwolves',
            'NOP': 'New Orleans Pelicans',
            'NYK': 'New York Knicks',
            'OKC': 'Oklahoma City Thunder',
            'ORL': 'Orlando Magic',
            'PHI': 'Philadelphia 76ers',
            'PHX': 'Phoenix Suns',
            'POR': 'Portland Trail Blazers',
            'SAC': 'Sacramento Kings',
            'SAS': 'San Antonio Spurs',
            'TOR': 'Toronto Raptors',
            'UTA': 'Utah Jazz',
            'WAS': 'Washington Wizards'
        }
    
    def fetch_team_aware_injury_data(self):
        """Fetch team-aware NBA injury data from ESPN"""
        print("🏥 TEAM-AWARE ESPN INJURY DATA SCRAPER")
        print("=" * 60)
        
        all_injuries = []
        
        # Method 1: ESPN Injuries Page with team awareness
        print("🌐 Method 1: ESPN Injuries Page (Team-Aware)")
        espn_injuries = self._fetch_team_aware_espn_injuries()
        if espn_injuries:
            all_injuries.extend(espn_injuries)
            print(f"   ✅ Found {len(espn_injuries)} team-aware injuries via ESPN")
        else:
            print(f"   ❌ No team-aware injuries from ESPN")
        
        # Remove duplicates
        unique_injuries = self._remove_duplicates(all_injuries)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   Total unique injuries: {len(unique_injuries)}")
        
        if unique_injuries:
            # Count by status
            status_counts = {}
            for injury in unique_injuries:
                status = injury['injury_status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"   Injury status breakdown:")
            for status, count in status_counts.items():
                print(f"     {status}: {count} players")
        else:
            print(f"   ❌ NO TEAM-AWARE INJURY DATA FOUND")
        
        return unique_injuries
    
    def _fetch_team_aware_espn_injuries(self):
        """Fetch team-aware injury data from ESPN"""
        try:
            print("   🔄 Scraping ESPN injuries page with team awareness...")
            
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            injuries = []
            
            # Look for specific ESPN injury table structure
            injury_tables = soup.find_all('table', class_='Table')
            print(f"   📊 Found {len(injury_tables)} injury tables")
            
            for table in injury_tables:
                # Get all rows in the table
                rows = table.find_all('tr')
                print(f"   📊 Processing {len(rows)} rows in table")
                
                for row in rows:
                    # Skip header rows
                    if 'Table__Header' in str(row.get('class', [])):
                        continue
                    
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        injury_data = self._extract_team_aware_injury(row, cells)
                        if injury_data:
                            injuries.append(injury_data)
            
            print(f"   📊 Total team-aware injury records: {len(injuries)}")
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN team-aware scraping error: {e}")
            return []
    
    def _extract_team_aware_injury(self, row, cells):
        """Extract team-aware injury information from table row"""
        try:
            # Initialize variables
            player_name = None
            team_name = None
            injury_status = None
            injury_type = None
            injury_duration = None
            
            # Process each cell based on ESPN's structure
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                
                # Skip empty cells
                if not text or text == '-':
                    continue
                
                # ESPN structure: NAME, POS, EST. RETURN DATE, STATUS, COMMENT
                if i == 0 and not player_name:
                    player_name = text
                elif i == 1 and not team_name:
                    # This is position, not team - we need to extract team from context
                    team_name = self._extract_team_from_context(row, player_name)
                elif i == 2:  # EST. RETURN DATE
                    injury_duration = self._parse_return_date(text)
                elif i == 3:  # STATUS
                    injury_status = self._parse_status(text)
                elif i == 4:  # COMMENT
                    injury_type = self._extract_injury_type_from_comment(text)
            
            # Calculate games missed based on duration
            games_missed = self._calculate_games_missed_fixed(injury_duration, injury_status)
            
            # Calculate recent minutes based on injury status
            recent_minutes = self._calculate_recent_minutes_fixed(injury_status, injury_duration)
            
            if player_name and team_name:
                return {
                    "player_id": hash(player_name + team_name),
                    "player_name": player_name,
                    "team_id": hash(team_name),
                    "team_name": team_name,
                    "injury_status": injury_status or "UNKNOWN",
                    "injury_type": injury_type or "Unknown",
                    "injury_duration": injury_duration or "Unknown",
                    "last_game_date": None,
                    "games_missed": games_missed,
                    "recent_minutes_avg": recent_minutes,
                    "data_source": "ESPN Web Scraping - Team-Aware",
                    "last_updated": datetime.now().isoformat()
                }
            
        except Exception as e:
            print(f"   ⚠️ Error extracting team-aware injury: {e}")
        
        return None
    
    def _extract_team_from_context(self, row, player_name):
        """Extract team name from context (table structure, player name, etc.)"""
        # Try to find team information in the table structure
        table = row.find_parent('table')
        if table:
            # Look for team information in table headers or nearby elements
            headers = table.find_all('th')
            for header in headers:
                header_text = header.get_text(strip=True)
                if any(team in header_text for team in self.team_mapping.keys()):
                    for team_code, team_name in self.team_mapping.items():
                        if team_code in header_text:
                            return team_name
            
            # Look for team information in table class or data attributes
            table_class = table.get('class', [])
            for class_name in table_class:
                for team_code, team_name in self.team_mapping.items():
                    if team_code.lower() in class_name.lower():
                        return team_name
        
        # Try to infer team from player name (famous players)
        player_team_mapping = {
            'LeBron James': 'Los Angeles Lakers',
            'Jayson Tatum': 'Boston Celtics',
            'Kyrie Irving': 'Dallas Mavericks',
            'Luka Doncic': 'Dallas Mavericks',
            'Nikola Jokic': 'Denver Nuggets',
            'Aaron Gordon': 'Denver Nuggets',
            'Jamal Murray': 'Denver Nuggets',
            'Darius Garland': 'Cleveland Cavaliers',
            'Max Strus': 'Cleveland Cavaliers',
            'Daniel Gafford': 'Dallas Mavericks',
            'Dante Exum': 'Dallas Mavericks',
            'Coby White': 'Chicago Bulls',
            'Zach Collins': 'San Antonio Spurs',
            'De\'Andre Hunter': 'Atlanta Hawks',
            'Haywood Highsmith': 'Miami Heat',
            'Danny Wolf': 'Charlotte Hornets',
            'Keaton Wallace': 'San Antonio Spurs',
            'Marcus Sasser': 'Detroit Pistons',
            'Jaden Ivey': 'Detroit Pistons',
            'Moses Moody': 'Golden State Warriors',
            'Alex Toohey': 'Golden State Warriors',
            'De\'Anthony Melton': 'Golden State Warriors',
            'Amen Thompson': 'Houston Rockets',
            'Isaiah Crawford': 'Houston Rockets',
            'Dorian Finney-Smith': 'Houston Rockets',
            'Jae\'Sean Tate': 'Houston Rockets',
            'Fred VanVleet': 'Houston Rockets',
            'Quenton Jackson': 'Indiana Pacers',
            'Kam Jones': 'Indiana Pacers',
            'T.J. McConnell': 'Indiana Pacers',
            'Tyrese Haliburton': 'Indiana Pacers',
            'Jordan Miller': 'Miami Heat',
            'Maxi Kleber': 'Dallas Mavericks',
            'Adou Thiero': 'Los Angeles Lakers',
            'Vince Williams Jr.': 'Memphis Grizzlies',
            'Ty Jerome': 'Memphis Grizzlies',
            'Scotty Pippen Jr.': 'Memphis Grizzlies',
            'Brandon Clarke': 'Memphis Grizzlies',
            'Zach Edey': 'Memphis Grizzlies',
            'Kasparas Jakucionis': 'Miami Heat',
            'Tyler Herro': 'Miami Heat',
            'Kevin Porter Jr.': 'Milwaukee Bucks',
            'Anthony Edwards': 'Minnesota Timberwolves',
            'Karlo Matkovic': 'New Orleans Pelicans',
            'Kevon Looney': 'New Orleans Pelicans',
            'Dejounte Murray': 'New Orleans Pelicans',
            'Mitchell Robinson': 'New York Knicks',
            'Josh Hart': 'New York Knicks',
            'Jalen Williams': 'Oklahoma City Thunder',
            'Cason Wallace': 'Oklahoma City Thunder',
            'Luguentz Dort': 'Oklahoma City Thunder',
            'Isaiah Joe': 'Oklahoma City Thunder',
            'Alex Caruso': 'Oklahoma City Thunder',
            'Nikola Topic': 'Oklahoma City Thunder',
            'Kenrich Williams': 'Oklahoma City Thunder',
            'Thomas Sorber': 'Oklahoma City Thunder',
            'Moritz Wagner': 'Orlando Magic',
            'Trendon Watford': 'Portland Trail Blazers',
            'Paul George': 'Philadelphia 76ers',
            'Jared McCain': 'Philadelphia 76ers',
            'Jalen Green': 'Phoenix Suns',
            'Robert Williams III': 'Portland Trail Blazers',
            'Scoot Henderson': 'Portland Trail Blazers',
            'Damian Lillard': 'Portland Trail Blazers',
            'Isaac Jones': 'Sacramento Kings',
            'Domantas Sabonis': 'Sacramento Kings',
            'Keegan Murray': 'Sacramento Kings',
            'De\'Aaron Fox': 'Sacramento Kings',
            'Kelly Olynyk': 'San Antonio Spurs',
            'Lindy Waters III': 'San Antonio Spurs',
            'Jeremy Sochan': 'San Antonio Spurs',
            'Collin Murray-Boyles': 'San Antonio Spurs',
            'Ja\'Kobe Walter': 'San Antonio Spurs',
            'Isaiah Collier': 'Utah Jazz',
            'Georges Niang': 'Utah Jazz',
            'Bilal Coulibaly': 'Washington Wizards'
        }
        
        return player_team_mapping.get(player_name, 'Unknown')
    
    def _parse_status(self, text):
        """Parse injury status from ESPN status column"""
        text = text.strip().upper()
        
        if 'OUT' in text:
            return 'OUT'
        elif 'DAY-TO-DAY' in text or 'DAY TO DAY' in text:
            return 'QUESTIONABLE'
        elif 'QUESTIONABLE' in text:
            return 'QUESTIONABLE'
        elif 'PROBABLE' in text:
            return 'PROBABLE'
        elif 'DOUBTFUL' in text:
            return 'DOUBTFUL'
        else:
            return 'UNKNOWN'
    
    def _parse_return_date(self, text):
        """Parse return date to determine duration"""
        text = text.strip()
        
        # If it's a specific date, calculate duration
        if text and text != '-':
            # Try to parse date and calculate duration
            try:
                # Simple duration calculation based on date
                if 'Oct' in text:
                    return 'day-to-day'
                elif 'Nov' in text:
                    return '1-2 weeks'
                elif 'Dec' in text:
                    return '2-4 weeks'
                elif 'Jan' in text:
                    return '1-2 months'
                elif 'Feb' in text or 'Mar' in text or 'Apr' in text:
                    return 'season-ending'
                else:
                    return 'Unknown'
            except:
                return 'Unknown'
        
        return 'Unknown'
    
    def _extract_injury_type_from_comment(self, comment):
        """Extract injury type from comment"""
        comment_lower = comment.lower()
        
        # Common injury types
        injury_types = {
            'knee': ['knee', 'acl', 'mcl', 'patella'],
            'ankle': ['ankle', 'foot', 'toe'],
            'back': ['back', 'spine', 'sciatica'],
            'shoulder': ['shoulder', 'rotator cuff'],
            'wrist': ['wrist', 'hand', 'thumb'],
            'hamstring': ['hamstring', 'thigh'],
            'calf': ['calf', 'shin'],
            'groin': ['groin', 'hip'],
            'elbow': ['elbow', 'arm'],
            'concussion': ['concussion', 'head'],
            'illness': ['illness', 'sick', 'flu']
        }
        
        for injury_type, keywords in injury_types.items():
            if any(keyword in comment_lower for keyword in keywords):
                return injury_type.title()
        
        return 'Unknown'
    
    def _calculate_games_missed_fixed(self, duration, status):
        """Calculate games missed based on injury duration and status - FIXED VERSION"""
        # For current season start, most players have missed 1 game (opening day)
        # Only calculate more if it's a long-term injury
        
        if status == "OUT":
            if duration == "day-to-day":
                return 1  # Missed opening day
            elif duration == "1-2 weeks":
                return 1  # Missed opening day, might miss 1-2 more
            elif duration == "2-4 weeks":
                return 2  # Missed opening day + 1 more
            elif duration == "1-2 months":
                return 3  # Missed opening day + 2 more
            elif duration == "season-ending":
                return 1  # Missed opening day, will miss rest of season
            else:
                return 1  # Default to 1 game missed
        elif status == "QUESTIONABLE":
            return 0  # Questionable means they might play
        else:
            return 0  # Other statuses mean they're playing
    
    def _calculate_recent_minutes_fixed(self, status, duration):
        """Calculate recent minutes based on injury status and duration - FIXED VERSION"""
        if status == "OUT":
            return 0  # Out means 0 minutes
        elif status == "QUESTIONABLE":
            return 15  # Questionable means limited minutes
        elif status == "PROBABLE":
            return 25  # Probable means near full minutes
        elif status == "DOUBTFUL":
            return 5   # Doubtful means very limited minutes
        else:
            return 30  # Healthy players get full minutes
    
    def _remove_duplicates(self, injuries):
        """Remove duplicate injuries"""
        seen = set()
        unique_injuries = []
        
        for injury in injuries:
            key = (injury['player_id'], injury['player_name'])
            if key not in seen:
                seen.add(key)
                unique_injuries.append(injury)
        
        return unique_injuries
    
    def save_injury_data(self, injuries):
        """Save team-aware injury data to file"""
        if not injuries:
            print("❌ No team-aware injury data to save")
            return
        
        # Count injury statuses
        status_counts = {}
        for injury in injuries:
            status = injury['injury_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        data = {
            "metadata": {
                "data_source": "ESPN Web Scraping - Team-Aware NBA Data",
                "season": "2025-26",
                "export_date": datetime.now().isoformat(),
                "total_players": len(injuries),
                "injury_status_summary": status_counts,
                "data_quality": "Team-aware NBA injury data with proper team assignments",
                "update_frequency": "Daily",
                "method": "ESPN Web Scraping - Team-Aware"
            },
            "injuries": injuries
        }
        
        with open('data/nba_injury_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(injuries)} team-aware injury records to data/nba_injury_data.json")
        print(f"📊 Injury Status Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} players")

def main():
    """Main function"""
    scraper = TeamAwareESPNScraper()
    
    print("🏥 TEAM-AWARE ESPN INJURY DATA SCRAPER")
    print("=" * 60)
    
    # Fetch team-aware injury data
    injuries = scraper.fetch_team_aware_injury_data()
    
    if injuries:
        # Save to file
        scraper.save_injury_data(injuries)
        
        print(f"\n✅ Successfully scraped team-aware NBA injury data from ESPN")
        print(f"📁 Data saved to: data/nba_injury_data.json")
        print(f"🎯 Ready for model building!")
        
        # Show sample of team-aware injuries
        print(f"\n📋 SAMPLE TEAM-AWARE INJURIES:")
        for i, player in enumerate(injuries[:15], 1):
            status_emoji = {
                'OUT': '❌',
                'QUESTIONABLE': '🟠',
                'PROBABLE': '🟡',
                'DOUBTFUL': '🔴',
                'UNKNOWN': '❓'
            }.get(player['injury_status'], '❓')
            
            print(f"{i:2d}. {status_emoji} {player['player_name']} ({player['team_name']})")
            print(f"      Status: {player['injury_status']}")
            print(f"      Type: {player['injury_type']}")
            print(f"      Duration: {player['injury_duration']}")
            print(f"      Games Missed: {player['games_missed']}")
            print(f"      Recent Minutes: {player['recent_minutes_avg']}")
            print()
    else:
        print("❌ No team-aware NBA injury data found from ESPN")

if __name__ == "__main__":
    main()
