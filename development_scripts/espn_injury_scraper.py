#!/usr/bin/env python3
"""
ESPN Injury Data Scraper
Scrapes real NBA injury data from ESPN's injury page
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

class ESPNInjuryScraper:
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
    
    def fetch_real_injury_data(self):
        """Fetch real NBA injury data from ESPN"""
        print("🏥 FETCHING REAL NBA INJURY DATA FROM ESPN")
        print("=" * 60)
        
        all_injuries = []
        
        # Method 1: ESPN Injuries Page
        print("🌐 Method 1: ESPN Injuries Page")
        espn_injuries = self._fetch_espn_injuries_page()
        if espn_injuries:
            all_injuries.extend(espn_injuries)
            print(f"   ✅ Found {len(espn_injuries)} injuries via ESPN web scraping")
        else:
            print(f"   ❌ No injuries from ESPN web scraping")
        
        # Method 2: ESPN API (if available)
        print("🌐 Method 2: ESPN API")
        api_injuries = self._fetch_espn_api()
        if api_injuries:
            all_injuries.extend(api_injuries)
            print(f"   ✅ Found {len(api_injuries)} injuries via ESPN API")
        else:
            print(f"   ❌ No injuries from ESPN API")
        
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
            print(f"   ❌ NO REAL INJURY DATA FOUND")
            print(f"   💡 This means ESPN structure may have changed")
        
        return unique_injuries
    
    def _fetch_espn_injuries_page(self):
        """Scrape ESPN injuries page"""
        try:
            print("   🔄 Scraping ESPN injuries page...")
            
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for injury data in the page
            injuries = []
            
            # Try different selectors for ESPN's injury data
            injury_selectors = [
                'table.Table',
                'div.Table',
                'tr.Table__TR',
                'div[data-module="InjuryReport"]',
                'div.injury-report',
                'table.injury-table'
            ]
            
            for selector in injury_selectors:
                elements = soup.select(selector)
                print(f"   📊 Found {len(elements)} elements with selector: {selector}")
                
                if elements:
                    # Process the elements
                    for element in elements:
                        injury_data = self._extract_injury_from_element(element)
                        if injury_data:
                            injuries.extend(injury_data)
            
            # Also try to find injury data in script tags (JSON)
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    injury_data = self._extract_injury_from_json(data)
                    if injury_data:
                        injuries.extend(injury_data)
                except:
                    continue
            
            print(f"   📊 Total injury records found: {len(injuries)}")
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN web scraping error: {e}")
            return []
    
    def _fetch_espn_api(self):
        """Try ESPN API for injury data"""
        try:
            print("   🔄 Trying ESPN API...")
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"   📊 ESPN API Response: {len(data)} items")
            
            # Process ESPN API data
            injuries = self._process_espn_api_data(data)
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN API error: {e}")
            return []
    
    def _extract_injury_from_element(self, element):
        """Extract injury data from HTML element"""
        injuries = []
        
        try:
            # Look for player names and injury info
            rows = element.find_all('tr') if element.name == 'table' else [element]
            
            for row in rows:
                cells = row.find_all(['td', 'div'])
                if len(cells) >= 3:
                    # Try to extract player name, team, and injury status
                    player_name = None
                    team_name = None
                    injury_status = None
                    injury_type = None
                    
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        
                        # Look for player name (usually first cell)
                        if not player_name and len(text) > 2 and not text.isdigit():
                            player_name = text
                        
                        # Look for team name
                        elif not team_name and len(text) <= 3 and text.isupper():
                            team_name = text
                        
                        # Look for injury status
                        elif text.upper() in ['OUT', 'QUESTIONABLE', 'PROBABLE', 'DOUBTFUL']:
                            injury_status = text.upper()
                        
                        # Look for injury type
                        elif not injury_type and len(text) > 3 and text not in [player_name, team_name]:
                            injury_type = text
                    
                    if player_name and team_name:
                        injury = {
                            "player_id": hash(player_name + team_name),
                            "player_name": player_name,
                            "team_id": hash(team_name),
                            "team_name": team_name,
                            "injury_status": injury_status or "UNKNOWN",
                            "injury_type": injury_type or "Unknown",
                            "injury_severity": "Unknown",
                            "expected_return": "TBD",
                            "last_game_date": None,
                            "games_missed": 0,
                            "recent_minutes_avg": 0,
                            "data_source": "ESPN Web Scraping",
                            "last_updated": datetime.now().isoformat()
                        }
                        injuries.append(injury)
            
        except Exception as e:
            print(f"   ⚠️ Error extracting injury data: {e}")
        
        return injuries
    
    def _extract_injury_from_json(self, data):
        """Extract injury data from JSON"""
        injuries = []
        
        try:
            # This would process JSON data from ESPN
            # Implementation depends on ESPN's JSON structure
            pass
        except Exception as e:
            print(f"   ⚠️ Error processing JSON data: {e}")
        
        return injuries
    
    def _process_espn_api_data(self, data):
        """Process ESPN API data"""
        injuries = []
        
        try:
            # Process ESPN API response
            # This depends on ESPN's API structure
            pass
        except Exception as e:
            print(f"   ⚠️ Error processing ESPN API data: {e}")
        
        return injuries
    
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
        """Save injury data to file"""
        if not injuries:
            print("❌ No real injury data to save")
            return
        
        # Count injury statuses
        status_counts = {}
        for injury in injuries:
            status = injury['injury_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        data = {
            "metadata": {
                "data_source": "ESPN Web Scraping - Real NBA Data",
                "season": "2025-26",
                "export_date": datetime.now().isoformat(),
                "total_players": len(injuries),
                "injury_status_summary": status_counts,
                "data_quality": "Real NBA injury data scraped from ESPN",
                "update_frequency": "Daily",
                "method": "ESPN Web Scraping"
            },
            "injuries": injuries
        }
        
        with open('data/nba_injury_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(injuries)} real injury records to data/nba_injury_data.json")
        print(f"📊 Injury Status Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} players")

def main():
    """Main function"""
    scraper = ESPNInjuryScraper()
    
    print("🏥 ESPN INJURY DATA SCRAPER")
    print("=" * 60)
    
    # Fetch real injury data
    injuries = scraper.fetch_real_injury_data()
    
    if injuries:
        # Save to file
        scraper.save_injury_data(injuries)
        
        print(f"\n✅ Successfully scraped real NBA injury data from ESPN")
        print(f"📁 Data saved to: data/nba_injury_data.json")
        print(f"🎯 Ready for model building!")
    else:
        print("❌ No real NBA injury data found from ESPN")
        print("💡 This might mean:")
        print("   1. ESPN's page structure changed")
        print("   2. No injuries currently reported")
        print("   3. Need to try different selectors")

if __name__ == "__main__":
    main()
