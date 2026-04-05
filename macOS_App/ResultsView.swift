//
//  ResultsView.swift
//  NBA_PICKS
//
//  View for entering game results and calculating profit/loss
//

import SwiftUI

struct ResultsView: View {
    @StateObject private var viewModel = ResultsViewModel()
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(spacing: 8) {
                Text("📊 Game Results")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Text("Mark your bets as Won or Lost")
                    .foregroundColor(.secondary)
            }
            .padding()
            
            Divider()
            
            // Content
            if viewModel.isLoading {
                Spacer()
                ProgressView("Loading bets...")
                Spacer()
            } else if viewModel.pendingBets.isEmpty {
                // Empty state
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "checkmark.circle")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text("No pending bets to update")
                        .foregroundColor(.secondary)
                    
                    Button("Refresh") {
                        viewModel.loadPendingBets()
                    }
                    .buttonStyle(.borderedProminent)
                }
                Spacer()
            } else {
                // Pending bets list
                ScrollView {
                    VStack(spacing: 16) {
                        Text("\(viewModel.pendingBets.count) Pending Bet\(viewModel.pendingBets.count == 1 ? "" : "s")")
                            .font(.title2)
                            .fontWeight(.semibold)
                        
                        ForEach(viewModel.pendingBets) { bet in
                            BetResultCard(
                                bet: bet,
                                onWon: { viewModel.markBetResult(betId: bet.id, won: true) },
                                onLost: { viewModel.markBetResult(betId: bet.id, won: false) }
                            )
                        }
                    }
                    .padding()
                }
            }
        }
        .onAppear {
            viewModel.loadPendingBets()
        }
    }
}

// MARK: - Bet Result Card

struct BetResultCard: View {
    let bet: Bet
    let onWon: () -> Void
    let onLost: () -> Void
    
    @State private var isProcessing = false
    
    var body: some View {
        VStack(spacing: 12) {
            // Game info
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(bet.game)
                        .font(.headline)
                    Text(bet.date)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Pick: \(bet.pick)")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                    Text("\(bet.odds > 0 ? "+" : "")\(bet.odds)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Bet details
            HStack {
                Label("$\(String(format: "%.2f", bet.amount))", systemImage: "dollarsign.circle")
                    .font(.caption)
                
                Spacer()
                
                if bet.odds > 0 {
                    let potentialWin = bet.amount * Double(abs(bet.odds)) / 100.0
                    Text("Win: $\(String(format: "%.2f", potentialWin))")
                        .font(.caption)
                        .foregroundColor(.green)
                } else {
                    let potentialWin = bet.amount * 100.0 / Double(abs(bet.odds))
                    Text("Win: $\(String(format: "%.2f", potentialWin))")
                        .font(.caption)
                        .foregroundColor(.green)
                }
            }
            .padding(.horizontal)
            
            Divider()
            
            // Action buttons
            HStack(spacing: 12) {
                Button(action: {
                    isProcessing = true
                    onWon()
                }) {
                    Label("Won", systemImage: "checkmark.circle.fill")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
                .disabled(isProcessing)
                
                Button(action: {
                    isProcessing = true
                    onLost()
                }) {
                    Label("Lost", systemImage: "xmark.circle.fill")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)
                .disabled(isProcessing)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }
}

// MARK: - View Model

@MainActor
class ResultsViewModel: ObservableObject {
    @Published var pendingBets: [Bet] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService()
    
    func loadPendingBets() {
        isLoading = true
        
        Task {
            do {
                let allBets = try await apiService.fetchBets()
                pendingBets = allBets.filter { $0.result == nil }
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    func markBetResult(betId: String, won: Bool) {
        Task {
            do {
                try await apiService.updateBetResult(betId: betId, won: won)
                // Reload bets after update
                loadPendingBets()
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
}

#Preview {
    ResultsView()
        .frame(width: 600, height: 500)
}


