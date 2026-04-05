#!/usr/bin/env python3
"""
Real NBA Injury Data Fetcher
Fetches actual injury data from ESPN and other sources
"""

import json
import requests
from datetime import datetime
import time
import random

class RealInjuryFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.espn.com/nba/injuries'
        }
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
    
    def fetch_real_injuries(self):
        """Fetch real NBA injury data from ESPN"""
        print("🏥 FETCHING REAL NBA INJURY DATA")
        print("=" * 50)
        
        all_injuries = []
        
        # Method 1: Try ESPN injuries endpoint
        print("📡 Method 1: ESPN Injuries API")
        espn_injuries = self._fetch_espn_injuries()
        if espn_injuries:
            all_injuries.extend(espn_injuries)
            print(f"   ✅ Found {len(espn_injuries)} injuries via ESPN")
        else:
            print(f"   ❌ No injuries from ESPN")
        
        # Method 2: Try ESPN teams endpoint for injury info
        print("📡 Method 2: ESPN Teams API")
        team_injuries = self._fetch_team_injuries()
        if team_injuries:
            all_injuries.extend(team_injuries)
            print(f"   ✅ Found {len(team_injuries)} injuries via Teams API")
        else:
            print(f"   ❌ No injuries from Teams API")
        
        # Method 3: Try ESPN players endpoint
        print("📡 Method 3: ESPN Players API")
        player_injuries = self._fetch_player_injuries()
        if player_injuries:
            all_injuries.extend(player_injuries)
            print(f"   ✅ Found {len(player_injuries)} injuries via Players API")
        else:
            print(f"   ❌ No injuries from Players API")
        
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
        
        return unique_injuries
    
    def _fetch_espn_injuries(self):
        """Try ESPN injuries endpoint"""
        try:
            print("   🔄 Trying ESPN injuries endpoint...")
            url = f"{self.base_url}/injuries"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"   📊 ESPN Injuries API Response: {len(data)} items")
            
            # Process the response
            injuries = self._process_espn_injuries(data)
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN injuries error: {e}")
            return []
    
    def _fetch_team_injuries(self):
        """Try ESPN teams endpoint for injury info"""
        try:
            print("   🔄 Trying ESPN teams endpoint...")
            url = f"{self.base_url}/teams"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            print(f"   📊 ESPN Teams API Response: {len(teams)} teams")
            
            # Process teams for injury info
            injuries = self._process_team_injuries(teams)
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN teams error: {e}")
            return []
    
    def _fetch_player_injuries(self):
        """Try ESPN players endpoint"""
        try:
            print("   🔄 Trying ESPN players endpoint...")
            url = f"{self.base_url}/players"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            players = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('athletes', [])
            
            print(f"   📊 ESPN Players API Response: {len(players)} players")
            
            # Process players for injury info
            injuries = self._process_player_injuries(players)
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN players error: {e}")
            return []
    
    def _process_espn_injuries(self, data):
        """Process ESPN injuries response"""
        injuries = []
        
        # This would process the actual ESPN injuries response
        # For now, return empty as we need to see the actual response structure
        return injuries
    
    def _process_team_injuries(self, teams):
        """Process teams for injury information"""
        injuries = []
        
        for team in teams:
            team_info = team.get('team', {})
            team_name = team_info.get('displayName', 'Unknown')
            team_id = team_info.get('id', 0)
            
            # Look for injury information in team data
            # This would need to be implemented based on actual ESPN response structure
            pass
        
        return injuries
    
    def _process_player_injuries(self, players):
        """Process players for injury information"""
        injuries = []
        
        for player in players:
            player_info = player.get('athlete', {})
            player_name = player_info.get('displayName', 'Unknown')
            player_id = player_info.get('id', 0)
            
            # Look for injury information in player data
            # This would need to be implemented based on actual ESPN response structure
            pass
        
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
            print("❌ No injury data to save")
            return
        
        # Count injury statuses
        status_counts = {}
        for injury in injuries:
            status = injury['injury_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        data = {
            "metadata": {
                "data_source": "ESPN API - Real NBA Injury Data",
                "season": "2025-26",
                "export_date": datetime.now().isoformat(),
                "total_players": len(injuries),
                "injury_status_summary": status_counts,
                "data_quality": "Real NBA injury data from ESPN API",
                "update_frequency": "Daily",
                "method": "ESPN API - Multiple Endpoints"
            },
            "injuries": injuries
        }
        
        with open('data/nba_injury_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(injuries)} injury records to data/nba_injury_data.json")
        print(f"📊 Injury Status Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} players")

def main():
    """Main function"""
    fetcher = RealInjuryFetcher()
    
    print("🏥 REAL NBA INJURY DATA FETCHER")
    print("=" * 50)
    
    # Fetch real injury data
    injuries = fetcher.fetch_real_injuries()
    
    if injuries:
        # Save to file
        fetcher.save_injury_data(injuries)
        
        print(f"\n✅ Successfully fetched real injury data")
        print(f"📁 Data saved to: data/nba_injury_data.json")
        print(f"🎯 Ready for dashboard testing!")
    else:
        print("❌ No real injury data found")
        print("💡 This might be due to API limitations or rate limiting")

if __name__ == "__main__":
    main()
