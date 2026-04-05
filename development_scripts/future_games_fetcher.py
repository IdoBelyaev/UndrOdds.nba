#!/usr/bin/env python3
"""
Future NBA Games Fetcher
Fetches NBA games for future dates and saves them to the data file
"""

import json
from datetime import datetime, timedelta
from espn_data_fetcher import ESPNDataFetcher

class FutureGamesFetcher:
    def __init__(self):
        self.espn_fetcher = ESPNDataFetcher()
        self.data_file = 'data/nba_game_data.json'
    
    def fetch_future_games(self, days_ahead=7):
        """Fetch games for the next N days"""
        print("🔮 FUTURE NBA GAMES FETCHER")
        print("=" * 50)
        
        # Fetch upcoming games
        future_games = self.espn_fetcher.fetch_upcoming_games(days_ahead)
        
        if future_games:
            print(f"\\n📊 Found {len(future_games)} future games")
            
            # Group by date
            games_by_date = {}
            for game in future_games:
                date = game['date'][:10]  # Get just the date part
                if date not in games_by_date:
                    games_by_date[date] = []
                games_by_date[date].append(game)
            
            print(f"\\n📅 Games by date:")
            for date in sorted(games_by_date.keys()):
                print(f"   {date}: {len(games_by_date[date])} games")
            
            # Save to file
            self._save_future_games(future_games)
            
            return future_games
        else:
            print("❌ No future games found")
            return []
    
    def _save_future_games(self, future_games):
        """Save future games to the data file"""
        try:
            # Load existing data
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {
                    "metadata": {
                        "season": "2025-26",
                        "data_source": "ESPN API - Future Games",
                        "export_date": datetime.now().isoformat(),
                        "date_range": {"start": "", "end": ""}
                    },
                    "games": []
                }
            
            # Merge with existing games (avoid duplicates)
            existing_games = data.get('games', [])
            existing_game_ids = {game['game_id'] for game in existing_games}
            
            # Add new games that don't already exist
            new_games = []
            for game in future_games:
                if game['game_id'] not in existing_game_ids:
                    new_games.append(game)
            
            # Combine existing and new games
            all_games = existing_games + new_games
            
            # Update metadata
            data['games'] = all_games
            data['metadata']['data_source'] = 'ESPN API - Complete Schedule'
            data['metadata']['export_date'] = datetime.now().isoformat()
            
            if all_games:
                dates = [game['date'][:10] for game in all_games]
                data['metadata']['date_range'] = {
                    "start": min(dates),
                    "end": max(dates)
                }
            
            # Save to file
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Saved {len(new_games)} new games to {self.data_file}")
            print(f"   Total games in file: {len(all_games)}")
            
        except Exception as e:
            print(f"❌ Error saving future games: {e}")
    
    def fetch_specific_date(self, target_date):
        """Fetch games for a specific future date"""
        print(f"📅 FETCHING GAMES FOR {target_date}")
        print("=" * 40)
        
        games = self.espn_fetcher.fetch_games_for_date(target_date)
        
        if games:
            print(f"✅ Found {len(games)} games for {target_date}")
            
            # Show the games
            for i, game in enumerate(games, 1):
                print(f"   {i}. {game['away_team']} @ {game['home_team']}")
            
            # Save to file
            self._save_future_games(games)
            
            return games
        else:
            print(f"❌ No games found for {target_date}")
            return []
    
    def fetch_week_schedule(self):
        """Fetch games for the next week"""
        return self.fetch_future_games(7)
    
    def fetch_month_schedule(self):
        """Fetch games for the next month"""
        return self.fetch_future_games(30)

def main():
    """Main function"""
    fetcher = FutureGamesFetcher()
    
    print("🔮 FUTURE NBA GAMES FETCHER")
    print("=" * 50)
    print("Choose an option:")
    print("1. Fetch next 7 days")
    print("2. Fetch next 30 days")
    print("3. Fetch specific date")
    print("4. Fetch next week")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        fetcher.fetch_future_games(7)
    elif choice == "2":
        fetcher.fetch_future_games(30)
    elif choice == "3":
        date = input("Enter date (YYYY-MM-DD): ").strip()
        fetcher.fetch_specific_date(date)
    elif choice == "4":
        fetcher.fetch_week_schedule()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
