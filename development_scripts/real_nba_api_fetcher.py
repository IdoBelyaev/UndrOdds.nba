#!/usr/bin/env python3
"""
Real NBA API Data Fetcher
Fetches actual injury data from real NBA APIs
"""

import json
import requests
from datetime import datetime
import time

class RealNBAAPIFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nba.com/'
        }
    
    def fetch_real_injury_data(self):
        """Fetch real NBA injury data from actual APIs"""
        print("🏥 FETCHING REAL NBA INJURY DATA FROM APIS")
        print("=" * 60)
        
        all_injuries = []
        
        # Method 1: Try NBA.com official API
        print("📡 Method 1: NBA.com Official API")
        nba_injuries = self._fetch_nba_official_api()
        if nba_injuries:
            all_injuries.extend(nba_injuries)
            print(f"   ✅ Found {len(nba_injuries)} injuries via NBA.com API")
        else:
            print(f"   ❌ No injuries from NBA.com API")
        
        # Method 2: Try ESPN API
        print("📡 Method 2: ESPN API")
        espn_injuries = self._fetch_espn_api()
        if espn_injuries:
            all_injuries.extend(espn_injuries)
            print(f"   ✅ Found {len(espn_injuries)} injuries via ESPN API")
        else:
            print(f"   ❌ No injuries from ESPN API")
        
        # Method 3: Try NBA Stats API
        print("📡 Method 3: NBA Stats API")
        stats_injuries = self._fetch_nba_stats_api()
        if stats_injuries:
            all_injuries.extend(stats_injuries)
            print(f"   ✅ Found {len(stats_injuries)} injuries via NBA Stats API")
        else:
            print(f"   ❌ No injuries from NBA Stats API")
        
        # Method 4: Try Basketball Reference
        print("📡 Method 4: Basketball Reference")
        br_injuries = self._fetch_basketball_reference()
        if br_injuries:
            all_injuries.extend(br_injuries)
            print(f"   ✅ Found {len(br_injuries)} injuries via Basketball Reference")
        else:
            print(f"   ❌ No injuries from Basketball Reference")
        
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
            print(f"   💡 This means we need to:")
            print(f"      - Check API endpoints")
            print(f"      - Verify authentication")
            print(f"      - Use different data sources")
        
        return unique_injuries
    
    def _fetch_nba_official_api(self):
        """Try NBA.com official API"""
        try:
            print("   🔄 Trying NBA.com official API...")
            # NBA.com doesn't have a public injury API
            # This would require authentication and proper API keys
            return []
        except Exception as e:
            print(f"   ❌ NBA.com API error: {e}")
            return []
    
    def _fetch_espn_api(self):
        """Try ESPN API"""
        try:
            print("   🔄 Trying ESPN API...")
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"   📊 ESPN API Response: {len(data)} items")
            
            # Process ESPN injury data
            injuries = self._process_espn_injuries(data)
            return injuries
            
        except Exception as e:
            print(f"   ❌ ESPN API error: {e}")
            return []
    
    def _fetch_nba_stats_api(self):
        """Try NBA Stats API"""
        try:
            print("   🔄 Trying NBA Stats API...")
            # NBA Stats API doesn't have injury data
            return []
        except Exception as e:
            print(f"   ❌ NBA Stats API error: {e}")
            return []
    
    def _fetch_basketball_reference(self):
        """Try Basketball Reference"""
        try:
            print("   🔄 Trying Basketball Reference...")
            # Basketball Reference doesn't have real-time injury data
            return []
        except Exception as e:
            print(f"   ❌ Basketball Reference error: {e}")
            return []
    
    def _process_espn_injuries(self, data):
        """Process ESPN injury data"""
        injuries = []
        
        # This would process the actual ESPN response
        # For now, return empty as we need to see the actual response structure
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
                "data_source": "Real NBA API Data",
                "season": "2025-26",
                "export_date": datetime.now().isoformat(),
                "total_players": len(injuries),
                "injury_status_summary": status_counts,
                "data_quality": "Real NBA injury data from official APIs",
                "update_frequency": "Real-time",
                "method": "NBA API - Multiple Sources"
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
    fetcher = RealNBAAPIFetcher()
    
    print("🏥 REAL NBA API INJURY DATA FETCHER")
    print("=" * 60)
    
    # Fetch real injury data
    injuries = fetcher.fetch_real_injury_data()
    
    if injuries:
        # Save to file
        fetcher.save_injury_data(injuries)
        
        print(f"\n✅ Successfully fetched real NBA injury data")
        print(f"📁 Data saved to: data/nba_injury_data.json")
        print(f"🎯 Ready for model building!")
    else:
        print("❌ No real NBA injury data found")
        print("💡 This means we need to:")
        print("   1. Check if NBA APIs are available")
        print("   2. Use different data sources")
        print("   3. Consider manual data entry")
        print("   4. Use third-party injury tracking services")

if __name__ == "__main__":
    main()
