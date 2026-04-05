# NBA Bet Selector - Data Documentation

**Last Updated:** October 13, 2025  
**Version:** 1.0  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Data Schemas](#data-schemas)
4. [Data Collection](#data-collection)
5. [Data Quality](#data-quality)
6. [Update Frequency](#update-frequency)
7. [Usage Guide](#usage-guide)

---

## Overview

This document provides comprehensive documentation for all data sources, schemas, and processes used in the NBA Bet Selector project. The system collects and validates NBA data to enable accurate game outcome prediction and Expected Value (EV) calculation for sports betting.

### Data Pipeline Summary

```
NBA Stats API → data_fetch.py → nba_team_data.json
NBA Stats API → game_data_fetch.py → nba_game_data.json
NBA Stats API → injury_data_fetch.py → nba_injury_data.json
User Input → odds_input_system.py → underdog_moneylines.json
```

---

## Data Sources

### 1. NBA Stats API (Primary Source)

**Source:** `nba_api` Python library (wrapper for stats.nba.com)  
**Reliability:** High (official NBA data)  
**Update Frequency:** Daily  
**Coverage:** 2024-25 NBA Regular Season  

**What We Collect:**
- Team statistics (30 NBA teams)
- Game results and schedules (1,230+ games)
- Player game logs (for injury inference)

**API Endpoints Used:**
- `LeagueDashTeamStats` - Team statistics
- `LeagueGameFinder` - Game data
- `PlayerGameLog` - Player participation data

### 2. Underdog Fantasy (Manual Input)

**Source:** Manual user input from Underdog Fantasy app/website  
**Reliability:** High (user-verified)  
**Update Frequency:** On-demand (daily before games)  
**Coverage:** Team moneyline odds only  

**What We Collect:**
- Moneyline odds for home teams
- Moneyline odds for away teams
- Game dates and matchups

---

## Data Schemas

### Team Statistics Schema

**File:** `nba_team_data.json`  
**Records:** 30 teams  
**Features:** 29 per team  

```json
{
  "metadata": {
    "season": "2024-25",
    "total_teams": 30,
    "total_features": 29,
    "export_date": "ISO-8601 timestamp",
    "data_source": "NBA Stats API"
  },
  "teams": [
    {
      "TEAM_NAME": "string",
      "TEAM_ID": "integer",
      
      // Record
      "W": "integer (wins)",
      "L": "integer (losses)",
      "GP": "integer (games played, ≤82)",
      "WIN_PCT": "float (0-1)",
      
      // Basic Stats (per game)
      "PPG": "float (points per game)",
      "PAPG": "float (points allowed per game)",
      "FG_PCT": "float (field goal %, 0-1)",
      "FG3_PCT": "float (3-point %, 0-1)",
      "FT_PCT": "float (free throw %, 0-1)",
      "REB": "float (rebounds per game)",
      "AST": "float (assists per game)",
      "TOV": "float (turnovers per game)",
      "STL": "float (steals per game)",
      "BLK": "float (blocks per game)",
      
      // Advanced Metrics
      "ORtg": "float (offensive rating, pts/100 poss)",
      "DRtg": "float (defensive rating, pts allowed/100 poss)",
      "NET_RTG": "float (net rating, ORtg - DRtg)",
      "eFG_PCT": "float (effective FG%)",
      "TOV_PCT": "float (turnover %)",
      "OREB_PCT": "float (offensive rebound %)",
      "FTA_RATE": "float (free throw attempt rate)",
      
      // Context Features (placeholder for model)
      "RECENT_WIN_PCT_10": "float (last 10 games)",
      "HOME_AWAY_FLAG": "integer (1=home, 0=away)",
      "DAYS_REST": "integer",
      "BACK_TO_BACK": "integer (1=yes, 0=no)"
    }
  ]
}
```

**Data Quality:**
- All teams have complete data
- All percentages in valid range (0-1)
- W + L = GP for all teams
- GP ≤ 82 (regular season only)

---

### Game Data Schema

**File:** `nba_game_data.json`  
**Records:** 1,230 games  
**Season:** 2024-25 Regular Season  

```json
{
  "metadata": {
    "data_source": "NBA Stats API - LeagueGameFinder",
    "season": "22024",
    "export_date": "ISO-8601 timestamp",
    "total_games": 1230,
    "date_range": {
      "start": "2024-10-22",
      "end": "2025-04-13"
    }
  },
  "games": [
    {
      "game_id": "string (unique)",
      "date": "YYYY-MM-DD HH:MM:SS",
      "season": "string",
      "season_type": "Regular Season",
      
      // Teams
      "home_team": "string (team name)",
      "away_team": "string (team name)",
      "home_team_id": "integer",
      "away_team_id": "integer",
      "home_team_abbr": "string (3-letter)",
      "away_team_abbr": "string (3-letter)",
      
      // Scores
      "home_score": "integer (0-200)",
      "away_score": "integer (0-200)",
      "home_win": "integer (1=win, 0=loss)",
      "away_win": "integer (1=win, 0=loss)",
      
      // Home Team Stats
      "home_fgm": "integer (field goals made)",
      "home_fga": "integer (field goals attempted)",
      "home_fg_pct": "float (0-1)",
      "home_fg3m": "integer (3-pointers made)",
      "home_fg3a": "integer (3-pointers attempted)",
      "home_fg3_pct": "float (0-1)",
      "home_ftm": "integer (free throws made)",
      "home_fta": "integer (free throws attempted)",
      "home_ft_pct": "float (0-1)",
      "home_reb": "integer (rebounds)",
      "home_ast": "integer (assists)",
      "home_stl": "integer (steals)",
      "home_blk": "integer (blocks)",
      "home_tov": "integer (turnovers)",
      "home_pf": "integer (personal fouls)",
      "home_plus_minus": "float",
      
      // Away Team Stats (same structure)
      "away_fgm": "integer",
      "away_fga": "integer",
      // ... (mirrors home stats)
      
      // Derived Fields
      "total_points": "integer (sum of both scores)",
      "point_differential": "integer (abs difference)"
    }
  ]
}
```

**Data Quality:**
- No duplicate game IDs
- All scores in valid range (0-200)
- Win/loss logic correct (higher score = win)
- All 30 NBA teams represented
- Date range covers full regular season

---

### Injury Data Schema

**File:** `nba_injury_data.json`  
**Records:** 530 players  
**Method:** Hybrid (NBA API game logs + web scraping placeholder)  

```json
{
  "metadata": {
    "data_source": "NBA API Game Logs + Web Scraping (Hybrid)",
    "season": "2024-25",
    "export_date": "ISO-8601 timestamp",
    "total_players": 530,
    "injury_status_summary": {
      "HEALTHY": "integer (count)",
      "PROBABLE": "integer",
      "QUESTIONABLE": "integer",
      "DOUBTFUL": "integer",
      "OUT": "integer"
    },
    "update_frequency": "Daily"
  },
  "injuries": [
    {
      "player_id": "integer (unique)",
      "player_name": "string",
      "team_id": "integer",
      "team_name": "string",
      "roster_status": "integer (1=active roster)",
      
      // Injury Status
      "injury_status": "string (HEALTHY|PROBABLE|QUESTIONABLE|DOUBTFUL|OUT)",
      "injury_type": "string (body part or 'None')",
      "injury_severity": "string (severity or 'None')",
      "expected_return": "string (date or 'N/A')",
      
      // Participation Data
      "last_game_date": "string (MMM DD, YYYY)",
      "games_missed": "integer (consecutive)",
      "recent_minutes_avg": "float (last 5 games)",
      
      // Metadata
      "data_source": "string (NBA API Game Logs or Web Scraping)"
    }
  ]
}
```

**Data Quality:**
- All required fields present (player_name, team_name, injury_status)
- Valid injury statuses only
- 30 teams represented
- Real participation data from NBA API

---

### Odds Data Schema

**File:** `underdog_moneylines.json`  
**Records:** Variable (user-inputted)  
**Update:** On-demand (before games)  

```json
{
  "metadata": {
    "data_source": "Underdog Fantasy - Manual Input",
    "export_date": "ISO-8601 timestamp",
    "total_games": "integer",
    "sportsbook": "Underdog Fantasy"
  },
  "odds": [
    {
      "game_id": "string (matches game_data)",
      "date": "YYYY-MM-DD",
      "home_team": "string",
      "away_team": "string",
      
      // Moneyline Odds
      "underdog_ml_home": "integer (e.g., +150, -200)",
      "underdog_ml_away": "integer",
      
      // Implied Probabilities
      "implied_prob_home": "float (0-1)",
      "implied_prob_away": "float (0-1)",
      
      // Metadata
      "input_timestamp": "ISO-8601 timestamp",
      "input_method": "manual"
    }
  ]
}
```

**Odds Format:**
- Positive odds (e.g., +150): Underdog
- Negative odds (e.g., -200): Favorite

**Implied Probability Calculation:**
```python
# Positive odds
implied_prob = 100 / (odds + 100)

# Negative odds
implied_prob = abs(odds) / (abs(odds) + 100)
```

---

## Data Collection

### Team Statistics Collection

**Script:** `data_fetch.py`  
**Frequency:** Daily (or on-demand)  
**Runtime:** ~5-10 seconds  

**Process:**
1. Import `nba_api` library
2. Call `LeagueDashTeamStats` endpoint
3. Apply bot detection avoidance (random delays)
4. Filter to 29 core features
5. Scale stats to 82-game season (cap GP at 82)
6. Calculate derived features (WIN_PCT, NET_RTG)
7. Save to `nba_team_data.json`

**Command:**
```bash
python data_fetch.py
```

---

### Game Data Collection

**Script:** `game_data_fetch.py`  
**Frequency:** Daily  
**Runtime:** ~10-15 seconds  

**Process:**
1. Import `nba_api` library
2. Call `LeagueGameFinder` endpoint
3. Filter to 30 NBA teams
4. Standardize date format
5. Calculate derived fields (total_points, point_differential)
6. Save to `nba_game_data.json`

**Command:**
```bash
python game_data_fetch.py
```

---

### Injury Data Collection

**Script:** `injury_data_fetch.py`  
**Frequency:** Daily  
**Runtime:** ~20-30 seconds  

**Process:**
1. Fetch player game logs from NBA API
2. Infer injury status based on participation
   - 0 minutes in recent games → PROBABLE/OUT
   - Missing from games → OUT
   - Normal minutes → HEALTHY
3. (Placeholder for web scraping enhancement)
4. Save to `nba_injury_data.json`

**Command:**
```bash
python injury_data_fetch.py
```

---

### Odds Data Collection

**Script:** `odds_input_system.py`  
**Frequency:** On-demand (before games)  
**Runtime:** Manual input (2-5 minutes)  

**Process:**
1. User inputs game date (DD-MM-YYYY)
2. System fetches games for that date
3. User inputs moneyline odds for each game
4. System calculates implied probabilities
5. User reviews and confirms
6. Save to `underdog_moneylines.json`

**Command:**
```bash
python odds_input_system.py
```

**Input Format:**
```
Date: 22-10-2024
Game 1: Lakers vs Warriors
  Lakers odds: +150
  Warriors odds: -180
```

---

## Data Quality

### Validation System

**Script:** `data_validation.py`  
**Checks:** 18 automated checks  

**What It Validates:**
- ✅ Data completeness (all expected records)
- ✅ Data accuracy (scores, stats in valid ranges)
- ✅ Date validity (proper formatting)
- ✅ Team consistency (30 teams across sources)
- ✅ No duplicates
- ✅ Win/loss logic
- ✅ Record consistency (W+L=GP)
- ✅ Percentage accuracy (0-1 range)

**Command:**
```bash
python data_validation.py
```

**Output:** `data_validation_results.json`

---

### Quality Monitoring

**Script:** `data_quality_monitor.py`  
**Checks:** 4 quality dimensions  

**What It Monitors:**
- Missing values (0 expected)
- Outliers (statistical anomalies)
- Data freshness (<24 hours)
- Schema consistency

**Quality Score:** 0-100
- 90-100: Excellent
- 75-89: Good
- 60-74: Fair
- <60: Poor

**Command:**
```bash
python data_quality_monitor.py
```

**Output:** `data_quality_report.json`

---

### Consistency Checking

**Script:** `data_consistency_checker.py`  
**Checks:** 4 consistency dimensions  

**What It Checks:**
- Team name standardization across sources
- Date format consistency (ISO-8601)
- ID mapping consistency (no conflicts)
- Cross-source reconciliation (win counts match)

**Command:**
```bash
python data_consistency_checker.py
```

**Output:** `data_consistency_report.json`

---

## Update Frequency

### Daily Updates (Recommended)

**Morning Routine (9 AM):**
1. Run data pipeline: `python data_pipeline.py --mode full`
2. Review validation reports
3. Fix any issues

**Before Games (1 hour before):**
1. Input moneyline odds: `python odds_input_system.py`
2. Verify game matchups
3. Calculate Expected Value (in M2)

### Weekly Updates

**Sunday (End of Week):**
1. Full data refresh
2. Review quality trends
3. Update injury data
4. Archive old odds data

---

## Usage Guide

### Quick Start

**1. Fetch All Data:**
```bash
python data_pipeline.py --mode full --season 2024-25
```

**2. Validate Data:**
```bash
python data_validation.py
```

**3. Input Odds:**
```bash
python odds_input_system.py
```

---

### Advanced Usage

**Custom Data Fetch:**
```python
from data_fetch import fetch_team_data
from game_data_fetch import fetch_game_data

# Fetch specific season
fetch_team_data("2023-24")
fetch_game_data("2023-24")
```

**Automated Daily Pipeline:**
```bash
# Add to crontab for daily 9 AM execution
0 9 * * * cd /path/to/NBA_winners && python data_pipeline.py --mode quick
```

**Quality Monitoring:**
```python
from data_quality_monitor import DataQualityMonitor

monitor = DataQualityMonitor()
report = monitor.run_all_checks()

if report['overall_score'] < 75:
    print("⚠️ Quality issue detected!")
```

---

### Troubleshooting

**Issue: NBA API returns HTTP 500**
- **Cause:** Aggressive bot detection
- **Solution:** Already handled with random delays and nba_api library

**Issue: Missing games in game data**
- **Cause:** Data pulled mid-season
- **Solution:** Normal, games not yet played won't appear

**Issue: Stale data warning**
- **Cause:** Data > 24 hours old
- **Solution:** Run `python data_pipeline.py --mode quick`

**Issue: Team name mismatch**
- **Cause:** "LA Clippers" vs "Los Angeles Clippers"
- **Solution:** Use team ID for matching, not name

---

## Data Retention

**Current Files:**
- `nba_team_data.json` - Overwritten daily
- `nba_game_data.json` - Overwritten daily
- `nba_injury_data.json` - Overwritten daily
- `underdog_moneylines.json` - Append only (historical)

**Archive Strategy:**
- Keep current season data
- Archive previous seasons to `archive/` folder
- Retain validation reports for 30 days

---

## API Rate Limits

**NBA Stats API:**
- No official rate limit documented
- Conservative approach: 1 request per 2-5 seconds
- Already implemented in our data collection scripts

**Underdog Fantasy:**
- Manual input, no API (user-verified)

---

## Data Privacy & Ethics

**No Personal Data:**
- Only public NBA statistics
- No player personal information
- No betting account data

**Intended Use:**
- Educational and analytical purposes
- Responsible sports betting
- No guarantee of profitability

---

## Contact & Support

**Project Repository:** NBA_winners  
**Last Updated:** October 13, 2025  
**Maintained By:** Project Team  

For issues or questions, refer to:
- `M1_PROGRESS.md` - Project progress
- `RFC-001.md` - Project specification
- `data_pipeline.log` - Execution logs

---

**End of Documentation**

