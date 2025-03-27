from scraper import scrapeOdds
import time
import schedule
import pandas as pd
from io import StringIO
import os
from datetime import date
from master_message_send import send_update_texts
txt_names = ["Fanatics", "FanDuel", "Bet365", "DraftKings", "ESPNBet", "BetMGM", "Caesars", "HardRock", "BetRivers"]
url = "https://www.oddsshopper.com/tools/arbitrage/MI"

class AccountManager:
    def __init__(self, txt_names, initial_balance=100):
        self.txt_names = txt_names
        self.initial_balance = initial_balance
        self.initialize_files()

    def initialize_files(self):
        """Create txt files for each sportsbook if they don't exist."""
        for name in self.txt_names:
            if not os.path.exists(f"../betting_accounts/{name}.txt"):
                with open(f"../betting_accounts/{name}.txt", "w") as f:
                    f.write(str(self.initial_balance))

    def read_balance(self, book):
        """Read the current balance from a sportsbook's file."""
        with open(f"../betting_accounts/{book}.txt", "r") as f:
            return round(float(f.readline().strip()), 2)

    def read_bets(self, book):
        """Read all existing bets from a sportsbook's file."""
        with open(f"../betting_accounts/{book}.txt", "r") as f:
            lines = f.readlines()
        return [line.strip() for line in lines[1:]]  # Skip balance line

    def update_account(self, book, new_balance, bet_name=None):
        """Update a sportsbook's balance and add new bet if provided."""
        existing_bets = self.read_bets(book)
        
        with open(f"../betting_accounts/{book}.txt", "w") as f:
            f.write(f"{new_balance}\n")  # Write new balance
            for bet in existing_bets:
                f.write(f"{bet}\n")  # Write existing bets
            if bet_name and bet_name not in existing_bets:
                f.write(f"{bet_name}\n")  # Add new bet if it doesn't exist
    def update_totals(self):
        # Update totals
        new_total = 0
        for file_name in txt_names:
            with open (f"../betting_accounts/{file_name}.txt", "r+") as file:
                lines = file.readlines()
                new_total+=float(lines[0].strip())
        with open("../betting_accounts/TOTALS.txt", "r+") as file:
            lines = file.readlines()
            total = float(lines[0].strip())
            #new_total = round(total + profit, 2)
            lines[0] = str(round(new_total, 2))
            file.seek(0)
            file.writelines(lines)
            file.truncate()
    def process_arbitrage_opportunities(self, df):
        """
        Process new arbitrage opportunities and update account balances.
        
        Args:
            df (pandas.DataFrame): DataFrame containing arbitrage opportunities with columns:
                Team/Player, Bet Type, Book 1, Book 2, Profit
        """
        # Process each arbitrage opportunity
        rows_to_drop = []
        for index, row in df.iterrows():
            bet_name = f"{date.today()} {row['Team/Player']} {row['Bet Type']}"
            profit_per_book = round(row['Profit'] / 2, 2)  # Split profit between two books
            
            # Process Book 1
            if row['Book 1'] in self.txt_names:
                current_balance = self.read_balance(row['Book 1'])
                existing_bets = self.read_bets(row['Book 1'])
                
                if bet_name not in existing_bets and row['Bet 1'] <= current_balance:
                    new_balance = current_balance - round(row['Bet 1'], 2)
                    self.update_account(row['Book 1'], new_balance, bet_name)
                else:
                    rows_to_drop.append(index)
                    continue
            
            # Process Book 2
            if row['Book 2'] in self.txt_names:
                current_balance = self.read_balance(row['Book 2'])
                existing_bets = self.read_bets(row['Book 2'])
                
                if bet_name not in existing_bets and row['Bet 2'] <= current_balance:
                    new_balance = current_balance - round(row['Bet 2'], 2)
                    self.update_account(row['Book 2'], new_balance, bet_name)
                else: 
                    rows_to_drop.append(index)
                    continue
        
        # Drop rows that couldn't be processed
        df.drop(rows_to_drop, inplace=True)
def main():
    open_bets = pd.read_csv("open_bets.csv")
    # Initialize account manager with sportsbook names
    manager = AccountManager(txt_names)
    
    # Get arbitrage opportunities from scraper
    odds_data = scrapeOdds(url)
    manager.process_arbitrage_opportunities(odds_data)
    open_bets = pd.concat([open_bets, odds_data], ignore_index=True).drop_duplicates(subset=['Team/Player'])
    open_bets.to_csv("open_bets.csv")
    # Process opportunities and update accounts
    
    send_update_texts("Cameron")
    send_update_texts("Javi")
    manager.update_totals()

if __name__ == "__main__":
        # Schedule the script to run at 5 PM and 8 PM daily
        main()
    # schedule.every().day.at("14:00").do(main)
    # schedule.every().day.at("20:00").do(main)

    # print("Scheduler is running. Waiting for tasks...")

    # # Keep the script running to execute scheduled tasks
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)