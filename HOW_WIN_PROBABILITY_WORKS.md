# 🎯 HOW WE CALCULATE A TEAM'S CHANCE TO WIN

**Last Updated:** October 12, 2025

---

## 🔍 CURRENT STATUS (IMPORTANT!)

### ⚠️ Right Now: Placeholder Probability

In the dashboard, you'll see this line:
```python
home_win_prob = 0.55  # Placeholder
```

**This means:**
- Currently using a **FIXED 55% probability** for home team
- This is a **PLACEHOLDER** for testing
- **NOT using the actual ML model yet**

**Why?**
- The trained model exists (`models/nba_model.pkl`)
- But it's not connected to the dashboard yet
- For now, it uses a simple 55/45 split (home advantage)

---

## 🎓 HOW IT SHOULD WORK (Full System)

### Method 1: Elo Rating System ⭐ (Simple & Effective)

**What is Elo?**
- Rating system (like chess)
- Each team has a number (e.g., 1500)
- Higher number = better team
- Updates after each game

**How It Calculates Win Probability:**

1. **Get Team Ratings**
   - Home team: 1600 Elo
   - Away team: 1500 Elo
   - Home advantage: +100 points

2. **Calculate Rating Difference**
   - Adjusted home rating: 1600 + 100 = 1700
   - Away rating: 1500
   - Difference: 1700 - 1500 = 200

3. **Convert to Probability**
   ```
   Win Probability = 1 / (1 + 10^(-difference/400))
   ```
   
   Example:
   - Difference: 200
   - Probability: 1 / (1 + 10^(-200/400))
   - Probability: 1 / (1 + 10^(-0.5))
   - Probability: 1 / (1 + 0.316)
   - **Probability: 76%**

**Advantages:**
- ✅ Simple and fast
- ✅ Updates automatically after games
- ✅ Proven system (used in many sports)
- ✅ Works well with limited data

---

### Method 2: Machine Learning Model 🤖 (Complex & Accurate)

**What It Uses:**
- Trained logistic regression model
- Multiple team statistics
- Historical game data

**Features (28 total):**

**Team Offensive Stats:**
- Points per game (PPG)
- Field goal % (FG_PCT)
- 3-point % (FG3_PCT)
- Free throw % (FT_PCT)
- Assists per game (AST)
- Offensive rating (OFF_RATING)

**Team Defensive Stats:**
- Opponent points per game (OPP_PPG)
- Defensive rating (DEF_RATING)
- Steals per game (STL)
- Blocks per game (BLK)

**Team Performance:**
- Win percentage (WIN_PCT)
- Net rating (NET_RATING)
- Pace (PACE)
- True shooting % (TS_PCT)

**Matchup Factors:**
- Home court advantage
- Rest days
- Recent form (last 10 games)
- Head-to-head record

**How It Works:**

1. **Gather Features**
   ```python
   features = {
       'home_ppg': 115.2,
       'home_fg_pct': 0.478,
       'home_def_rating': 108.5,
       'away_ppg': 110.3,
       'away_fg_pct': 0.465,
       'away_def_rating': 112.1,
       # ... 22 more features
   }
   ```

2. **Scale Features**
   - Normalize all values to same range
   - Prevents one feature from dominating

3. **Run Through Model**
   ```python
   X = prepare_features(features)
   X_scaled = scaler.transform(X)
   probability = model.predict_proba(X_scaled)
   ```

4. **Get Probability**
   - Model outputs: 0.62 (62% chance home team wins)
   - Away team: 1 - 0.62 = 0.38 (38%)

**Advantages:**
- ✅ More accurate (uses all available data)
- ✅ Considers many factors
- ✅ Learns from historical patterns
- ✅ Better for mid/late season

**Disadvantages:**
- ❌ Needs lots of data (20+ games per team)
- ❌ Less accurate early season
- ❌ More complex to update

---

## 📊 COMPARISON: Elo vs ML Model

| Feature | Elo Rating | ML Model |
|---------|-----------|----------|
| **Simplicity** | ⭐⭐⭐⭐⭐ Very simple | ⭐⭐ Complex |
| **Speed** | ⭐⭐⭐⭐⭐ Instant | ⭐⭐⭐⭐ Fast |
| **Data Needed** | ⭐⭐⭐ Minimal | ⭐ Lots |
| **Early Season** | ⭐⭐⭐⭐ Good | ⭐⭐ Poor |
| **Mid Season** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Late Season** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Accuracy** | ⭐⭐⭐ 65-68% | ⭐⭐⭐⭐ 68-72% |

---

## 🎯 WHAT YOUR SYSTEM USES

### Current Setup (Dashboard)

**Right Now:**
```python
home_win_prob = 0.55  # Fixed placeholder
```

**What This Means:**
- Home team: 55% chance to win
- Away team: 45% chance to win
- Same for EVERY game
- Just for testing the system

### Available But Not Connected

**You Have:**
1. **Trained ML Model** (`models/nba_model.pkl`)
   - Logistic regression
   - 28 features
   - Trained on historical data

2. **Elo System** (`archive/elo_ratings.py`)
   - Rating for each team
   - Updates after games
   - Calculates probabilities

**To Use Them:**
- Need to connect model to dashboard
- Need to load team features
- Need to update after each game

---

## 🔧 HOW TO IMPROVE YOUR SYSTEM

### Option 1: Connect Elo System (Easier)

**Steps:**
1. Load Elo ratings for all teams
2. Calculate probability using Elo formula
3. Update ratings after each game

**Code Example:**
```python
from archive.elo_ratings import EloRatingSystem

elo = EloRatingSystem()
prediction = elo.predict_game('Lakers', 'Warriors')
home_win_prob = prediction['home_win_prob']  # e.g., 0.58
```

### Option 2: Connect ML Model (Better)

**Steps:**
1. Load trained model
2. Gather team statistics
3. Calculate features
4. Get prediction

**Code Example:**
```python
import pickle

# Load model
with open('models/nba_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model']
scaler = model_data['scaler']

# Get features
features = get_team_features('Lakers', 'Warriors')

# Predict
X_scaled = scaler.transform([features])
home_win_prob = model.predict_proba(X_scaled)[0, 1]
```

### Option 3: Hybrid Approach (Best)

**Combine Both:**
- Use Elo for early season (games 1-20)
- Use ML model for mid/late season (games 20+)
- Blend both predictions

**Example:**
```python
if games_played < 20:
    # Use Elo
    prob = elo.predict_game(home, away)['home_win_prob']
else:
    # Use ML model
    prob = model.predict_proba(features)[0, 1]
```

---

## 📈 EXAMPLE CALCULATION

### Scenario: Lakers vs Warriors

**Using Elo:**
1. Lakers Elo: 1580
2. Warriors Elo: 1520
3. Home advantage: +100
4. Adjusted Lakers: 1580 + 100 = 1680
5. Difference: 1680 - 1520 = 160
6. Probability: 1 / (1 + 10^(-160/400)) = 71%

**Using ML Model:**
1. Lakers stats: PPG=118, FG%=48%, DEF=110
2. Warriors stats: PPG=115, FG%=47%, DEF=112
3. Features: [118, 0.48, 110, 115, 0.47, 112, ...]
4. Model prediction: 68%

**Hybrid (Average):**
- (71% + 68%) / 2 = **69.5% Lakers win**

---

## 💡 KEY TAKEAWAYS

### For Your System:

1. **Currently:** Using 55% placeholder
   - Good for testing
   - Not accurate for real betting

2. **You Have:** Trained model available
   - In `models/nba_model.pkl`
   - Just needs to be connected

3. **Recommendation:** 
   - Start with Elo (simpler)
   - Add ML model later (better)
   - Use hybrid approach (best)

4. **When to Use Each:**
   - **Early season:** Elo or 55/45 split
   - **Mid season:** ML model
   - **Late season:** ML model or hybrid

### For Betting:

1. **Don't trust 55% placeholder** for real money
2. **Wait for model to have data** (3-4 weeks)
3. **Start small** when testing predictions
4. **Track accuracy** to validate system

---

## 🎓 FURTHER READING

### In Your Codebase:

- `archive/elo_ratings.py` - Elo system
- `archive/model_training.py` - ML model training
- `models/nba_model.pkl` - Trained model
- `ev_calculator.py` - EV calculations

### Concepts:

- **Elo Rating:** Chess-style rating system
- **Logistic Regression:** ML classification model
- **Feature Engineering:** Creating useful inputs
- **Probability Calibration:** Adjusting predictions

---

## ✅ SUMMARY

**How We Calculate Win Probability:**

1. **Current (Placeholder):** 55% home, 45% away
2. **Elo Method:** Based on team ratings
3. **ML Method:** Based on 28 team statistics
4. **Best:** Combine both methods

**For Real Betting:**
- Connect Elo or ML model
- Wait for enough games (20+)
- Validate predictions
- Start small

**Remember:** The prediction is just a probability, not a guarantee!

---

*Last Updated: October 12, 2025*
