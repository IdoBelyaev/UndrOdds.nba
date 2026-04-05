"""
NBA Bet Selector Dashboard - M4 Redesign
=========================================

4 Tabs:
1. Picks - Enter date and lines, get recommendations
2. Results - Enter game results, calculate profit/loss
3. Track - Table view of all bets
4. Visuals - Charts and graphs

M4: Dashboard Improvements
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import pickle
import numpy as np
from datetime import datetime, date, timedelta
from pathlib import Path
from bet_tracker import BetTracker
from ev_calculator import EVCalculator
from archive.elo_ratings import EloRatingSystem

# NBA Team Logo URLs (from NBA.com)
TEAM_LOGOS = {
    'Atlanta Hawks': 'https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg',
    'Boston Celtics': 'https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg',
    'Brooklyn Nets': 'https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg',
    'Charlotte Hornets': 'https://cdn.nba.com/logos/nba/1610612766/primary/L/logo.svg',
    'Chicago Bulls': 'https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg',
    'Cleveland Cavaliers': 'https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg',
    'Dallas Mavericks': 'https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg',
    'Denver Nuggets': 'https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg',
    'Detroit Pistons': 'https://cdn.nba.com/logos/nba/1610612765/primary/L/logo.svg',
    'Golden State Warriors': 'https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg',
    'Houston Rockets': 'https://cdn.nba.com/logos/nba/1610612745/primary/L/logo.svg',
    'Indiana Pacers': 'https://cdn.nba.com/logos/nba/1610612754/primary/L/logo.svg',
    'LA Clippers': 'https://cdn.nba.com/logos/nba/1610612746/primary/L/logo.svg',
    'Los Angeles Lakers': 'https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg',
    'Memphis Grizzlies': 'https://cdn.nba.com/logos/nba/1610612763/primary/L/logo.svg',
    'Miami Heat': 'https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg',
    'Milwaukee Bucks': 'https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg',
    'Minnesota Timberwolves': 'https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg',
    'New Orleans Pelicans': 'https://cdn.nba.com/logos/nba/1610612740/primary/L/logo.svg',
    'New York Knicks': 'https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg',
    'Oklahoma City Thunder': 'https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg',
    'Orlando Magic': 'https://cdn.nba.com/logos/nba/1610612753/primary/L/logo.svg',
    'Philadelphia 76ers': 'https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg',
    'Phoenix Suns': 'https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg',
    'Portland Trail Blazers': 'https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg',
    'Sacramento Kings': 'https://cdn.nba.com/logos/nba/1610612758/primary/L/logo.svg',
    'San Antonio Spurs': 'https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg',
    'Toronto Raptors': 'https://cdn.nba.com/logos/nba/1610612761/primary/L/logo.svg',
    'Utah Jazz': 'https://cdn.nba.com/logos/nba/1610612762/primary/L/logo.svg',
    'Washington Wizards': 'https://cdn.nba.com/logos/nba/1610612764/primary/L/logo.svg'
}

def get_team_logo(team_name: str) -> str:
    """Get logo URL for team"""
    return TEAM_LOGOS.get(team_name, "")

@st.cache_data
def get_team_record(team_name: str) -> dict:
    """Get team record (wins, losses) from team data or game data"""
    # Handle team name variations
    name_mappings = {
        'LA Clippers': 'Los Angeles Clippers',
        'Los Angeles Clippers': 'LA Clippers'
    }
    
    # Try to get from team data first
    try:
        with open('data/nba_team_data.json', 'r') as f:
            data = json.load(f)
            for team in data.get('teams', []):
                team_data_name = team.get('team_name', '')
                # Check exact match or mapped name
                if team_data_name == team_name or team_data_name == name_mappings.get(team_name):
                    wins = team.get('wins', 0)
                    losses = team.get('losses', 0)
                    # Only return if record is valid (not 0-0 with no stats)
                    if wins > 0 or losses > 0:
                        return {'wins': wins, 'losses': losses, 'record': f"{wins}-{losses}"}
    except (FileNotFoundError, KeyError, Exception):
        pass
    
    # Fallback: Calculate from game data if team data doesn't have it
    try:
        with open('data/nba_game_data.json', 'r') as f:
            game_data = json.load(f)
            wins = 0
            losses = 0
            
            for game in game_data.get('games', []):
                # Only count 2025-26 season games that have been played
                if game.get('season') != '22025':
                    continue
                if game.get('home_score', 0) == 0 and game.get('away_score', 0) == 0:
                    continue
                
                # Check if this team is home or away
                if game.get('home_team') == team_name or game.get('home_team') == name_mappings.get(team_name):
                    home_win = game.get('home_win', 1 if game.get('home_score', 0) > game.get('away_score', 0) else 0)
                    if home_win:
                        wins += 1
                    else:
                        losses += 1
                elif game.get('away_team') == team_name or game.get('away_team') == name_mappings.get(team_name):
                    home_win = game.get('home_win', 1 if game.get('home_score', 0) > game.get('away_score', 0) else 0)
                    if not home_win:
                        wins += 1
                    else:
                        losses += 1
            
            if wins > 0 or losses > 0:
                return {'wins': wins, 'losses': losses, 'record': f"{wins}-{losses}"}
    except (FileNotFoundError, KeyError, Exception):
        pass
    
    return {'wins': 0, 'losses': 0, 'record': '0-0'}

# Page config
st.set_page_config(
    page_title="NBA Bet Selector",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'bet_tracker' not in st.session_state:
    st.session_state.bet_tracker = BetTracker('bet_history.json')

if 'current_bankroll' not in st.session_state:
    st.session_state.current_bankroll = 1000.0

if 'odds_input' not in st.session_state:
    st.session_state.odds_input = {}

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B35;
    }
    .positive-ev {
        color: #28a745;
        font-weight: bold;
    }
    .negative-ev {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def load_model():
    """Load calibrated model"""
    try:
        with open('nba_model_calibrated.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


def load_games_for_date(selected_date):
    """Load NBA games for a specific date"""
    try:
        with open('data/nba_game_data.json', 'r') as f:
            data = json.load(f)
            games = data['games']
        
        # Filter games for the selected date
        date_str = selected_date.strftime('%Y-%m-%d')
        today = datetime.now().date()
        
        # Filter games for the selected date only
        date_games = [g for g in games if g['date'].startswith(date_str)]
        
        # If no games found for the selected date, try to fetch future games
        if not date_games and selected_date >= datetime.now().date():
            try:
                from future_games_fetcher import FutureGamesFetcher
                fetcher = FutureGamesFetcher()
                future_games = fetcher.fetch_specific_date(date_str)
                if future_games:
                    # Reload the data file to get the new games
                    with open('data/nba_game_data.json', 'r') as f:
                        updated_data = json.load(f)
                        updated_games = updated_data['games']
                    # Filter for the selected date again
                    date_games = [g for g in updated_games if g['date'].startswith(date_str)]
            except Exception as e:
                print(f"Error fetching future games: {e}")
        
        return date_games
        
    except FileNotFoundError:
        return []


@st.cache_resource
def load_elo_system():
    """Load existing Elo ratings from 2025-26 season"""
    elo = EloRatingSystem()
    
    # Load current season ratings (2025-26)
    try:
        # First try current season ratings
        with open('data/elo_ratings.json', 'r') as f:
            data = json.load(f)
            if 'ratings' in data:
                elo.ratings = data['ratings']
                return elo
    except FileNotFoundError:
        pass
    
    # Fallback to archive if current season doesn't exist
    try:
        with open('data/data_archive/elo_ratings.json', 'r') as f:
            data = json.load(f)
            if 'ratings' in data:
                elo.ratings = data['ratings']
                return elo
    except FileNotFoundError:
        pass
    
    # Fallback: initialize all teams at 1500 if file not found
    nba_teams = [
        'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets',
        'Charlotte Hornets', 'Chicago Bulls', 'Cleveland Cavaliers',
        'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons',
        'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
        'LA Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies',
        'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves',
        'New Orleans Pelicans', 'New York Knicks', 'Oklahoma City Thunder',
        'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
        'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs',
        'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'
    ]
    elo.initialize_teams(nba_teams)
    return elo


def main():
    """Main dashboard"""
    
    # Load Elo system (cached for performance)
    elo = load_elo_system()
    
    # Header
    st.markdown('<h1 class="main-header">🏀 NBA Bet Selector</h1>', unsafe_allow_html=True)
    st.markdown("### Your Complete Betting System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Bankroll
        st.subheader("💰 Bankroll")
        st.session_state.current_bankroll = st.number_input(
            "Current Bankroll ($)",
            min_value=0.0,
            max_value=100000.0,
            value=float(st.session_state.current_bankroll),
            step=100.0
        )
        
        flat_bet = st.number_input(
            "Flat Bet Amount ($)",
            min_value=1.0,
            max_value=1000.0,
            value=20.0,
            step=1.0
        )
        
        bet_pct = (flat_bet / st.session_state.current_bankroll) * 100 if st.session_state.current_bankroll > 0 else 0
        st.metric("Bet as % of Bankroll", f"{bet_pct:.1f}%")
        
        st.markdown("---")
        
        # Model settings
        st.subheader("🎯 Model Settings")
        min_ev = st.slider(
            "Min EV Threshold (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=1.0
        ) / 100
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        stats = st.session_state.bet_tracker.get_summary_stats()
        st.metric("Total Bets", stats['total_bets'])
        st.metric("Win Rate", f"{stats['win_rate']:.1%}")
        st.metric("Total Profit", f"${stats['total_profit']:+,.2f}")
        st.metric("ROI", f"{stats['roi']:+.1f}%")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Picks",
        "📊 Results",
        "📈 Track",
        "📉 Visuals"
    ])
    
    # ========================================================================
    # TAB 1: PICKS - Enter date and lines, get recommendations
    # ========================================================================
    with tab1:
        st.header("🎯 Today's Picks")
        st.markdown("Enter date and moneylines to get betting recommendations")
        
        # Date selector
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_date = st.date_input(
                "Select Game Date",
                value=date.today(),
                format="DD/MM/YYYY"
            )
        
        with col2:
            if st.button("🔄 Fetch Games", use_container_width=True):
                games = load_games_for_date(selected_date)
                st.session_state.games_for_date = games
                st.success(f"✅ Found {len(games)} games")
        
        st.markdown("---")
        
        # Display games and input odds
        if 'games_for_date' in st.session_state and st.session_state.games_for_date:
            st.subheader(f"📅 Games on {selected_date.strftime('%B %d, %Y')}")
            
            # Load model
            model_data = load_model()
            ev_calc = EVCalculator()
            
            recommendations = []
            
            for i, game in enumerate(st.session_state.games_for_date):
                # Simple game display with Pacific Time and team logos
                # Always show 0-0 for betting purposes (no live scores)
                away_score = 0
                home_score = 0
                
                # No game times displayed
                
                with st.expander(f"🏀 {game['away_team']} @ {game['home_team']}", expanded=True):
                    
                    # Team logos and names row
                    logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
                    
                    with logo_col1:
                        home_logo = get_team_logo(game['home_team'])
                        if home_logo:
                            st.markdown(f"<div style='text-align: center;'><img src='{home_logo}' width='80'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 16px; font-weight: bold; margin-top: 10px;'>{game['home_team']}</div>", unsafe_allow_html=True)
                        home_record = get_team_record(game['home_team'])
                        st.markdown(f"<div style='text-align: center; font-size: 14px; color: #888; margin-top: 5px;'>{home_record['record']}</div>", unsafe_allow_html=True)
                    
                    with logo_col2:
                        st.markdown("<div style='text-align: center; padding-top: 30px;'><h2>VS</h2></div>", unsafe_allow_html=True)
                    
                    with logo_col3:
                        away_logo = get_team_logo(game['away_team'])
                        if away_logo:
                            st.markdown(f"<div style='text-align: center;'><img src='{away_logo}' width='80'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; font-size: 16px; font-weight: bold; margin-top: 10px;'>{game['away_team']}</div>", unsafe_allow_html=True)
                        away_record = get_team_record(game['away_team'])
                        st.markdown(f"<div style='text-align: center; font-size: 14px; color: #888; margin-top: 5px;'>{away_record['record']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Odds input row
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        home_ml = st.number_input(
                            f"{game['home_team']} Moneyline",
                            min_value=-1000,
                            max_value=1000,
                            value=0,
                            step=5,
                            key=f"home_ml_{i}"
                        )
                    
                    with col2:
                        away_ml = st.number_input(
                            f"{game['away_team']} Moneyline",
                            min_value=-1000,
                            max_value=1000,
                            value=0,
                            step=5,
                            key=f"away_ml_{i}"
                        )
                    
                    with col3:
                        st.markdown("**Actions**")
                        
                    # Store EV calculation results in session state
                    ev_key = f"ev_results_{i}"
                    if ev_key not in st.session_state:
                        st.session_state[ev_key] = None
                        
                    if st.button("Calculate EV", key=f"calc_{i}"):
                        if home_ml != 0 and away_ml != 0:
                            # Get Elo prediction
                            try:
                                prediction = elo.predict_game(game['home_team'], game['away_team'])
                                home_win_prob = prediction['home_win_prob']
                            except Exception as e:
                                # Fallback to 50/50 if Elo fails
                                st.warning(f"⚠️ Elo prediction failed: {e}. Using 50/50.")
                                home_win_prob = 0.50
                            
                            # Calculate EV
                            home_ev = ev_calc.calculate_ev(home_win_prob, home_ml)
                            away_ev = ev_calc.calculate_ev(1 - home_win_prob, away_ml)
                            
                            # Store results in session state
                            st.session_state[ev_key] = {
                                'home_ev': home_ev,
                                'away_ev': away_ev,
                                'home_win_prob': home_win_prob,
                                'home_ml': home_ml,
                                'away_ml': away_ml
                            }
                        else:
                            st.error("❌ Please enter both moneyline odds")
                    
                    # Display EV results if they exist
                    if st.session_state[ev_key] is not None:
                        results = st.session_state[ev_key]
                        home_ev = results['home_ev']
                        away_ev = results['away_ev']
                        home_win_prob = results['home_win_prob']
                        home_ml = results['home_ml']
                        away_ml = results['away_ml']
                        
                        # Calculate implied probabilities from odds
                        home_implied_prob = ev_calc.implied_probability(home_ml)
                        away_implied_prob = ev_calc.implied_probability(away_ml)
                        
                        # Show comprehensive analysis
                        st.markdown("### 📊 Analysis")
                        
                        # Create comparison table
                        analysis_data = {
                            'Team': [game['home_team'], game['away_team']],
                            'Sportsbook Odds': [f"{home_ml:+d}", f"{away_ml:+d}"],
                            'Sportsbook Prob': [f"{home_implied_prob:.1%}", f"{away_implied_prob:.1%}"],
                            'Model Prob': [f"{home_win_prob:.1%}", f"{1-home_win_prob:.1%}"],
                            'EV': [f"{home_ev['ev_percent']:+.1f}%", f"{away_ev['ev_percent']:+.1f}%"],
                            'Decision': ['✅ BET' if home_ev['ev_percent'] > min_ev * 100 else '❌ NO BET',
                                       '✅ BET' if away_ev['ev_percent'] > min_ev * 100 else '❌ NO BET']
                        }
                        
                        analysis_df = pd.DataFrame(analysis_data)
                        st.dataframe(analysis_df, use_container_width=True, hide_index=True)
                        
                        # Show reasoning
                        st.markdown("### 🧠 Reasoning")
                        
                        # Determine best bet for this specific game
                        game_best_bet = None
                        game_best_ev = 0
                        if home_ev['ev_percent'] > min_ev * 100:
                            game_best_bet = game['home_team']
                            game_best_ev = home_ev['ev_percent']
                        if away_ev['ev_percent'] > min_ev * 100 and away_ev['ev_percent'] > game_best_ev:
                            game_best_bet = game['away_team']
                            game_best_ev = away_ev['ev_percent']
                        
                        if game_best_bet:
                            if game_best_bet == game['home_team']:
                                model_prob = home_win_prob
                                sportsbook_prob = home_implied_prob
                                odds = home_ml
                            else:
                                model_prob = 1 - home_win_prob
                                sportsbook_prob = away_implied_prob
                                odds = away_ml
                            
                            edge = (model_prob - sportsbook_prob) * 100
                            
                            # Calculate potential winnings
                            if odds > 0:
                                potential_winnings = flat_bet * (odds / 100)
                                total_return = flat_bet + potential_winnings
                            else:
                                potential_winnings = flat_bet * (100 / abs(odds))
                                total_return = flat_bet + potential_winnings
                            
                            st.success(f"**✅ RECOMMEND: {game_best_bet}**")
                            st.markdown(f"""
                            **Why bet {game_best_bet}?**
                            - **Our model says:** {game_best_bet} has a {model_prob:.1%} chance to win
                            - **Sportsbook says:** {game_best_bet} has a {sportsbook_prob:.1%} chance to win  
                            - **Edge:** {edge:+.1f} percentage points in our favor
                            - **Expected Value:** {game_best_ev:+.1f}% per bet
                            - **Odds:** {odds:+d} (good value)
                            
                            **💰 Betting Details:**
                            - **Bet Amount:** ${flat_bet:.2f}
                            - **Potential Winnings:** +${potential_winnings:.2f}
                            - **Total Return:** ${total_return:.2f} (if win)
                            - **Expected Profit:** +${(game_best_ev/100) * flat_bet:.2f}
                            """)
                        else:
                            # Calculate expected losses for both teams
                            home_expected_loss = (home_ev['ev_percent'] / 100) * flat_bet
                            away_expected_loss = (away_ev['ev_percent'] / 100) * flat_bet
                            
                            st.error("**❌ DO NOT BET**")
                            st.markdown(f"""
                            **Why not bet?**
                            - **Our model vs Sportsbook:** Both teams' odds are too close to our predictions
                            - **No edge found:** Neither team offers significant value
                            - **Risk vs Reward:** EV below {min_ev*100:.0f}% threshold
                            - **Recommendation:** Wait for better odds or skip this game
                            
                            **💰 Betting Details:**
                            - **Bet Amount:** ${flat_bet:.2f}
                            - **{game['home_team']} EV:** {home_ev['ev_percent']:+.1f}% (Expected Loss: ${home_expected_loss:+.2f})
                            - **{game['away_team']} EV:** {away_ev['ev_percent']:+.1f}% (Expected Loss: ${away_expected_loss:+.2f})
                            - **Recommendation:** Skip this game
                            """)
                        
                        # Add "Place Bet" button if there's a positive EV bet (outside the Calculate EV block)
                        if game_best_bet:
                            if st.button(f"🎯 Place Bet on {game_best_bet}", key=f"place_bet_{i}_{game_best_bet}"):
                                # Log the bet
                                bet_id = st.session_state.bet_tracker.log_bet(
                                    date=selected_date.strftime('%Y-%m-%d'),
                                    game=f"{game['home_team']} vs {game['away_team']}",
                                    team=game_best_bet,
                                    opponent=game['away_team'] if game_best_bet == game['home_team'] else game['home_team'],
                                    moneyline=odds,
                                    bet_amount=flat_bet,
                                    win_probability=model_prob,
                                    ev_percent=game_best_ev,
                                    bankroll_before=st.session_state.current_bankroll
                                )
                                st.success(f"✅ Bet placed! Bet ID: {bet_id}")
                                st.info(f"💡 Go to Results tab to track this bet's outcome")
                                st.rerun()
            
        else:
            st.info("👆 Select a date and click 'Fetch Games' to get started")
    
    # ========================================================================
    # TAB 2: RESULTS - Enter game results and calculate profit/loss
    # ========================================================================
    with tab2:
        st.header("📊 Results")
        st.markdown("Enter game results to calculate profit/loss")
        
        # Get pending bets
        all_bets = st.session_state.bet_tracker.get_bets_dataframe()
        
        if not all_bets.empty:
            pending_bets = all_bets[all_bets['status'] == 'pending']
            
            if not pending_bets.empty:
                st.subheader(f"⏳ Pending Bets ({len(pending_bets)})")
                
                for idx, bet in pending_bets.iterrows():
                    with st.expander(f"🏀 {bet['game']}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Pick:** {bet['team']}")
                            st.markdown(f"**Odds:** {bet['moneyline']:+d}")
                            st.markdown(f"**Bet:** ${bet['bet_amount']:.2f}")
                        
                        with col2:
                            result = st.radio(
                                "Result",
                                options=["Pending", "Won", "Lost"],
                                key=f"result_{bet['bet_id']}"
                            )
                        
                        with col3:
                            if result != "Pending":
                                won = (result == "Won")
                                
                                # Calculate profit
                                if won:
                                    if bet['moneyline'] > 0:
                                        profit = bet['bet_amount'] * (bet['moneyline'] / 100)
                                    else:
                                        profit = bet['bet_amount'] * (100 / abs(bet['moneyline']))
                                else:
                                    profit = -bet['bet_amount']
                                
                                st.metric("Profit/Loss", f"${profit:+.2f}")
                                
                                if st.button("💾 Save Result", key=f"save_{bet['bet_id']}"):
                                    new_bankroll = st.session_state.current_bankroll + profit
                                    st.session_state.bet_tracker.update_bet_result(
                                        bet['bet_id'],
                                        won,
                                        new_bankroll
                                    )
                                    st.session_state.current_bankroll = new_bankroll
                                    st.success(f"✅ Result saved! New bankroll: ${new_bankroll:.2f}")
                                    st.rerun()
                            
                            # Delete button for pending bets
                            if result == "Pending":
                                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                                if st.button("🗑️ Delete Bet", key=f"delete_{bet['bet_id']}", type="secondary"):
                                    # Refund the bet amount to bankroll
                                    st.session_state.current_bankroll += bet['bet_amount']
                                    # Delete the bet
                                    deleted = st.session_state.bet_tracker.delete_bet(bet['bet_id'])
                                    if deleted:
                                        st.success(f"✅ Bet deleted! Refunded ${bet['bet_amount']:.2f} to bankroll.")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete bet.")
            else:
                st.info("✅ No pending bets")
        else:
            st.info("📝 No bets logged yet. Go to Picks tab to start betting!")
    
    # ========================================================================
    # TAB 3: TRACK - Table view of all bets
    # ========================================================================
    with tab3:
        st.header("📈 Track")
        st.markdown("Complete bet history")
        
        all_bets = st.session_state.bet_tracker.get_bets_dataframe()
        
        if not all_bets.empty:
            # Prepare display dataframe
            display_df = pd.DataFrame({
                'Date': pd.to_datetime(all_bets['date']).dt.strftime('%m/%d/%Y'),
                'Game': all_bets['game'],
                'Pick': all_bets['team'],
                'Odds': all_bets['moneyline'],
                'Amount': all_bets['bet_amount'].apply(lambda x: f"${x:.2f}"),
                'Result': all_bets['status'].str.upper(),
                'Return': all_bets['profit'].apply(lambda x: f"${x:+.2f}" if pd.notna(x) else "Pending")
            })
            
            # Display table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Delete pending bets section
            pending_bets = all_bets[all_bets['status'] == 'pending']
            if not pending_bets.empty:
                st.markdown("---")
                st.subheader("🗑️ Delete Pending Bets")
                st.markdown("Delete accidentally placed bets (only pending bets can be deleted)")
                
                for idx, bet in pending_bets.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{bet['game']}** - {bet['team']} ({bet['moneyline']:+d}) - ${bet['bet_amount']:.2f}")
                    with col2:
                        if st.button("Delete", key=f"track_delete_{bet['bet_id']}", type="secondary"):
                            # Refund the bet amount to bankroll
                            st.session_state.current_bankroll += bet['bet_amount']
                            # Delete the bet
                            deleted = st.session_state.bet_tracker.delete_bet(bet['bet_id'])
                            if deleted:
                                st.success(f"✅ Bet deleted! Refunded ${bet['bet_amount']:.2f} to bankroll.")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete bet.")
            
            # Summary row
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            stats = st.session_state.bet_tracker.get_summary_stats()
            
            with col1:
                st.metric("Total Bets", stats['total_bets'])
            
            with col2:
                st.metric("Win Rate", f"{stats['win_rate']:.1%}")
            
            with col3:
                st.metric("Total Wagered", f"${stats['total_wagered']:,.2f}")
            
            with col4:
                st.metric("Total Profit", f"${stats['total_profit']:+,.2f}")
            
            # Export button
            if st.button("📥 Export to CSV"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"bet_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("📝 No bets logged yet")
    
    # ========================================================================
    # TAB 4: VISUALS - Charts and graphs
    # ========================================================================
    with tab4:
        st.header("📉 Visuals")
        st.markdown("Performance visualizations")
        
        all_bets = st.session_state.bet_tracker.get_bets_dataframe()
        
        if not all_bets.empty and len(all_bets[all_bets['status'].isin(['won', 'lost'])]) > 0:
            settled_bets = all_bets[all_bets['status'].isin(['won', 'lost'])].copy()
            
            # Chart 1: Bankroll Growth
            st.subheader("💰 Bankroll Growth")
            
            if st.session_state.bet_tracker.bankroll_history:
                bankroll_data = pd.DataFrame(st.session_state.bet_tracker.bankroll_history)
                bankroll_data['timestamp'] = pd.to_datetime(bankroll_data['timestamp'])
                
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(
                    x=bankroll_data['timestamp'],
                    y=bankroll_data['bankroll'],
                    mode='lines+markers',
                    name='Bankroll',
                    line=dict(color='#1f77b4', width=3)
                ))
                
                # Add starting bankroll line
                fig1.add_hline(
                    y=1000,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Starting Bankroll"
                )
                
                fig1.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Bankroll ($)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig1, use_container_width=True)
            
            # Chart 2: Win Rate / Success
            st.subheader("🎯 Win Rate")
            
            col1, col2 = st.columns(2)
            
            with col1:
                wins = len(settled_bets[settled_bets['status'] == 'won'])
                losses = len(settled_bets[settled_bets['status'] == 'lost'])
                
                fig2 = go.Figure(data=[go.Pie(
                    labels=['Wins', 'Losses'],
                    values=[wins, losses],
                    marker=dict(colors=['#28a745', '#dc3545']),
                    hole=0.4
                )])
                
                fig2.update_layout(
                    title="Win/Loss Distribution",
                    height=350
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
                
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=win_rate * 100,
                    title={'text': "Win Rate (%)"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#1f77b4"},
                        'steps': [
                            {'range': [0, 50], 'color': "#ffcccc"},
                            {'range': [50, 60], 'color': "#ffffcc"},
                            {'range': [60, 100], 'color': "#ccffcc"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 52.4
                        }
                    }
                ))
                
                fig3.update_layout(height=350)
                st.plotly_chart(fig3, use_container_width=True)
            
            # Chart 3: Cumulative Profit
            st.subheader("📈 Cumulative Profit")
            
            settled_bets = settled_bets.sort_values('timestamp')
            settled_bets['cumulative_profit'] = settled_bets['profit'].cumsum()
            
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=list(range(1, len(settled_bets) + 1)),
                y=settled_bets['cumulative_profit'],
                mode='lines',
                fill='tozeroy',
                name='Cumulative Profit',
                line=dict(color='#28a745', width=3)
            ))
            
            fig4.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Breakeven")
            
            fig4.update_layout(
                xaxis_title="Bet Number",
                yaxis_title="Cumulative Profit ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig4, use_container_width=True)
            
            # Chart 4: Profit Distribution
            st.subheader("💵 Profit Distribution")
            
            fig5 = go.Figure()
            
            wins_profit = settled_bets[settled_bets['status'] == 'won']['profit']
            losses_profit = settled_bets[settled_bets['status'] == 'lost']['profit']
            
            fig5.add_trace(go.Histogram(
                x=wins_profit,
                name='Wins',
                marker_color='#28a745',
                opacity=0.7
            ))
            
            fig5.add_trace(go.Histogram(
                x=losses_profit,
                name='Losses',
                marker_color='#dc3545',
                opacity=0.7
            ))
            
            fig5.update_layout(
                xaxis_title="Profit/Loss ($)",
                yaxis_title="Frequency",
                barmode='overlay',
                height=400
            )
            
            st.plotly_chart(fig5, use_container_width=True)
            
        else:
            st.info("📝 No bet history yet. Start betting to see visualizations!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>NBA Bet Selector v2.0 | M4 Dashboard | Built with ❤️ and 🐍</p>
        <p>⚠️ Bet Responsibly | Past Performance ≠ Future Results</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
