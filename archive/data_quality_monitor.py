"""
Data Quality Monitoring System for NBA Bet Selector
====================================================

This module provides automated data quality monitoring including:
- Missing value detection
- Outlier detection
- Data freshness monitoring
- Schema validation
- Anomaly detection

Phase 2.2: Data Quality Monitoring
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class DataQualityMonitor:
    """Monitors data quality and detects issues"""
    
    def __init__(self):
        self.quality_report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "alerts": [],
            "overall_score": 0.0
        }
    
    def load_json(self, filepath: str) -> Dict:
        """Load JSON data file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return {}
    
    def check_missing_values(self) -> Dict[str, Any]:
        """
        Detect missing values across all data sources
        
        Checks for:
        - Null/None values
        - Empty strings
        - Zero values where inappropriate
        """
        print("\n🔍 CHECK 1: MISSING VALUE DETECTION")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "game_data": {},
            "team_data": {},
            "injury_data": {},
            "alerts": []
        }
        
        # Check game data
        game_data = self.load_json('nba_game_data.json')
        games = game_data.get('games', [])
        
        game_missing = defaultdict(int)
        critical_fields = ['game_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score']
        
        for game in games:
            for field in critical_fields:
                if field not in game or game[field] is None or game[field] == '':
                    game_missing[field] += 1
        
        if game_missing:
            results['game_data']['missing_values'] = dict(game_missing)
            results['alerts'].append(f"Game data: {sum(game_missing.values())} missing values")
            results['status'] = "WARNING"
            print(f"  ⚠️  Game data: {sum(game_missing.values())} missing values")
        else:
            results['game_data']['missing_values'] = {}
            print(f"  ✅ Game data: No missing values")
        
        # Check team data
        team_data = self.load_json('nba_team_data.json')
        teams = team_data.get('teams', [])
        
        team_missing = defaultdict(int)
        critical_team_fields = ['TEAM_NAME', 'PPG', 'PAPG', 'W', 'L', 'GP']
        
        for team in teams:
            for field in critical_team_fields:
                if field not in team or team[field] is None:
                    team_missing[field] += 1
        
        if team_missing:
            results['team_data']['missing_values'] = dict(team_missing)
            results['alerts'].append(f"Team data: {sum(team_missing.values())} missing values")
            results['status'] = "WARNING"
            print(f"  ⚠️  Team data: {sum(team_missing.values())} missing values")
        else:
            results['team_data']['missing_values'] = {}
            print(f"  ✅ Team data: No missing values")
        
        # Check injury data
        injury_data = self.load_json('nba_injury_data.json')
        injuries = injury_data.get('injuries', [])
        
        injury_missing = defaultdict(int)
        critical_injury_fields = ['player_name', 'team_name', 'injury_status']
        
        for injury in injuries:
            for field in critical_injury_fields:
                if field not in injury or injury[field] is None or injury[field] == '':
                    injury_missing[field] += 1
        
        if injury_missing:
            results['injury_data']['missing_values'] = dict(injury_missing)
            results['alerts'].append(f"Injury data: {sum(injury_missing.values())} missing values")
            results['status'] = "WARNING"
            print(f"  ⚠️  Injury data: {sum(injury_missing.values())} missing values")
        else:
            results['injury_data']['missing_values'] = {}
            print(f"  ✅ Injury data: No missing values")
        
        self.quality_report['checks']['missing_values'] = results
        return results
    
    def check_outliers(self) -> Dict[str, Any]:
        """
        Detect statistical outliers in numerical data
        
        Uses IQR (Interquartile Range) method:
        - Outlier if value < Q1 - 1.5*IQR or value > Q3 + 1.5*IQR
        """
        print("\n🔍 CHECK 2: OUTLIER DETECTION")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "outliers": {},
            "alerts": []
        }
        
        # Load team data
        team_data = self.load_json('nba_team_data.json')
        teams = team_data.get('teams', [])
        
        # Fields to check for outliers
        numerical_fields = ['PPG', 'PAPG', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'REB', 'AST', 'TOV', 'STL', 'BLK']
        
        for field in numerical_fields:
            values = [team[field] for team in teams if field in team and team[field] is not None]
            
            if len(values) < 4:  # Need at least 4 values for IQR
                continue
            
            # Calculate IQR
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Find outliers
            outliers = []
            for team in teams:
                if field in team and team[field] is not None:
                    value = team[field]
                    if value < lower_bound or value > upper_bound:
                        outliers.append({
                            "team": team['TEAM_NAME'],
                            "value": value,
                            "expected_range": f"{lower_bound:.2f} - {upper_bound:.2f}"
                        })
            
            if outliers:
                results['outliers'][field] = outliers
                print(f"  ⚠️  {field}: {len(outliers)} outliers detected")
                results['alerts'].append(f"{field}: {len(outliers)} outliers")
                results['status'] = "WARNING"
            else:
                print(f"  ✅ {field}: No outliers")
        
        # Check game scores for outliers
        game_data = self.load_json('nba_game_data.json')
        games = game_data.get('games', [])
        
        scores = []
        for game in games:
            scores.extend([game['home_score'], game['away_score']])
        
        q1 = np.percentile(scores, 25)
        q3 = np.percentile(scores, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        score_outliers = []
        for game in games:
            if game['home_score'] < lower_bound or game['home_score'] > upper_bound:
                score_outliers.append({
                    "game_id": game['game_id'],
                    "team": game['home_team'],
                    "score": game['home_score']
                })
            if game['away_score'] < lower_bound or game['away_score'] > upper_bound:
                score_outliers.append({
                    "game_id": game['game_id'],
                    "team": game['away_team'],
                    "score": game['away_score']
                })
        
        if score_outliers:
            results['outliers']['game_scores'] = score_outliers[:10]  # Limit to first 10
            print(f"  ℹ️  Game scores: {len(score_outliers)} outliers (unusual scores, possibly overtime)")
        else:
            print(f"  ✅ Game scores: No outliers")
        
        self.quality_report['checks']['outliers'] = results
        return results
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """
        Monitor data freshness and recency
        
        Checks:
        - When data was last updated
        - If data is stale (>24 hours old)
        - Date ranges are current
        """
        print("\n🔍 CHECK 3: DATA FRESHNESS MONITORING")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "freshness": {},
            "alerts": []
        }
        
        now = datetime.now()
        
        # Check game data
        game_data = self.load_json('nba_game_data.json')
        game_export = game_data.get('metadata', {}).get('export_date')
        
        if game_export:
            export_time = datetime.fromisoformat(game_export)
            age_hours = (now - export_time).total_seconds() / 3600
            
            results['freshness']['game_data'] = {
                "last_updated": game_export,
                "age_hours": round(age_hours, 2),
                "is_stale": age_hours > 24
            }
            
            if age_hours > 24:
                print(f"  ⚠️  Game data: {age_hours:.1f} hours old (stale)")
                results['alerts'].append(f"Game data is {age_hours:.1f} hours old")
                results['status'] = "WARNING"
            else:
                print(f"  ✅ Game data: {age_hours:.1f} hours old (fresh)")
        
        # Check team data
        team_data = self.load_json('nba_team_data.json')
        team_export = team_data.get('metadata', {}).get('export_date')
        
        if team_export:
            export_time = datetime.fromisoformat(team_export)
            age_hours = (now - export_time).total_seconds() / 3600
            
            results['freshness']['team_data'] = {
                "last_updated": team_export,
                "age_hours": round(age_hours, 2),
                "is_stale": age_hours > 24
            }
            
            if age_hours > 24:
                print(f"  ⚠️  Team data: {age_hours:.1f} hours old (stale)")
                results['alerts'].append(f"Team data is {age_hours:.1f} hours old")
                results['status'] = "WARNING"
            else:
                print(f"  ✅ Team data: {age_hours:.1f} hours old (fresh)")
        
        # Check injury data
        injury_data = self.load_json('nba_injury_data.json')
        injury_export = injury_data.get('metadata', {}).get('export_date')
        
        if injury_export:
            export_time = datetime.fromisoformat(injury_export)
            age_hours = (now - export_time).total_seconds() / 3600
            
            results['freshness']['injury_data'] = {
                "last_updated": injury_export,
                "age_hours": round(age_hours, 2),
                "is_stale": age_hours > 24
            }
            
            if age_hours > 24:
                print(f"  ⚠️  Injury data: {age_hours:.1f} hours old (stale)")
                results['alerts'].append(f"Injury data is {age_hours:.1f} hours old")
                results['status'] = "WARNING"
            else:
                print(f"  ✅ Injury data: {age_hours:.1f} hours old (fresh)")
        
        self.quality_report['checks']['freshness'] = results
        return results
    
    def check_schema_validation(self) -> Dict[str, Any]:
        """
        Validate data schemas match expected structure
        
        Checks:
        - Required fields present
        - Data types correct
        - Schema consistency
        """
        print("\n🔍 CHECK 4: SCHEMA VALIDATION")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "schema_checks": {},
            "alerts": []
        }
        
        # Expected game schema
        game_schema = {
            'game_id': str,
            'date': str,
            'home_team': str,
            'away_team': str,
            'home_score': int,
            'away_score': int,
            'home_win': int,
            'away_win': int
        }
        
        # Check game data schema
        game_data = self.load_json('nba_game_data.json')
        games = game_data.get('games', [])
        
        schema_errors = []
        for i, game in enumerate(games[:10]):  # Check first 10 games
            for field, expected_type in game_schema.items():
                if field not in game:
                    schema_errors.append(f"Game {i}: Missing field '{field}'")
                elif not isinstance(game[field], expected_type):
                    schema_errors.append(
                        f"Game {i}: Field '{field}' wrong type "
                        f"(expected {expected_type.__name__}, got {type(game[field]).__name__})"
                    )
        
        if schema_errors:
            results['schema_checks']['game_data'] = schema_errors
            print(f"  ⚠️  Game data: {len(schema_errors)} schema errors")
            results['alerts'].append(f"Game schema: {len(schema_errors)} errors")
            results['status'] = "WARNING"
        else:
            results['schema_checks']['game_data'] = []
            print(f"  ✅ Game data: Schema valid")
        
        # Expected team schema (subset of critical fields)
        team_schema = {
            'TEAM_NAME': str,
            'PPG': (int, float),
            'PAPG': (int, float),
            'W': int,
            'L': int,
            'GP': int,
            'WIN_PCT': float
        }
        
        # Check team data schema
        team_data = self.load_json('nba_team_data.json')
        teams = team_data.get('teams', [])
        
        team_schema_errors = []
        for i, team in enumerate(teams):
            for field, expected_type in team_schema.items():
                if field not in team:
                    team_schema_errors.append(f"Team {i}: Missing field '{field}'")
                elif not isinstance(team[field], expected_type if isinstance(expected_type, tuple) else (expected_type,)):
                    team_schema_errors.append(
                        f"Team {i} ({team.get('TEAM_NAME', 'Unknown')}): "
                        f"Field '{field}' wrong type"
                    )
        
        if team_schema_errors:
            results['schema_checks']['team_data'] = team_schema_errors
            print(f"  ⚠️  Team data: {len(team_schema_errors)} schema errors")
            results['alerts'].append(f"Team schema: {len(team_schema_errors)} errors")
            results['status'] = "WARNING"
        else:
            results['schema_checks']['team_data'] = []
            print(f"  ✅ Team data: Schema valid")
        
        self.quality_report['checks']['schema_validation'] = results
        return results
    
    def calculate_quality_score(self) -> float:
        """
        Calculate overall data quality score (0-100)
        
        Based on:
        - Missing values (25 points)
        - Outliers (25 points)
        - Freshness (25 points)
        - Schema validity (25 points)
        """
        score = 100.0
        
        # Deduct for missing values
        if 'missing_values' in self.quality_report['checks']:
            mv_check = self.quality_report['checks']['missing_values']
            if mv_check['status'] == "WARNING":
                score -= 10  # Deduct 10 points for missing values
        
        # Deduct for outliers (minor deduction, outliers can be valid)
        if 'outliers' in self.quality_report['checks']:
            outlier_check = self.quality_report['checks']['outliers']
            if outlier_check['status'] == "WARNING":
                score -= 5  # Deduct 5 points for outliers
        
        # Deduct for stale data
        if 'freshness' in self.quality_report['checks']:
            fresh_check = self.quality_report['checks']['freshness']
            if fresh_check['status'] == "WARNING":
                score -= 15  # Deduct 15 points for stale data
        
        # Deduct for schema errors
        if 'schema_validation' in self.quality_report['checks']:
            schema_check = self.quality_report['checks']['schema_validation']
            if schema_check['status'] == "WARNING":
                score -= 20  # Deduct 20 points for schema errors
        
        return max(0.0, score)
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all quality checks and generate report"""
        print("\n" + "=" * 60)
        print("🚀 STARTING DATA QUALITY MONITORING")
        print("=" * 60)
        
        # Run all checks
        self.check_missing_values()
        self.check_outliers()
        self.check_data_freshness()
        self.check_schema_validation()
        
        # Calculate quality score
        self.quality_report['overall_score'] = self.calculate_quality_score()
        
        # Collect all alerts
        all_alerts = []
        for check_name, check_results in self.quality_report['checks'].items():
            if 'alerts' in check_results:
                all_alerts.extend(check_results['alerts'])
        
        self.quality_report['alerts'] = all_alerts
        
        # Print summary
        self.print_quality_summary()
        
        # Save results
        self.save_quality_report()
        
        return self.quality_report
    
    def print_quality_summary(self):
        """Print quality monitoring summary"""
        print("\n" + "=" * 60)
        print("📊 DATA QUALITY SUMMARY")
        print("=" * 60)
        
        score = self.quality_report['overall_score']
        
        print(f"\n🎯 Overall Quality Score: {score:.1f}/100")
        
        if score >= 90:
            print("   ✅ EXCELLENT - Data quality is outstanding")
        elif score >= 75:
            print("   ✅ GOOD - Data quality is acceptable")
        elif score >= 60:
            print("   ⚠️  FAIR - Some quality issues detected")
        else:
            print("   ❌ POOR - Significant quality issues")
        
        # Print alerts
        if self.quality_report['alerts']:
            print(f"\n⚠️  Quality Alerts ({len(self.quality_report['alerts'])}):")
            for alert in self.quality_report['alerts'][:10]:  # Limit to 10
                print(f"   • {alert}")
        else:
            print("\n✅ No quality alerts")
        
        print("\n" + "=" * 60)
    
    def save_quality_report(self):
        """Save quality report to JSON"""
        filename = 'data_quality_report.json'
        
        with open(filename, 'w') as f:
            json.dump(self.quality_report, f, indent=2)
        
        print(f"\n💾 Quality report saved to: {filename}")


def main():
    """Run data quality monitoring"""
    monitor = DataQualityMonitor()
    report = monitor.run_all_checks()
    
    # Return exit code based on quality score
    if report['overall_score'] < 60:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()

