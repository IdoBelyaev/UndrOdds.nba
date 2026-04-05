# NBA Game Winner Prediction

A machine learning project to predict NBA game winners using team statistics and basketball analytics.

## 🎯 **Project Overview**
Building a machine learning model to predict NBA game winners for resume portfolio. Focus on feature analysis and data collection.

## 🚀 **Getting Started**

### Prerequisites
- Python 3.7+
- Required packages (see requirements.txt)

### Installation
```bash
git clone <repository-url>
cd NBA_winners
pip install -r requirements.txt
```

### Usage
```bash
python main.py
```

## 🏀 **Basketball Feature Analysis**

### **Core Basketball Principles for Prediction:**

#### **1. OFFENSIVE EFFICIENCY (HIGH Importance)**
- **Description**: How well a team scores
- **Key Metrics**:
  - Points per game (PTS)
  - Field goal percentage (FG_PCT)
  - Three-point percentage (FG3_PCT)
  - Free throw percentage (FT_PCT)
  - Assists per game (AST)
  - Turnovers per game (TOV) - lower is better
- **Why Important**: You need to score to win

#### **2. DEFENSIVE EFFICIENCY (HIGH Importance)**
- **Description**: How well a team prevents scoring
- **Key Metrics**:
  - Opponent points per game (OPP_PTS) - lower is better
  - Steals per game (STL)
  - Blocks per game (BLK)
  - Defensive rebounds (DREB)
  - Opponent field goal percentage - lower is better
- **Why Important**: Defense wins championships

#### **3. PACE & POSSESSIONS (HIGH Importance)**
- **Description**: Game tempo and efficiency
- **Key Metrics**:
  - Pace (possessions per game)
  - Offensive rating (points per 100 possessions)
  - Defensive rating (opponent points per 100 possessions)
  - Net rating (offensive - defensive rating)
- **Why Important**: Efficiency matters more than volume

#### **4. REBOUNDING (MEDIUM-HIGH Importance)**
- **Description**: Controlling possession
- **Key Metrics**:
  - Total rebounds per game (REB)
  - Offensive rebounds (OREB)
  - Defensive rebounds (DREB)
  - Rebound percentage
- **Why Important**: More possessions = more opportunities

#### **5. CONTEXTUAL FACTORS (MEDIUM Importance)**
- **Description**: Game situation factors
- **Key Metrics**:
  - Home vs Away record
  - Days of rest
  - Back-to-back games
  - Strength of schedule
  - Recent form (last 10 games)
  - Head-to-head history
- **Why Important**: Can swing close games

## 📊 **Data Analysis Results**

### **Feature Correlations with Win Percentage:**
1. **Point Differential**: 0.361 (Most Important)
2. **Field Goals Made**: 0.323
3. **Points per Game**: 0.275
4. **Free Throw %**: 0.230
5. **Field Goals Attempted**: 0.164
6. **Three-Point %**: 0.126
7. **Rebounds**: 0.066
8. **Field Goal %**: -0.010
9. **Blocks**: -0.015
10. **Steals**: -0.042
11. **Turnovers**: -0.207
12. **Opponent Points**: -0.273
13. **Assists**: -0.323

### **Key Insights:**
- **Point Differential is King**: The difference between points scored and allowed is the strongest predictor
- **Volume Matters**: Teams that make more field goals tend to win more
- **Defense Matters**: Lower opponent points correlates with wins
- **Efficiency vs Volume**: Need both raw scoring ability AND efficiency metrics

## 🎯 **Prediction Strategy**

1. **Focus on EFFICIENCY metrics over raw volume**
2. **Balance OFFENSIVE and DEFENSIVE capabilities**
3. **Consider CONTEXTUAL factors for edge cases**
4. **Use RECENT FORM (last 10-15 games) over season totals**
5. **Account for HOME COURT ADVANTAGE (~3-4 points)**

## 🛠 **Technical Implementation**

### **Project Structure:**
```
NBA_winners/
├── main.py              # Main analysis script
├── requirements.txt     # Python dependencies
├── data/               # Data storage
│   └── team_season_stats.csv
└── README.md           # This file
```

### **Key Functions in main.py:**
- `analyze_basketball_features()` - Basketball knowledge analysis
- `get_team_season_stats()` - Data collection from NBA API
- `analyze_features()` - Statistical correlation analysis
- `create_sample_data()` - Fallback data for testing

### **Dependencies:**
- `requests` - API calls
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `nba_api` - NBA data access

## 🚀 **Next Steps & Roadmap**

### **Phase 1: Data Collection (Current)**
- [x] Basic team statistics collection
- [x] Feature correlation analysis
- [ ] Fix NBA API integration for real-time data
- [ ] Collect opponent-specific matchup data

### **Phase 2: Feature Engineering**
- [ ] Add recent form metrics (last 10-15 games)
- [ ] Implement home/away performance splits
- [ ] Add rest day and back-to-back game factors
- [ ] Create advanced efficiency metrics

### **Phase 3: Model Development**
- [ ] Build baseline logistic regression model
- [ ] Implement Random Forest classifier
- [ ] Add XGBoost for improved performance
- [ ] Cross-validation and hyperparameter tuning

### **Feature Engineering Ideas:**
- **Rolling Averages**: 5-game, 10-game, 20-game averages
- **Trend Analysis**: Improving/declining performance indicators
- **Matchup-Specific Metrics**: How teams perform against similar opponents
- **Situational Performance**: Performance in close games, blowouts, etc.

### **Model Development Strategy:**
1. **Start Simple**: Logistic regression with key features
2. **Add Complexity**: Random Forest, XGBoost
3. **Feature Selection**: Use correlation analysis and domain knowledge
4. **Validation**: Cross-validation with recent seasons
5. **Deployment**: Simple web interface or API

## 📊 **Results & Performance**

### **Current Model Performance:**
- **Target Accuracy**: >60% (better than random)
- **Key Features**: Point differential, field goals made, points per game
- **Data Source**: NBA Stats API with fallback to sample data

### **Feature Importance Rankings:**
1. Point Differential: 0.361 correlation
2. Field Goals Made: 0.323 correlation  
3. Points per Game: 0.275 correlation
4. Free Throw %: 0.230 correlation

## 📈 **Success Metrics**
- **Accuracy**: Target >60% (better than random)
- **Precision/Recall**: Balance for different prediction scenarios
- **Feature Importance**: Validate against basketball knowledge
- **Model Interpretability**: Explainable predictions for resume

## 🤝 **Contributing**
This is a portfolio project, but suggestions and improvements are welcome!

## 📄 **License**
This project is for educational and portfolio purposes.

## 🔗 **Resources & APIs**
- **NBA Stats API**: https://stats.nba.com/stats/
- **nba_api Python Package**: https://github.com/swar/nba_api
- **Alternative APIs**: ESPN, Basketball Reference

## 💡 **Key Learnings**
1. **Domain Knowledge is Critical**: Basketball understanding guides feature selection
2. **Point Differential Dominates**: Simple metrics often work best
3. **Context Matters**: Home/away, rest, recent form all impact outcomes
4. **Efficiency > Volume**: Quality of possessions matters more than quantity
5. **Defense Wins**: Preventing points is as important as scoring them

---
*This document captures the complete analysis and context for the NBA Game Winner Prediction project.*
