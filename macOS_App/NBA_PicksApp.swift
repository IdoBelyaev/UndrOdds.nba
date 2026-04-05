//
//  NBA_PicksApp.swift
//  NBA_PICKS
//
//  Main app entry point with MenuBar support
//

import SwiftUI

@main
struct NBA_PicksApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var menuBarManager = MenuBarManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 1000, minHeight: 700)
                .environmentObject(menuBarManager)
        }
        .commands {
            CommandGroup(after: .appInfo) {
                Button("Check for Picks") {
                    menuBarManager.refreshPicks()
                }
                .keyboardShortcut("R", modifiers: .command)
            }
            
            CommandGroup(replacing: .newItem) {
                Button("New Pick Session") {
                    menuBarManager.startNewSession()
                }
                .keyboardShortcut("N", modifiers: .command)
            }
        }
        
        Settings {
            SettingsView()
        }
    }
}

// MARK: - App Delegate for MenuBar

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var popover = NSPopover()
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Create status bar item
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        
        if let button = statusItem?.button {
            button.image = NSImage(systemSymbolName: "basketball.fill", accessibilityDescription: "NBA Picks")
            button.action = #selector(togglePopover)
            button.target = self
        }
        
        // Setup popover
        popover.contentSize = NSSize(width: 350, height: 400)
        popover.behavior = .transient
        popover.contentViewController = NSHostingController(rootView: MenuBarView())
    }
    
    @objc func togglePopover() {
        if let button = statusItem?.button {
            if popover.isShown {
                popover.performClose(nil)
            } else {
                popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
            }
        }
    }
}

// MARK: - MenuBar Manager

class MenuBarManager: ObservableObject {
    @Published var todaysPicks: [Pick] = []
    @Published var stats: Stats?
    
    private let apiService = APIService()
    
    init() {
        refreshPicks()
        refreshStats()
    }
    
    func refreshPicks() {
        Task {
            // Fetch today's picks
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "dd-MM-yyyy"
            let today = dateFormatter.string(from: Date())
            
            do {
                let games = try await apiService.fetchGames(for: today)
                // You would need to add odds here
                // For now, we'll just keep empty
            } catch {
                print("Error fetching picks: \(error)")
            }
        }
    }
    
    func refreshStats() {
        Task {
            do {
                stats = try await apiService.fetchStats()
            } catch {
                print("Error fetching stats: \(error)")
            }
        }
    }
    
    func startNewSession() {
        // Open main window focused on Picks tab
        if let window = NSApplication.shared.windows.first {
            window.makeKeyAndOrderFront(nil)
            NSApplication.shared.activate(ignoringOtherApps: true)
        }
    }
}

// MARK: - MenuBar View

struct MenuBarView: View {
    @StateObject private var menuBarManager = MenuBarManager()
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Image(systemName: "basketball.fill")
                    .foregroundColor(.orange)
                Text("NBA Picks")
                    .font(.headline)
                Spacer()
                Button(action: { menuBarManager.refreshPicks() }) {
                    Image(systemName: "arrow.clockwise")
                }
                .buttonStyle(.plain)
            }
            .padding()
            .background(Color.blue.opacity(0.1))
            
            Divider()
            
            // Stats summary
            if let stats = menuBarManager.stats {
                VStack(spacing: 8) {
                    HStack {
                        StatBadge(label: "Bets", value: "\(stats.totalBets)", color: .blue)
                        StatBadge(label: "Win Rate", value: String(format: "%.1f%%", stats.winRate), color: .green)
                    }
                    HStack {
                        StatBadge(label: "ROI", value: String(format: "%.1f%%", stats.roi), color: stats.roi >= 0 ? .green : .red)
                        StatBadge(label: "Profit", value: String(format: "$%.0f", stats.totalProfit), color: stats.totalProfit >= 0 ? .green : .red)
                    }
                }
                .padding()
                
                Divider()
            }
            
            // Today's picks
            ScrollView {
                if menuBarManager.todaysPicks.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "tray")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                        Text("No picks for today yet")
                            .foregroundColor(.secondary)
                        Button("Open App") {
                            menuBarManager.startNewSession()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                } else {
                    VStack(spacing: 8) {
                        ForEach(menuBarManager.todaysPicks) { pick in
                            MenuBarPickCard(pick: pick)
                        }
                    }
                    .padding()
                }
            }
            
            Divider()
            
            // Footer
            HStack {
                Button("Open Dashboard") {
                    menuBarManager.startNewSession()
                }
                .buttonStyle(.borderedProminent)
                
                Spacer()
                
                Button("Quit") {
                    NSApplication.shared.terminate(nil)
                }
                .buttonStyle(.plain)
                .foregroundColor(.red)
            }
            .padding()
        }
        .frame(width: 350, height: 400)
    }
}

struct StatBadge: View {
    let label: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(color)
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

struct MenuBarPickCard: View {
    let pick: Pick
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(pick.pick)
                    .font(.headline)
                Text("\(pick.odds > 0 ? "+" : "")\(pick.odds)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text("EV: +\(String(format: "%.1f", pick.ev))%")
                    .font(.headline)
                    .foregroundColor(.green)
                Text("$\(String(format: "%.0f", pick.betAmount))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(8)
        .background(Color.gray.opacity(0.05))
        .cornerRadius(6)
    }
}

// MARK: - Settings View

struct SettingsView: View {
    @AppStorage("minEV") private var minEV: Double = 5.0
    @AppStorage("betAmount") private var betAmount: Double = 20.0
    @AppStorage("bankroll") private var bankroll: Double = 1000.0
    
    var body: some View {
        Form {
            Section("Betting Settings") {
                HStack {
                    Text("Min EV Threshold:")
                    TextField("", value: $minEV, format: .number)
                        .frame(width: 60)
                    Text("%")
                }
                
                HStack {
                    Text("Default Bet Amount:")
                    TextField("", value: $betAmount, format: .currency(code: "USD"))
                        .frame(width: 100)
                }
                
                HStack {
                    Text("Starting Bankroll:")
                    TextField("", value: $bankroll, format: .currency(code: "USD"))
                        .frame(width: 100)
                }
            }
            
            Section("API Settings") {
                Text("API Endpoint: http://localhost:5000")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
        }
        .padding()
        .frame(width: 450)
    }
}

#Preview {
    MenuBarView()
}



