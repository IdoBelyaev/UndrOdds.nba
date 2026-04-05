#!/usr/bin/env python3
"""
Simple script to create JSON file from team data
"""

import pandas as pd
import json
from main import get_comprehensive_team_features, export_to_json

def main():
    print("🏀 Creating NBA Team Data JSON File...")
    
    # Get the comprehensive team data
    team_stats = get_comprehensive_team_features()
    
    # Export to JSON
    json_data = export_to_json(team_stats, "nba_team_data.json")
    
    print("✅ JSON file created successfully!")
    print(f"📁 Location: data/nba_team_data.json")
    print(f"📊 Contains: {len(json_data['teams'])} teams with comprehensive stats")

if __name__ == "__main__":
    main()
