#!/usr/bin/env python3
"""
Web Scraping Fallback for NBA Data
Scrapes NBA.com for game data when API fails
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
import time

class NBAWebScraper:
    def __init__(self):
        self.base_url = "https://www.nba.com"
        self.schedule_url = "https://www.nba.com/schedule"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_today_games(self):
        """Scrape today's games from NBA.com"""
        print("🌐 WEB SCRAPING NBA.COM FOR TODAY'S GAMES")
        print("=" * 50)
        
        try:
            # Get today's date
            today = datetime.now()
            today_str = today.strftime('%Y-%m-%d')
            
            # Try to get games from NBA.com schedule
            response = requests.get(self.schedule_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for game data in various formats
            games = self._extract_games_from_html(soup, today_str)
            
            if games:
                print(f"✅ Found {len(games)} games via web scraping")
                return games
            else:
                print("❌ No games found via web scraping")
                return []
                
        except Exception as e:
            print(f"❌ Web scraping failed: {e}")
            return []
    
    def _extract_games_from_html(self, soup, target_date):
        """Extract game data from HTML"""
        games = []
        
        # Method 1: Look for game cards/containers
        game_containers = soup.find_all(['div', 'section'], class_=re.compile(r'game|match|schedule', re.I))
        
        for container in game_containers:
            try:
                game_data = self._parse_game_container(container, target_date)
                if game_data:
                    games.append(game_data)
            except Exception as e:
                continue
        
        # Method 2: Look for JSON data in script tags
        script_tags = soup.find_all('script', type='application/json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                games.extend(self._extract_games_from_json(data, target_date))
            except:
                continue
        
        return games
    
    def _parse_game_container(self, container, target_date):
        """Parse individual game container"""
        # This would need to be customized based on NBA.com's actual HTML structure
        # For now, return None as we'd need to inspect the actual site
        return None
    
    def _extract_games_from_json(self, data, target_date):
        """Extract games from JSON data in script tags"""
        games = []
        
        # Recursively search for game data in JSON
        def search_for_games(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if 'game' in key.lower() or 'match' in key.lower():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and self._is_game_data(item):
                                    game = self._convert_to_game_format(item, target_date)
                                    if game:
                                        games.append(game)
                    else:
                        search_for_games(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_for_games(item, f"{path}[{i}]")
        
        search_for_games(data)
        return games
    
    def _is_game_data(self, obj):
        """Check if object contains game data"""
        game_indicators = ['home', 'away', 'team', 'score', 'date', 'time']
        return any(indicator in str(obj).lower() for indicator in game_indicators)
    
    def _convert_to_game_format(self, game_data, target_date):
        """Convert scraped data to our game format"""
        try:
            # This would need to be customized based on the actual data structure
            # For now, return a placeholder
            return {
                'game_id': f"scraped_{int(time.time())}",
                'date': f"{target_date} 00:00:00",
                'away_team': "Away Team",
                'home_team': "Home Team", 
                'away_score': 0,
                'home_score': 0,
                'home_win': False,
                'status': 'Scheduled'
            }
        except:
            return None

def main():
    """Main function to scrape NBA data"""
    scraper = NBAWebScraper()
    games = scraper.fetch_today_games()
    
    if games:
        print(f"\\n🎮 Scraped games:")
        for game in games:
            print(f"   {game['away_team']} @ {game['home_team']} - {game['date'][:10]}")
    else:
        print("\\n❌ No games found via web scraping")

if __name__ == "__main__":
    main()
