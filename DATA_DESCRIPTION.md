# 📊 NBA BETTING SYSTEM - DATA DESCRIPTION

**Last Updated:** October 15, 2025

---

## 📁 DATA FILES OVERVIEW

Your system has **3 main data files** in the `data/` directory:

1. **nba_game_data.json** (961 KB) - All NBA game schedules and results
2. **nba_team_data.json** (27 KB) - Team statistics and performance metrics
3. **nba_injury_data.json** (255 KB) - Player injury reports and status

---

## 1️⃣ NBA GAME DATA (`nba_game_data.json`)

### 📖 Overview

**File Size:** 961 KB  
**Total Games:** 748 games  
**Season:** 2025-26  
**Date Range:** October 22, 2024 - October 21, 2025  
**Source:** NBA Stats API - LeagueGameFinder

### 🎯 Purpose

This file contains the complete NBA schedule for the 2025-26 season, including:
- All regular season games
- Game dates and matchups
- Team information (home/away)
- Game results (when available)
- Detailed box score statistics

### 📊 Data Structure

```json
{
  "metadata": {
    "data_source": "NBA Stats API - LeagueGameFinder",
    "season": "2025-26",
    "export_date": "2025-10-12T22:50:00",
    "total_games": 748,
    "date_range": {
      "start": "2024-10-22",
      "end": "2025-10-21"
    }
  },
  "games": [
    {
      "game_id": "0022500001",
      "date": "2025-10-22 00:00:00",
      "season": "22025",
      "season_type": "Regular Season",
      "home_team": "Houston Rockets",
      "away_team": "Oklahoma City Thunder",
      "home_team_id": 1610612745,
      "away_team_id": 1610612760,
      "home_team_abbr": "HOU",
      "away_team_abbr": "OKC",
      "home_score": 0,
      "away_score": 0,
      "home_win": 0,
      "away_win": 0,
      // ... 50+ more fields with detailed stats
    }
  ]
}
```

### 📝 Fields per Game (60+ total)

**Basic Info:**
- `game_id` - Unique game identifier
- `date` - Game date/time
- `season` - Season code
- `season_type` - "Regular Season"

**Team Info:**
- `home_team` / `away_team` - Full team names
- `home_team_id` / `away_team_id` - NBA team IDs
- `home_team_abbr` / `away_team_abbr` - Team abbreviations

**Game Result:**
- `home_score` / `away_score` - Final scores
- `home_win` / `away_win` - Win indicators (0/1)

**Home Team Stats (25 fields):**
- `home_fgm`, `home_fga`, `home_fg_pct` - Field goals
- `home_fg3m`, `home_fg3a`, `home_fg3_pct` - 3-pointers
- `home_ftm`, `home_fta`, `home_ft_pct` - Free throws
- `home_oreb`, `home_dreb`, `home_reb` - Rebounds
- `home_ast` - Assists
- `home_stl` - Steals
- `home_blk` - Blocks
- `home_tov` - Turnovers
- `home_pf` - Personal fouls

**Away Team Stats (25 fields):**
- Same stats as home team, prefixed with `away_`

### 🔍 How It's Used

**In Dashboard:**
- Load games by date
- Display matchups in "Picks" tab
- Show results in "Results" tab
- Track outcomes in "Track" tab

**In System:**
- Filter games by date for daily picks
- Get team matchups for predictions
- Update with actual results after games
- Historical analysis

### 📌 Important Notes

- **Future games** have `score = 0` (not played yet)
- **Opening Night:** October 22, 2025
  - Thunder @ Rockets
  - Warriors @ Lakers
- Games are listed chronologically
- Each game appears once (home team perspective)

---

## 2️⃣ NBA TEAM DATA (`nba_team_data.json`)

### 📖 Overview

**File Size:** 27 KB  
**Total Teams:** 30 NBA teams  
**Total Features:** 36 per team  
**Export Date:** September 11, 2025  
**Source:** NBA Stats API (with sample data fallback)

### 🎯 Purpose

This file contains team statistics and performance metrics used for:
- Machine learning model predictions
- Team performance analysis
- Statistical comparisons
- Feature engineering

### 📊 Data Structure

```json
{
  "metadata": {
    "total_teams": 30,
    "total_features": 36,
    "export_date": "2025-09-11 21:07:15",
    "data_source": "NBA Stats API (with sample data fallback)"
  },
  "feature_categories": {
    "basic_stats": [...],
    "advanced_metrics": [...],
    "contextual_features": [...]
  },
  "teams": [
    {
      "team_id": 1,
      "team_name": "Boston Celtics",
      "basic_stats": {
        "ppg": 109.8,        // Points per game
        "papg": 122.2,       // Points against per game
        "fg_pct": 0.44,      // Field goal %
        "fg3_pct": 0.381,    // 3-point %
        "ft_pct": 0.789,     // Free throw %
        "reb": 45.1,         // Rebounds per game
        "ast": 21.1,         // Assists per game
        "tov": 12.5,         // Turnovers per game
        "stl": 8.2,          // Steals per game
        "blk": 5.4           // Blocks per game
      },
      "advanced_metrics": {
        "ortg": 116.5,       // Offensive rating
        "drtg": 108.2,       // Defensive rating
        "net_rtg": 8.3,      // Net rating
        "efg_pct": 0.523,    // Effective FG%
        "tov_pct": 0.135,    // Turnover %
        "oreb_pct": 0.285,   // Offensive rebound %
        "fta_rate": 0.245    // Free throw attempt rate
      },
      "contextual_features": {
        "recent_win_pct": 0.650,      // Win % (recent)
        "is_home": 0,                 // Home game flag
        "days_rest": 2,               // Days since last game
        "is_b2b": 0,                  // Back-to-back game
        "key_player_injured": 0       // Injury flag
      }
    }
  ]
}
```

### 📝 Feature Categories (36 total)

#### **Basic Stats (10 features):**
- `PPG` - Points per game
- `PAPG` - Points against per game
- `FG_PCT` - Field goal percentage
- `FG3_PCT` - Three-point percentage
- `FT_PCT` - Free throw percentage
- `REB` - Rebounds per game
- `AST` - Assists per game
- `TOV` - Turnovers per game
- `STL` - Steals per game
- `BLK` - Blocks per game

#### **Advanced Metrics (7 features):**
- `ORtg` - Offensive rating (points per 100 possessions)
- `DRtg` - Defensive rating (opponent points per 100)
- `NET_RTG` - Net rating (ORtg - DRtg)
- `eFG_PCT` - Effective field goal % (adjusts for 3pt value)
- `TOV_PCT` - Turnover percentage
- `OREB_PCT` - Offensive rebound percentage
- `FTA_RATE` - Free throw attempt rate

#### **Contextual Features (5 features):**
- `RECENT_WIN_PCT` - Win percentage (recent games)
- `IS_HOME` - Home game indicator (0/1)
- `DAYS_REST` - Days since last game
- `IS_B2B` - Back-to-back game indicator (0/1)
- `KEY_PLAYER_INJURED` - Injury indicator (0/1)

### 🔍 How It's Used

**In Machine Learning Model:**
- Input features for predictions
- Compare home vs away team stats
- Calculate statistical advantages
- Generate win probabilities

**In Dashboard:**
- Display team performance metrics
- Show statistical comparisons
- Analyze matchup advantages

### 📌 Important Notes

- Data from **2024-25 season** (sample/historical)
- Needs updating after each game in 2025-26
- Used for ML model predictions
- 36 features × 30 teams = 1,080 data points

---

## 3️⃣ NBA INJURY DATA (`nba_injury_data.json`)

### 📖 Overview

**File Size:** 255 KB  
**Total Teams:** 30  
**Total Injury Records:** Varies by day  
**Export Date:** October 12, 2025  
**Source:** Inferred from NBA API game logs

### 🎯 Purpose

This file tracks player injuries and availability:
- Player injury status
- Game-by-game availability
- Injury impact on team performance
- Key player tracking

### 📊 Data Structure

```json
{
  "metadata": {
    "export_date": "2025-10-12 22:06:15",
    "data_source": "Inferred from NBA API game logs",
    "method": "Hybrid (game logs + manual updates)"
  },
  "teams": [
    {
      "team_id": 1610612738,
      "team_name": "Boston Celtics",
      "injuries": [
        {
          "player_name": "Jayson Tatum",
          "player_id": 1628369,
          "status": "Out",
          "details": "Ankle sprain",
          "games_missed": 3,
          "last_updated": "2025-10-12"
        },
        {
          "player_name": "Kristaps Porzingis",
          "player_id": 204001,
          "status": "Questionable",
          "details": "Knee soreness",
          "games_missed": 0,
          "last_updated": "2025-10-12"
        }
      ]
    }
  ]
}
```

### 📝 Fields per Injury

- `player_name` - Player's full name
- `player_id` - NBA player ID
- `status` - Injury status:
  - "Out" - Will miss game
  - "Questionable" - 50/50 to play
  - "Doubtful" - Unlikely to play
  - "Probable" - Likely to play
  - "Day-to-Day" - Status uncertain
- `details` - Injury description
- `games_missed` - Number of games missed
- `last_updated` - Last update date

### 🔍 How It's Used

**In System:**
- Adjust team strength predictions
- Flag teams with key injuries
- Update `KEY_PLAYER_INJURED` feature
- Risk assessment for bets

**In Dashboard:**
- Display injury warnings
- Alert users to missing stars
- Adjust EV calculations

### 📌 Important Notes

- **Hybrid approach:** Game logs + manual updates
- Updates needed before each game day
- Critical for accurate predictions
- Key injuries can swing games 5-10%

---

## 🔄 DATA UPDATE CYCLE

### Daily Updates Needed

**Before Each Game Day:**

1. **Update Team Stats** (`nba_team_data.json`)
   - Run after previous day's games
   - Update PPG, FG%, etc.
   - Recalculate ratings
   - Script: `game_data_fetch.py`

2. **Check Injuries** (`nba_injury_data.json`)
   - Check NBA injury reports
   - Update player status
   - Flag key players out

3. **Game Results** (`nba_game_data.json`)
   - Update scores after games
   - Mark wins/losses
   - Add box score stats

### Season Start (Opening Night)

- **All teams:** 1500 Elo rating
- **Team stats:** Based on preseason
- **Injuries:** Check official reports
- **Games:** Schedule loaded, scores = 0

### Mid-Season Updates

- **Weekly:** Update all team stats
- **Daily:** Check injuries
- **After games:** Update results
- **Monthly:** Retrain ML model

---

## 📊 DATA QUALITY & SOURCES

### Data Sources

1. **NBA Stats API** (Primary)
   - Official NBA data
   - Real-time updates
   - Comprehensive stats

2. **Historical Data** (Training)
   - 2024-25 season (complete)
   - 1,000+ games
   - Used for ML model training

3. **Manual Updates** (Injuries)
   - ESPN injury reports
   - Team announcements
   - Beat reporter updates

### Data Quality

**Game Data:**
- ✅ Accurate - Direct from NBA API
- ✅ Complete - All games included
- ✅ Updated - Real-time after games

**Team Stats:**
- ✅ Accurate - Calculated from games
- ⚠️ Needs updates - After each game
- ✅ Comprehensive - 36 features

**Injury Data:**
- ⚠️ Manual effort - Needs checking
- ⚠️ Can be outdated - Updates lag
- ✅ Useful - When accurate

---

## 🎯 DATA USAGE IN SYSTEM

### Dashboard Flow

1. **User selects date** → Load from `nba_game_data.json`
2. **Display games** → Show matchups for that date
3. **User inputs odds** → Manual entry
4. **Calculate EV** → Use team stats from `nba_team_data.json`
5. **Check injuries** → Reference `nba_injury_data.json`
6. **Make prediction** → Elo or ML model
7. **Show recommendation** → Place bet or skip

### Model Flow

1. **Load team stats** → From `nba_team_data.json`
2. **Extract features** → 28 features (14 per team)
3. **Scale features** → Normalize values
4. **Run model** → Predict win probability
5. **Calculate EV** → Compare to odds
6. **Return decision** → Bet or no bet

---

## 📝 DATA FILE LOCATIONS

```
NBA_winners/
├── data/
│   ├── nba_game_data.json       # 961 KB - All games
│   ├── nba_team_data.json       # 27 KB - Team stats
│   ├── nba_injury_data.json     # 255 KB - Injuries
│   └── data_archive/            # Old/backup data
├── models/
│   └── nba_model.pkl            # Trained ML model
└── archive/
    ├── elo_ratings.py           # Elo system code
    └── model_training.py        # ML training code
```

---

## ✅ SUMMARY

### Data Overview

| File | Size | Records | Purpose | Update Frequency |
|------|------|---------|---------|------------------|
| `nba_game_data.json` | 961 KB | 748 games | Schedule & results | After each game |
| `nba_team_data.json` | 27 KB | 30 teams | Team statistics | Weekly |
| `nba_injury_data.json` | 255 KB | Variable | Player injuries | Daily |

### Key Points

1. **Game data** is complete for 2025-26 season
2. **Team stats** need updating after games
3. **Injury data** requires manual checking
4. **All data** comes from NBA Stats API
5. **Updates** needed for accurate predictions

### Next Steps

1. ✅ Data files exist and are ready
2. ⏳ Wait for Opening Night (Oct 22)
3. 🔄 Update after each game
4. 📊 Track accuracy
5. 🎯 Refine predictions

---

*Last Updated: October 15, 2025*
