# Xcode Setup Guide for NBA_PICKS macOS App

**Complete Step-by-Step Guide**  
**Timeline:** 30-60 minutes  
**Status:** 🚀 Ready to Build  

---

## 📋 Overview

This guide will help you build a **native macOS app** for your NBA betting system with:
- 🏀 **MenuBar Integration** - Quick access from menu bar
- 📱 **4 Tabs** - Picks, Results, Track, Visuals
- 🎨 **Team Logos** - All 30 NBA teams
- 📊 **Performance Charts** - Real-time tracking
- ⌘ **Keyboard Shortcuts** - Professional UX

---

## 🎯 M1: Xcode Project Setup (10 minutes)

### Phase 1.1: Install Prerequisites

**Status:** ⏳ Pending

**What you need:**
- ✅ macOS 13.0 (Ventura) or later
- ✅ Xcode 15.0 or later (free from App Store)
- ✅ Python 3.9+ with Flask installed

**Steps:**

1. **Install Xcode** (if not installed):
   - Open **App Store**
   - Search for "Xcode"
   - Click **Get** / **Install**
   - Wait for installation (takes 10-20 minutes)

2. **Verify Xcode Installation**:
   ```bash
   xcode-select --version
   ```
   Should show: `xcode-select version 2395` or similar

3. **Install Python Dependencies**:
   ```bash
   cd /Users/idobelyaev/NBA_winners
   pip install -r requirements.txt
   ```

**✅ Checkpoint:** Xcode installed and Python dependencies ready

---

### Phase 1.2: Create New Xcode Project

**Status:** ⏳ Pending

**Steps:**

1. **Open Xcode**

2. **Create New Project:**
   - Click **"Create New Project"** (or File → New → Project)
   - Or press: **⌘⇧N**

3. **Choose Template:**
   - Select **macOS** tab at the top
   - Choose **App** template
   - Click **Next**

4. **Configure Project:**
   ```
   Product Name:           NBA_PICKS
   Team:                   Your Name (or leave default)
   Organization Identifier: com.yourname (or leave default)
   Interface:              SwiftUI ✅
   Language:               Swift ✅
   Storage:                None
   Include Tests:          ☐ (optional)
   ```
   - Click **Next**

5. **Save Location:**
   - Choose any location (e.g., Documents/Xcode Projects/)
   - ☐ Uncheck "Create Git repository" (optional)
   - Click **Create**

**✅ Checkpoint:** Xcode project created with default files

---

### Phase 1.3: Verify Project Structure

**Status:** ⏳ Pending

**What you should see in Xcode Navigator (left sidebar):**

```
NBA_PICKS/
├── NBA_PICSKApp.swift      (or NBA_PicksApp.swift)
├── ContentView.swift
├── Assets.xcassets/
└── NBA_PICKS.entitlements
```

**✅ Checkpoint:** Project structure looks correct

---

## 🎯 M2: Add Swift Files (15 minutes)

### Phase 2.1: Add All Swift Files to Project

**Status:** ⏳ Pending

**Steps:**

1. **In Xcode Navigator** (left sidebar):
   - **Right-click** on the **"NBA_PICKS"** folder (blue icon)
   - Select **"Add Files to NBA_PICKS..."**

2. **Navigate to Swift Files:**
   ```
   /Users/idobelyaev/NBA_winners/macOS_App/
   ```

3. **Select ALL 8 Swift Files:**
   - ✅ `Models.swift`
   - ✅ `APIService.swift`
   - ✅ `PicksView.swift`
   - ✅ `ResultsView.swift`
   - ✅ `TrackView.swift`
   - ✅ `VisualsView.swift`
   - ✅ `ContentView.swift`
   - ✅ `NBA_PicksApp.swift`

4. **IMPORTANT - Check These Options:**
   - ✅ **"Copy items if needed"** ← MUST be checked!
   - ✅ **"Create groups"** (not "Create folder references")
   - ✅ **"NBA_PICKS" target** is selected

5. **Click "Add"**

**✅ Checkpoint:** All 8 Swift files appear in Xcode Navigator

---

### Phase 2.2: Delete Old Default Files

**Status:** ⏳ Pending

**Steps:**

1. **Find OLD ContentView.swift:**
   - Look for `ContentView.swift` with a timestamp or older date
   - **Right-click** → **Delete**
   - Choose **"Move to Trash"**

2. **Find OLD App File:**
   - Look for `NBA_PICSKApp.swift` or old `NBA_PicksApp.swift`
   - **Right-click** → **Delete**
   - Choose **"Move to Trash"**

**Note:** The NEW files you just added will replace these!

**✅ Checkpoint:** Only the new Swift files remain

---

### Phase 2.3: Verify File Structure

**Status:** ⏳ Pending

**Your Xcode Navigator should now show:**

```
NBA_PICKS/
├── NBA_PicksApp.swift       ← Main app entry
├── ContentView.swift         ← Main view with tabs
├── Models.swift              ← Data models
├── APIService.swift          ← API client
├── PicksView.swift           ← Tab 1
├── ResultsView.swift         ← Tab 2
├── TrackView.swift           ← Tab 3
├── VisualsView.swift         ← Tab 4
├── Assets.xcassets/
└── NBA_PICKS.entitlements
```

**✅ Checkpoint:** All files in correct location

---

## 🎯 M3: Build and Test (10 minutes)

### Phase 3.1: First Build

**Status:** ⏳ Pending

**Steps:**

1. **Clean Build Folder:**
   - Press **⌘⇧K** (or Product → Clean Build Folder)
   - Wait for "Clean Finished"

2. **Build Project:**
   - Press **⌘B** (or Product → Build)
   - Wait for build to complete
   - Watch the progress bar at top

3. **Check for Errors:**
   - Look at the bottom panel (Issues Navigator)
   - **If build succeeds:** ✅ Continue to next step
   - **If errors appear:** See Troubleshooting section below

**Common Build Errors & Fixes:**

| Error | Fix |
|-------|-----|
| "Cannot find type 'XXX'" | Make sure all 8 Swift files are added |
| "Duplicate symbol" | Delete old ContentView/App files |
| "Missing import" | Clean build folder (⌘⇧K) then rebuild |

**✅ Checkpoint:** Build succeeds with 0 errors

---

### Phase 3.2: Start Python Backend

**Status:** ⏳ Pending

**IMPORTANT:** The app needs the Python backend running!

**Steps:**

1. **Open Terminal** (new window)

2. **Navigate to project:**
   ```bash
   cd /Users/idobelyaev/NBA_winners
   ```

3. **Start API server:**
   ```bash
   python3 api_server.py
   ```

4. **Verify it's running:**
   ```
   You should see:
   🏀 NBA Betting API Server
   Starting Flask API server on http://localhost:5000
   ```

5. **KEEP THIS TERMINAL OPEN!**
   - Don't close it while using the app
   - The app communicates with this server

**✅ Checkpoint:** API server running on localhost:5000

---

### Phase 3.3: Run the macOS App

**Status:** ⏳ Pending

**Steps:**

1. **Back in Xcode:**
   - Press **⌘R** (or click Play button ▶️)
   - Or: Product → Run

2. **Wait for Launch:**
   - App will compile and launch
   - Takes 10-30 seconds first time

3. **What You Should See:**
   - A window opens with your app
   - Sidebar with 4 tabs:
     - 🎯 Picks
     - 📊 Results
     - 📈 Track
     - 📉 Visuals
   - **Look in menu bar** for 🏀 icon!

**✅ Checkpoint:** App launches successfully

---

## 🎯 M4: Test All Features (15 minutes)

### Phase 4.1: Test Picks Tab

**Status:** ⏳ Pending

**Steps:**

1. **Click "Picks" tab** in sidebar

2. **Select Today's Date:**
   - Click the date picker
   - Choose today's date

3. **Click "Fetch Games":**
   - Should load games for that date
   - If no games: Try a different date

4. **Enter Test Moneylines:**
   - Home ML: `+150`
   - Away ML: `-200`

5. **Click "Calculate Picks":**
   - Should show EV calculations
   - See positive EV recommendations

**✅ Checkpoint:** Picks tab works

---

### Phase 4.2: Test Results Tab

**Status:** ⏳ Pending

**Steps:**

1. **Click "Results" tab**

2. **Should show:**
   - Pending bets (if any)
   - Won/Lost buttons

3. **Test marking a result:**
   - Click "Won" or "Lost"
   - Profit/loss calculated automatically

**✅ Checkpoint:** Results tab works

---

### Phase 4.3: Test Track Tab

**Status:** ⏳ Pending

**Steps:**

1. **Click "Track" tab**

2. **Should show:**
   - Table with bet history
   - Columns: Date, Game, Pick, Odds, Amount, Result, Return
   - Summary statistics at bottom

3. **Test Export:**
   - Click "Export CSV" button
   - Choose save location
   - Verify CSV file created

**✅ Checkpoint:** Track tab works

---

### Phase 4.4: Test Visuals Tab

**Status:** ⏳ Pending

**Steps:**

1. **Click "Visuals" tab**

2. **Should show 4 charts:**
   - 📈 Bankroll Growth (line chart)
   - 🥧 Win Rate (pie chart)
   - 💰 Cumulative Profit (line chart)
   - 📊 Profit Distribution (histogram)

3. **If charts show "No data":**
   - Normal! You need to place bets first
   - Charts will populate as you use the app

**✅ Checkpoint:** Visuals tab works

---

### Phase 4.5: Test MenuBar Icon

**Status:** ⏳ Pending

**Steps:**

1. **Look at top menu bar** (where battery, WiFi icons are)

2. **Find 🏀 icon** (basketball)

3. **Click it:**
   - Should show dropdown menu
   - Quick stats displayed
   - "Open Dashboard" button
   - "Quit" button

4. **Test Quick Actions:**
   - Click "Open Dashboard" → Main window appears
   - Press **⌘R** → Refreshes picks

**✅ Checkpoint:** MenuBar integration works

---

## 🎯 M5: Daily Usage Workflow (Reference)

### Morning Routine: Get Picks

**Steps:**

1. **Start Python Backend:**
   ```bash
   python3 api_server.py
   ```

2. **Launch App:**
   - Open from Applications
   - Or run from Xcode (⌘R)

3. **Get Today's Picks:**
   - Click **Picks** tab
   - Select today's date
   - Click **Fetch Games**
   - Enter moneylines from Underdog Fantasy
   - Click **Calculate Picks**

4. **Review Recommendations:**
   - See positive EV bets
   - Note bet amounts
   - Expected profit shown

5. **Place Bets:**
   - Go to Underdog Fantasy
   - Place recommended bets

---

### Evening Routine: Enter Results

**Steps:**

1. **Open App** (if closed)

2. **Go to Results Tab:**
   - See pending bets
   - Check game scores

3. **Mark Results:**
   - Click **Won** or **Lost** for each bet
   - Profit/loss calculated automatically
   - Bankroll updated

4. **Check Performance:**
   - Go to **Visuals** tab
   - See updated charts
   - Track your progress

---

### Anytime: Track Performance

**Quick Stats (MenuBar):**
- Click 🏀 icon
- See: Total Bets, Win Rate, ROI, Profit

**Detailed View (Track Tab):**
- Complete bet history
- Filter by date
- Export to CSV

**Visual Analysis (Visuals Tab):**
- Bankroll growth over time
- Win rate trends
- Profit distribution

---

## 🐛 Troubleshooting

### Issue: "Cannot find type 'Pick'" or similar

**Problem:** Swift files not properly added

**Fix:**
1. Check all 8 files are in Navigator
2. Click each file → File Inspector (right panel)
3. Verify "Target Membership" has NBA_PICKS checked
4. Clean build (⌘⇧K) and rebuild (⌘B)

---

### Issue: "Connection refused" when fetching games

**Problem:** Python backend not running

**Fix:**
```bash
cd /Users/idobelyaev/NBA_winners
python3 api_server.py
```
Keep terminal open!

---

### Issue: No menu bar icon appears

**Problem:** App delegate not initialized

**Fix:**
1. Check `NBA_PicksApp.swift` is in project
2. Verify it has `@NSApplicationDelegateAdaptor`
3. Restart app

---

### Issue: Charts show "No data yet"

**Problem:** No bet history

**Fix:**
- This is normal for new installation
- Place some bets first
- Mark them as Won/Lost
- Charts will populate

---

### Issue: Build succeeds but app crashes on launch

**Problem:** Missing dependencies

**Fix:**
1. Check Console.app for error logs
2. Verify Python backend is running
3. Check API endpoint: `http://localhost:5000/api/health`

---

## 📱 App Features Reference

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| ⌘N | New pick session |
| ⌘R | Refresh picks |
| ⌘, | Settings |
| ⌘Q | Quit app |
| ⌘O | Open dashboard |

---

### Settings (⌘,)

**Betting Settings:**
- Min EV Threshold: 5% (default)
- Default Bet Amount: $20
- Starting Bankroll: $1,000

**API Settings:**
- Endpoint: http://localhost:5000
- Auto-refresh: Enabled

---

### Data Storage

**All data stored locally:**
- Location: `/Users/idobelyaev/NBA_winners/data/`
- Files:
  - `bet_history.json` - Your bets
  - `nba_games.json` - Game data
  - `elo_ratings.json` - Team ratings

**No cloud sync** - Everything stays on your Mac

---

## 🎯 Success Metrics

**After completing this guide, you should have:**

✅ **Working macOS App:**
- Launches successfully
- All 4 tabs functional
- MenuBar icon appears
- Connects to Python backend

✅ **Complete Workflow:**
- Can fetch games
- Can calculate EV
- Can enter results
- Can track performance

✅ **Professional Features:**
- Team logos display
- Charts render correctly
- Export to CSV works
- Keyboard shortcuts work

---

## 📚 Additional Resources

**Documentation:**
- `README.md` - Project overview
- `RFC-001.md` - System architecture
- `M1-M4_PROGRESS.md` - Development milestones

**Code Files:**
- `macOS_App/` - All Swift source files
- `api_server.py` - Python backend
- `dashboard.py` - Web version (alternative)

**Support:**
- Check Console.app for error logs
- Verify Python backend is running
- Review troubleshooting section above

---

## 🎉 Congratulations!

You now have a **professional native macOS app** for NBA betting!

**What you built:**
- 🏀 MenuBar app with quick access
- 📱 4-tab interface (Picks, Results, Track, Visuals)
- 🎨 Team logos for all 30 NBA teams
- 📊 Real-time performance charts
- ⌘ Professional keyboard shortcuts
- 🔒 Local data storage (no cloud)

**Next Steps:**
1. Use it daily for NBA betting
2. Track your performance
3. Refine your strategy
4. Share with friends (optional)

**Happy Betting!** 🏀💰🚀

---

**Last Updated:** October 13, 2025  
**Version:** 2.0  
**Status:** ✅ Complete

