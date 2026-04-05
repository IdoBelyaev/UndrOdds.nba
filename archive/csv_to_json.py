#!/usr/bin/env python3
"""
Convert existing CSV file to JSON format
"""

import pandas as pd
import json

def csv_to_json(csv_file="data/comprehensive_team_features.csv", json_file="data/team_data.json"):
    """Convert CSV file to JSON format"""
    
    print(f"📄 Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    
    print(f"📊 Found {len(df)} teams with {len(df.columns)} features")
    
    # Create JSON structure
    json_data = {
        "metadata": {
            "total_teams": len(df),
            "total_features": len(df.columns),
            "source_file": csv_file,
            "conversion_date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "teams": []
    }
    
    # Convert each row to JSON format
    for _, row in df.iterrows():
        team_data = {
            "team_id": int(row.get('TEAM_ID', 0)),
            "team_name": row.get('TEAM_NAME', ''),
            "stats": {}
        }
        
        # Add all other columns as stats
        for col in df.columns:
            if col not in ['TEAM_ID', 'TEAM_NAME']:
                value = row[col]
                if pd.isna(value):
                    value = None
                elif isinstance(value, (int, float)):
                    if isinstance(value, float):
                        value = round(value, 3)
                team_data["stats"][col.lower()] = value
        
        json_data["teams"].append(team_data)
    
    # Save to JSON file
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✅ JSON file created: {json_file}")
    return json_data

if __name__ == "__main__":
    csv_to_json()
