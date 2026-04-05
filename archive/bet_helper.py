"""
Bet Placement Helper
====================

Helper tools for placing bets:
- Bet slip generator
- Quick copy bet details
- Bankroll calculator
- Bet confirmation checklist

M3 Phase 3: Bet Placement Helper
"""

import json
from datetime import datetime
from typing import Dict, List


class BetHelper:
    """Helper tools for placing bets"""
    
    def __init__(self):
        """Initialize bet helper"""
        pass
    
    def generate_bet_slip(self, recommendations: List[Dict]) -> str:
        """
        Generate formatted bet slip
        
        Args:
            recommendations: List of bet recommendations
        
        Returns:
            Formatted bet slip text
        """
        slip = []
        slip.append("=" * 60)
        slip.append("🎯 NBA BET SLIP")
        slip.append("=" * 60)
        slip.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        slip.append(f"Total Bets: {len(recommendations)}")
        slip.append("")
        
        total_wagered = 0
        
        for i, rec in enumerate(recommendations, 1):
            best_side = rec['best_bet']
            bet = rec[f'{best_side}_bet']
            
            slip.append(f"BET #{i}")
            slip.append(f"Game: {rec['home_team']} vs {rec['away_team']}")
            slip.append(f"Pick: {bet['team']} ({bet['moneyline']:+d})")
            slip.append(f"Bet Amount: ${bet['bet_amount']:.2f}")
            slip.append(f"Win Probability: {bet['true_probability']:.1%}")
            slip.append(f"Expected Value: {bet['ev_percent']:+.1f}%")
            slip.append("")
            
            total_wagered += bet['bet_amount']
        
        slip.append("=" * 60)
        slip.append(f"TOTAL WAGERED: ${total_wagered:.2f}")
        slip.append("=" * 60)
        
        return "\n".join(slip)
    
    def copy_bet_details(self, bet: Dict) -> str:
        """
        Format bet details for easy copying
        
        Args:
            bet: Bet dictionary
        
        Returns:
            Formatted string for copying
        """
        return f"{bet['team']} {bet['moneyline']:+d} | ${bet['bet_amount']:.2f}"
    
    def calculate_bankroll_requirements(
        self,
        num_bets: int,
        bet_amount: float,
        safety_margin: int = 20
    ) -> Dict:
        """
        Calculate bankroll requirements
        
        Args:
            num_bets: Number of bets to place
            bet_amount: Amount per bet
            safety_margin: Number of losing bets to survive
        
        Returns:
            Dictionary with bankroll calculations
        """
        total_wagered = num_bets * bet_amount
        min_bankroll = safety_margin * bet_amount
        recommended_bankroll = min_bankroll * 2  # 2x safety margin
        
        return {
            'num_bets': num_bets,
            'bet_amount': bet_amount,
            'total_wagered': total_wagered,
            'min_bankroll': min_bankroll,
            'recommended_bankroll': recommended_bankroll,
            'safety_margin': safety_margin
        }
    
    def bet_confirmation_checklist(self) -> str:
        """
        Generate bet confirmation checklist
        
        Returns:
            Formatted checklist
        """
        checklist = []
        checklist.append("✅ BET CONFIRMATION CHECKLIST")
        checklist.append("=" * 60)
        checklist.append("")
        checklist.append("Before placing bet, confirm:")
        checklist.append("  [ ] Checked model prediction")
        checklist.append("  [ ] Verified EV is positive (>5%)")
        checklist.append("  [ ] Confirmed bet amount ($20 flat)")
        checklist.append("  [ ] Checked injury reports")
        checklist.append("  [ ] Verified odds on Underdog Fantasy")
        checklist.append("  [ ] Confirmed sufficient bankroll")
        checklist.append("  [ ] Not chasing losses")
        checklist.append("  [ ] Following betting plan")
        checklist.append("")
        checklist.append("=" * 60)
        
        return "\n".join(checklist)
    
    def print_quick_reference(self):
        """Print quick reference guide"""
        print("\n" + "=" * 70)
        print("📋 QUICK REFERENCE GUIDE")
        print("=" * 70)
        
        print("\n💰 Bankroll Management:")
        print("   • Starting: $1,000")
        print("   • Bet Size: $20 flat (2%)")
        print("   • Never bet more than 2-3% per game")
        print("   • If bankroll drops to $500, reduce to $10 bets")
        
        print("\n🎯 Betting Rules:")
        print("   • Only bet positive EV (>5%)")
        print("   • Prefer high confidence bets (>65%)")
        print("   • Max 3-5 bets per day")
        print("   • Never chase losses")
        
        print("\n📊 When to Stop:")
        print("   • 10+ losing bets in a row: Pause and review")
        print("   • Negative ROI after 100 bets: Reassess strategy")
        print("   • Bankroll below $500: Reduce bet size")
        
        print("\n" + "=" * 70)


def main():
    """Run bet helper examples"""
    print("=" * 70)
    print("🛠️  BET PLACEMENT HELPER")
    print("=" * 70)
    
    helper = BetHelper()
    
    # Example: Generate bet slip
    print("\n1️⃣  Generating bet slip...")
    sample_recs = [
        {
            'home_team': 'Lakers',
            'away_team': 'Warriors',
            'best_bet': 'home',
            'home_bet': {
                'team': 'Lakers',
                'moneyline': +120,
                'bet_amount': 20.0,
                'true_probability': 0.636,
                'ev_percent': 40.0
            }
        }
    ]
    
    bet_slip = helper.generate_bet_slip(sample_recs)
    print(bet_slip)
    
    # Example: Bankroll calculator
    print("\n2️⃣  Calculating bankroll requirements...")
    bankroll_calc = helper.calculate_bankroll_requirements(
        num_bets=5,
        bet_amount=20.0,
        safety_margin=20
    )
    
    print(f"   For {bankroll_calc['num_bets']} bets at ${bankroll_calc['bet_amount']:.2f} each:")
    print(f"   Total Wagered: ${bankroll_calc['total_wagered']:.2f}")
    print(f"   Min Bankroll: ${bankroll_calc['min_bankroll']:.2f}")
    print(f"   Recommended: ${bankroll_calc['recommended_bankroll']:.2f}")
    
    # Example: Confirmation checklist
    print("\n3️⃣  Bet confirmation checklist...")
    print(helper.bet_confirmation_checklist())
    
    # Quick reference
    helper.print_quick_reference()
    
    print("\n✅ BET HELPER COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

