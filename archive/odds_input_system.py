#!/usr/bin/env python3
"""
🏀 UNDERDOG FANTASY MONEYLINE INPUT SYSTEM
==========================================

User-friendly interface for manually inputting Underdog Fantasy moneyline odds.
Designed to be simple, intuitive, and error-free.

Usage:
    python odds_input_system.py
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import pandas as pd

# NBA Team Names (for validation)
NBA_TEAMS = [
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
    'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
    'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
    'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
    'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
    'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
    'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
    'Utah Jazz', 'Washington Wizards'
]

def print_header():
    """Print a beautiful header for the input system."""
    print("🏀" + "="*60 + "🏀")
    print("   UNDERDOG FANTASY MONEYLINE INPUT SYSTEM")
    print("🏀" + "="*60 + "🏀")
    print()

def print_instructions():
    """Print clear instructions for the user."""
    print("📋 INSTRUCTIONS:")
    print("   1. Enter the game date (DD-MM-YYYY format)")
    print("   2. System will show all NBA games for that date")
    print("   3. Enter Underdog Fantasy moneyline odds for each game")
    print("   4. Review and confirm all inputs")
    print("   5. Save to the database")
    print()
    print("💡 TIP: Moneyline odds are like +150 or -200")
    print("   • Positive odds (+150) = Underdog")
    print("   • Negative odds (-200) = Favorite")
    print()
    print("🎯 SEASON INFO:")
    print("   • Testing: Use 2024-2025 season data (complete games)")
    print("   • Live betting: Ready for 2025-2026 season when it starts")
    print()

def get_game_date() -> str:
    """Get game date from user with validation."""
    while True:
        try:
            date_input = input("📅 Enter game date (DD-MM-YYYY): ").strip()
            
            # Try to parse the date in DD-MM-YYYY format
            game_date = datetime.strptime(date_input, "%d-%m-%Y").date()
            
            # Check if date is reasonable (not too far in past/future)
            today = date.today()
            
            # Allow dates from 2024-25 season onwards (NBA 2024-25 season started Oct 2024)
            if game_date < date(2024, 10, 1):
                print("❌ Date is too far in the past. Please enter a date from October 2024 onwards.")
                print("💡 Note: Use 2024-2025 season data for testing, 2025-2026 for live betting.")
                continue
            if game_date > today + timedelta(days=365):
                print("❌ Date is too far in the future. Please enter a reasonable date.")
                continue
            
            # Convert back to YYYY-MM-DD format for internal use
            formatted_date = game_date.strftime("%Y-%m-%d")
            return formatted_date
            
        except ValueError:
            print("❌ Invalid date format. Please use DD-MM-YYYY (e.g., 22-10-2024)")
        except Exception as e:
            print(f"❌ Error: {e}")


def get_moneyline_odds(team_name: str) -> int:
    """Get moneyline odds from user with validation."""
    while True:
        try:
            odds_input = input(f"💰 Enter Underdog Fantasy moneyline for {team_name}: ").strip()
            
            # Remove any spaces and validate format
            odds_input = odds_input.replace(" ", "")
            
            # Check if it starts with + or -
            if not (odds_input.startswith('+') or odds_input.startswith('-')):
                print("❌ Moneyline odds must start with + or - (e.g., +150 or -200)")
                continue
            
            # Convert to integer
            odds = int(odds_input)
            
            # Validate reasonable range
            if odds < -1000 or odds > 1000:
                print("❌ Odds seem unrealistic. Please check and re-enter.")
                continue
                
            print(f"✅ {team_name}: {odds_input}")
            return odds
            
        except ValueError:
            print("❌ Invalid odds format. Please enter like +150 or -200")
        except Exception as e:
            print(f"❌ Error: {e}")

def calculate_implied_probability(odds: int) -> float:
    """Calculate implied probability from moneyline odds."""
    if odds > 0:
        # Positive odds: probability = 100 / (odds + 100)
        return round(100 / (odds + 100), 4)
    else:
        # Negative odds: probability = |odds| / (|odds| + 100)
        return round(abs(odds) / (abs(odds) + 100), 4)


def load_existing_data() -> List[Dict]:
    """Load existing moneylines data."""
    if os.path.exists('underdog_moneylines.json'):
        try:
            with open('underdog_moneylines.json', 'r') as f:
                data = json.load(f)
                return data.get('moneylines', [])
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing data: {e}")
    return []

def load_nba_games() -> pd.DataFrame:
    """Load NBA game data to find games by date."""
    try:
        with open('nba_game_data.json', 'r') as f:
            data = json.load(f)
            games_df = pd.DataFrame(data['games'])
            games_df['date'] = pd.to_datetime(games_df['date'])
            return games_df
    except Exception as e:
        print(f"❌ Error loading NBA game data: {e}")
        return pd.DataFrame()

def get_games_for_date(games_df: pd.DataFrame, target_date: str) -> List[Dict]:
    """Get all NBA games for a specific date."""
    try:
        target_date_obj = pd.to_datetime(target_date).date()
        
        # Filter games for the target date
        games_on_date = games_df[games_df['date'].dt.date == target_date_obj]
        
        if games_on_date.empty:
            return []
        
        # Convert to list of dictionaries
        games_list = []
        for _, game in games_on_date.iterrows():
            games_list.append({
                'game_id': game['game_id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'game_date': target_date
            })
        
        return games_list
        
    except Exception as e:
        print(f"❌ Error filtering games by date: {e}")
        return []

def save_moneylines_data(moneylines: List[Dict]):
    """Save moneylines data to JSON file."""
    data = {
        "metadata": {
            "data_source": "Manual Input - Underdog Fantasy",
            "last_updated": datetime.now().isoformat(),
            "total_games": len(moneylines),
            "input_method": "Interactive Command Line Interface"
        },
        "moneylines": moneylines
    }
    
    with open('underdog_moneylines.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Data saved to underdog_moneylines.json")

def display_games_for_date(games: List[Dict]):
    """Display all games for the selected date."""
    if not games:
        print("❌ No games found for this date.")
        return
    
    # Convert YYYY-MM-DD back to DD-MM-YYYY for display
    display_date = datetime.strptime(games[0]['game_date'], "%Y-%m-%d").strftime("%d-%m-%Y")
    
    print(f"\n🏀 GAMES ON {display_date}:")
    print("=" * 60)
    
    for i, game in enumerate(games, 1):
        print(f"   {i}. {game['away_team']} @ {game['home_team']}")
    
    print("=" * 60)
    print(f"📊 Total games: {len(games)}")
    print()

def input_moneylines_for_games(games: List[Dict]) -> List[Dict]:
    """Input moneylines for all games on the date."""
    game_data_list = []
    
    print("💰 ENTER UNDERDOG FANTASY MONEYLINES:")
    print("-" * 50)
    
    for i, game in enumerate(games, 1):
        print(f"\n🎯 Game {i}/{len(games)}: {game['away_team']} @ {game['home_team']}")
        print("-" * 40)
        
        # Get moneylines for this game
        home_ml = get_moneyline_odds(game['home_team'])
        away_ml = get_moneyline_odds(game['away_team'])
        
        # Calculate implied probabilities
        home_prob = calculate_implied_probability(home_ml)
        away_prob = calculate_implied_probability(away_ml)
        
        # Create game data
        game_data = {
            "game_id": game['game_id'],
            "date": game['game_date'],
            "home_team": game['home_team'],
            "away_team": game['away_team'],
            "underdog_ml_home": home_ml,
            "underdog_ml_away": away_ml,
            "implied_prob_home": home_prob,
            "implied_prob_away": away_prob,
            "input_timestamp": datetime.now().isoformat()
        }
        
        game_data_list.append(game_data)
    
    return game_data_list

def confirm_batch_input(game_data_list: List[Dict]) -> bool:
    """Display summary of all games and get user confirmation."""
    print("\n" + "="*80)
    print("📋 REVIEW ALL GAMES:")
    print("="*80)
    
    for i, game_data in enumerate(game_data_list, 1):
        # Convert YYYY-MM-DD back to DD-MM-YYYY for display
        display_date = datetime.strptime(game_data['date'], "%Y-%m-%d").strftime("%d-%m-%Y")
        print(f"{i}. {display_date}: {game_data['away_team']} ({game_data['underdog_ml_away']:+d}) @ {game_data['home_team']} ({game_data['underdog_ml_home']:+d})")
        print(f"   Implied Probability: {game_data['away_team']} {game_data['implied_prob_away']:.1%} | {game_data['home_team']} {game_data['implied_prob_home']:.1%}")
        print()
    
    print("="*80)
    
    while True:
        confirm = input("✅ Save all these games? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            return True
        elif confirm in ['n', 'no']:
            return False
        else:
            print("❌ Please enter 'y' for yes or 'n' for no")

def display_recent_games(moneylines: List[Dict], limit: int = 5):
    """Display recent games for reference."""
    if not moneylines:
        return
        
    print(f"\n📊 RECENT GAMES (Last {limit}):")
    print("-" * 80)
    
    recent_games = sorted(moneylines, key=lambda x: x['date'], reverse=True)[:limit]
    
    for game in recent_games:
        print(f"   {game['date']}: {game['away_team']} ({game['underdog_ml_away']:+d}) @ {game['home_team']} ({game['underdog_ml_home']:+d})")
    
    print("-" * 80)

def main():
    """Main function to run the input system."""
    print_header()
    print_instructions()
    
    # Load existing data
    existing_moneylines = load_existing_data()
    display_recent_games(existing_moneylines)
    
    # Load NBA games data
    print("\n🔄 Loading NBA game data...")
    games_df = load_nba_games()
    if games_df.empty:
        print("❌ Could not load NBA game data. Please ensure nba_game_data.json exists.")
        return
    
    print("✅ NBA game data loaded successfully!")
    
    print("\n🚀 Starting batch input for a date...")
    print("-" * 50)
    
    # Get game date
    game_date = get_game_date()
    
    # Find games for that date
    print(f"\n🔍 Finding games for {game_date}...")
    games_for_date = get_games_for_date(games_df, game_date)
    
    if not games_for_date:
        print(f"❌ No NBA games found for {game_date}")
        print("💡 Try a different date or check if games are scheduled.")
        return
    
    # Display games for the date
    display_games_for_date(games_for_date)
    
    # Input moneylines for all games
    game_data_list = input_moneylines_for_games(games_for_date)
    
    # Confirm and save
    if confirm_batch_input(game_data_list):
        existing_moneylines.extend(game_data_list)
        save_moneylines_data(existing_moneylines)
        print(f"\n🎉 {len(game_data_list)} games saved successfully!")
        print(f"📊 Total games in database: {len(existing_moneylines)}")
    else:
        print("\n❌ Input cancelled. No data saved.")
    
    # Ask if user wants to input another date
    while True:
        another = input("\n🔄 Input moneylines for another date? (y/n): ").strip().lower()
        if another in ['y', 'yes']:
            print("\n" + "="*60)
            main()  # Recursive call for another date
            break
        elif another in ['n', 'no']:
            print("\n👋 Thanks for using the Underdog Fantasy Moneyline Input System!")
            break
        else:
            print("❌ Please enter 'y' for yes or 'n' for no")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Input cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please try again or contact support.")
