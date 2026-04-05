#!/usr/bin/env python3
"""
Fetch Upcoming NBA Games
Fetches scheduled games for the next 2 weeks and adds them to the database
"""
import json
import requests
from datetime import datetime, timedelta
import time

def fetch_upcoming_games(days_ahead=14):
    """Fetch upcoming NBA games from ESPN API"""
    print("🔮 FETCHING UPCOMING NBA GAMES")
    print("=" * 50)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    all_games = []
    today = datetime.now()
    
    print(f"📅 Fetching games for next {days_ahead} days...")
    
    for i in range(days_ahead):
        target_date = today + timedelta(days=i)
        date_str = target_date.strftime('%Y-%m-%d')
        espn_date = target_date.strftime('%Y%m%d')
        
        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
            params = {'dates': espn_date}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            for event in events:
                game = process_espn_event(event, date_str)
                if game:
                    all_games.append(game)
            
            if events:
                print(f"   ✅ {date_str}: {len(events)} games")
            
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            print(f"   ⚠️ {date_str}: Error - {e}")
            continue
    
    print(f"\n📊 Found {len(all_games)} upcoming games")
    
    # Save to file
    if all_games:
        save_games(all_games)
    
    return all_games

def process_espn_event(event, date_str):
    """Process ESPN event into our game format"""
    try:
        competitions = event.get('competitions', [])
        if not competitions:
            return None
        
        comp = competitions[0]
        competitors = comp.get('competitors', [])
        
        if len(competitors) != 2:
            return None
        
        # Determine home/away
        home_team = None
        away_team = None
        
        for team in competitors:
            if team.get('homeAway') == 'home':
                home_team = team.get('team', {}).get('displayName', '')
            else:
                away_team = team.get('team', {}).get('displayName', '')
        
        if not home_team or not away_team:
            return None
        
        # Get scores (0 if not played yet)
        home_score = int(competitors[0].get('score', 0)) if competitors[0].get('homeAway') == 'home' else int(competitors[1].get('score', 0))
        away_score = int(competitors[1].get('score', 0)) if competitors[1].get('homeAway') == 'away' else int(competitors[0].get('score', 0))
        
        # Game ID
        game_id = event.get('id', '')
        
        # Create game object
        game = {
            'game_id': f"espn_{game_id}",
            'date': f"{date_str} 00:00:00",
            'season': '2025-26',
            'season_type': 'Regular Season',
            'home_team': home_team,
            'away_team': away_team,
            'home_team_id': 0,  # Will be filled later
            'away_team_id': 0,
            'home_team_abbr': '',  # Will be filled later
            'away_team_abbr': '',
            'home_score': home_score,
            'away_score': away_score,
            'home_win': 1 if home_score > away_score else 0,
            'away_win': 1 if away_score > home_score else 0,
            # Add placeholder stats for future games
            'home_fgm': 0, 'home_fga': 0, 'home_fg_pct': 0.0,
            'home_fg3m': 0, 'home_fg3a': 0, 'home_fg3_pct': 0.0,
            'home_ftm': 0, 'home_fta': 0, 'home_ft_pct': 0.0,
            'home_reb': 0, 'home_ast': 0, 'home_stl': 0, 'home_blk': 0, 'home_tov': 0,
            'away_fgm': 0, 'away_fga': 0, 'away_fg_pct': 0.0,
            'away_fg3m': 0, 'away_fg3a': 0, 'away_fg3_pct': 0.0,
            'away_ftm': 0, 'away_fta': 0, 'away_ft_pct': 0.0,
            'away_reb': 0, 'away_ast': 0, 'away_stl': 0, 'away_blk': 0, 'away_tov': 0,
            'total_points': home_score + away_score,
            'point_differential': home_score - away_score
        }
        
        return game
        
    except Exception as e:
        return None

def save_games(new_games):
    """Save new games to the data file"""
    data_file = 'data/nba_game_data.json'
    
    try:
        # Load existing data
        with open(data_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
            "metadata": {
                "season": "2025-26",
                "data_source": "ESPN API - Upcoming Games",
                "export_date": datetime.now().isoformat(),
                "date_range": {"start": "", "end": ""}
            },
            "games": []
        }
    
    # Get existing games - track by both game_id AND matchup (date + teams)
    existing_games = data.get('games', [])
    existing_ids = {game.get('game_id') for game in existing_games}
    
    # Also track by matchup to avoid duplicates from different sources
    existing_matchups = {}
    for game in existing_games:
        date = game['date'][:10]
        matchup_key = f"{date}|{game['away_team']}|{game['home_team']}"
        existing_matchups[matchup_key] = game
    
    # Add only new games (check both game_id and matchup)
    added = 0
    skipped = 0
    for game in new_games:
        date = game['date'][:10]
        matchup_key = f"{date}|{game['away_team']}|{game['home_team']}"
        
        # Skip if game_id already exists
        if game['game_id'] in existing_ids:
            skipped += 1
            continue
        
        # Skip if matchup already exists (different source, same game)
        if matchup_key in existing_matchups:
            existing = existing_matchups[matchup_key]
            # Prefer NBA API games (00225...) over ESPN games (espn_...)
            if existing.get('game_id', '').startswith('00225') and game['game_id'].startswith('espn_'):
                skipped += 1
                continue
            # If ESPN already exists and we have NBA API, replace it
            elif existing.get('game_id', '').startswith('espn_') and game['game_id'].startswith('00225'):
                # Remove old ESPN version
                existing_games = [g for g in existing_games if g != existing]
                existing_matchups[matchup_key] = game
                existing_games.append(game)
                existing_ids.add(game['game_id'])
                added += 1
            else:
                skipped += 1
                continue
        else:
            # New unique game
            existing_games.append(game)
            existing_matchups[matchup_key] = game
            existing_ids.add(game['game_id'])
            added += 1
    
    # Update metadata
    data['games'] = existing_games
    data['metadata']['export_date'] = datetime.now().isoformat()
    data['metadata']['data_source'] = 'NBA Stats API + ESPN API - Complete Schedule'
    
    if existing_games:
        dates = [g['date'][:10] for g in existing_games]
        data['metadata']['date_range'] = {
            "start": min(dates),
            "end": max(dates)
        }
        data['metadata']['total_games'] = len(existing_games)
    
    # Save
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Added {added} new games to schedule")
    print(f"   Total games in database: {len(existing_games)}")
    print(f"   Date range: {data['metadata']['date_range']['start']} to {data['metadata']['date_range']['end']}")

if __name__ == "__main__":
    fetch_upcoming_games(14)  # Next 2 weeks

