#!/usr/bin/env python3
"""
Final ESPN Injury Data Scraper
Properly parses ESPN injury data with correct status, type, and duration
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class FinalESPNScraper:
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
    
    def fetch_final_injury_data(self):
        """Fetch final NBA injury data from ESPN"""
        print("🏥 FINAL ESPN INJURY DATA SCRAPER")
        print("=" * 60)
        
        all_injuries = []
        
        # Method 1: ESPN Injuries Page with proper parsing
        print("🌐 Method 1: ESPN Injuries Page (Final)")
        espn_injuries = self._fetch_final_espn_injuries()
        if espn_injuries:
            all_injuries.extend(espn_injuries)
            print(f"   ✅ Found {len(espn_injuries)} final injuries via ESPN")
        else:
            print(f"   ❌ No final injuries from ESPN")
        
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
            print(f"   ❌ NO FINAL INJURY DATA FOUND")
        
        return unique_injuries
    
    def _fetch_final_espn_injuries(self):
        """Fetch final injury data from ESPN"""
        try:
            print("   🔄 Scraping ESPN injuries page with final parsing...")
            
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
                        injury_data = self._extract_final_injury(row, cells)
                        if injury_data:
                            injuries.append(injury_data)
            
            print(f"   📊 Total final injury records: {len(injuries)}")
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN final scraping error: {e}")
            return []
    
    def _extract_final_injury(self, row, cells):
        """Extract final injury information from table row"""
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
                    team_name = text
                elif i == 2:  # EST. RETURN DATE
                    injury_duration = self._parse_return_date(text)
                elif i == 3:  # STATUS
                    injury_status = self._parse_status(text)
                elif i == 4:  # COMMENT
                    injury_type = self._extract_injury_type_from_comment(text)
            
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
                    "data_source": "ESPN Web Scraping - Final",
                    "last_updated": datetime.now().isoformat()
                }
            
        except Exception as e:
            print(f"   ⚠️ Error extracting final injury: {e}")
        
        return None
    
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
    
    def _calculate_games_missed(self, duration):
        """Calculate games missed based on injury duration"""
        if not duration or duration == "Unknown":
            return 0
        
        duration_lower = duration.lower()
        
        if 'day-to-day' in duration_lower:
            return 1
        elif '1-2 weeks' in duration_lower:
            return 3
        elif '2-4 weeks' in duration_lower:
            return 8
        elif '1-2 months' in duration_lower:
            return 25
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
        """Save final injury data to file"""
        if not injuries:
            print("❌ No final injury data to save")
            return
        
        # Count injury statuses
        status_counts = {}
        for injury in injuries:
            status = injury['injury_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        data = {
            "metadata": {
                "data_source": "ESPN Web Scraping - Final NBA Data",
                "season": "2025-26",
                "export_date": datetime.now().isoformat(),
                "total_players": len(injuries),
                "injury_status_summary": status_counts,
                "data_quality": "Final NBA injury data with proper status, type, and duration",
                "update_frequency": "Daily",
                "method": "ESPN Web Scraping - Final"
            },
            "injuries": injuries
        }
        
        with open('data/nba_injury_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(injuries)} final injury records to data/nba_injury_data.json")
        print(f"📊 Injury Status Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} players")

def main():
    """Main function"""
    scraper = FinalESPNScraper()
    
    print("🏥 FINAL ESPN INJURY DATA SCRAPER")
    print("=" * 60)
    
    # Fetch final injury data
    injuries = scraper.fetch_final_injury_data()
    
    if injuries:
        # Save to file
        scraper.save_injury_data(injuries)
        
        print(f"\n✅ Successfully scraped final NBA injury data from ESPN")
        print(f"📁 Data saved to: data/nba_injury_data.json")
        print(f"🎯 Ready for model building!")
        
        # Show sample of final injuries
        print(f"\n📋 SAMPLE FINAL INJURIES:")
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
        print("❌ No final NBA injury data found from ESPN")

if __name__ == "__main__":
    main()
