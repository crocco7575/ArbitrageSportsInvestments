import pandas as pd


columns = ["Team/Player", "Bet Type", "Side 1", "Line 1", "Book 1", "Odds 1", "Side 2", "Line 2", "Book 2", "Odds 2", "Link 1", "Link 2", "Winner"]

df = pd.DataFrame(columns=columns)

# Save the DataFrame as a CSV file
df.to_csv("./open_bets.csv", index=False)

print("CSV file created successfully as 'empty_bets.csv'")