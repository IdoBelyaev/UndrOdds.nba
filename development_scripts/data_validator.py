#!/usr/bin/env python3
"""
NBA Data Validator
Validates that all data is correct and complete
"""

import json
from datetime import datetime, date

class DataValidator:
    def __init__(self):
        self.data_dir = 'data/'
    
    def validate_all_data(self):
        """Validate all data files"""
        print("🔍 NBA DATA VALIDATOR")
        print("=" * 50)
        
        results = {
            'game_data': self._validate_game_data(),
            'team_data': self._validate_team_data(),
            'injury_data': self._validate_injury_data(),
            'bet_history': self._validate_bet_history()
        }
        
        # Overall assessment
        all_valid = all(results.values())
        
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"   Game Data: {'✅ Valid' if results['game_data'] else '❌ Issues'}")
        print(f"   Team Data: {'✅ Valid' if results['team_data'] else '❌ Issues'}")
        print(f"   Injury Data: {'✅ Valid' if results['injury_data'] else '❌ Issues'}")
        print(f"   Bet History: {'✅ Valid' if results['bet_history'] else '❌ Issues'}")
        
        if all_valid:
            print(f"\n🎉 ALL DATA IS VALID!")
        else:
            print(f"\n⚠️ SOME DATA HAS ISSUES - CHECK ABOVE")
        
        return results
    
    def _validate_game_data(self):
        """Validate game data"""
        print("\n🏀 VALIDATING GAME DATA:")
        try:
            with open(f'{self.data_dir}nba_game_data.json', 'r') as f:
                data = json.load(f)
            
            games = data.get('games', [])
            metadata = data.get('metadata', {})
            
            print(f"   Total games: {len(games)}")
            print(f"   Date range: {metadata.get('date_range', {}).get('start', 'Unknown')} to {metadata.get('date_range', {}).get('end', 'Unknown')}")
            print(f"   Data source: {metadata.get('data_source', 'Unknown')}")
            
            # Check for required fields
            required_fields = ['game_id', 'date', 'away_team', 'home_team']
            missing_fields = []
            
            for game in games[:5]:  # Check first 5 games
                for field in required_fields:
                    if field not in game:
                        missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            # Check for duplicate games
            game_ids = [game['game_id'] for game in games]
            duplicates = len(game_ids) - len(set(game_ids))
            if duplicates > 0:
                print(f"   ❌ Found {duplicates} duplicate games")
                return False
            
            print(f"   ✅ Game data is valid")
            return True
            
        except Exception as e:
            print(f"   ❌ Error reading game data: {e}")
            return False
    
    def _validate_team_data(self):
        """Validate team data"""
        print("\n🏀 VALIDATING TEAM DATA:")
        try:
            with open(f'{self.data_dir}nba_team_data.json', 'r') as f:
                data = json.load(f)
            
            teams = data.get('teams', [])
            metadata = data.get('metadata', {})
            
            print(f"   Total teams: {len(teams)}")
            print(f"   Expected: 30 NBA teams")
            print(f"   Data source: {metadata.get('data_source', 'Unknown')}")
            
            if len(teams) != 30:
                print(f"   ❌ Expected 30 teams, found {len(teams)}")
                return False
            
            # Check for required fields
            required_fields = ['team_id', 'team_name', 'basic_stats']
            missing_fields = []
            
            for team in teams[:5]:  # Check first 5 teams
                for field in required_fields:
                    if field not in team:
                        missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            print(f"   ✅ Team data is valid")
            return True
            
        except Exception as e:
            print(f"   ❌ Error reading team data: {e}")
            return False
    
    def _validate_injury_data(self):
        """Validate injury data"""
        print("\n🏥 VALIDATING INJURY DATA:")
        try:
            with open(f'{self.data_dir}nba_injury_data.json', 'r') as f:
                data = json.load(f)
            
            injuries = data.get('injuries', [])
            metadata = data.get('metadata', {})
            
            print(f"   Total players: {len(injuries)}")
            print(f"   Data source: {metadata.get('data_source', 'Unknown')}")
            
            # Check injury status distribution
            status_summary = metadata.get('injury_status_summary', {})
            print(f"   Injury status distribution:")
            for status, count in status_summary.items():
                print(f"     {status}: {count} players")
            
            # Check for required fields
            required_fields = ['player_id', 'player_name', 'team_name', 'injury_status']
            missing_fields = []
            
            for injury in injuries[:5]:  # Check first 5 injuries
                for field in required_fields:
                    if field not in injury:
                        missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            print(f"   ✅ Injury data is valid")
            return True
            
        except Exception as e:
            print(f"   ❌ Error reading injury data: {e}")
            return False
    
    def _validate_bet_history(self):
        """Validate bet history"""
        print("\n💰 VALIDATING BET HISTORY:")
        try:
            with open(f'{self.data_dir}bet_history.json', 'r') as f:
                data = json.load(f)
            
            bets = data.get('bets', [])
            total_bets = data.get('total_bets', 0)
            
            print(f"   Total bets: {len(bets)}")
            print(f"   Recorded total: {total_bets}")
            
            if len(bets) != total_bets:
                print(f"   ❌ Mismatch: {len(bets)} bets vs {total_bets} recorded")
                return False
            
            print(f"   ✅ Bet history is valid")
            return True
            
        except Exception as e:
            print(f"   ❌ Error reading bet history: {e}")
            return False
    
    def check_date_accuracy(self, selected_date):
        """Check if the selected date has the correct games"""
        print(f"\n📅 CHECKING DATE ACCURACY FOR {selected_date}:")
        
        try:
            with open(f'{self.data_dir}nba_game_data.json', 'r') as f:
                data = json.load(f)
            
            games = data.get('games', [])
            date_str = selected_date.strftime('%Y-%m-%d')
            
            # Filter games for the selected date
            date_games = [g for g in games if g['date'].startswith(date_str)]
            
            print(f"   Games on {date_str}: {len(date_games)}")
            
            if len(date_games) == 0:
                print(f"   ❌ No games found for {date_str}")
                return False
            
            # Show the games
            print(f"   Games found:")
            for i, game in enumerate(date_games, 1):
                print(f"     {i}. {game['away_team']} @ {game['home_team']}")
            
            print(f"   ✅ Date accuracy confirmed")
            return True
            
        except Exception as e:
            print(f"   ❌ Error checking date accuracy: {e}")
            return False

def main():
    """Main function"""
    validator = DataValidator()
    
    # Validate all data
    results = validator.validate_all_data()
    
    # Check today's date accuracy
    today = date.today()
    validator.check_date_accuracy(today)

if __name__ == "__main__":
    main()
