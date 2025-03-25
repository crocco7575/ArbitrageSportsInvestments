
#MODIFY THESE#############################

bet_amount = 40
odds_1 = 370
odds_2 = -345


##########################################
def calculate_arbitrage(total_bet, odds1, odds2):
    """
    Calculate optimal bet amounts for arbitrage betting.
    
    Args:
        total_bet (float): Total amount to bet
        odds1 (float): First betting line (American odds format)
        odds2 (float): Second betting line (American odds format)
    
    Returns:
        tuple: (bet1, bet2, payout) if arbitrage exists, None if no arbitrage possible
    """
    
    # Convert American odds to decimal odds
    def american_to_decimal(american_odds):
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    decimal1 = american_to_decimal(odds1)
    decimal2 = american_to_decimal(odds2)
    
    # Calculate implied probabilities
    prob1 = 1 / decimal1
    prob2 = 1 / decimal2
    
    # Check if arbitrage exists (sum of probabilities < 1)
    total_prob = prob1 + prob2
    if total_prob >= 1:
        return None
    
    # Calculate optimal bet amounts
    bet1 = round((total_bet * prob1) / total_prob)
    bet2 = round((total_bet * prob2) / total_prob)
    
    # Calculate expected payout
    payout = min(round(bet1 * decimal1, 2), round(bet2 * decimal2, 2))
    
    # Verify payout is greater than total bet
    if payout < total_bet:
        return None
        
    return bet1, bet2, payout

# Example usage
def print_arbitrage_opportunity(total_bet, odds1, odds2):
    result = calculate_arbitrage(total_bet, odds1, odds2)
    
    if result is None:
        print("No arbitrage opportunity exists for these odds")
        return False
        
    bet1, bet2, payout = result
    profit = payout - total_bet
    
    print(f"Total bet: ${total_bet:.2f}")
    print(f"Bet 1: ${bet1:.2f} @ {odds1}")
    print(f"Bet 2: ${bet2:.2f} @ {odds2}")
    print(f"Expected payout: ${payout:.2f}")
    print(f"Profit: ${profit:.2f}")
    print(f"Return on investment: {(profit/total_bet)*100:.2f}%")
    return True

################# Test cases
print_arbitrage_opportunity(bet_amount, odds_1, odds_2)

######################################################