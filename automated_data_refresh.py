#!/usr/bin/env python3
"""
Automated Daily NBA Data Refresh System
Runs automatically to fetch fresh data every day
"""

import json
import schedule
import time
from datetime import datetime, timedelta
from robust_nba_fetcher import RobustNBADataFetcher
# Make web scraper fallback optional and resilient to path differences
try:
    # Local module path
    from web_scraper_fallback import NBAWebScraper  # type: ignore
except Exception:
    try:
        # development_scripts path
        from development_scripts.web_scraper_fallback import NBAWebScraper  # type: ignore
    except Exception:
        NBAWebScraper = None  # Fallback disabled
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nba_data_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedDataRefresh:
    def __init__(self):
        self.api_fetcher = RobustNBADataFetcher()
        self.web_scraper = NBAWebScraper() if NBAWebScraper else None
        self.data_file = 'data/nba_game_data.json'
        
    def refresh_daily_data(self):
        """Main function to refresh all NBA data daily"""
        logger.info("🔄 STARTING DAILY NBA DATA REFRESH")
        logger.info("=" * 60)
        
        try:
            # Step 1: Try API first
            logger.info("📡 Attempting API data fetch...")
            api_games = self.api_fetcher.fetch_today_games()
            
            if api_games:
                logger.info(f"✅ API Success: Found {len(api_games)} games")
                self._save_games(api_games, "API")
                return True
            else:
                if self.web_scraper is None:
                    logger.warning("❌ API failed and web scraper fallback is unavailable")
                    return False
                logger.warning("❌ API failed, trying web scraping...")
                # Step 2: Try web scraping as fallback
                web_games = self.web_scraper.fetch_today_games()
                if web_games:
                    logger.info(f"✅ Web Scraping Success: Found {len(web_games)} games")
                    self._save_games(web_games, "Web Scraping")
                    return True
                logger.error("❌ Both API and web scraping failed")
                return False
                    
        except Exception as e:
            logger.error(f"❌ Daily refresh failed: {e}")
            return False
    
    def _save_games(self, games, source):
        """Save games to file with metadata"""
        try:
            # Load existing data
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {
                    "metadata": {
                        "season": "2025-26",
                        "data_source": source,
                        "export_date": datetime.now().isoformat(),
                        "date_range": {"start": "", "end": ""}
                    },
                    "games": []
                }
            
            # Update with new games
            data['games'] = games
            data['metadata']['data_source'] = source
            data['metadata']['export_date'] = datetime.now().isoformat()
            
            if games:
                dates = [game['date'][:10] for game in games]
                data['metadata']['date_range'] = {
                    "start": min(dates),
                    "end": max(dates)
                }
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved {len(games)} games from {source}")
            
            # Log game details
            for game in games:
                logger.info(f"   🎮 {game['away_team']} @ {game['home_team']} - {game['date'][:10]}")

            # After saving games, update team stats from completed games
            try:
                self._update_team_stats_from_games()
            except Exception as e:
                logger.warning(f"⚠️ Team stats update skipped due to error: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error saving games: {e}")

    def _update_team_stats_from_games(self):
        """Compute team stats from completed games and update data/nba_team_data.json"""
        try:
            with open(self.data_file, 'r') as f:
                game_data = json.load(f)
        except FileNotFoundError:
            logger.warning("Team stats update skipped: game data file not found")
            return

        try:
            with open('data/nba_team_data.json', 'r') as f:
                team_data = json.load(f)
        except FileNotFoundError:
            logger.warning("Team stats update skipped: team data file not found")
            return

        # Aggregate stats
        from collections import defaultdict
        team_stats = defaultdict(lambda: {'gp': 0, 'w': 0, 'l': 0, 'pf': 0, 'pa': 0})
        for g in game_data.get('games', []):
            hs = g.get('home_score', 0); as_ = g.get('away_score', 0)
            if hs > 0 and as_ > 0:
                h = g['home_team']; a = g['away_team']
                home_win = g.get('home_win', hs > as_)
                # home
                s = team_stats[h]; s['gp'] += 1; s['pf'] += hs; s['pa'] += as_; s['w'] += 1 if home_win else 0; s['l'] += 0 if home_win else 1
                # away
                s = team_stats[a]; s['gp'] += 1; s['pf'] += as_; s['pa'] += hs; s['w'] += 0 if home_win else 1; s['l'] += 1 if home_win else 0

        updated = 0
        for t in team_data.get('teams', []):
            name = t.get('team_name')
            s = team_stats.get(name)
            if not s or s['gp'] == 0:
                continue
            gp = s['gp']
            t['basic_stats']['ppg'] = round(s['pf'] / gp, 1)
            t['basic_stats']['papg'] = round(s['pa'] / gp, 1)
            t['wins'] = s['w']
            t['losses'] = s['l']
            t['win_pct'] = round(s['w'] / gp, 3)
            # Simple advanced metrics
            t['advanced_metrics']['net_rtg'] = round(t['basic_stats']['ppg'] - t['basic_stats']['papg'], 1)
            t['advanced_metrics']['ortg'] = t['basic_stats']['ppg']
            t['advanced_metrics']['drtg'] = t['basic_stats']['papg']
            updated += 1

        team_data['metadata']['export_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        team_data['metadata']['data_source'] = 'NBA Stats API - Updated from Real Game Results'
        team_data['metadata']['description'] = f"Team data updated from {game_data.get('metadata', {}).get('total_games', 'N/A')} games"

        with open('data/nba_team_data.json', 'w') as f:
            json.dump(team_data, f, indent=2)

        logger.info(f"📈 Team stats updated for {updated} teams based on completed games")
    
    def schedule_daily_refresh(self):
        """Schedule daily data refresh"""
        # Schedule refresh at 9 AM PST (morning - gets previous night's results)
        schedule.every().day.at("09:00").do(self.refresh_daily_data)
        
        # Schedule refresh at 11 PM PST (evening - gets that day's final results)
        schedule.every().day.at("23:00").do(self.refresh_daily_data)
        
        logger.info("⏰ Scheduled daily data refresh:")
        logger.info("   - 9:00 AM PST (morning - previous night's results)")
        logger.info("   - 11:00 PM PST (evening - that day's final results)")
        
        # Run initial refresh
        self.refresh_daily_data()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_manual_refresh(self):
        """Run manual refresh for testing"""
        logger.info("🔧 MANUAL DATA REFRESH")
        logger.info("=" * 40)
        
        success = self.refresh_daily_data()
        
        if success:
            logger.info("✅ Manual refresh completed successfully")
        else:
            logger.error("❌ Manual refresh failed")
        
        return success

def main():
    """Main function"""
    refresh_system = AutomatedDataRefresh()
    
    print("🤖 AUTOMATED NBA DATA REFRESH SYSTEM")
    print("=" * 50)
    print("Choose an option:")
    print("1. Run manual refresh now")
    print("2. Start automated daily refresh")
    print("3. Test data fetching")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        refresh_system.run_manual_refresh()
    elif choice == "2":
        print("🔄 Starting automated daily refresh...")
        print("Press Ctrl+C to stop")
        refresh_system.schedule_daily_refresh()
    elif choice == "3":
        print("🧪 Testing data fetching...")
        refresh_system.refresh_daily_data()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
