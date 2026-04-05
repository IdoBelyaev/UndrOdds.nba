#!/usr/bin/env python3
"""
ESPN NBA Data Fetcher
Gets NBA games and data from ESPN API as alternative to NBA API
"""

import json
import requests
from datetime import datetime, timedelta
import time

class ESPNDataFetcher:
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_today_games(self):
        """Fetch today's NBA games from ESPN"""
        print("🏀 FETCHING TODAY'S NBA GAMES FROM ESPN")
        print("=" * 50)
        
        try:
            # ESPN scoreboard endpoint
            url = f"{self.base_url}/scoreboard"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            print(f"📊 ESPN API Results:")
            print(f"   Total events: {len(events)}")
            print(f"   Date: {data.get('date', 'Unknown')}")
            
            games = []
            for event in events:
                game = self._process_event(event)
                if game:
                    games.append(game)
            
            print(f"✅ Successfully processed {len(games)} games")
            return games
            
        except Exception as e:
            print(f"❌ ESPN API error: {e}")
            return []
    
    def fetch_games_for_date(self, target_date):
        """Fetch games for a specific date"""
        print(f"🏀 FETCHING NBA GAMES FOR {target_date}")
        print("=" * 50)
        
        try:
            # ESPN scoreboard endpoint with date parameter
            # ESPN API expects YYYYMMDD format, not YYYY-MM-DD
            if '-' in target_date:
                espn_date = target_date.replace('-', '')
            else:
                espn_date = target_date
                
            url = f"{self.base_url}/scoreboard"
            params = {'dates': espn_date}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            print(f"📊 ESPN API Results for {target_date} (format: {espn_date}):")
            print(f"   Total events: {len(events)}")
            
            games = []
            for event in events:
                game = self._process_event(event)
                if game:
                    games.append(game)
            
            print(f"✅ Successfully processed {len(games)} games for {target_date}")
            return games
            
        except Exception as e:
            print(f"❌ ESPN API error for {target_date}: {e}")
            return []
    
    def fetch_games_for_date_range(self, start_date, end_date):
        """Fetch games for a date range"""
        print(f"🏀 FETCHING NBA GAMES FOR DATE RANGE: {start_date} to {end_date}")
        print("=" * 60)
        
        all_games = []
        
        # Generate list of dates
        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"\\n📅 Fetching games for {date_str}...")
            
            games = self.fetch_games_for_date(date_str)
            all_games.extend(games)
            
            current_date += timedelta(days=1)
        
        print(f"\\n📊 TOTAL GAMES FOUND: {len(all_games)}")
        return all_games
    
    def fetch_upcoming_games(self, days_ahead=7):
        """Fetch upcoming games for the next N days"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        start_date_str = today.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"🔮 FETCHING UPCOMING GAMES (Next {days_ahead} days)")
        print("=" * 50)
        
        return self.fetch_games_for_date_range(start_date_str, end_date_str)
    
    def _process_event(self, event):
        """Process ESPN event data into our game format"""
        try:
            # Get basic event info
            event_id = event.get('id', '')
            name = event.get('name', '')
            date = event.get('date', '')
            status = event.get('status', {})
            
            # Get competition data
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            comp = competitions[0]
            competitors = comp.get('competitors', [])
            
            if len(competitors) < 2:
                return None
            
            # Get team data
            away_team_data = competitors[0]
            home_team_data = competitors[1]
            
            away_team = away_team_data.get('team', {}).get('displayName', 'Away Team')
            home_team = home_team_data.get('team', {}).get('displayName', 'Home Team')
            away_score = int(away_team_data.get('score', 0))
            home_score = int(home_team_data.get('score', 0))
            
            # Determine winner
            home_win = home_score > away_score if away_score > 0 or home_score > 0 else False
            
            # Determine status
            status_type = status.get('type', '')
            if status_type == 'STATUS_FINAL':
                game_status = 'Completed'
            elif status_type == 'STATUS_SCHEDULED':
                game_status = 'Scheduled'
            else:
                game_status = 'In Progress'
            
            # Get quarter and time information from ESPN status
            quarter_info = ''
            time_left = ''
            
            # Extract from status details
            detail = status.get('detail', '')
            short_detail = status.get('shortDetail', '')
            
            # Parse quarter and time information
            if status_type == 'STATUS_IN_PROGRESS':
                if 'Halftime' in detail:
                    quarter_info = 'Halftime'
                elif 'End of' in detail:
                    quarter_info = short_detail if short_detail else detail
                elif 'Quarter' in detail:
                    quarter_info = short_detail if short_detail else detail
                    # Extract time left from detail (format: "X:XX - 2nd Quarter")
                    if ':' in detail and ' - ' in detail:
                        time_left = detail.split(' - ')[0]
                else:
                    quarter_info = short_detail if short_detail else detail
                    
            elif status_type == 'STATUS_SCHEDULED':
                quarter_info = 'Scheduled'
                time_left = detail if detail else short_detail
                    
            elif status_type == 'STATUS_FINAL':
                quarter_info = 'Final'
                time_left = ''
            
            # Debug: Print status info for troubleshooting
            if quarter_info or time_left:
                print(f"   Debug: {away_team} @ {home_team} - Quarter: '{quarter_info}', Time: '{time_left}'")
            
            # Format date - preserve timezone info
            if date:
                try:
                    # Keep the original ESPN date format with timezone
                    if date.endswith('Z'):
                        # ESPN gives us UTC times, keep the Z for timezone info
                        formatted_date = date
                    else:
                        # If no timezone, assume UTC
                        formatted_date = f"{date}Z"
                except:
                    formatted_date = f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}Z"
            else:
                formatted_date = f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}Z"
            
            game_data = {
                'game_id': f"espn_{event_id}",
                'date': formatted_date,
                'away_team': away_team,
                'home_team': home_team,
                'away_score': away_score,
                'home_score': home_score,
                'home_win': home_win,
                'status': game_status,
                'espn_status': status_type,
                'quarter': quarter_info,
                'time_left': time_left,
                'data_source': 'ESPN API'
            }
            
            return game_data
            
        except Exception as e:
            print(f"⚠️ Error processing event: {e}")
            return None
    
    def save_games_to_file(self, games, filename='data/nba_game_data.json'):
        """Save games to JSON file"""
        if not games:
            print("❌ No games to save")
            return
        
        # Load existing data
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {
                "metadata": {
                    "season": "2025-26",
                    "data_source": "ESPN API",
                    "export_date": datetime.now().isoformat(),
                    "date_range": {"start": "", "end": ""}
                },
                "games": []
            }
        
        # Update with new games
        data['games'] = games
        data['metadata']['data_source'] = 'ESPN API'
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
        
        print(f"💾 Saved {len(games)} games to {filename}")
    
    def fetch_and_save_today_games(self):
        """Fetch today's games and save to file"""
        games = self.fetch_today_games()
        
        if games:
            self.save_games_to_file(games)
            
            print(f"\\n🎮 Today's games:")
            for game in games:
                status_icon = "🏁" if game['status'] == 'Completed' else "⏰" if game['status'] == 'Scheduled' else "🏃"
                print(f"   {status_icon} {game['away_team']} @ {game['home_team']} - {game['away_score']}-{game['home_score']} ({game['status']})")
        else:
            print("❌ No games found for today")
        
        return games

def main():
    """Main function"""
    fetcher = ESPNDataFetcher()
    
    print("🏀 ESPN NBA DATA FETCHER")
    print("=" * 40)
    
    # Fetch today's games
    games = fetcher.fetch_and_save_today_games()
    
    if games:
        print(f"\\n✅ SUCCESS! Found {len(games)} games via ESPN API")
        print(f"   This solves the NBA API issue!")
    else:
        print("\\n❌ No games found")

if __name__ == "__main__":
    main()
