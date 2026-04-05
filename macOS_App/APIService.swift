///
//  APIService.swift
//  NBA_PICKS
//
//  Service to communicate with Python backend API
//

import Foundation

class APIService: ObservableObject {
    private let baseURL = "http://localhost:5000/api"
    
    // MARK: - Health Check
    
    func checkHealth() async throws -> Bool {
        let url = URL(string: "\(baseURL)/health")!
        let (_, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return false
        }
        
        return httpResponse.statusCode == 200
    }
    
    // MARK: - Games
    
    func fetchGames(for date: String) async throws -> [Game] {
        let url = URL(string: "\(baseURL)/games/\(date)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        
        let response = try JSONDecoder().decode(GamesResponse.self, from: data)
        
        if response.success {
            return response.games
        } else {
            throw APIError.requestFailed
        }
    }
    
    // MARK: - Picks
    
    func calculatePicks(
        date: String,
        games: [GameWithOdds],
        minEV: Double = 0.05,
        betAmount: Double = 20
    ) async throws -> [Pick] {
        let url = URL(string: "\(baseURL)/picks")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = PicksRequest(
            date: date,
            games: games,
            minEV: minEV,
            betAmount: betAmount
        )
        
        request.httpBody = try JSONEncoder().encode(requestBody)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(PicksResponse.self, from: data)
        
        if response.success {
            return response.picks
        } else {
            throw APIError.requestFailed
        }
    }
    
    // MARK: - Bets
    
    func fetchBets() async throws -> [Bet] {
        let url = URL(string: "\(baseURL)/bets")!
        let (data, _) = try await URLSession.shared.data(from: url)
        
        let response = try JSONDecoder().decode(BetsResponse.self, from: data)
        
        if response.success {
            return response.bets
        } else {
            throw APIError.requestFailed
        }
    }
    
    func saveBet(bet: Bet) async throws {
        let url = URL(string: "\(baseURL)/bets")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        request.httpBody = try JSONEncoder().encode(bet)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.requestFailed
        }
    }
    
    func updateBetResult(betId: String, won: Bool) async throws {
        let url = URL(string: "\(baseURL)/bets/\(betId)/result")!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["won": won]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.requestFailed
        }
    }
    
    // MARK: - Stats
    
    func fetchStats() async throws -> Stats {
        let url = URL(string: "\(baseURL)/stats")!
        let (data, _) = try await URLSession.shared.data(from: url)
        
        let response = try JSONDecoder().decode(StatsResponse.self, from: data)
        
        if response.success {
            return response.stats
        } else {
            throw APIError.requestFailed
        }
    }
    
    // MARK: - Elo Rankings
    
    func fetchEloRankings() async throws -> [EloRanking] {
        let url = URL(string: "\(baseURL)/elo-rankings")!
        let (data, _) = try await URLSession.shared.data(from: url)
        
        let response = try JSONDecoder().decode(EloResponse.self, from: data)
        
        if response.success {
            return response.rankings
        } else {
            throw APIError.requestFailed
        }
    }
}

// MARK: - Error Handling

enum APIError: LocalizedError {
    case invalidURL
    case requestFailed
    case decodingError
    case serverError(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .requestFailed:
            return "Request failed"
        case .decodingError:
            return "Failed to decode response"
        case .serverError(let message):
            return "Server error: \(message)"
        }
    }
}


