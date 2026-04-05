//
//  TrackView.swift
//  NBA_PICKS
//
//  View for tracking bet history
//

import SwiftUI

struct TrackView: View {
    @StateObject private var viewModel = TrackViewModel()
    @State private var searchText = ""
    @State private var filterOption: FilterOption = .all
    
    enum FilterOption: String, CaseIterable {
        case all = "All"
        case won = "Won"
        case lost = "Lost"
        case pending = "Pending"
    }
    
    var filteredBets: [Bet] {
        let filtered = viewModel.bets.filter { bet in
            if searchText.isEmpty {
                return true
            }
            return bet.game.localizedCaseInsensitiveContains(searchText) ||
                   bet.pick.localizedCaseInsensitiveContains(searchText)
        }
        
        switch filterOption {
        case .all:
            return filtered
        case .won:
            return filtered.filter { $0.result == "won" }
        case .lost:
            return filtered.filter { $0.result == "lost" }
        case .pending:
            return filtered.filter { $0.result == nil }
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                Text("📈 Bet Tracking")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                // Search and filter
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.secondary)
                    TextField("Search bets...", text: $searchText)
                        .textFieldStyle(.plain)
                    
                    if !searchText.isEmpty {
                        Button(action: { searchText = "" }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(.secondary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(8)
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
                
                // Filter picker
                Picker("Filter", selection: $filterOption) {
                    ForEach(FilterOption.allCases, id: \.self) { option in
                        Text(option.rawValue).tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }
            .padding()
            
            Divider()
            
            // Content
            if viewModel.isLoading {
                Spacer()
                ProgressView("Loading bets...")
                Spacer()
            } else if filteredBets.isEmpty {
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "tray")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text(searchText.isEmpty ? "No bets yet" : "No bets match your search")
                        .foregroundColor(.secondary)
                }
                Spacer()
            } else {
                // Bets table
                ScrollView {
                    VStack(spacing: 1) {
                        // Header row
                        HStack {
                            Text("Date").frame(width: 90, alignment: .leading)
                            Text("Game").frame(minWidth: 200, alignment: .leading)
                            Text("Pick").frame(width: 120, alignment: .leading)
                            Text("Odds").frame(width: 60, alignment: .trailing)
                            Text("Amount").frame(width: 70, alignment: .trailing)
                            Text("Result").frame(width: 70, alignment: .center)
                            Text("Return").frame(width: 80, alignment: .trailing)
                        }
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.secondary)
                        .padding(.horizontal)
                        .padding(.vertical, 8)
                        .background(Color.gray.opacity(0.1))
                        
                        // Bet rows
                        ForEach(filteredBets) { bet in
                            BetRow(bet: bet)
                        }
                        
                        // Summary row
                        if !filteredBets.isEmpty {
                            BetSummaryRow(bets: filteredBets)
                        }
                    }
                }
                
                // Export button
                HStack {
                    Spacer()
                    Button(action: { viewModel.exportToCSV() }) {
                        Label("Export CSV", systemImage: "arrow.down.doc")
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            }
        }
        .onAppear {
            viewModel.loadBets()
        }
    }
}

// MARK: - Bet Row

struct BetRow: View {
    let bet: Bet
    
    var body: some View {
        HStack {
            Text(bet.date).frame(width: 90, alignment: .leading)
            Text(bet.game).frame(minWidth: 200, alignment: .leading)
            Text(bet.pick).frame(width: 120, alignment: .leading)
            Text("\(bet.odds > 0 ? "+" : "")\(bet.odds)").frame(width: 60, alignment: .trailing)
            Text("$\(String(format: "%.0f", bet.amount))").frame(width: 70, alignment: .trailing)
            
            // Result badge
            Group {
                if let result = bet.result {
                    Text(result.uppercased())
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(result == "won" ? .green : .red)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(result == "won" ? Color.green.opacity(0.2) : Color.red.opacity(0.2))
                        .cornerRadius(4)
                } else {
                    Text("PENDING")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.orange)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.orange.opacity(0.2))
                        .cornerRadius(4)
                }
            }
            .frame(width: 70, alignment: .center)
            
            // Return
            Group {
                if let profit = bet.profit {
                    Text("$\(String(format: "%.2f", profit))")
                        .foregroundColor(profit >= 0 ? .green : .red)
                } else {
                    Text("-")
                        .foregroundColor(.secondary)
                }
            }
            .frame(width: 80, alignment: .trailing)
        }
        .font(.caption)
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.02))
    }
}

// MARK: - Summary Row

struct BetSummaryRow: View {
    let bets: [Bet]
    
    var totalWagered: Double {
        bets.filter { $0.result != nil }.reduce(0) { $0 + $1.amount }
    }
    
    var totalProfit: Double {
        bets.compactMap { $0.profit }.reduce(0, +)
    }
    
    var body: some View {
        HStack {
            Text("Total").frame(width: 90, alignment: .leading)
            Spacer()
            Text("$\(String(format: "%.0f", totalWagered))").frame(width: 70, alignment: .trailing)
            Text("").frame(width: 70, alignment: .center)
            Text("$\(String(format: "%.2f", totalProfit))")
                .foregroundColor(totalProfit >= 0 ? .green : .red)
                .fontWeight(.bold)
                .frame(width: 80, alignment: .trailing)
        }
        .font(.caption)
        .fontWeight(.semibold)
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color.blue.opacity(0.1))
    }
}

// MARK: - View Model

@MainActor
class TrackViewModel: ObservableObject {
    @Published var bets: [Bet] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService()
    
    func loadBets() {
        isLoading = true
        
        Task {
            do {
                bets = try await apiService.fetchBets()
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    func exportToCSV() {
        let csvString = generateCSV()
        
        let savePanel = NSSavePanel()
        savePanel.allowedContentTypes = [.commaSeparatedText]
        savePanel.nameFieldStringValue = "nba_bets_\(Date().formatted(date: .numeric, time: .omitted)).csv"
        
        savePanel.begin { response in
            if response == .OK, let url = savePanel.url {
                do {
                    try csvString.write(to: url, atomically: true, encoding: .utf8)
                } catch {
                    print("Error saving CSV: \(error)")
                }
            }
        }
    }
    
    private func generateCSV() -> String {
        var csv = "Date,Game,Pick,Odds,Amount,Result,Return\n"
        
        for bet in bets {
            let result = bet.result ?? "Pending"
            let returnAmount = bet.profit.map { String(format: "%.2f", $0) } ?? "-"
            csv += "\(bet.date),\"\(bet.game)\",\(bet.pick),\(bet.odds),\(bet.amount),\(result),\(returnAmount)\n"
        }
        
        return csv
    }
}

#Preview {
    TrackView()
        .frame(width: 900, height: 600)
}


