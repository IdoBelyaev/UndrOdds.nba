//
//  ContentView.swift
//  NBA_PICKS
//
//  Main content view with 4 tabs
//

import SwiftUI

struct ContentView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationSplitView {
            // Sidebar
            List(selection: $selectedTab) {
                Label("Picks", systemImage: "target")
                    .tag(0)
                
                Label("Results", systemImage: "checkmark.circle")
                    .tag(1)
                
                Label("Track", systemImage: "chart.bar.doc.horizontal")
                    .tag(2)
                
                Label("Visuals", systemImage: "chart.xyaxis.line")
                    .tag(3)
            }
            .navigationSplitViewColumnWidth(min: 180, ideal: 200)
            .toolbar {
                ToolbarItem(placement: .automatic) {
                    Button(action: {
                        selectedTab = 0
                    }) {
                        Label("Refresh", systemImage: "arrow.clockwise")
                    }
                }
            }
        } detail: {
            // Main content based on selection
            Group {
                switch selectedTab {
                case 0:
                    PicksView()
                case 1:
                    ResultsView()
                case 2:
                    TrackView()
                case 3:
                    VisualsView()
                default:
                    PicksView()
                }
            }
        }
        .navigationTitle("NBA Bet Selector")
    }
}

#Preview {
    ContentView()
        .frame(width: 1200, height: 800)
}


