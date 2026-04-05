"""
Underdog Fantasy Lines Fetcher
Handles fetching and processing Underdog Fantasy team moneyline betting lines.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


def run_underdog_scraper() -> Optional[Path]:
    """Run the Underdog scraper and return path to output CSV"""
    
    print("🔄 Underdog Fantasy scraper not available")
    print("💡 To use real data, you would need to set up the vendor scraper")
    return None


def load_props_csv(csv_path: Path) -> pd.DataFrame:
    """Load and clean props data from CSV"""
    
    try:
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} prop lines from {csv_path}")
        
        # Clean and standardize column names
        df = clean_props_data(df)
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()


def clean_props_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize props data"""
    
    # Column mapping for common variations
    column_mapping = {
        # Player variations
        "player_name": "player",
        "name": "player",
        "athlete": "player",
        
        # Stat variations
        "stat_type": "stat",
        "stat_name": "stat",
        "metric": "stat",
        "prop": "stat",
        
        # Line variations
        "line_value": "line",
        "value": "line",
        "threshold": "line",
        "total": "line",
        
        # Team variations
        "team_name": "team",
        "home_team": "team",
        "away_team": "team",
        
        # Game time variations
        "game_date": "game_time",
        "start_time": "game_time",
        "scheduled_time": "game_time",
        
        # Direction variations
        "direction": "direction_optional",
        "over_under": "direction_optional",
        "side": "direction_optional",
    }
    
    # Apply column mapping
    df_clean = df.rename(columns=column_mapping)
    
    # Clean string columns
    string_cols = ["player", "stat", "team", "opponent", "league"]
    for col in string_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Clean numeric columns
    if "line" in df_clean.columns:
        df_clean["line"] = pd.to_numeric(df_clean["line"], errors="coerce")
    
    # Remove rows with missing critical data
    critical_cols = ["player", "stat", "line"]
    existing_critical = [col for col in critical_cols if col in df_clean.columns]
    df_clean = df_clean.dropna(subset=existing_critical)
    
    return df_clean


def create_sample_props_data() -> Dict:
    """Create sample team moneyline data for demonstration"""
    
    sample_props = {
        "game": "Lakers vs Warriors",
        "date": "2024-01-15",
        "team_moneylines": [
            {
                "team": "Lakers",
                "opponent": "Warriors",
                "moneyline": "+203",
                "implied_probability": 0.330,  # +203 = 33.0% implied probability
                "league": "NBA"
            },
            {
                "team": "Warriors",
                "opponent": "Lakers", 
                "moneyline": "-271",
                "implied_probability": 0.730,  # -271 = 73.0% implied probability
                "league": "NBA"
            }
        ]
    }
    
    return sample_props


def save_props_to_json(props_data: Dict, filename: str = "underdog_props.json") -> str:
    """Save props data to JSON file"""
    
    with open(filename, 'w') as f:
        json.dump(props_data, f, indent=2)
    
    return filename


def filter_props_by_league(props_data: Dict, league: str = "NBA") -> Dict:
    """Filter team moneylines by league"""
    
    if "team_moneylines" not in props_data:
        return props_data
    
    filtered_props = props_data.copy()
    filtered_props["team_moneylines"] = [
        prop for prop in props_data["team_moneylines"]
        if prop.get("league", "").upper() == league.upper()
    ]
    
    return filtered_props


def filter_props_by_date(props_data: Dict, date: str = None) -> Dict:
    """Filter props data by date"""
    
    if not date or "player_props" not in props_data:
        return props_data
    
    # This is a placeholder - real implementation would parse dates
    # and filter based on game_time field
    return props_data


def analyze_props_data(props_data: Dict) -> Dict:
    """Analyze team moneyline data and return insights"""
    
    if "team_moneylines" not in props_data:
        return {"error": "No team moneyline data found"}
    
    moneylines = props_data["team_moneylines"]
    
    # Basic statistics
    total_moneylines = len(moneylines)
    unique_teams = len(set(prop["team"] for prop in moneylines))
    
    # Team distribution
    team_counts = {}
    for prop in moneylines:
        team = prop["team"]
        team_counts[team] = team_counts.get(team, 0) + 1
    
    # Moneyline analysis
    implied_probs = [prop["implied_probability"] for prop in moneylines if "implied_probability" in prop]
    avg_prob = sum(implied_probs) / len(implied_probs) if implied_probs else 0
    min_prob = min(implied_probs) if implied_probs else 0
    max_prob = max(implied_probs) if implied_probs else 0
    
    # Favorite vs Underdog analysis
    favorites = [prop for prop in moneylines if prop.get("implied_probability", 0) > 0.5]
    underdogs = [prop for prop in moneylines if prop.get("implied_probability", 0) <= 0.5]
    
    analysis = {
        "total_moneylines": total_moneylines,
        "unique_teams": unique_teams,
        "team_distribution": team_counts,
        "implied_probability_analysis": {
            "average": round(avg_prob, 3),
            "minimum": round(min_prob, 3),
            "maximum": round(max_prob, 3)
        },
        "favorites_count": len(favorites),
        "underdogs_count": len(underdogs)
    }
    
    return analysis


def fetch_underdog_props(use_real_data: bool = False, league: str = "NBA") -> Dict:
    """Main function to fetch Underdog Fantasy team moneyline data"""
    
    print("🎲 UNDERDOG FANTASY TEAM MONEYLINE FETCHER")
    print("=" * 50)
    
    if use_real_data:
        print("🔄 Attempting to fetch real Underdog props data...")
        
        # Try to run the scraper
        csv_path = run_underdog_scraper()
        
        if csv_path:
            # Load and process the CSV
            df = load_props_csv(csv_path)
            
            if not df.empty:
                # Convert DataFrame to team moneyline format
                props_data = {
                    "source": "real_data",
                    "date": "2024-01-15",  # Would be extracted from data
                    "team_moneylines": df.to_dict('records')
                }
                
                # Filter by league
                props_data = filter_props_by_league(props_data, league)
                
                # Analyze the data
                analysis = analyze_props_data(props_data)
                props_data["analysis"] = analysis
                
                # Save to JSON
                json_file = save_props_to_json(props_data, "underdog_props_real.json")
                print(f"💾 Real props data saved to: {json_file}")
                
                return props_data
    
    # Fall back to sample data
    print("💡 Using sample team moneyline data for demonstration")
    print("🔧 To use real data, you would need to set up the vendor scraper")
    
    props_data = create_sample_props_data()
    props_data["source"] = "sample_data"
    
    # Filter by league
    props_data = filter_props_by_league(props_data, league)
    
    # Analyze the data
    analysis = analyze_props_data(props_data)
    props_data["analysis"] = analysis
    
    # Save to JSON
    json_file = save_props_to_json(props_data, "underdog_moneylines_sample.json")
    print(f"💾 Sample team moneyline data saved to: {json_file}")
    
    return props_data


if __name__ == "__main__":
    # Test the team moneyline fetcher
    props_data = fetch_underdog_props(use_real_data=False, league="NBA")
    
    print(f"\n📊 Team Moneyline Data Summary:")
    if "analysis" in props_data:
        analysis = props_data["analysis"]
        print(f"Total Moneylines: {analysis['total_moneylines']}")
        print(f"Unique Teams: {analysis['unique_teams']}")
        print(f"Average Implied Probability: {analysis['implied_probability_analysis']['average']}")
        print(f"Favorites: {analysis['favorites_count']}, Underdogs: {analysis['underdogs_count']}")
    
    print(f"\n🎲 Sample Team Moneylines:")
    for prop in props_data["team_moneylines"]:
        print(f"  {prop['team']} vs {prop['opponent']} - {prop['moneyline']} ({prop['implied_probability']:.1%})")
