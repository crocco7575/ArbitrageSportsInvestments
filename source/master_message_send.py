from telegram_sender import send_message
import pandas as pd

def send_update_texts(recipient):
    df = pd.read_csv("arbitrage_opportunities.csv")
    #for (i in range(7))
    
    
    #print(a)
    if (df.empty):
        print("df is empty")
    else:
        a = df["Team/Player"][0]
        for i in range(df.shape[0]):
                message = (f"MAKE A BET: {df['Team/Player'][i]}  --> {df['Bet Type'][i]}\n\n"
                        f"Bet 1: {df['Side 1'][i]} {df['Line 1'][i]} || PUT ${df['Bet 1'][i]} @ {df['Odds 1'][i]} with {df['Book 1'][i]} here: {df['Link 1'][i]} \n\n"
                        f"Bet 2: {df['Side 2'][i]} {df['Line 2'][i]} || PUT ${df['Bet 2'][i]} @ {df['Odds 2'][i]} with {df['Book 2'][i]} here: {df['Link 2'][i]}\n\n"
                        f"ENSURE Payout is AT OR ABOVE ${df['Payout'][i]} for each bet")
                send_message(recipient, message)

    
#send_update_texts("Cameron")