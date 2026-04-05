"""
NBA Game Data Fetcher
Handles fetching and processing NBA game data for betting analysis.
"""

import requests
import pandas as pd
import numpy as np
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from nba_api.stats.endpoints import leaguegamefinder, scoreboardv2


def fetch_nba_games(season: str, season_type: str = 'Regular Season') -> pd.DataFrame:
    """
    Fetch NBA game data using nba_api library
    
    Args:
        season: NBA season (e.g., '2024-25')
        season_type: Season type ('Regular Season', 'Playoffs', 'Pre Season')
    
    Returns:
        DataFrame with game data
    """
    print(f"🔄 Fetching NBA game data for {season} {season_type}...")
    
    try:
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Fetch game data
        games = leaguegamefinder.LeagueGameFinder(
            season_nullable=season,
            season_type_nullable=season_type
        )
        
        df = games.get_data_frames()[0]
        print(f"📈 Found {len(df)} games")
        
        # Process and clean the data
        processed_df = process_game_data(df)
        
        print(f"✅ Successfully processed {len(processed_df)} games")
        return processed_df
        
    except Exception as e:
        print(f"❌ Error fetching game data: {e}")
        return pd.DataFrame()


def process_game_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw game data into our standardized format
    
    Args:
        df: Raw game data from NBA API
    
    Returns:
        Processed DataFrame with standardized columns
    """
    print("🔧 Processing game data...")
    
    # Filter to only NBA teams (30 teams)
    nba_teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets',
        'Chicago Bulls', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
        'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
        'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans', 'New York Knicks',
        'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
        'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors',
        'Utah Jazz', 'Washington Wizards'
    ]
    
    # Filter to only NBA teams
    df = df[df['TEAM_NAME'].isin(nba_teams)]
    print(f"📊 Filtered to {len(df)} NBA team games")
    
    # Create a list to store processed games
    processed_games = []
    
    # Group by game_id to process each game
    for game_id, game_data in df.groupby('GAME_ID'):
        if len(game_data) != 2:
            print(f"⚠️ Warning: Game {game_id} has {len(game_data)} teams (expected 2)")
            continue
            
        # Sort by team name to ensure consistent home/away assignment
        game_data = game_data.sort_values('TEAM_NAME').reset_index(drop=True)
        
        # Extract game information
        game_info = {
            'game_id': game_id,
            'date': game_data['GAME_DATE'].iloc[0],
            'season': game_data['SEASON_ID'].iloc[0],
            'season_type': 'Regular Season',  # We'll determine this from season_id if needed
        }
        
        # Determine home and away teams
        # NBA API doesn't clearly indicate home/away, so we'll use matchup format
        matchup_0 = game_data['MATCHUP'].iloc[0]
        matchup_1 = game_data['MATCHUP'].iloc[1]
        
        # Check which team has '@' in their matchup (away team)
        if '@' in matchup_0:
            away_team = game_data.iloc[0]
            home_team = game_data.iloc[1]
        else:
            away_team = game_data.iloc[1]
            home_team = game_data.iloc[0]
        
        # Add team information
        game_info.update({
            'home_team': home_team['TEAM_NAME'],
            'away_team': away_team['TEAM_NAME'],
            'home_team_id': home_team['TEAM_ID'],
            'away_team_id': away_team['TEAM_ID'],
            'home_team_abbr': home_team['TEAM_ABBREVIATION'],
            'away_team_abbr': away_team['TEAM_ABBREVIATION'],
        })
        
        # Add game results
        game_info.update({
            'home_score': home_team['PTS'],
            'away_score': away_team['PTS'],
            'home_win': 1 if home_team['WL'] == 'W' else 0,
            'away_win': 1 if away_team['WL'] == 'W' else 0,
        })
        
        # Add additional stats
        game_info.update({
            'home_fgm': home_team['FGM'],
            'home_fga': home_team['FGA'],
            'home_fg_pct': home_team['FG_PCT'],
            'home_fg3m': home_team['FG3M'],
            'home_fg3a': home_team['FG3A'],
            'home_fg3_pct': home_team['FG3_PCT'],
            'home_ftm': home_team['FTM'],
            'home_fta': home_team['FTA'],
            'home_ft_pct': home_team['FT_PCT'],
            'home_reb': home_team['REB'],
            'home_ast': home_team['AST'],
            'home_stl': home_team['STL'],
            'home_blk': home_team['BLK'],
            'home_tov': home_team['TOV'],
            'home_pf': home_team['PF'],
            'home_plus_minus': home_team['PLUS_MINUS'],
        })
        
        game_info.update({
            'away_fgm': away_team['FGM'],
            'away_fga': away_team['FGA'],
            'away_fg_pct': away_team['FG_PCT'],
            'away_fg3m': away_team['FG3M'],
            'away_fg3a': away_team['FG3A'],
            'away_fg3_pct': away_team['FG3_PCT'],
            'away_ftm': away_team['FTM'],
            'away_fta': away_team['FTA'],
            'away_ft_pct': away_team['FT_PCT'],
            'away_reb': away_team['REB'],
            'away_ast': away_team['AST'],
            'away_stl': away_team['STL'],
            'away_blk': away_team['BLK'],
            'away_tov': away_team['TOV'],
            'away_pf': away_team['PF'],
            'away_plus_minus': away_team['PLUS_MINUS'],
        })
        
        # Calculate derived metrics
        game_info.update({
            'total_points': home_team['PTS'] + away_team['PTS'],
            'point_differential': home_team['PTS'] - away_team['PTS'],
            'home_win_margin': home_team['PTS'] - away_team['PTS'] if home_team['WL'] == 'W' else 0,
            'away_win_margin': away_team['PTS'] - home_team['PTS'] if away_team['WL'] == 'W' else 0,
        })
        
        processed_games.append(game_info)
    
    # Convert to DataFrame
    processed_df = pd.DataFrame(processed_games)
    
    # Sort by date
    processed_df['date'] = pd.to_datetime(processed_df['date'])
    processed_df = processed_df.sort_values('date').reset_index(drop=True)
    
    print(f"📊 Processed {len(processed_df)} games")
    return processed_df


def validate_game_data(df: pd.DataFrame) -> Dict[str, any]:
    """
    Validate game data quality
    
    Args:
        df: Processed game data
    
    Returns:
        Dictionary with validation results
    """
    print("🔍 Validating game data...")
    
    validation_results = {
        'total_games': len(df),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d'),
            'end': df['date'].max().strftime('%Y-%m-%d')
        },
        'unique_teams': df['home_team'].nunique(),
        'missing_values': df.isnull().sum().to_dict(),
        'data_quality_issues': []
    }
    
    # Check for data quality issues
    if len(df) == 0:
        validation_results['data_quality_issues'].append('No games found')
    
    if df['home_team'].nunique() != 30:
        validation_results['data_quality_issues'].append(f'Expected 30 teams, found {df["home_team"].nunique()}')
    
    # Check for duplicate games
    duplicate_games = df['game_id'].duplicated().sum()
    if duplicate_games > 0:
        validation_results['data_quality_issues'].append(f'{duplicate_games} duplicate games found')
    
    # Check for impossible scores
    negative_scores = (df['home_score'] < 0) | (df['away_score'] < 0)
    if negative_scores.any():
        validation_results['data_quality_issues'].append(f'{negative_scores.sum()} games with negative scores')
    
    # Check win consistency
    win_inconsistency = (df['home_win'] + df['away_win']) != 1
    if win_inconsistency.any():
        validation_results['data_quality_issues'].append(f'{win_inconsistency.sum()} games with win inconsistency')
    
    print(f"✅ Validation complete: {len(validation_results['data_quality_issues'])} issues found")
    return validation_results


def save_game_data_to_json(df: pd.DataFrame, filename: str = 'nba_game_data.json') -> None:
    """
    Save game data to JSON file with metadata
    
    Args:
        df: Processed game data
        filename: Output filename
    """
    print(f"💾 Saving game data to {filename}...")
    
    # Create data structure
    data = {
        'metadata': {
            'data_source': 'NBA Stats API - LeagueGameFinder',
            'season': df['season'].iloc[0] if len(df) > 0 else 'Unknown',
            'export_date': datetime.now().isoformat(),
            'total_games': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if len(df) > 0 else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if len(df) > 0 else None
            },
            'data_quality': 'Real NBA game data with comprehensive statistics'
        },
        'games': df.to_dict('records')
    }
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Game data saved to {filename}")


def get_recent_games(days: int = 7) -> pd.DataFrame:
    """
    Get recent games from scoreboard
    
    Args:
        days: Number of days to look back
    
    Returns:
        DataFrame with recent games
    """
    print(f"🔄 Fetching recent games from last {days} days...")
    
    try:
        # Get recent scoreboard
        scoreboard = scoreboardv2.ScoreboardV2()
        df = scoreboard.get_data_frames()[0]
        
        if len(df) > 0:
            print(f"📈 Found {len(df)} recent games")
            return df
        else:
            print("📈 No recent games found")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error fetching recent games: {e}")
        return pd.DataFrame()


def main():
    """Main function to fetch and process NBA game data"""
    print("🏀 NBA GAME DATA FETCHER")
    print("=" * 50)
    
    # Fetch 2025-26 regular season games
    df = fetch_nba_games('2025-26', 'Regular Season')
    
    if len(df) > 0:
        # Validate data
        validation_results = validate_game_data(df)
        
        # Print validation results
        print("\n📊 VALIDATION RESULTS:")
        print(f"Total games: {validation_results['total_games']}")
        print(f"Date range: {validation_results['date_range']['start']} to {validation_results['date_range']['end']}")
        print(f"Unique teams: {validation_results['unique_teams']}")
        
        if validation_results['data_quality_issues']:
            print("\n⚠️ DATA QUALITY ISSUES:")
            for issue in validation_results['data_quality_issues']:
                print(f"  • {issue}")
        else:
            print("\n✅ No data quality issues found")
        
        # Save data
        save_game_data_to_json(df)
        
        # Show sample data
        print("\n🏀 SAMPLE GAME DATA:")
        sample_game = df.iloc[0]
        print(f"Game ID: {sample_game['game_id']}")
        print(f"Date: {sample_game['date']}")
        print(f"Matchup: {sample_game['away_team']} @ {sample_game['home_team']}")
        print(f"Score: {sample_game['away_score']} - {sample_game['home_score']}")
        print(f"Winner: {sample_game['away_team'] if sample_game['away_win'] else sample_game['home_team']}")
        
    else:
        print("❌ No game data retrieved")


if __name__ == "__main__":
    main()
