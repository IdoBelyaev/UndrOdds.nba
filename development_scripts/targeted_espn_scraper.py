#!/usr/bin/env python3
"""
Targeted ESPN Injury Data Scraper
Specifically targets ESPN's injury page structure for accurate data
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class TargetedESPNScraper:
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
    
    def fetch_targeted_injury_data(self):
        """Fetch targeted NBA injury data from ESPN"""
        print("🏥 TARGETED ESPN INJURY DATA SCRAPER")
        print("=" * 60)
        
        all_injuries = []
        
        # Method 1: ESPN Injuries Page with targeted parsing
        print("🌐 Method 1: ESPN Injuries Page (Targeted)")
        espn_injuries = self._fetch_targeted_espn_injuries()
        if espn_injuries:
            all_injuries.extend(espn_injuries)
            print(f"   ✅ Found {len(espn_injuries)} targeted injuries via ESPN")
        else:
            print(f"   ❌ No targeted injuries from ESPN")
        
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
            print(f"   ❌ NO TARGETED INJURY DATA FOUND")
        
        return unique_injuries
    
    def _fetch_targeted_espn_injuries(self):
        """Fetch targeted injury data from ESPN"""
        try:
            print("   🔄 Scraping ESPN injuries page with targeted parsing...")
            
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
                        injury_data = self._extract_targeted_injury(row, cells)
                        if injury_data:
                            injuries.append(injury_data)
            
            print(f"   📊 Total targeted injury records: {len(injuries)}")
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN targeted scraping error: {e}")
            return []
    
    def _extract_targeted_injury(self, row, cells):
        """Extract targeted injury information from table row"""
        try:
            # Initialize variables
            player_name = None
            team_name = None
            injury_status = None
            injury_type = None
            injury_duration = None
            
            # Process each cell
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                
                # Skip empty cells
                if not text or text == '-':
                    continue
                
                # Debug: Print cell content
                print(f"      Cell {i}: '{text}'")
                
                # Player name (usually first cell)
                if i == 0 and not player_name:
                    player_name = text
                
                # Team name (usually second cell)
                elif i == 1 and not team_name:
                    team_name = text
                
                # Injury status and duration (usually third cell)
                elif i == 2:
                    injury_status, injury_duration = self._parse_targeted_injury_status(text)
                
                # Injury type (usually fourth cell)
                elif i == 3 and not injury_type:
                    injury_type = text
                
                # Additional injury details
                elif i >= 4:
                    if not injury_type:
                        injury_type = text
                    elif not injury_duration and any(word in text.lower() for word in ['week', 'month', 'day', 'season']):
                        injury_duration = text
            
            # Calculate games missed based on duration
            games_missed = self._calculate_games_missed(injury_duration)
            
            # Calculate recent minutes based on injury status
            recent_minutes = self._calculate_recent_minutes(injury_status, injury_duration)
            
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
                    "data_source": "ESPN Web Scraping - Targeted",
                    "last_updated": datetime.now().isoformat()
                }
            
        except Exception as e:
            print(f"   ⚠️ Error extracting targeted injury: {e}")
        
        return None
    
    def _parse_targeted_injury_status(self, text):
        """Parse injury status and duration from text"""
        text = text.strip()
        
        # Common injury status patterns
        status_patterns = {
            'OUT': ['out', 'injured', 'sidelined'],
            'QUESTIONABLE': ['questionable', 'doubtful', 'day-to-day'],
            'PROBABLE': ['probable', 'likely'],
            'DOUBTFUL': ['doubtful', 'unlikely']
        }
        
        # Common duration patterns
        duration_patterns = {
            'day-to-day': ['day-to-day', 'daily', 'day to day'],
            '1-2 weeks': ['1-2 weeks', '1-2 week', '1 week', '2 weeks'],
            '2-4 weeks': ['2-4 weeks', '3-4 weeks', '2-3 weeks'],
            '1-2 months': ['1-2 months', '1 month', '2 months'],
            '2-3 months': ['2-3 months', '3 months'],
            'season-ending': ['season-ending', 'season ending', 'out for season'],
            '6-8 weeks': ['6-8 weeks', '6 weeks', '8 weeks'],
            '4-6 weeks': ['4-6 weeks', '4 weeks', '6 weeks']
        }
        
        # Determine status
        injury_status = "UNKNOWN"
        for status, patterns in status_patterns.items():
            if any(pattern in text.lower() for pattern in patterns):
                injury_status = status
                break
        
        # Determine duration
        injury_duration = "Unknown"
        for duration, patterns in duration_patterns.items():
            if any(pattern in text.lower() for pattern in patterns):
                injury_duration = duration
                break
        
        return injury_status, injury_duration
    
    def _calculate_games_missed(self, duration):
        """Calculate games missed based on injury duration"""
        if not duration or duration == "Unknown":
            return 0
        
        duration_lower = duration.lower()
        
        if 'day-to-day' in duration_lower:
            return 1
        elif '1-2 weeks' in duration_lower or '1 week' in duration_lower:
            return 3
        elif '2-4 weeks' in duration_lower or '2-3 weeks' in duration_lower:
            return 8
        elif '4-6 weeks' in duration_lower:
            return 15
        elif '6-8 weeks' in duration_lower:
            return 20
        elif '1-2 months' in duration_lower:
            return 25
        elif '2-3 months' in duration_lower:
            return 35
        elif 'season-ending' in duration_lower:
            return 50
        else:
            return 5  # Default estimate
    
    def _calculate_recent_minutes(self, status, duration):
        """Calculate recent minutes based on injury status and duration"""
        if status == "OUT" or status == "UNKNOWN":
            return 0
        elif status == "DOUBTFUL":
            return 5
        elif status == "QUESTIONABLE":
            return 15
        elif status == "PROBABLE":
            return 25
        else:
            return 30  # Healthy players
    
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
        """Save targeted injury data to file"""
        if not injuries:
            print("❌ No targeted injury data to save")
            return
        
        # Count injury statuses
        status_counts = {}
        for injury in injuries:
            status = injury['injury_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        data = {
            "metadata": {
                "data_source": "ESPN Web Scraping - Targeted NBA Data",
                "season": "2025-26",
                "export_date": datetime.now().isoformat(),
                "total_players": len(injuries),
                "injury_status_summary": status_counts,
                "data_quality": "Targeted NBA injury data with duration and type",
                "update_frequency": "Daily",
                "method": "ESPN Web Scraping - Targeted"
            },
            "injuries": injuries
        }
        
        with open('data/nba_injury_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(injuries)} targeted injury records to data/nba_injury_data.json")
        print(f"📊 Injury Status Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} players")

def main():
    """Main function"""
    scraper = TargetedESPNScraper()
    
    print("🏥 TARGETED ESPN INJURY DATA SCRAPER")
    print("=" * 60)
    
    # Fetch targeted injury data
    injuries = scraper.fetch_targeted_injury_data()
    
    if injuries:
        # Save to file
        scraper.save_injury_data(injuries)
        
        print(f"\n✅ Successfully scraped targeted NBA injury data from ESPN")
        print(f"📁 Data saved to: data/nba_injury_data.json")
        print(f"🎯 Ready for model building!")
        
        # Show sample of targeted injuries
        print(f"\n📋 SAMPLE TARGETED INJURIES:")
        for i, player in enumerate(injuries[:10], 1):
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
        print("❌ No targeted NBA injury data found from ESPN")

if __name__ == "__main__":
    main()
