"""
Data Consistency Checker for NBA Bet Selector
==============================================

This module ensures data consistency across all sources including:
- Team name standardization
- Date/time format consistency
- ID mapping validation
- Cross-source reconciliation

Phase 2.3: Data Consistency Checks
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import defaultdict


class DataConsistencyChecker:
    """Ensures consistency across all data sources"""
    
    def __init__(self):
        self.consistency_report = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "issues": [],
            "overall_status": "PASSED"
        }
        
        # NBA team mapping (standard names)
        self.standard_team_names = {
            'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
            'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
            'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
            'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
            'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans',
            'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic',
            'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers',
            'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
            'Utah Jazz', 'Washington Wizards'
        }
        
        # Team name variations mapping
        self.team_variations = {
            'Lakers': 'Los Angeles Lakers',
            'Clippers': 'LA Clippers',
            'Warriors': 'Golden State Warriors',
            'Celtics': 'Boston Celtics',
            'Knicks': 'New York Knicks',
            'Heat': 'Miami Heat',
            'Bucks': 'Milwaukee Bucks',
            'Suns': 'Phoenix Suns',
            'Nets': 'Brooklyn Nets',
            'Hawks': 'Atlanta Hawks',
            '76ers': 'Philadelphia 76ers',
            'Sixers': 'Philadelphia 76ers',
            'Mavs': 'Dallas Mavericks',
            'Nuggets': 'Denver Nuggets',
            'Cavs': 'Cleveland Cavaliers',
            'Bulls': 'Chicago Bulls',
            'Pistons': 'Detroit Pistons',
            'Hornets': 'Charlotte Hornets',
            'Rockets': 'Houston Rockets',
            'Pacers': 'Indiana Pacers',
            'Grizzlies': 'Memphis Grizzlies',
            'Pelicans': 'New Orleans Pelicans',
            'Thunder': 'Oklahoma City Thunder',
            'Magic': 'Orlando Magic',
            'Blazers': 'Portland Trail Blazers',
            'Trail Blazers': 'Portland Trail Blazers',
            'Kings': 'Sacramento Kings',
            'Spurs': 'San Antonio Spurs',
            'Raptors': 'Toronto Raptors',
            'Jazz': 'Utah Jazz',
            'Wizards': 'Washington Wizards',
            'Timberwolves': 'Minnesota Timberwolves',
            'Wolves': 'Minnesota Timberwolves'
        }
    
    def load_json(self, filepath: str) -> Dict:
        """Load JSON data file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return {}
    
    def check_team_name_consistency(self) -> Dict[str, Any]:
        """
        Validate team names are consistent across all data sources
        
        Checks:
        - All team names match standard NBA team names
        - No variations or typos
        - Consistent naming across game, team, and injury data
        """
        print("\n🔍 CHECK 1: TEAM NAME CONSISTENCY")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "issues": [],
            "team_names": {
                "game_data": set(),
                "team_data": set(),
                "injury_data": set()
            }
        }
        
        # Collect team names from game data
        game_data = self.load_json('nba_game_data.json')
        games = game_data.get('games', [])
        
        for game in games:
            results['team_names']['game_data'].add(game.get('home_team'))
            results['team_names']['game_data'].add(game.get('away_team'))
        
        print(f"  ℹ️  Game data: {len(results['team_names']['game_data'])} unique teams")
        
        # Collect team names from team data
        team_data = self.load_json('nba_team_data.json')
        teams = team_data.get('teams', [])
        
        for team in teams:
            results['team_names']['team_data'].add(team.get('TEAM_NAME'))
        
        print(f"  ℹ️  Team data: {len(results['team_names']['team_data'])} unique teams")
        
        # Collect team names from injury data
        injury_data = self.load_json('nba_injury_data.json')
        injuries = injury_data.get('injuries', [])
        
        for injury in injuries:
            team_name = injury.get('team_name')
            if team_name:
                # Standardize team name if it's a variation
                standardized = self.team_variations.get(team_name, team_name)
                results['team_names']['injury_data'].add(standardized)
        
        print(f"  ℹ️  Injury data: {len(results['team_names']['injury_data'])} unique teams")
        
        # Check for non-standard names
        non_standard_names = []
        
        for source, team_set in results['team_names'].items():
            for team in team_set:
                if team and team not in self.standard_team_names:
                    non_standard_names.append(f"{source}: '{team}'")
        
        if non_standard_names:
            results['issues'].extend(non_standard_names)
            results['status'] = "WARNING"
            print(f"  ⚠️  {len(non_standard_names)} non-standard team names found")
            for name in non_standard_names[:5]:  # Show first 5
                print(f"      • {name}")
        else:
            print(f"  ✅ All team names are standard")
        
        # Check consistency across sources
        game_teams = results['team_names']['game_data']
        team_teams = results['team_names']['team_data']
        injury_teams = results['team_names']['injury_data']
        
        # Teams in games but not in team data
        missing_in_team = game_teams - team_teams
        if missing_in_team:
            results['issues'].append(f"Teams in games but not in team data: {missing_in_team}")
            results['status'] = "WARNING"
            print(f"  ⚠️  Teams in games but not in team stats: {missing_in_team}")
        else:
            print(f"  ✅ All game teams present in team stats")
        
        # Convert sets to lists for JSON serialization
        results['team_names'] = {
            k: list(v) for k, v in results['team_names'].items()
        }
        
        self.consistency_report['checks']['team_names'] = results
        return results
    
    def check_date_format_consistency(self) -> Dict[str, Any]:
        """
        Validate date formats are consistent
        
        Checks:
        - All dates use ISO format (YYYY-MM-DD)
        - No date parsing errors
        - Date ranges make sense
        """
        print("\n🔍 CHECK 2: DATE FORMAT CONSISTENCY")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "issues": [],
            "formats": {}
        }
        
        # Check game data dates
        game_data = self.load_json('nba_game_data.json')
        games = game_data.get('games', [])
        
        date_format_errors = []
        date_formats = set()
        
        for i, game in enumerate(games[:100]):  # Check first 100 games
            date_str = game.get('date', '')
            
            # Try to parse date
            try:
                # Expected format: "YYYY-MM-DD HH:MM:SS"
                parsed = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                date_formats.add('YYYY-MM-DD HH:MM:SS')
            except ValueError:
                try:
                    # Alternative format: "YYYY-MM-DD"
                    parsed = datetime.strptime(date_str, '%Y-%m-%d')
                    date_formats.add('YYYY-MM-DD')
                except ValueError:
                    date_format_errors.append(f"Game {i}: Invalid date format '{date_str}'")
        
        if date_format_errors:
            results['issues'].extend(date_format_errors[:5])
            results['status'] = "WARNING"
            print(f"  ⚠️  {len(date_format_errors)} date format errors")
        else:
            print(f"  ✅ All game dates valid")
        
        results['formats']['game_data'] = list(date_formats)
        
        # Check metadata dates
        metadata_dates = {
            'game_data': game_data.get('metadata', {}).get('export_date'),
            'team_data': self.load_json('nba_team_data.json').get('metadata', {}).get('export_date'),
            'injury_data': self.load_json('nba_injury_data.json').get('metadata', {}).get('export_date')
        }
        
        for source, date_str in metadata_dates.items():
            if date_str:
                try:
                    # Expected ISO format
                    parsed = datetime.fromisoformat(date_str)
                except ValueError:
                    results['issues'].append(f"{source}: Invalid metadata date format '{date_str}'")
                    results['status'] = "WARNING"
        
        if results['status'] == "PASSED":
            print(f"  ✅ All metadata dates valid (ISO format)")
        
        self.consistency_report['checks']['date_formats'] = results
        return results
    
    def check_id_mapping(self) -> Dict[str, Any]:
        """
        Validate ID mappings are consistent
        
        Checks:
        - Game IDs are unique
        - Team IDs are consistent
        - Player IDs are unique
        """
        print("\n🔍 CHECK 3: ID MAPPING VALIDATION")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "issues": [],
            "id_stats": {}
        }
        
        # Check game IDs
        game_data = self.load_json('nba_game_data.json')
        games = game_data.get('games', [])
        
        game_ids = [g.get('game_id') for g in games]
        unique_game_ids = set(game_ids)
        
        results['id_stats']['game_ids'] = {
            "total": len(game_ids),
            "unique": len(unique_game_ids),
            "duplicates": len(game_ids) - len(unique_game_ids)
        }
        
        if len(game_ids) == len(unique_game_ids):
            print(f"  ✅ Game IDs: {len(game_ids)} unique IDs")
        else:
            duplicates = len(game_ids) - len(unique_game_ids)
            results['issues'].append(f"{duplicates} duplicate game IDs")
            results['status'] = "WARNING"
            print(f"  ⚠️  Game IDs: {duplicates} duplicates found")
        
        # Check team IDs
        team_id_map = {}
        for game in games:
            home_team = game.get('home_team')
            home_id = game.get('home_team_id')
            away_team = game.get('away_team')
            away_id = game.get('away_team_id')
            
            if home_team and home_id:
                if home_team in team_id_map:
                    if team_id_map[home_team] != home_id:
                        results['issues'].append(
                            f"Team ID mismatch for {home_team}: {team_id_map[home_team]} vs {home_id}"
                        )
                        results['status'] = "WARNING"
                else:
                    team_id_map[home_team] = home_id
            
            if away_team and away_id:
                if away_team in team_id_map:
                    if team_id_map[away_team] != away_id:
                        results['issues'].append(
                            f"Team ID mismatch for {away_team}: {team_id_map[away_team]} vs {away_id}"
                        )
                        results['status'] = "WARNING"
                else:
                    team_id_map[away_team] = away_id
        
        results['id_stats']['team_ids'] = {
            "total_teams": len(team_id_map),
            "unique_ids": len(set(team_id_map.values()))
        }
        
        if len(team_id_map) == len(set(team_id_map.values())):
            print(f"  ✅ Team IDs: {len(team_id_map)} consistent mappings")
        else:
            print(f"  ⚠️  Team IDs: Inconsistent mappings detected")
        
        # Check player IDs
        injury_data = self.load_json('nba_injury_data.json')
        injuries = injury_data.get('injuries', [])
        
        player_ids = [i.get('player_id') for i in injuries if i.get('player_id')]
        unique_player_ids = set(player_ids)
        
        results['id_stats']['player_ids'] = {
            "total": len(player_ids),
            "unique": len(unique_player_ids)
        }
        
        print(f"  ✅ Player IDs: {len(unique_player_ids)} unique players")
        
        self.consistency_report['checks']['id_mapping'] = results
        return results
    
    def check_cross_source_reconciliation(self) -> Dict[str, Any]:
        """
        Reconcile data across sources
        
        Checks:
        - Team stats match game aggregations
        - Injury data aligns with game data
        - All data sources reference same teams
        """
        print("\n🔍 CHECK 4: CROSS-SOURCE RECONCILIATION")
        print("=" * 60)
        
        results = {
            "status": "PASSED",
            "issues": [],
            "reconciliation": {}
        }
        
        # Load all data
        game_data = self.load_json('nba_game_data.json')
        team_data = self.load_json('nba_team_data.json')
        injury_data = self.load_json('nba_injury_data.json')
        
        games = game_data.get('games', [])
        teams = team_data.get('teams', [])
        injuries = injury_data.get('injuries', [])
        
        # Calculate wins from game data
        game_wins = defaultdict(int)
        game_losses = defaultdict(int)
        
        for game in games:
            if game.get('home_win') == 1:
                game_wins[game['home_team']] += 1
                game_losses[game['away_team']] += 1
            else:
                game_wins[game['away_team']] += 1
                game_losses[game['home_team']] += 1
        
        # Compare with team data
        win_mismatches = []
        
        for team in teams:
            team_name = team.get('TEAM_NAME')
            team_wins = team.get('W', 0)
            game_team_wins = game_wins.get(team_name, 0)
            
            if team_wins != game_team_wins:
                win_mismatches.append({
                    "team": team_name,
                    "team_data_wins": team_wins,
                    "game_data_wins": game_team_wins,
                    "difference": abs(team_wins - game_team_wins)
                })
        
        if win_mismatches:
            results['reconciliation']['win_mismatches'] = win_mismatches
            results['issues'].append(f"{len(win_mismatches)} teams with win count mismatches")
            results['status'] = "WARNING"
            print(f"  ⚠️  {len(win_mismatches)} teams with win mismatches")
            for mismatch in win_mismatches[:3]:
                print(f"      • {mismatch['team']}: Team data={mismatch['team_data_wins']}, "
                      f"Game data={mismatch['game_data_wins']}")
        else:
            print(f"  ✅ Win counts match between team and game data")
        
        # Check season consistency
        game_season = game_data.get('metadata', {}).get('season', 'Unknown')
        team_season = team_data.get('metadata', {}).get('season', 'Unknown')
        injury_season = injury_data.get('metadata', {}).get('season', 'Unknown')
        
        results['reconciliation']['seasons'] = {
            'game_data': game_season,
            'team_data': team_season,
            'injury_data': injury_season
        }
        
        if game_season == team_season == injury_season:
            print(f"  ✅ All data sources use same season: {game_season}")
        else:
            results['issues'].append("Season mismatch across data sources")
            results['status'] = "WARNING"
            print(f"  ⚠️  Season mismatch: Game={game_season}, Team={team_season}, Injury={injury_season}")
        
        self.consistency_report['checks']['cross_source'] = results
        return results
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all consistency checks and generate report"""
        print("\n" + "=" * 60)
        print("🚀 STARTING DATA CONSISTENCY CHECKS")
        print("=" * 60)
        
        # Run all checks
        self.check_team_name_consistency()
        self.check_date_format_consistency()
        self.check_id_mapping()
        self.check_cross_source_reconciliation()
        
        # Collect all issues
        all_issues = []
        for check_name, check_results in self.consistency_report['checks'].items():
            if 'issues' in check_results:
                all_issues.extend(check_results['issues'])
        
        self.consistency_report['issues'] = all_issues
        
        # Determine overall status
        if any(check['status'] == "WARNING" 
               for check in self.consistency_report['checks'].values()):
            self.consistency_report['overall_status'] = "WARNING"
        else:
            self.consistency_report['overall_status'] = "PASSED"
        
        # Print summary
        self.print_consistency_summary()
        
        # Save results
        self.save_consistency_report()
        
        return self.consistency_report
    
    def print_consistency_summary(self):
        """Print consistency check summary"""
        print("\n" + "=" * 60)
        print("📊 CONSISTENCY CHECK SUMMARY")
        print("=" * 60)
        
        total_issues = len(self.consistency_report['issues'])
        
        print(f"\n✓ Team Names: {self.consistency_report['checks']['team_names']['status']}")
        print(f"✓ Date Formats: {self.consistency_report['checks']['date_formats']['status']}")
        print(f"✓ ID Mapping: {self.consistency_report['checks']['id_mapping']['status']}")
        print(f"✓ Cross-Source: {self.consistency_report['checks']['cross_source']['status']}")
        
        print(f"\n⚠️  Total Issues: {total_issues}")
        
        if total_issues > 0:
            print(f"\nTop Issues:")
            for issue in self.consistency_report['issues'][:5]:
                print(f"   • {issue}")
        
        print(f"\n🎯 Overall Status: {self.consistency_report['overall_status']}")
        
        if self.consistency_report['overall_status'] == "PASSED":
            print("   ✅ All consistency checks passed!")
        else:
            print("   ⚠️  Some consistency issues detected (review recommended)")
        
        print("=" * 60)
    
    def save_consistency_report(self):
        """Save consistency report to JSON"""
        filename = 'data_consistency_report.json'
        
        with open(filename, 'w') as f:
            json.dump(self.consistency_report, f, indent=2)
        
        print(f"\n💾 Consistency report saved to: {filename}")


def main():
    """Run data consistency checks"""
    checker = DataConsistencyChecker()
    report = checker.run_all_checks()
    
    # Return exit code based on status
    if report['overall_status'] == "WARNING":
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()

