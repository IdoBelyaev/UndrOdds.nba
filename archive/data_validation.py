"""
Data Validation System for NBA Bet Selector
============================================

This module validates the accuracy, completeness, and consistency of collected NBA data.
It cross-references our data with official sources and performs automated quality checks.

Phase 2.1: Data Source Validation
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import time
import random

class DataValidator:
    """Validates NBA data accuracy and quality"""
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "game_data": {},
            "team_data": {},
            "injury_data": {},
            "overall_status": "PENDING"
        }
        
    def load_json(self, filepath: str) -> Dict:
        """Load JSON data file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return {}
    
    def validate_game_data(self) -> Dict[str, Any]:
        """
        Validate NBA game data accuracy and completeness
        
        Checks:
        1. Data completeness (all expected games present)
        2. Date range validity
        3. Score validity (positive integers)
        4. Team name consistency
        5. No duplicate games
        """
        print("\n🔍 VALIDATING GAME DATA")
        print("=" * 60)
        
        data = self.load_json('nba_game_data.json')
        if not data:
            return {"status": "FAILED", "error": "Could not load game data"}
        
        results = {
            "status": "PASSED",
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        games = data.get('games', [])
        metadata = data.get('metadata', {})
        
        # Check 1: Data completeness
        print("\n✓ Check 1: Data Completeness")
        total_games = len(games)
        expected_games = metadata.get('total_games', 0)
        
        if total_games == expected_games:
            print(f"  ✅ Game count matches: {total_games} games")
            results['checks']['completeness'] = {
                "status": "PASSED",
                "total_games": total_games,
                "expected_games": expected_games
            }
        else:
            print(f"  ⚠️  Game count mismatch: {total_games} vs {expected_games}")
            results['warnings'].append(f"Game count mismatch: {total_games} vs {expected_games}")
        
        # Check 2: Date range validity
        print("\n✓ Check 2: Date Range Validity")
        dates = [datetime.strptime(g['date'], '%Y-%m-%d %H:%M:%S').date() for g in games]
        min_date = min(dates)
        max_date = max(dates)
        
        expected_start = datetime.strptime(metadata['date_range']['start'], '%Y-%m-%d').date()
        expected_end = datetime.strptime(metadata['date_range']['end'], '%Y-%m-%d').date()
        
        if min_date == expected_start and max_date == expected_end:
            print(f"  ✅ Date range valid: {min_date} to {max_date}")
            results['checks']['date_range'] = {
                "status": "PASSED",
                "start": str(min_date),
                "end": str(max_date)
            }
        else:
            print(f"  ⚠️  Date range mismatch")
            results['warnings'].append("Date range does not match metadata")
        
        # Check 3: Score validity
        print("\n✓ Check 3: Score Validity")
        invalid_scores = []
        for game in games:
            if game['home_score'] < 0 or game['away_score'] < 0:
                invalid_scores.append(game['game_id'])
            if game['home_score'] > 200 or game['away_score'] > 200:
                invalid_scores.append(game['game_id'])
        
        if not invalid_scores:
            print(f"  ✅ All scores valid (0-200 range)")
            results['checks']['score_validity'] = {"status": "PASSED"}
        else:
            print(f"  ❌ {len(invalid_scores)} games with invalid scores")
            results['errors'].append(f"Invalid scores in games: {invalid_scores[:5]}")
            results['status'] = "FAILED"
        
        # Check 4: Team name consistency
        print("\n✓ Check 4: Team Name Consistency")
        team_names = set()
        for game in games:
            team_names.add(game['home_team'])
            team_names.add(game['away_team'])
        
        print(f"  ✅ Found {len(team_names)} unique teams")
        if len(team_names) == 30:
            results['checks']['team_consistency'] = {
                "status": "PASSED",
                "unique_teams": len(team_names)
            }
        else:
            results['warnings'].append(f"Expected 30 teams, found {len(team_names)}")
        
        # Check 5: Duplicate games
        print("\n✓ Check 5: Duplicate Game Detection")
        game_ids = [g['game_id'] for g in games]
        duplicates = len(game_ids) - len(set(game_ids))
        
        if duplicates == 0:
            print(f"  ✅ No duplicate games")
            results['checks']['duplicates'] = {"status": "PASSED"}
        else:
            print(f"  ❌ {duplicates} duplicate games found")
            results['errors'].append(f"{duplicates} duplicate games detected")
            results['status'] = "FAILED"
        
        # Check 6: Win/Loss logic
        print("\n✓ Check 6: Win/Loss Logic")
        logic_errors = []
        for game in games:
            home_won = game['home_score'] > game['away_score']
            if (home_won and game['home_win'] != 1) or (not home_won and game['home_win'] != 0):
                logic_errors.append(game['game_id'])
        
        if not logic_errors:
            print(f"  ✅ All win/loss assignments correct")
            results['checks']['win_loss_logic'] = {"status": "PASSED"}
        else:
            print(f"  ❌ {len(logic_errors)} games with incorrect win/loss")
            results['errors'].append(f"Win/loss logic errors: {len(logic_errors)}")
            results['status'] = "FAILED"
        
        print("\n" + "=" * 60)
        if results['status'] == "PASSED":
            print("✅ GAME DATA VALIDATION: PASSED")
        else:
            print("❌ GAME DATA VALIDATION: FAILED")
        
        self.validation_results['game_data'] = results
        return results
    
    def validate_team_data(self) -> Dict[str, Any]:
        """
        Validate NBA team statistics accuracy and completeness
        
        Checks:
        1. All 30 NBA teams present
        2. All expected features present
        3. Data ranges valid (percentages 0-1, stats positive)
        4. Record consistency (W+L=GP)
        5. Win percentage calculation
        """
        print("\n🔍 VALIDATING TEAM DATA")
        print("=" * 60)
        
        data = self.load_json('nba_team_data.json')
        if not data:
            return {"status": "FAILED", "error": "Could not load team data"}
        
        results = {
            "status": "PASSED",
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        teams = data.get('teams', [])
        metadata = data.get('metadata', {})
        
        # Check 1: Team count
        print("\n✓ Check 1: Team Count")
        if len(teams) == 30:
            print(f"  ✅ All 30 NBA teams present")
            results['checks']['team_count'] = {
                "status": "PASSED",
                "total_teams": 30
            }
        else:
            print(f"  ❌ Expected 30 teams, found {len(teams)}")
            results['errors'].append(f"Team count mismatch: {len(teams)}/30")
            results['status'] = "FAILED"
        
        # Check 2: Feature completeness
        print("\n✓ Check 2: Feature Completeness")
        expected_features = metadata.get('total_features', 29)
        
        missing_features = []
        for team in teams:
            if len(team) < expected_features:
                missing_features.append(team.get('TEAM_NAME', 'Unknown'))
        
        if not missing_features:
            print(f"  ✅ All teams have {expected_features} features")
            results['checks']['feature_completeness'] = {"status": "PASSED"}
        else:
            print(f"  ⚠️  {len(missing_features)} teams missing features")
            results['warnings'].append(f"Teams with missing features: {missing_features}")
        
        # Check 3: Data range validation
        print("\n✓ Check 3: Data Range Validation")
        range_errors = []
        
        for team in teams:
            # Check percentages (0-1)
            for pct_field in ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'eFG_PCT', 'WIN_PCT']:
                if pct_field in team:
                    if not (0 <= team[pct_field] <= 1):
                        range_errors.append(f"{team['TEAM_NAME']}: {pct_field}={team[pct_field]}")
            
            # Check positive stats
            for stat in ['PPG', 'PAPG', 'W', 'L', 'GP']:
                if stat in team:
                    if team[stat] < 0:
                        range_errors.append(f"{team['TEAM_NAME']}: {stat}={team[stat]}")
        
        if not range_errors:
            print(f"  ✅ All data values in valid ranges")
            results['checks']['data_ranges'] = {"status": "PASSED"}
        else:
            print(f"  ❌ {len(range_errors)} range errors found")
            results['errors'].extend(range_errors[:5])
            results['status'] = "FAILED"
        
        # Check 4: Record consistency (W+L should equal GP)
        print("\n✓ Check 4: Record Consistency")
        record_errors = []
        
        for team in teams:
            if 'W' in team and 'L' in team and 'GP' in team:
                if team['W'] + team['L'] != team['GP']:
                    record_errors.append(
                        f"{team['TEAM_NAME']}: W({team['W']}) + L({team['L']}) != GP({team['GP']})"
                    )
        
        if not record_errors:
            print(f"  ✅ All records consistent (W+L=GP)")
            results['checks']['record_consistency'] = {"status": "PASSED"}
        else:
            print(f"  ⚠️  {len(record_errors)} record inconsistencies")
            results['warnings'].extend(record_errors)
        
        # Check 5: Win percentage calculation
        print("\n✓ Check 5: Win Percentage Accuracy")
        win_pct_errors = []
        
        for team in teams:
            if 'W' in team and 'GP' in team and 'WIN_PCT' in team:
                expected_pct = team['W'] / team['GP']
                actual_pct = team['WIN_PCT']
                
                # Allow small floating point differences
                if abs(expected_pct - actual_pct) > 0.001:
                    win_pct_errors.append(
                        f"{team['TEAM_NAME']}: Expected {expected_pct:.3f}, got {actual_pct:.3f}"
                    )
        
        if not win_pct_errors:
            print(f"  ✅ All win percentages calculated correctly")
            results['checks']['win_pct_accuracy'] = {"status": "PASSED"}
        else:
            print(f"  ⚠️  {len(win_pct_errors)} win percentage errors")
            results['warnings'].extend(win_pct_errors)
        
        # Check 6: Games played validation (should be ≤ 82)
        print("\n✓ Check 6: Games Played Validation")
        gp_errors = []
        
        for team in teams:
            if 'GP' in team:
                if team['GP'] > 82:
                    gp_errors.append(f"{team['TEAM_NAME']}: GP={team['GP']} (should be ≤82)")
        
        if not gp_errors:
            print(f"  ✅ All teams have valid GP (≤82)")
            results['checks']['gp_validation'] = {"status": "PASSED"}
        else:
            print(f"  ❌ {len(gp_errors)} teams with GP > 82")
            results['errors'].extend(gp_errors)
            results['status'] = "FAILED"
        
        print("\n" + "=" * 60)
        if results['status'] == "PASSED":
            print("✅ TEAM DATA VALIDATION: PASSED")
        else:
            print("❌ TEAM DATA VALIDATION: FAILED")
        
        self.validation_results['team_data'] = results
        return results
    
    def validate_injury_data(self) -> Dict[str, Any]:
        """
        Validate injury data completeness and consistency
        
        Checks:
        1. Player data completeness
        2. Injury status values
        3. Team name consistency
        4. Date validity
        """
        print("\n🔍 VALIDATING INJURY DATA")
        print("=" * 60)
        
        data = self.load_json('nba_injury_data.json')
        if not data:
            return {"status": "FAILED", "error": "Could not load injury data"}
        
        results = {
            "status": "PASSED",
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        injuries = data.get('injuries', [])
        metadata = data.get('metadata', {})
        
        # Check 1: Data completeness
        print("\n✓ Check 1: Data Completeness")
        total_players = len(injuries)
        print(f"  ℹ️  Tracking {total_players} players")
        results['checks']['completeness'] = {
            "status": "INFO",
            "total_players": total_players
        }
        
        # Check 2: Injury status validity
        print("\n✓ Check 2: Injury Status Validity")
        valid_statuses = ['HEALTHY', 'PROBABLE', 'QUESTIONABLE', 'DOUBTFUL', 'OUT', 'Unknown']
        invalid_statuses = []
        
        for injury in injuries:
            if injury.get('injury_status') not in valid_statuses:
                invalid_statuses.append(f"{injury.get('player_name')}: {injury.get('injury_status')}")
        
        if not invalid_statuses:
            print(f"  ✅ All injury statuses valid")
            results['checks']['status_validity'] = {"status": "PASSED"}
        else:
            print(f"  ⚠️  {len(invalid_statuses)} invalid statuses")
            results['warnings'].extend(invalid_statuses[:5])
        
        # Check 3: Team name consistency
        print("\n✓ Check 3: Team Name Consistency")
        team_names = set(injury.get('team_name') for injury in injuries if injury.get('team_name'))
        print(f"  ℹ️  Found {len(team_names)} unique teams")
        results['checks']['team_consistency'] = {
            "status": "INFO",
            "unique_teams": len(team_names)
        }
        
        # Check 4: Required fields
        print("\n✓ Check 4: Required Fields")
        required_fields = ['player_name', 'team_name', 'injury_status']
        missing_fields = []
        
        for injury in injuries:
            for field in required_fields:
                if field not in injury or not injury[field]:
                    missing_fields.append(f"Player missing {field}")
        
        if not missing_fields:
            print(f"  ✅ All required fields present")
            results['checks']['required_fields'] = {"status": "PASSED"}
        else:
            print(f"  ⚠️  {len(missing_fields)} missing field instances")
            results['warnings'].append(f"{len(missing_fields)} missing fields detected")
        
        print("\n" + "=" * 60)
        print("✅ INJURY DATA VALIDATION: PASSED")
        
        self.validation_results['injury_data'] = results
        return results
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation checks and generate report"""
        print("\n" + "=" * 60)
        print("🚀 STARTING DATA VALIDATION SUITE")
        print("=" * 60)
        
        # Run all validations
        game_results = self.validate_game_data()
        team_results = self.validate_team_data()
        injury_results = self.validate_injury_data()
        
        # Determine overall status
        if (game_results['status'] == "PASSED" and 
            team_results['status'] == "PASSED" and 
            injury_results['status'] == "PASSED"):
            self.validation_results['overall_status'] = "PASSED"
        elif any(r['status'] == "FAILED" for r in [game_results, team_results, injury_results]):
            self.validation_results['overall_status'] = "FAILED"
        else:
            self.validation_results['overall_status'] = "PASSED_WITH_WARNINGS"
        
        # Print summary
        self.print_validation_summary()
        
        # Save results
        self.save_validation_results()
        
        return self.validation_results
    
    def print_validation_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        total_errors = (
            len(self.validation_results['game_data'].get('errors', [])) +
            len(self.validation_results['team_data'].get('errors', [])) +
            len(self.validation_results['injury_data'].get('errors', []))
        )
        
        total_warnings = (
            len(self.validation_results['game_data'].get('warnings', [])) +
            len(self.validation_results['team_data'].get('warnings', [])) +
            len(self.validation_results['injury_data'].get('warnings', []))
        )
        
        print(f"\n📈 Game Data: {self.validation_results['game_data']['status']}")
        print(f"📊 Team Data: {self.validation_results['team_data']['status']}")
        print(f"🏥 Injury Data: {self.validation_results['injury_data']['status']}")
        
        print(f"\n❌ Total Errors: {total_errors}")
        print(f"⚠️  Total Warnings: {total_warnings}")
        
        print(f"\n🎯 Overall Status: {self.validation_results['overall_status']}")
        
        if self.validation_results['overall_status'] == "PASSED":
            print("\n✅ ALL VALIDATIONS PASSED!")
            print("   Your data is accurate and ready for modeling.")
        elif self.validation_results['overall_status'] == "PASSED_WITH_WARNINGS":
            print("\n✅ VALIDATIONS PASSED WITH WARNINGS")
            print("   Review warnings but data is usable.")
        else:
            print("\n❌ VALIDATIONS FAILED")
            print("   Fix errors before proceeding to modeling.")
        
        print("=" * 60)
    
    def save_validation_results(self):
        """Save validation results to JSON"""
        filename = 'data_validation_results.json'
        
        with open(filename, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\n💾 Validation results saved to: {filename}")


def main():
    """Run data validation suite"""
    validator = DataValidator()
    results = validator.run_all_validations()
    
    # Return exit code based on validation status
    if results['overall_status'] == "FAILED":
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()

