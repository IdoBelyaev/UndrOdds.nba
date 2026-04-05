#!/usr/bin/env python3
"""
Complete NBA Schedule Fetcher
Gets the entire NBA schedule using multiple methods
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from nba_api.stats.endpoints import LeagueGameFinder
from nba_api.stats.static import teams
import re

class CompleteNBAScheduleFetcher:
    def __init__(self):
        self.nba_teams = {team['abbreviation']: team for team in teams.get_teams()}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_complete_schedule(self):
        """Get the complete NBA schedule using all available methods"""
        print("🏀 FETCHING COMPLETE NBA SCHEDULE")
        print("=" * 50)
        
        all_games = []
        
        # Method 1: NBA API
        print("📡 Method 1: NBA API")
        api_games = self._fetch_from_api()
        if api_games:
            all_games.extend(api_games)
            print(f"   ✅ Found {len(api_games)} games via API")
        else:
            print(f"   ❌ No games from API")
        
        # Method 2: Web Scraping
        print("🌐 Method 2: Web Scraping")
        web_games = self._fetch_from_web()
        if web_games:
            all_games.extend(web_games)
            print(f"   ✅ Found {len(web_games)} games via web scraping")
        else:
            print(f"   ❌ No games from web scraping")
        
        # Method 3: Try different seasons
        print("📅 Method 3: Different Seasons")
        season_games = self._fetch_from_different_seasons()
        if season_games:
            all_games.extend(season_games)
            print(f"   ✅ Found {len(season_games)} games from different seasons")
        else:
            print(f"   ❌ No games from different seasons")
        
        # Remove duplicates
        unique_games = self._remove_duplicates(all_games)
        
        print(f"\\n📊 FINAL RESULTS:")
        print(f"   Total unique games: {len(unique_games)}")
        
        if unique_games:
            # Group by date
            games_by_date = {}
            for game in unique_games:
                date = game['date'][:10]
                if date not in games_by_date:
                    games_by_date[date] = []
                games_by_date[date].append(game)
            
            print(f"   Games by date:")
            for date in sorted(games_by_date.keys()):
                print(f"     {date}: {len(games_by_date[date])} games")
        
        return unique_games
    
    def _fetch_from_api(self):
        """Fetch games from NBA API"""
        try:
            gamefinder = LeagueGameFinder(
                season_nullable='2025-26',
                season_type_nullable='Regular Season'
            )
            
            games_df = gamefinder.get_data_frames()[0]
            games = []
            
            for _, game in games_df.iterrows():
                try:
                    game_data = {
                        'game_id': str(game['GAME_ID']),
                        'date': game['GAME_DATE'] + ' 00:00:00',
                        'away_team': self._get_team_name(game['AWAY_TEAM_ID']),
                        'home_team': self._get_team_name(game['HOME_TEAM_ID']),
                        'away_score': int(game.get('AWAY_TEAM_SCORE', 0)),
                        'home_score': int(game.get('HOME_TEAM_SCORE', 0)),
                        'home_win': bool(game.get('HOME_TEAM_WINS', False)),
                        'status': 'Completed' if game.get('GAME_STATUS_TEXT') == 'Final' else 'Scheduled'
                    }
                    games.append(game_data)
                except Exception as e:
                    continue
            
            return games
            
        except Exception as e:
            print(f"   ❌ API error: {e}")
            return []
    
    def _fetch_from_web(self):
        """Fetch games from NBA.com"""
        try:
            url = 'https://www.nba.com/schedule'
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for JSON data in script tags
            games = []
            script_tags = soup.find_all('script', type='application/json')
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    games.extend(self._extract_games_from_json(data))
                except:
                    continue
            
            return games
            
        except Exception as e:
            print(f"   ❌ Web scraping error: {e}")
            return []
    
    def _fetch_from_different_seasons(self):
        """Try different seasons to find more games"""
        seasons = ['2025', '2024', '2023']
        all_games = []
        
        for season in seasons:
            try:
                gamefinder = LeagueGameFinder(
                    season_nullable=season,
                    season_type_nullable='Regular Season'
                )
                
                games_df = gamefinder.get_data_frames()[0]
                
                # Filter for 2025 dates
                games_2025 = games_df[games_df['GAME_DATE'].str.contains('2025')]
                
                for _, game in games_2025.iterrows():
                    try:
                        game_data = {
                            'game_id': str(game['GAME_ID']),
                            'date': game['GAME_DATE'] + ' 00:00:00',
                            'away_team': self._get_team_name(game['AWAY_TEAM_ID']),
                            'home_team': self._get_team_name(game['HOME_TEAM_ID']),
                            'away_score': int(game.get('AWAY_TEAM_SCORE', 0)),
                            'home_score': int(game.get('HOME_TEAM_SCORE', 0)),
                            'home_win': bool(game.get('HOME_TEAM_WINS', False)),
                            'status': 'Completed' if game.get('GAME_STATUS_TEXT') == 'Final' else 'Scheduled'
                        }
                        all_games.append(game_data)
                    except Exception as e:
                        continue
                        
            except Exception as e:
                continue
        
        return all_games
    
    def _extract_games_from_json(self, data):
        """Extract games from JSON data"""
        games = []
        
        def search_for_games(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if 'game' in key.lower() or 'match' in key.lower():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and self._is_game_data(item):
                                    game = self._convert_to_game_format(item)
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
    
    def _convert_to_game_format(self, game_data):
        """Convert scraped data to our game format"""
        try:
            return {
                'game_id': f"scraped_{int(datetime.now().timestamp())}",
                'date': f"{datetime.now().strftime('%Y-%m-%d')} 00:00:00",
                'away_team': "Away Team",
                'home_team': "Home Team",
                'away_score': 0,
                'home_score': 0,
                'home_win': False,
                'status': 'Scheduled'
            }
        except:
            return None
    
    def _get_team_name(self, team_id):
        """Get team name from team ID"""
        for team in self.nba_teams.values():
            if team['id'] == team_id:
                return team['full_name']
        return f"Team_{team_id}"
    
    def _remove_duplicates(self, games):
        """Remove duplicate games"""
        seen = set()
        unique_games = []
        
        for game in games:
            key = (game['away_team'], game['home_team'], game['date'][:10])
            if key not in seen:
                seen.add(key)
                unique_games.append(game)
        
        return unique_games
    
    def save_schedule(self, games, filename='data/nba_complete_schedule.json'):
        """Save complete schedule to file"""
        if not games:
            print("❌ No games to save")
            return
        
        data = {
            "metadata": {
                "season": "2025-26",
                "data_source": "Complete Schedule Fetcher",
                "export_date": datetime.now().isoformat(),
                "total_games": len(games),
                "date_range": {"start": "", "end": ""}
            },
            "games": games
        }
        
        if games:
            dates = [game['date'][:10] for game in games]
            data['metadata']['date_range'] = {
                "start": min(dates),
                "end": max(dates)
            }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {len(games)} games to {filename}")

def main():
    """Main function"""
    fetcher = CompleteNBAScheduleFetcher()
    
    print("🏀 COMPLETE NBA SCHEDULE FETCHER")
    print("=" * 50)
    
    # Fetch complete schedule
    games = fetcher.fetch_complete_schedule()
    
    if games:
        # Save to file
        fetcher.save_schedule(games)
        
        print(f"\\n🎮 Sample games:")
        for game in games[:5]:
            print(f"   {game['away_team']} @ {game['home_team']} - {game['date'][:10]}")
    else:
        print("❌ No games found")

if __name__ == "__main__":
    main()
