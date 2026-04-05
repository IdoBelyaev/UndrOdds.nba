//
//  PicksView.swift
//  NBA_PICKS
//
//  View for entering odds and getting picks
//

import SwiftUI

struct PicksView: View {
    @StateObject private var viewModel = PicksViewModel()
    @State private var selectedDate = Date()
    @State private var minEV: Double = 5.0
    @State private var betAmount: Double = 20.0
    
    var body: some View {
        VStack(spacing: 0) {
            // Header with settings
            VStack(spacing: 16) {
                Text("🏀 Today's Picks")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                // Date picker and settings
                HStack(spacing: 20) {
                    DatePicker("Game Date:", selection: $selectedDate, displayedComponents: [.date])
                        .datePickerStyle(.compact)
                    
                    Divider()
                    
                    HStack {
                        Text("Min EV:")
                        TextField("", value: $minEV, format: .number)
                            .frame(width: 50)
                            .textFieldStyle(.roundedBorder)
                        Text("%")
                    }
                    
                    HStack {
                        Text("Bet:")
                        TextField("", value: $betAmount, format: .currency(code: "USD"))
                            .frame(width: 80)
                            .textFieldStyle(.roundedBorder)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
                
                // Action buttons
                HStack(spacing: 12) {
                    Button(action: { viewModel.fetchGames(for: selectedDate) }) {
                        Label("Fetch Games", systemImage: "arrow.down.circle.fill")
                    }
                    .buttonStyle(.borderedProminent)
                    
                    if !viewModel.games.isEmpty {
                        Button(action: {
                            viewModel.calculatePicks(
                                date: selectedDate,
                                minEV: minEV / 100,
                                betAmount: betAmount
                            )
                        }) {
                            Label("Calculate Picks", systemImage: "chart.bar.fill")
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(.green)
                    }
                }
            }
            .padding()
            
            Divider()
            
            // Main content
            if viewModel.isLoading {
                Spacer()
                ProgressView("Loading...")
                Spacer()
            } else if !viewModel.picks.isEmpty {
                // Show picks
                picksListView
            } else if !viewModel.games.isEmpty {
                // Show games with odds input
                gamesInputView
            } else {
                // Empty state
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "basketball")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text("Select a date and fetch games to get started")
                        .foregroundColor(.secondary)
                }
                Spacer()
            }
        }
    }
    
    // MARK: - Games Input View
    
    private var gamesInputView: some View {
        ScrollView {
            VStack(spacing: 16) {
                Text("Enter Moneylines")
                    .font(.title2)
                    .fontWeight(.semibold)
                
                ForEach($viewModel.games) { $game in
                    GameOddsInputCard(game: $game)
                }
            }
            .padding()
        }
    }
    
    // MARK: - Picks List View
    
    private var picksListView: some View {
        ScrollView {
            VStack(spacing: 16) {
                Text("\(viewModel.picks.count) Positive EV Pick\(viewModel.picks.count == 1 ? "" : "s")")
                    .font(.title2)
                    .fontWeight(.semibold)
                
                ForEach(viewModel.picks) { pick in
                    PickCard(pick: pick)
                }
            }
            .padding()
        }
    }
}

// MARK: - Game Odds Input Card

struct GameOddsInputCard: View {
    @Binding var game: Game
    
    var body: some View {
        VStack(spacing: 12) {
            // Teams with logos
            HStack(spacing: 40) {
                // Home team
                VStack {
                    if let logoURL = TeamLogos.getLogoURL(for: game.homeTeam),
                       let url = URL(string: logoURL) {
                        AsyncImage(url: url) { image in
                            image.resizable()
                        } placeholder: {
                            ProgressView()
                        }
                        .frame(width: 50, height: 50)
                    }
                    Text(game.homeTeam)
                        .font(.headline)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                
                Text("VS")
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.secondary)
                
                // Away team
                VStack {
                    if let logoURL = TeamLogos.getLogoURL(for: game.awayTeam),
                       let url = URL(string: logoURL) {
                        AsyncImage(url: url) { image in
                            image.resizable()
                        } placeholder: {
                            ProgressView()
                        }
                        .frame(width: 50, height: 50)
                    }
                    Text(game.awayTeam)
                        .font(.headline)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
            }
            
            Divider()
            
            // Odds input
            HStack(spacing: 20) {
                VStack(alignment: .leading) {
                    Text("\(game.homeTeam) ML")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    TextField("Home ML", value: $game.homeML, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 100)
                }
                
                VStack(alignment: .leading) {
                    Text("\(game.awayTeam) ML")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    TextField("Away ML", value: $game.awayML, format: .number)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 100)
                }
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }
}

// MARK: - Pick Card

struct PickCard: View {
    let pick: Pick
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 8) {
                Text(pick.game)
                    .font(.headline)
                
                HStack {
                    Text("Pick:")
                    Text(pick.pick)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                }
                
                HStack(spacing: 16) {
                    Label("\(pick.odds > 0 ? "+" : "")\(pick.odds)", systemImage: "chart.line.uptrend.xyaxis")
                    Label("\(String(format: "%.1f", pick.winProbability))%", systemImage: "percent")
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 8) {
                HStack {
                    Text("EV:")
                    Text("+\(String(format: "%.1f", pick.ev))%")
                        .fontWeight(.bold)
                        .foregroundColor(.green)
                }
                .font(.headline)
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("Bet: $\(String(format: "%.0f", pick.betAmount))")
                    Text("Profit: $\(String(format: "%.2f", pick.expectedProfit))")
                        .foregroundColor(.green)
                    Text("Return: $\(String(format: "%.2f", pick.potentialReturn))")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color.green.opacity(0.1), Color.blue.opacity(0.05)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.green.opacity(0.3), lineWidth: 2)
        )
    }
}

// MARK: - View Model

@MainActor
class PicksViewModel: ObservableObject {
    @Published var games: [Game] = []
    @Published var picks: [Pick] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService()
    
    func fetchGames(for date: Date) {
        isLoading = true
        picks = [] // Clear previous picks
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "dd-MM-yyyy"
        let dateString = dateFormatter.string(from: date)
        
        Task {
            do {
                games = try await apiService.fetchGames(for: dateString)
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
    
    func calculatePicks(date: Date, minEV: Double, betAmount: Double) {
        isLoading = true
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "dd-MM-yyyy"
        let dateString = dateFormatter.string(from: date)
        
        let gamesWithOdds = games.compactMap { game -> GameWithOdds? in
            guard let homeML = game.homeML, let awayML = game.awayML else {
                return nil
            }
            return GameWithOdds(
                homeTeam: game.homeTeam,
                awayTeam: game.awayTeam,
                homeML: homeML,
                awayML: awayML
            )
        }
        
        Task {
            do {
                picks = try await apiService.calculatePicks(
                    date: dateString,
                    games: gamesWithOdds,
                    minEV: minEV,
                    betAmount: betAmount
                )
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
}

#Preview {
    PicksView()
        .frame(width: 800, height: 600)
}


