# Xcode Setup Guide for NBA_PICKS

## 📋 Complete Step-by-Step Instructions

### Step 1: Create New Xcode Project

1. **Open Xcode**
2. **File → New → Project** (or ⌘⇧N)
3. Select **macOS** tab
4. Choose **App** template
5. Click **Next**
6. Configure your project:
   - **Product Name:** `NBA_PICKS`
   - **Team:** Your team (or personal)
   - **Organization Identifier:** `com.yourname` (or use default)
   - **Interface:** **SwiftUI**
   - **Language:** **Swift**
   - **Storage:** None
   - **Testing:** Optional (uncheck if you don't need)
7. Click **Next**
8. Choose where to save (anywhere you want)
9. Click **Create**

### Step 2: Add Swift Files to Project ✅ COMPLETED

1. In Xcode, **right-click** on the **NBA_PICKS** folder in the Navigator (left sidebar)
2. Select **"Add Files to NBA_PICKS..."**
3. Navigate to:
   ```
   ~/Desktop/Swift_Files_For_Xcode/
   ```
4. **Select ALL** these files:
   - ✅ `Models.swift`
   - ✅ `APIService.swift`
   - ✅ `PicksView.swift`
   - ✅ `ResultsView.swift`
   - ✅ `TrackView.swift`
   - ✅ `VisualsView.swift`
   - ✅ `ContentView.swift`
   - ✅ `NBA_PicksApp.swift`

5. **Important options:**
   - ✅ Check **"Copy items if needed"**
   - ✅ Check **"Create groups"**
   - ✅ Make sure **NBA_PICKS target** is selected
6. Click **Add**

### Step 3: Replace Default Files

Xcode created default files. You need to replace them:

1. **Delete** these default files:
   - Find `ContentView.swift` (the default one) → Right-click → Delete → Move to Trash
   - Find `NBA_PicksApp.swift` (or `NBA_PICSKApp.swift`) → Right-click → Delete → Move to Trash

2. The ones you just added will take their place!

### Step 4: Verify Project Structure

Your Xcode Navigator should look like:

```
NBA_PICKS/
├── NBA_PicksApp.swift        (main app entry)
├── ContentView.swift          (main view)
├── Models.swift               (data models)
├── APIService.swift           (API client)
├── PicksView.swift            (Tab 1)
├── ResultsView.swift          (Tab 2)
├── TrackView.swift            (Tab 3)
├── VisualsView.swift          (Tab 4)
├── Assets.xcassets/
└── NBA_PICKS.entitlements
```

### Step 5: Configure App Permissions (Optional)

If you want network access (which you do!):

1. Click on **NBA_PICKS** (blue icon at top of Navigator)
2. Select **NBA_PICKS** target
3. Go to **Signing & Capabilities** tab
4. Click **+ Capability**
5. Add **Outgoing Connections (Client)** if asked

### Step 6: Build the Project

1. Press **⌘B** or **Product → Build**
2. Wait for build to complete
3. Fix any errors (there shouldn't be any!)

### Step 7: Start Python Backend ✅ COMPLETED

**IMPORTANT:** The app needs the Python backend running!

✅ Flask installed and API server started

Open Terminal and run:

```bash
cd /Users/idobelyaev/NBA_winners
python3 api_server.py
```

You should see:
```
🏀 NBA Betting API Server
Starting Flask API server on http://localhost:5000
```

**Keep this terminal window open!**

### Step 8: Run the App!

1. In Xcode, press **⌘R** or click the **Play** button (▶️)
2. The app will launch!
3. You'll see the 4-tab interface
4. Look in your **menu bar** for the **🏀 icon**!

## 🎉 You're Done!

Your native macOS app is now running with:
- ✅ MenuBar icon
- ✅ 4 tabs (Picks, Results, Track, Visuals)
- ✅ Team logos
- ✅ Performance charts
- ✅ Connection to Python backend

## 🐛 Troubleshooting

### Build Errors

**Problem:** "Cannot find type 'XXX' in scope"

**Solution:**
- Make sure ALL Swift files are added to the project
- Check that files are in the NBA_PICKS target
- Clean build folder: **⌘⇧K** then **⌘B**

### Connection Error

**Problem:** "Failed to connect to API"

**Solution:**
```bash
# Make sure Python backend is running
python3 api_server.py
```

### Menu Bar Icon Not Showing

**Problem:** No basketball icon in menu bar

**Solution:**
- Check Console.app for errors
- Make sure `AppDelegate` is initialized
- Try restarting the app

### Missing Charts

**Problem:** "No data yet" in Visuals tab

**Solution:**
- You need to place some bets first!
- Go to Picks tab → Enter odds → Get recommendations
- Then Results tab → Mark Won/Lost
- Then Visuals will have data

## 📝 Quick Reference

### Keyboard Shortcuts in App
- **⌘N** - New pick session
- **⌘R** - Refresh picks
- **⌘,** - Settings
- **⌘Q** - Quit

### File Locations
- **Swift Files:** `/Users/idobelyaev/NBA_winners/macOS_App/`
- **Python Backend:** `/Users/idobelyaev/NBA_winners/api_server.py`
- **Data Files:** `/Users/idobelyaev/NBA_winners/data/`

## 🚀 Ready to Bet!

1. **Start backend:** `./start_api.sh`
2. **Run app:** Press ▶️ in Xcode
3. **Click menu bar icon:** See quick stats
4. **Open dashboard:** Get today's picks!

Happy betting! 🏀💰

