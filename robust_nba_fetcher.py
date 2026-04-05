#!/usr/bin/env python3
"""
Robust NBA Data Fetcher with Multiple Fallback Sources
Handles API failures and provides automated data fetching
"""

import json
import time
import requests
from datetime import datetime, timedelta
from nba_api.stats.endpoints import LeagueGameFinder, Scoreboard
from nba_api.stats.static import teams
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustNBADataFetcher:
    def __init__(self):
        self.nba_teams = {team['abbreviation']: team for team in teams.get_teams()}
        self.max_retries = 3
        self.retry_delay = 5
        
    def fetch_games_with_retry(self, date_str, season='2025-26'):
        """Fetch games with retry logic and multiple endpoints"""
        logger.info(f"🔄 Fetching games for {date_str}")
        
        # Method 1: Try LeagueGameFinder with retry
        for attempt in range(self.max_retries):
            try:
                logger.info(f"   Attempt {attempt + 1}: LeagueGameFinder")
                gamefinder = LeagueGameFinder(
                    season_nullable=season,
                    season_type_nullable='Regular Season',
                    date_from_nullable=date_str,
                    date_to_nullable=date_str
                )
                games_df = gamefinder.get_data_frames()[0]
                
                if len(games_df) > 0:
                    logger.info(f"   ✅ Found {len(games_df)} games via LeagueGameFinder")
                    return self._process_games_df(games_df)
                    
            except Exception as e:
                logger.warning(f"   ❌ LeagueGameFinder attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # Method 2: Try Scoreboard with retry
        for attempt in range(self.max_retries):
            try:
                logger.info(f"   Attempt {attempt + 1}: Scoreboard")
                scoreboard = Scoreboard(game_date=date_str)
                games_df = scoreboard.get_data_frames()[0]
                
                if len(games_df) > 0:
                    logger.info(f"   ✅ Found {len(games_df)} games via Scoreboard")
                    return self._process_games_df(games_df)
                    
            except Exception as e:
                logger.warning(f"   ❌ Scoreboard attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # Method 3: Try different date formats
        date_formats = [
            date_str,
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%m/%d/%Y'),
            datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d')
        ]
        
        for date_format in date_formats:
            try:
                logger.info(f"   Trying date format: {date_format}")
                scoreboard = Scoreboard(game_date=date_format)
                games_df = scoreboard.get_data_frames()[0]
                
                if len(games_df) > 0:
                    logger.info(f"   ✅ Found {len(games_df)} games with format {date_format}")
                    return self._process_games_df(games_df)
                    
            except Exception as e:
                logger.warning(f"   ❌ Date format {date_format} failed: {e}")
        
        logger.error(f"   ❌ All methods failed for {date_str}")
        return []
    
    def _process_games_df(self, games_df):
        """Process games DataFrame into our format"""
        games = []
        
        for _, game in games_df.iterrows():
            try:
                # Determine winner
                home_win = game['HOME_TEAM_WINS'] if 'HOME_TEAM_WINS' in game else False
                
                # Get team names
                home_team = self._get_team_name(game['HOME_TEAM_ID'])
                away_team = self._get_team_name(game['AWAY_TEAM_ID'])
                
                game_data = {
                    'game_id': str(game['GAME_ID']),
                    'date': game['GAME_DATE'] + ' 00:00:00',
                    'away_team': away_team,
                    'home_team': home_team,
                    'away_score': int(game['AWAY_TEAM_SCORE']) if 'AWAY_TEAM_SCORE' in game else 0,
                    'home_score': int(game['HOME_TEAM_SCORE']) if 'HOME_TEAM_SCORE' in game else 0,
                    'home_win': home_win,
                    'status': 'Completed' if game.get('GAME_STATUS_TEXT') == 'Final' else 'Scheduled'
                }
                
                games.append(game_data)
                
            except Exception as e:
                logger.warning(f"   ⚠️ Error processing game {game.get('GAME_ID', 'unknown')}: {e}")
                continue
        
        return games
    
    def _get_team_name(self, team_id):
        """Get team name from team ID"""
        for team in self.nba_teams.values():
            if team['id'] == team_id:
                return team['full_name']
        return f"Team_{team_id}"
    
    def fetch_today_games(self):
        """Fetch today's games with all fallback methods"""
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        logger.info(f"🏀 Fetching today's games ({today_str})")
        
        # Try to fetch today's games
        games = self.fetch_games_with_retry(today_str)
        
        if games:
            logger.info(f"✅ Successfully fetched {len(games)} games for today")
            return games
        else:
            logger.warning("❌ No games found for today, trying tomorrow")
            # Try tomorrow as fallback
            tomorrow = today + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            return self.fetch_games_with_retry(tomorrow_str)
    
    def save_games_to_file(self, games, filename='data/nba_game_data.json'):
        """Save games to JSON file"""
        if not games:
            logger.warning("No games to save")
            return
        
        # Load existing data
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {
                "metadata": {
                    "season": "2025-26",
                    "data_source": "Robust NBA Fetcher",
                    "export_date": datetime.now().isoformat(),
                    "date_range": {"start": "", "end": ""}
                },
                "games": []
            }
        
        # Update with new games
        data['games'] = games
        data['metadata']['export_date'] = datetime.now().isoformat()
        
        if games:
            dates = [game['date'][:10] for game in games]
            data['metadata']['date_range'] = {
                "start": min(dates),
                "end": max(dates)
            }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"💾 Saved {len(games)} games to {filename}")

def main():
    """Main function to fetch and save today's games"""
    fetcher = RobustNBADataFetcher()
    
    print("🤖 ROBUST NBA DATA FETCHER")
    print("=" * 50)
    
    # Fetch today's games
    games = fetcher.fetch_today_games()
    
    if games:
        print(f"✅ Successfully fetched {len(games)} games")
        
        # Save to file
        fetcher.save_games_to_file(games)
        
        print(f"\\n🎮 Games found:")
        for game in games:
            print(f"   {game['away_team']} @ {game['home_team']} - {game['date'][:10]}")
    else:
        print("❌ No games found for today")
        print("💡 This might be an off-day or API issue")

if __name__ == "__main__":
    main()
