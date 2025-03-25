import pandas as pd
from account_manager import AccountManager
import datetime

txt_names = ["Fanatics", "FanDuel", "Bet365", "DraftKings", "ESPNBet", "BetMGM", "Caesars", "HardRock", "BetRivers"]
manager = AccountManager(txt_names)
df = pd.read_csv('weeklypaysheet.csv')
for _, row in df.iterrows():
    with open (f"../betting_accounts/{row['Account 1']}.txt", "r+") as file:
        lines = file.readlines()
        total =float(lines[0].strip())
        total-=row['Amount']
        lines[0] = f"{total}\n"
        file.seek(0)
        file.writelines(lines)
    with open (f"../betting_accounts/{row['Account 2']}.txt", "r+") as file:
        lines = file.readlines()
        total =float(lines[0].strip())
        total+=row['Amount']
        lines[0] = f"{total}\n"
        file.seek(0)
        file.writelines(lines)
df.to_csv(f"../weekly_dataframes/{datetime.date.today()}-paysheet-record.csv")
df.drop(df.index, inplace=True)
df.to_csv("weeklypaysheet.csv")
manager.update_totals()
print("done")

    