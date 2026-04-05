# 🚀 Quick Start Guide - NBA Picks macOS App

## Follow These Steps IN ORDER

---

### ✅ STEP 1: Install Python Dependencies

Open **Terminal** and run:

```bash
cd /Users/idobelyaev/NBA_winners
pip install flask flask-cors
```

Wait for installation to complete.

---

### ✅ STEP 2: Test Python Backend

In Terminal, run:

```bash
python3 api_server.py
```

**You should see:**
```
🏀 NBA Betting API Server
Starting Flask API server on http://localhost:5000
```

✅ **If you see this** → Backend works! Press `Ctrl+C` to stop it.

❌ **If errors** → Let me know what the error says.

---

### ✅ STEP 3: Open Xcode Project

1. Open **Xcode**
2. Open your **NBA_PICKS** project

*(If you don't have one yet: File → New → Project → macOS → App → Name it "NBA_PICKS")*

---

### ✅ STEP 4: Add Swift Files to Xcode

**In Xcode:**

1. **Right-click** on "NBA_PICKS" folder (left sidebar)
2. Select **"Add Files to NBA_PICKS..."**
3. Navigate to:
   ```
   /Users/idobelyaev/NBA_winners/macOS_App/
   ```
4. **Select ALL 8 files:**
   - ✓ Models.swift
   - ✓ APIService.swift
   - ✓ PicksView.swift
   - ✓ ResultsView.swift
   - ✓ TrackView.swift
   - ✓ VisualsView.swift
   - ✓ ContentView.swift
   - ✓ NBA_PicksApp.swift

5. **Check these boxes:**
   - ✅ "Copy items if needed"
   - ✅ "Create groups"
   - ✅ NBA_PICKS target selected

6. Click **"Add"**

---

### ✅ STEP 5: Delete Old Default Files

**In Xcode Navigator (left sidebar):**

If you see OLD versions of these files, delete them:
- Old `ContentView.swift` → Right-click → Delete → Move to Trash
- Old `NBA_PicksApp.swift` → Right-click → Delete → Move to Trash

*(The new files you added will replace them)*

---

### ✅ STEP 6: Build the Project

**In Xcode:**

1. Press **⌘B** (or Product → Build)
2. Wait for build to complete
3. Check bottom panel for errors

✅ **Build Succeeded?** → Continue to Step 7

❌ **Build Failed?** → Let me know the error message

---

### ✅ STEP 7: Start Python Backend (KEEP RUNNING)

**Open a NEW Terminal window** and run:

```bash
cd /Users/idobelyaev/NBA_winners
python3 api_server.py
```

**You should see:**
```
🏀 NBA Betting API Server
Starting Flask API server on http://localhost:5000
```

⚠️ **KEEP THIS TERMINAL WINDOW OPEN!**

The app needs this running to work.

---

### ✅ STEP 8: Run the macOS App!

**Back in Xcode:**

1. Press **⌘R** (or click Play button ▶️)
2. The app will launch!
3. You should see a window with 4 tabs:
   - Picks
   - Results
   - Track
   - Visuals
4. **Look in your menu bar** for the **🏀 icon**!

---

### ✅ STEP 9: Test the App

**Try it out:**

1. Click **Picks** tab
2. Select today's date
3. Click **"Fetch Games"**
4. Enter some test moneylines:
   - Home: `+150`
   - Away: `-200`
5. Click **"Calculate Picks"**

✅ **See recommendations?** → SUCCESS! 🎉

---

## 🎉 YOU'RE DONE!

Your native macOS app is now running!

### What You Have:

- 🏀 **Menu bar icon** - Click for quick stats
- 📱 **4 tabs** - Complete betting workflow
- 🎨 **Team logos** - All 30 NBA teams
- 📊 **Charts** - Performance tracking
- ⌘ **Shortcuts** - ⌘N, ⌘R

---

## 🐛 Troubleshooting

### "Connection refused" error

**Problem:** App can't connect to backend

**Fix:**
```bash
# Make sure backend is running
python3 api_server.py
```

### Build errors in Xcode

**Problem:** "Cannot find type 'XXX'"

**Fix:**
- Make sure ALL 8 Swift files are added
- Clean build: ⌘⇧K then ⌘B

### No menu bar icon

**Problem:** Basketball icon not showing

**Fix:**
- Restart the app
- Check Console.app for errors

---

## 📖 Need More Help?

Read the detailed guides:
- `XCODE_SETUP.md` - Complete Xcode setup
- `macOS_App/README.md` - Full app documentation

---

## 🚀 Daily Usage

**Every time you use the app:**

1. Start backend: `python3 api_server.py`
2. Run app in Xcode: ⌘R
3. Click menu bar 🏀 icon for quick access
4. Use 4 tabs for complete workflow

**Happy betting!** 🏀💰

