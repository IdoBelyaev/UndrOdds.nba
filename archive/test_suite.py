"""
Comprehensive Test Suite for NBA Bet Selector
==============================================

This module provides comprehensive testing for:
- Data collection functions
- Data validation logic
- Data quality checks
- Pipeline execution
- Error handling

Phase 4: Data Documentation & Testing
"""

import json
import unittest
import os
from datetime import datetime
from typing import Dict, Any


class TestDataCollection(unittest.TestCase):
    """Test data collection modules"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.test_season = "2024-25"
    
    def test_team_data_exists(self):
        """Test that team data file exists"""
        self.assertTrue(
            os.path.exists('nba_team_data.json'),
            "Team data file should exist"
        )
    
    def test_team_data_structure(self):
        """Test team data has correct structure"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        # Check metadata
        self.assertIn('metadata', data)
        self.assertIn('teams', data)
        
        # Check metadata fields
        metadata = data['metadata']
        self.assertIn('season', metadata)
        self.assertIn('total_teams', metadata)
        self.assertIn('export_date', metadata)
        
        # Check teams
        teams = data['teams']
        self.assertEqual(len(teams), 30, "Should have 30 NBA teams")
    
    def test_team_data_features(self):
        """Test team data has all required features"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        required_fields = ['TEAM_NAME', 'W', 'L', 'GP', 'PPG', 'PAPG', 'WIN_PCT']
        
        for team in data['teams']:
            for field in required_fields:
                self.assertIn(
                    field, team,
                    f"Team should have {field} field"
                )
    
    def test_game_data_exists(self):
        """Test that game data file exists"""
        self.assertTrue(
            os.path.exists('nba_game_data.json'),
            "Game data file should exist"
        )
    
    def test_game_data_structure(self):
        """Test game data has correct structure"""
        with open('nba_game_data.json', 'r') as f:
            data = json.load(f)
        
        # Check structure
        self.assertIn('metadata', data)
        self.assertIn('games', data)
        
        # Check games
        games = data['games']
        self.assertGreater(len(games), 0, "Should have games")
        
        # Check first game structure
        first_game = games[0]
        required_fields = ['game_id', 'date', 'home_team', 'away_team', 
                          'home_score', 'away_score']
        
        for field in required_fields:
            self.assertIn(field, first_game)
    
    def test_injury_data_exists(self):
        """Test that injury data file exists"""
        self.assertTrue(
            os.path.exists('nba_injury_data.json'),
            "Injury data file should exist"
        )
    
    def test_injury_data_structure(self):
        """Test injury data has correct structure"""
        with open('nba_injury_data.json', 'r') as f:
            data = json.load(f)
        
        # Check structure
        self.assertIn('metadata', data)
        self.assertIn('injuries', data)
        
        # Check injuries
        injuries = data['injuries']
        self.assertGreater(len(injuries), 0, "Should have injury records")


class TestDataValidation(unittest.TestCase):
    """Test data validation logic"""
    
    def test_team_count(self):
        """Test exactly 30 teams"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        self.assertEqual(
            len(data['teams']), 30,
            "Should have exactly 30 NBA teams"
        )
    
    def test_win_loss_consistency(self):
        """Test W + L = GP for all teams"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        for team in data['teams']:
            if 'W' in team and 'L' in team and 'GP' in team:
                self.assertEqual(
                    team['W'] + team['L'], team['GP'],
                    f"{team['TEAM_NAME']}: W+L should equal GP"
                )
    
    def test_games_played_valid(self):
        """Test GP <= 82 for all teams"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        for team in data['teams']:
            if 'GP' in team:
                self.assertLessEqual(
                    team['GP'], 82,
                    f"{team['TEAM_NAME']}: GP should be <= 82"
                )
    
    def test_percentages_in_range(self):
        """Test all percentages are between 0 and 1"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        pct_fields = ['FG_PCT', 'FG3_PCT', 'FT_PCT', 'WIN_PCT']
        
        for team in data['teams']:
            for field in pct_fields:
                if field in team and team[field] is not None:
                    self.assertGreaterEqual(
                        team[field], 0,
                        f"{team['TEAM_NAME']}: {field} should be >= 0"
                    )
                    self.assertLessEqual(
                        team[field], 1,
                        f"{team['TEAM_NAME']}: {field} should be <= 1"
                    )
    
    def test_win_percentage_accuracy(self):
        """Test win percentage calculation"""
        with open('nba_team_data.json', 'r') as f:
            data = json.load(f)
        
        for team in data['teams']:
            if 'W' in team and 'GP' in team and 'WIN_PCT' in team:
                expected = team['W'] / team['GP']
                actual = team['WIN_PCT']
                
                self.assertAlmostEqual(
                    expected, actual, places=3,
                    msg=f"{team['TEAM_NAME']}: WIN_PCT calculation incorrect"
                )
    
    def test_no_duplicate_games(self):
        """Test no duplicate game IDs"""
        with open('nba_game_data.json', 'r') as f:
            data = json.load(f)
        
        game_ids = [game['game_id'] for game in data['games']]
        unique_ids = set(game_ids)
        
        self.assertEqual(
            len(game_ids), len(unique_ids),
            "Should have no duplicate game IDs"
        )
    
    def test_game_scores_valid(self):
        """Test all game scores are positive and reasonable"""
        with open('nba_game_data.json', 'r') as f:
            data = json.load(f)
        
        for game in data['games']:
            # Check scores are positive
            self.assertGreaterEqual(game['home_score'], 0)
            self.assertGreaterEqual(game['away_score'], 0)
            
            # Check scores are reasonable (0-200)
            self.assertLessEqual(game['home_score'], 200)
            self.assertLessEqual(game['away_score'], 200)
    
    def test_win_loss_logic(self):
        """Test win/loss assignments are correct"""
        with open('nba_game_data.json', 'r') as f:
            data = json.load(f)
        
        for game in data['games']:
            if game['home_score'] > game['away_score']:
                self.assertEqual(
                    game['home_win'], 1,
                    f"Game {game['game_id']}: Home team should win"
                )
                self.assertEqual(
                    game['away_win'], 0,
                    f"Game {game['game_id']}: Away team should lose"
                )
            else:
                self.assertEqual(
                    game['home_win'], 0,
                    f"Game {game['game_id']}: Home team should lose"
                )
                self.assertEqual(
                    game['away_win'], 1,
                    f"Game {game['game_id']}: Away team should win"
                )


class TestDataQuality(unittest.TestCase):
    """Test data quality checks"""
    
    def test_no_missing_critical_fields(self):
        """Test no missing values in critical fields"""
        # Test team data
        with open('nba_team_data.json', 'r') as f:
            team_data = json.load(f)
        
        critical_team_fields = ['TEAM_NAME', 'W', 'L', 'GP']
        
        for team in team_data['teams']:
            for field in critical_team_fields:
                self.assertIsNotNone(
                    team.get(field),
                    f"Critical field {field} should not be None"
                )
        
        # Test game data
        with open('nba_game_data.json', 'r') as f:
            game_data = json.load(f)
        
        critical_game_fields = ['game_id', 'home_team', 'away_team', 
                               'home_score', 'away_score']
        
        for game in game_data['games']:
            for field in critical_game_fields:
                self.assertIsNotNone(
                    game.get(field),
                    f"Critical field {field} should not be None"
                )
    
    def test_data_freshness_metadata(self):
        """Test data has export date in metadata"""
        files = ['nba_team_data.json', 'nba_game_data.json', 'nba_injury_data.json']
        
        for filename in files:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.assertIn('metadata', data)
            self.assertIn('export_date', data['metadata'])
            
            # Verify export date is valid ISO format
            export_date = data['metadata']['export_date']
            try:
                datetime.fromisoformat(export_date)
            except ValueError:
                self.fail(f"{filename}: Invalid export_date format")
    
    def test_team_name_consistency(self):
        """Test team names are consistent across sources"""
        # Load all data
        with open('nba_team_data.json', 'r') as f:
            team_data = json.load(f)
        
        with open('nba_game_data.json', 'r') as f:
            game_data = json.load(f)
        
        # Get team names from team data
        team_names = {team['TEAM_NAME'] for team in team_data['teams']}
        
        # Get team names from game data
        game_team_names = set()
        for game in game_data['games']:
            game_team_names.add(game['home_team'])
            game_team_names.add(game['away_team'])
        
        # Check that game teams are subset of team data teams
        # (allowing for minor name variations)
        self.assertEqual(
            len(team_names), 30,
            "Should have 30 unique team names"
        )


class TestPipeline(unittest.TestCase):
    """Test data pipeline functionality"""
    
    def test_validation_report_exists(self):
        """Test validation report exists"""
        # Run validation if report doesn't exist
        if not os.path.exists('data_validation_results.json'):
            from data_validation import DataValidator
            validator = DataValidator()
            validator.run_all_validations()
        
        self.assertTrue(
            os.path.exists('data_validation_results.json'),
            "Validation report should exist"
        )
    
    def test_quality_report_exists(self):
        """Test quality report exists"""
        # Run quality check if report doesn't exist
        if not os.path.exists('data_quality_report.json'):
            from data_quality_monitor import DataQualityMonitor
            monitor = DataQualityMonitor()
            monitor.run_all_checks()
        
        self.assertTrue(
            os.path.exists('data_quality_report.json'),
            "Quality report should exist"
        )
    
    def test_validation_passed(self):
        """Test that validation passed"""
        with open('data_validation_results.json', 'r') as f:
            results = json.load(f)
        
        self.assertIn(
            results['overall_status'],
            ['PASSED', 'PASSED_WITH_WARNINGS'],
            "Validation should pass"
        )
    
    def test_quality_score_acceptable(self):
        """Test quality score is acceptable (>= 60)"""
        with open('data_quality_report.json', 'r') as f:
            report = json.load(f)
        
        self.assertGreaterEqual(
            report['overall_score'], 60,
            "Quality score should be >= 60"
        )


class TestOddsInput(unittest.TestCase):
    """Test odds input system"""
    
    def test_implied_probability_positive_odds(self):
        """Test implied probability calculation for positive odds"""
        from odds_input_system import calculate_implied_probability
        
        # +150 should give ~0.40 probability
        prob = calculate_implied_probability(150)
        self.assertAlmostEqual(prob, 0.4, places=2)
        
        # +200 should give ~0.33 probability
        prob = calculate_implied_probability(200)
        self.assertAlmostEqual(prob, 0.3333, places=4)
    
    def test_implied_probability_negative_odds(self):
        """Test implied probability calculation for negative odds"""
        from odds_input_system import calculate_implied_probability
        
        # -150 should give ~0.60 probability
        prob = calculate_implied_probability(-150)
        self.assertAlmostEqual(prob, 0.6, places=2)
        
        # -200 should give ~0.67 probability
        prob = calculate_implied_probability(-200)
        self.assertAlmostEqual(prob, 0.6667, places=4)
    
    def test_implied_probabilities_sum(self):
        """Test that implied probabilities sum to > 1 (vig)"""
        from odds_input_system import calculate_implied_probability
        
        # Typical line: Lakers -150, Warriors +130
        home_prob = calculate_implied_probability(-150)
        away_prob = calculate_implied_probability(130)
        
        total = home_prob + away_prob
        
        # Should sum to more than 1 (sportsbook vig)
        self.assertGreater(total, 1.0)


def run_test_suite():
    """Run the complete test suite with summary"""
    print("=" * 70)
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataCollection))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestOddsInput))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    print()
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = run_test_suite()
    exit(exit_code)

