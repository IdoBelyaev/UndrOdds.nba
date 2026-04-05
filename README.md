# 🏀 NBA Betting System

A complete NBA betting analysis and tracking system with Expected Value (EV) calculations, bet tracking, and performance visualization.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

---

## 📊 Features

### **Picks Tab**
- Fetch games for any date
- Enter moneyline odds from your sportsbook
- Calculate Expected Value (EV) for each game
- Get betting recommendations
- Place bets with one click

### **Results Tab**
- View pending bets
- Mark bets as Won/Lost
- Track profit/loss
- Update bankroll automatically

### **Track Tab**
- Complete bet history table
- View all bets with dates, picks, odds, and results
- Summary statistics (total bets, wins, losses, profit)

### **Visuals Tab**
- Bankroll growth chart
- Win rate gauge
- Cumulative profit chart
- Profit distribution histogram

---

## 📁 Project Structure

```
NBA_winners/
├── dashboard.py              # Main Streamlit dashboard
├── bet_tracker.py           # Bet tracking and history
├── ev_calculator.py         # Expected Value calculations
├── game_data_fetch.py       # Fetch NBA game data
├── bet_history.json         # Your bet history (auto-generated)
├── requirements.txt         # Python dependencies
│
├── data/                    # Game and team data
│   ├── nba_game_data.json   # All NBA games (1,233 games)
│   ├── nba_team_data.json   # Team statistics
│   └── nba_injury_data.json # Injury data
│
├── models/                  # ML models
│   └── nba_model.pkl        # Trained prediction model
│
├── docs/                    # Documentation
│   ├── README.md            # Detailed documentation
│   ├── QUICK_START.md       # Quick start guide
│   └── RFC-001.md           # Project specification
│
├── archive/                 # Development files (archived)
└── macOS_App/              # Swift/SwiftUI app (future)
```

---

## 🎯 Usage

### For Opening Night (Oct 21, 2025)

1. **Open Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

2. **Go to Picks Tab**
   - Enter date: `21/10/2025`
   - Click "Fetch Games"
   - See 3 Opening Night games

3. **Enter Odds**
   - Get moneyline odds from your sportsbook
   - Enter for each team
   - Click "Calculate EV"

4. **Place Bets**
   - Review recommendations
   - Click "Place Bet" for positive EV games
   - Bets are automatically tracked

5. **Track Results**
   - After games finish, go to Results tab
   - Mark bets as Won/Lost
   - View updated bankroll and stats

---

## 📅 Season Updates

### When New Games Are Played

Run this to fetch new game data:
```bash
python3 game_data_fetch.py
```

This will:
- Fetch all newly played games from NBA API
- Update `nba_game_data.json`
- Add games with scores and stats

---

## 🔧 Configuration

### Sidebar Settings (in Dashboard)
- **Bankroll**: Set your starting bankroll
- **Flat Bet Amount**: Set bet size per game
- **Minimum EV**: Set EV threshold for recommendations (default: 3%)

---

## 📈 How It Works

1. **Fetch Games**: Get games for a specific date
2. **Enter Odds**: Input moneyline odds from sportsbook
3. **Calculate EV**: System calculates Expected Value
   - Compares model probability vs sportsbook probability
   - Identifies value bets (positive EV)
4. **Place Bets**: Log bets with one click
5. **Track Results**: Mark outcomes and track performance
6. **Analyze**: View charts and statistics

---

## 🎓 Understanding Expected Value (EV)

**Expected Value** = (Win Probability × Profit) - (Loss Probability × Loss)

**Positive EV** = Good bet (edge over sportsbook)  
**Negative EV** = Bad bet (sportsbook has edge)

The system only recommends bets with positive EV above your threshold.

---

## 📝 Notes

- **Current Data**: 2024-25 season (1,230 games) + 3 sample 2025-26 Opening Night games
- **Season Start**: October 21, 2025
- **Odds Input**: Manual (from your sportsbook)
- **Model**: Uses Elo ratings + team statistics

---

## 🆘 Support

For issues or questions, check:
- `docs/README.md` - Detailed documentation
- `docs/QUICK_START.md` - Quick start guide
- `docs/RFC-001.md` - Full project specification

---

## 🚀 Ready for Opening Night!

Your system is clean, organized, and ready to track real bets starting October 21, 2025!

**Good luck and bet responsibly!** 🏀💰



