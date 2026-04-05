# 🏀 NBA BETTING SYSTEM - GETTING STARTED

**Last Updated:** October 12, 2025  
**Opening Night:** October 22, 2025  
**Status:** ✅ Ready to Use

---

## 🚀 QUICK START

### 1. Start the Dashboard
```bash
streamlit run dashboard.py
```

### 2. Test with Opening Night
- **Date:** `22/10/2025`
- **Games:**
  - Thunder @ Rockets (7:30 PM ET)
  - Warriors @ Lakers (10:00 PM ET)

### 3. Enter Odds & Calculate EV
- Get moneyline odds from your sportsbook
- Enter for each team
- Click "Calculate EV"
- Review recommendations

### 4. Place Bets & Track Results
- Click "Place Bet" for positive EV games
- Go to Results tab after games
- Mark as Won/Lost
- View performance in Track & Visuals tabs

---

## 📊 SYSTEM STATUS

### ✅ What's Ready
- **748 games** from 2025-26 season
- **2 Opening Night games** (Oct 22, 2025)
- **Dashboard** fully functional (4 tabs)
- **Bet tracking** system clean (0 bets)
- **File structure** organized and minimal

### 📁 Project Structure
```
NBA_winners/
├── dashboard.py              # Main application ⭐
├── bet_tracker.py           # Bet tracking
├── ev_calculator.py         # EV calculations
├── game_data_fetch.py       # Data fetching
├── bet_history.json         # Your bets (clean)
├── requirements.txt         # Dependencies
├── README.md                # Documentation
│
├── data/                    # Game data
│   ├── nba_game_data.json   # 748 games (2025-26 only)
│   ├── nba_team_data.json   # Team stats
│   └── nba_injury_data.json # Injury data
│
├── models/                  # ML models
├── docs/                    # Documentation
└── archive/                 # Old files (archived)
```

---

## 📅 IMPORTANT DATES

### 2025-26 NBA Season Timeline

**October 22, 2025** - Opening Night
- Thunder @ Rockets (7:30 PM ET)
- Warriors @ Lakers (10:00 PM ET)

**October 22 - November 15** - Observation Period
- ⏸️ **DON'T BET YET**
- Track model predictions
- See how accurate it is
- Learn the system

**November 15-30** - Start Betting (Small)
- 💰 **Use 50% bet size** ($10 instead of $20)
- Teams have ~10-15 games
- Build confidence
- Test the system

**December 1+** - Full Betting
- 💰 **Use 100% bet size** ($20)
- Teams have ~20+ games
- Confident predictions
- Full operation

**April 2026** - End of Regular Season
- All ~1,230 games played
- Complete season data

---

## 🎯 WHEN TO START BETTING

### ✅ RECOMMENDED: Wait 3-4 Weeks (mid-November)

**Why Wait?**
- Teams need 10-15 games to establish patterns
- Model needs data to be accurate
- You need time to learn the system
- Lower risk, higher confidence

**Sample Size Guidelines:**
- **10 games** = Minimum for trends
- **20 games** = Good confidence
- **30+ games** = High confidence

**Timeline:**
- **Weeks 1-3:** Observe only (no betting)
- **Weeks 4-5:** Start betting (50% size)
- **Week 6+:** Full betting (100% size)

---

## 💰 BANKROLL MANAGEMENT

### Starting Bankroll
- Recommended: $500 - $2,000
- Set in dashboard sidebar

### Bet Sizing
- **Conservative:** 1-2% of bankroll per bet
- **Moderate:** 2-3% of bankroll per bet
- **Aggressive:** 3-5% of bankroll per bet

**Example (with $1,000 bankroll):**
- Conservative: $10-20 per bet
- Moderate: $20-30 per bet
- Aggressive: $30-50 per bet

### EV Threshold
- **Default:** 3% minimum EV
- **Conservative:** 5% minimum EV
- **Aggressive:** 1-2% minimum EV

**Higher threshold = Fewer bets, higher quality**

---

## 📊 DATA COLLECTION

### Current Data
- **748 games** from 2025-26 season
- **All games are placeholders** (0-0 scores)
- Games haven't been played yet

### After Games Are Played

**Weekly Update:**
```bash
python3 game_data_fetch.py
```

**What It Does:**
1. Connects to NBA API
2. Fetches all newly played games
3. Gets real scores and statistics
4. Updates `nba_game_data.json`
5. Replaces placeholders with real data

**Timeline:**
- **Oct 22:** Run after Opening Night → 2 games
- **Oct 23:** Run daily → ~12 games total
- **Weekly:** Run once per week → keeps database current
- **April 2026:** Complete season data (~1,230 games)

---

## 🎮 DAILY WORKFLOW

### For Betting

1. **Check Today's Games**
   - NBA.com or ESPN schedule
   - Note which games interest you

2. **Open Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

3. **Go to Picks Tab**
   - Enter today's date (format: DD/MM/YYYY)
   - Click "Fetch Games"

4. **Enter Moneyline Odds**
   - Get odds from your sportsbook
   - Enter for each team
   - Click "Calculate EV"

5. **Review Recommendations**
   - Check analysis table
   - Read reasoning
   - Note EV percentages

6. **Place Bets**
   - Click "Place Bet" for positive EV games
   - Bets are automatically tracked

7. **After Games Finish**
   - Go to Results tab
   - Mark bets as Won/Lost
   - Click "Save Result"

8. **Review Performance**
   - Track tab: Bet history table
   - Visuals tab: Charts and analytics

---

## 📈 UNDERSTANDING EXPECTED VALUE (EV)

### What is EV?

**Expected Value** = (Win Probability × Profit) - (Loss Probability × Loss)

**Example:**
- Bet: $20 on Celtics +150
- Model says: 45% win probability
- Sportsbook implies: 40% win probability
- **Edge:** 5 percentage points
- **EV:** +8.3% (good bet!)

### EV Interpretation

- **Positive EV (+):** Good bet (you have edge)
- **Negative EV (-):** Bad bet (sportsbook has edge)
- **Zero EV (0):** Break-even (no edge)

### Recommendations

- **EV > 3%:** ✅ BET (default threshold)
- **EV 1-3%:** ⚠️ Marginal (increase threshold)
- **EV < 1%:** ❌ NO BET (no edge)

---

## 🔧 DASHBOARD FEATURES

### Tab 1: Picks
- Fetch games for any date
- Enter moneyline odds
- Calculate Expected Value
- Get betting recommendations
- Place bets with one click

### Tab 2: Results
- View pending bets
- Mark bets as Won/Lost
- Automatic profit/loss calculation
- Update bankroll

### Tab 3: Track
- Complete bet history table
- Sort by date, game, result
- Summary statistics
- Total bets, wins, losses, profit

### Tab 4: Visuals
- Bankroll growth chart
- Win rate gauge
- Cumulative profit chart
- Profit distribution histogram

---

## ⚙️ SETTINGS (Sidebar)

### Bankroll
- Set your starting bankroll
- Updates automatically with wins/losses

### Flat Bet Amount
- Set your bet size per game
- Recommended: 1-3% of bankroll

### Minimum EV
- Set EV threshold for recommendations
- Default: 3%
- Higher = fewer, better quality bets

---

## 🎓 TIPS FOR SUCCESS

### 1. Bankroll Management
- Start with comfortable amount
- Use flat betting (same size)
- Don't bet more than 1-5% per game
- Never chase losses

### 2. EV Threshold
- Start conservative (3-5%)
- Lower threshold = more bets
- Higher threshold = better quality
- Adjust based on results

### 3. Track Everything
- Log every bet (system does this)
- Review performance weekly
- Adjust strategy based on data
- Learn from mistakes

### 4. Be Patient
- Don't bet early season
- Wait for model to have data
- Season is 6 months long
- Missing first few weeks is fine

### 5. Bet Responsibly
- Only bet what you can afford
- This is entertainment/analysis
- Past performance ≠ future results
- Know when to stop

---

## 🚨 IMPORTANT REMINDERS

### Data
- **Current:** 748 games (2025-26 season only)
- **All 2024-25 data removed** (as requested)
- **Opening Night:** October 22, 2025
- **Games are placeholders** until played

### Odds
- **Manual entry** from your sportsbook
- System doesn't fetch odds automatically
- You must enter them each time

### Model
- Uses **Elo ratings** + **team statistics**
- Improves with more games played
- More accurate mid-season
- Less accurate early season

### Updates
- Run `python3 game_data_fetch.py` weekly
- Fetches newly played games
- Keeps database current
- Required for historical analysis

---

## 📞 TROUBLESHOOTING

### Dashboard Won't Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard.py
```

### No Games Found
- Check date format: DD/MM/YYYY
- Use: 22/10/2025 for Opening Night
- Games must be in database

### Place Bet Button Not Working
- Make sure you clicked "Calculate EV" first
- Button only appears for positive EV games
- Refresh page if needed

### Results Tab Empty
- No bets placed yet
- Place bets in Picks tab first
- Bets appear after clicking "Place Bet"

---

## 📚 ADDITIONAL RESOURCES

### Documentation
- `README.md` - Main documentation
- `SYSTEM_READY.md` - Readiness checklist
- `docs/QUICK_START.md` - Quick reference
- `docs/RFC-001.md` - Full specification

### Key Files
- `dashboard.py` - Main application
- `bet_tracker.py` - Bet tracking logic
- `ev_calculator.py` - EV calculations
- `game_data_fetch.py` - Data fetching

---

## ✅ FINAL CHECKLIST

Before Opening Night:
- [x] Dashboard tested and working
- [x] Bet tracking system clean
- [x] Opening Night games correct (Oct 22)
- [x] All 2024-25 data removed
- [x] File structure organized
- [x] Documentation complete

Ready to Start:
- [ ] Wait 3-4 weeks (mid-November)
- [ ] Run `game_data_fetch.py` weekly
- [ ] Track model accuracy
- [ ] Start with small bets
- [ ] Build confidence
- [ ] Scale up gradually

---

## 🎉 YOU'RE ALL SET!

Your NBA betting system is:
- ✅ **Fully functional** - All features working
- ✅ **Clean** - No test data
- ✅ **Organized** - Simple structure
- ✅ **Ready** - Opening Night in 10 days!

**Good luck and bet responsibly!** 🏀💰

---

*Last Updated: October 12, 2025*
*Opening Night: October 22, 2025*
*Season: 2025-26 NBA*



