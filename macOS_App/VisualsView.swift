//
//  VisualsView.swift
//  NBA_PICKS
//
//  View for performance visualizations
//

import SwiftUI
import Charts

struct VisualsView: View {
    @StateObject private var viewModel = VisualsViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                Text("📉 Performance Dashboard")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.top)
                
                // Stats summary
                if let stats = viewModel.stats {
                    StatsCard(stats: stats)
                }
                
                // Charts
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 20) {
                    // Bankroll growth
                    ChartCard(title: "Bankroll Growth") {
                        bankrollChart
                    }
                    
                    // Win rate
                    ChartCard(title: "Win Rate") {
                        winRateChart
                    }
                    
                    // Cumulative profit
                    ChartCard(title: "Cumulative Profit") {
                        cumulativeProfitChart
                    }
                    
                    // Profit distribution
                    ChartCard(title: "Profit Distribution") {
                        profitDistributionChart
                    }
                }
                .padding(.horizontal)
            }
            .padding(.bottom)
        }
        .onAppear {
            viewModel.loadData()
        }
    }
    
    // MARK: - Charts
    
    @ViewBuilder
    private var bankrollChart: some View {
        if !viewModel.bankrollHistory.isEmpty {
            Chart(viewModel.bankrollHistory) { dataPoint in
                LineMark(
                    x: .value("Date", dataPoint.date),
                    y: .value("Bankroll", dataPoint.value)
                )
                .foregroundStyle(.blue)
                .interpolationMethod(.catmullRom)
                
                AreaMark(
                    x: .value("Date", dataPoint.date),
                    y: .value("Bankroll", dataPoint.value)
                )
                .foregroundStyle(
                    LinearGradient(
                        colors: [.blue.opacity(0.3), .blue.opacity(0.05)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .interpolationMethod(.catmullRom)
            }
            .chartYScale(domain: .automatic(includesZero: false))
            .frame(height: 200)
        } else {
            emptyChartView
        }
    }
    
    @ViewBuilder
    private var winRateChart: some View {
        if let stats = viewModel.stats, stats.totalBets > 0 {
            Chart {
                SectorMark(
                    angle: .value("Wins", stats.wins),
                    innerRadius: .ratio(0.5),
                    angularInset: 2
                )
                .foregroundStyle(.green)
                .annotation(position: .overlay) {
                    Text("\(stats.wins)")
                        .font(.headline)
                        .foregroundColor(.white)
                }
                
                SectorMark(
                    angle: .value("Losses", stats.losses),
                    innerRadius: .ratio(0.5),
                    angularInset: 2
                )
                .foregroundStyle(.red)
                .annotation(position: .overlay) {
                    Text("\(stats.losses)")
                        .font(.headline)
                        .foregroundColor(.white)
                }
            }
            .frame(height: 200)
            .overlay {
                VStack(spacing: 4) {
                    Text(String(format: "%.1f%%", stats.winRate))
                        .font(.title)
                        .fontWeight(.bold)
                    Text("Win Rate")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        } else {
            emptyChartView
        }
    }
    
    @ViewBuilder
    private var cumulativeProfitChart: some View {
        if !viewModel.cumulativeProfitHistory.isEmpty {
            Chart(viewModel.cumulativeProfitHistory) { dataPoint in
                LineMark(
                    x: .value("Date", dataPoint.date),
                    y: .value("Profit", dataPoint.value)
                )
                .foregroundStyle(dataPoint.value >= 0 ? .green : .red)
                .interpolationMethod(.catmullRom)
                
                RuleMark(y: .value("Break Even", 0))
                    .foregroundStyle(.gray.opacity(0.5))
                    .lineStyle(StrokeStyle(lineWidth: 1, dash: [5]))
            }
            .frame(height: 200)
        } else {
            emptyChartView
        }
    }
    
    @ViewBuilder
    private var profitDistributionChart: some View {
        if !viewModel.profitDistribution.isEmpty {
            Chart(viewModel.profitDistribution) { item in
                BarMark(
                    x: .value("Range", item.range),
                    y: .value("Count", item.count)
                )
                .foregroundStyle(item.isPositive ? .green : .red)
            }
            .frame(height: 200)
        } else {
            emptyChartView
        }
    }
    
    private var emptyChartView: some View {
        VStack {
            Image(systemName: "chart.bar.xaxis")
                .font(.system(size: 40))
                .foregroundColor(.gray)
            Text("No data yet")
                .foregroundColor(.secondary)
        }
        .frame(height: 200)
    }
}

// MARK: - Stats Card

struct StatsCard: View {
    let stats: Stats
    
    var body: some View {
        HStack(spacing: 20) {
            StatItem(title: "Total Bets", value: "\(stats.totalBets)", color: .blue)
            Divider()
            StatItem(title: "Win Rate", value: String(format: "%.1f%%", stats.winRate), color: .green)
            Divider()
            StatItem(title: "ROI", value: String(format: "%.1f%%", stats.roi), color: stats.roi >= 0 ? .green : .red)
            Divider()
            StatItem(title: "Total Profit", value: String(format: "$%.2f", stats.totalProfit), color: stats.totalProfit >= 0 ? .green : .red)
            Divider()
            StatItem(title: "Bankroll", value: String(format: "$%.0f", stats.currentBankroll), color: .blue)
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.05)],
                startPoint: .leading,
                endPoint: .trailing
            )
        )
        .cornerRadius(12)
        .padding(.horizontal)
    }
}

struct StatItem: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Chart Card

struct ChartCard<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
                .padding(.horizontal)
            
            content()
                .padding(.horizontal)
        }
        .padding(.vertical)
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }
}

// MARK: - Data Models

struct ChartDataPoint: Identifiable {
    let id = UUID()
    let date: Date
    let value: Double
}

struct ProfitDistributionItem: Identifiable {
    let id = UUID()
    let range: String
    let count: Int
    let isPositive: Bool
}

// MARK: - View Model

@MainActor
class VisualsViewModel: ObservableObject {
    @Published var stats: Stats?
    @Published var bankrollHistory: [ChartDataPoint] = []
    @Published var cumulativeProfitHistory: [ChartDataPoint] = []
    @Published var profitDistribution: [ProfitDistributionItem] = []
    @Published var isLoading = false
    
    private let apiService = APIService()
    
    func loadData() {
        isLoading = true
        
        Task {
            do {
                // Load stats
                stats = try await apiService.fetchStats()
                
                // Load bets for charts
                let bets = try await apiService.fetchBets()
                generateChartData(from: bets)
                
                isLoading = false
            } catch {
                print("Error loading data: \(error)")
                isLoading = false
            }
        }
    }
    
    private func generateChartData(from bets: [Bet]) {
        // Sort bets by date
        let sortedBets = bets.sorted { bet1, bet2 in
            let formatter = DateFormatter()
            formatter.dateFormat = "dd-MM-yyyy"
            let date1 = formatter.date(from: bet1.date) ?? Date()
            let date2 = formatter.date(from: bet2.date) ?? Date()
            return date1 < date2
        }
        
        // Bankroll history
        var bankroll = stats?.currentBankroll ?? 1000.0
        var bankrollData: [ChartDataPoint] = []
        
        let formatter = DateFormatter()
        formatter.dateFormat = "dd-MM-yyyy"
        
        for bet in sortedBets.reversed() {
            if let date = formatter.date(from: bet.date), let profit = bet.profit {
                bankrollData.insert(ChartDataPoint(date: date, value: bankroll), at: 0)
                bankroll -= profit
            }
        }
        self.bankrollHistory = bankrollData
        
        // Cumulative profit
        var cumulativeProfit = 0.0
        var profitData: [ChartDataPoint] = []
        
        for bet in sortedBets {
            if let date = formatter.date(from: bet.date), let profit = bet.profit {
                cumulativeProfit += profit
                profitData.append(ChartDataPoint(date: date, value: cumulativeProfit))
            }
        }
        self.cumulativeProfitHistory = profitData
        
        // Profit distribution
        let completedBets = sortedBets.filter { $0.profit != nil }
        let profits = completedBets.compactMap { $0.profit }
        
        let ranges = [
            (-100.0, -50.0, "-$100 to -$50"),
            (-50.0, -20.0, "-$50 to -$20"),
            (-20.0, 0.0, "-$20 to $0"),
            (0.0, 20.0, "$0 to $20"),
            (20.0, 50.0, "$20 to $50"),
            (50.0, 100.0, "$50 to $100")
        ]
        
        var distribution: [ProfitDistributionItem] = []
        for (min, max, label) in ranges {
            let count = profits.filter { $0 >= min && $0 < max }.count
            if count > 0 {
                distribution.append(ProfitDistributionItem(
                    range: label,
                    count: count,
                    isPositive: min >= 0
                ))
            }
        }
        self.profitDistribution = distribution
    }
}

#Preview {
    VisualsView()
        .frame(width: 1000, height: 800)
}


