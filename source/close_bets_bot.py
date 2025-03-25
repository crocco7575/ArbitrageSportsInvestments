import pandas as pd
import time
import schedule
from telegram.ext import Application, MessageHandler
from telegram.ext.filters import TEXT
import requests
from account_manager import AccountManager
# iterate through each bet in open bets to get the messages to send

messages_to_send = []
df = pd.read_csv("open_bets.csv")
for i in range(df.shape[0]):
    messages_to_send.append(f"{df['Team/Player'][i]} {df['Bet Type'][i]}\n"
                    f"Type 1 if {df['Book 1'][i]} ({df['Side 1'][i]} {df['Line 1'][i]}) hit\n"
                    f"Type 2 if {df['Book 2'][i]} ({df['Side 2'][i]} {df['Line 2'][i]}) hit\n"
                    f"Type 3 if this bet hasn't happened yet\n"
                    f"Type 4 if the bet was never placed or there was an issue. This will cancel the bet.")

# ask which book won for that each open bet through telegram
# Put responses in list. 1 if book 1, 2 if book 2, 3 if not yet played


user_responses = []  # To store user responses
message_index = {"value": 1}  # Using a mutable object to allow modification within handler

BOT_TOKEN = '7357326085:AAGruL07kqq15YhfH4vWOHrZiRaXmM2jfK8'

# IF WE WANT WE CAN ALSO SEND A MESSAGE LIKE "IT'S 10:00PM! Respond to the following outcomes with 1 or 2:"

# send the initial message
CHAT_ID = "8133083076"# CHANGE CHAT ID IF YOU WANT TO TEST

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
params = {"chat_id": CHAT_ID, "text": messages_to_send[0]}

response = requests.get(url, params=params)

# Create the Application instance
app = Application.builder().token(BOT_TOKEN).build()

# Define an async callback to handle messages
async def handle_message(update, context):
    global message_index
    # Log user response and store it in the list
    user_responses.append(update.message.text)
    
    # Check if there are more messages to send
    if message_index["value"] < len(messages_to_send):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages_to_send[message_index["value"]]
        )
        message_index["value"] += 1
    else:
        # All messages sent and last response recorded
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="All outcomes recieved. Thank you!"
        )
        print("All responses recorded:", user_responses)
        app.stop_running()  # Stop the bot
def main():
    # Add the MessageHandler to the application
    app.add_handler(MessageHandler(TEXT, handle_message))

    # Start the bot
    app.run_polling()
    # if 1, add payout to that account and remove bet from open bets. if 2, add payout to that account and remove bet from open bets. If 3, leave it.
    row = 0
    paysheet = pd.read_csv('weeklypaysheet.csv')
    new_rows = []

    for response in user_responses:
        if int(response) == 1:
            # Update book 1 balance
            with open(f"../betting_accounts/{df['Book 1'][row]}.txt", "r+") as f:
                # Read all lines from the file
                lines = f.readlines()

                # Calculate the new balance and update the first line
                old_balance = round(float(lines[0].strip()), 2)
                new_balance = round(df['Payout'][row], 2) + old_balance
                lines[0] = f"{new_balance}\n"
                f.seek(0)
                f.writelines(lines)

            
            # Create new row for paysheet
            new_rows.append({
                'Account 1': df['Book 1'][row],
                'Account 2': df['Book 2'][row],
                'Amount': round(df['Bet 2'][row], 2) + round(df['Profit'][row]/2, 2)
            })
            
        elif int(response) == 2:
            # Update book 2 balance
            with open(f"../betting_accounts/{df['Book 2'][row]}.txt", "r+") as f:
                lines = f.readlines()

                # Calculate the new balance and update the first line
                old_balance = round(float(lines[0].strip()), 2)
                new_balance = round(df['Payout'][row], 2) + old_balance
                lines[0] = f"{new_balance}\n"
                f.seek(0)
                f.writelines(lines)
                
            # Create new row for paysheet
            new_rows.append({
                'Account 1': df['Book 1'][row],
                'Account 2': df['Book 2'][row],
                'Amount': round(df['Bet 1'][row], 2) + round(df['Profit'][row]/2, 2)
            })
        elif int(response) == 4: 
            with open(f"../betting_accounts/{df['Book 1'][row]}.txt", "r+") as f1:
                lines = f1.readlines()
                old_balance = round(float(lines[0].strip()), 2)
                new_balance = round(df['Bet 1'][row], 2) + old_balance
                lines[0] = f"{new_balance}\n"
                f1.seek(0)
                f1.writelines(lines)
            with open(f"../betting_accounts/{df['Book 2'][row]}.txt", "r+") as f2:
                lines = f2.readlines()
                old_balance = round(float(lines[0].strip()), 2)
                new_balance = round(df['Bet 2'][row], 2) + old_balance
                lines[0] = f"{new_balance}\n"
                f2.seek(0)
                f2.writelines(lines)
        row += 1

    # Append new rows to paysheet
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        paysheet = pd.concat([paysheet, new_rows_df], ignore_index=True)
        paysheet.to_csv('weeklypaysheet.csv', index=False)

    for index in range(len(user_responses)):
        if user_responses[index] == '1' or user_responses[index] == '2' or user_responses[index] == '4':
            df.drop(index, inplace=True)
    df.to_csv('open_bets.csv')


    txt_names = ["Fanatics", "FanDuel", "Bet365", "DraftKings", "ESPNBet", "BetMGM", "Caesars", "HardRock", "BetRivers"]
    manager = AccountManager(txt_names)
    manager.update_totals()
    print("Done")
if __name__ == "__main__":
    main()
#     #Schedule the script to run at 5 PM and 8 PM daily

#     schedule.every().day.at("22:00").do(main)

#     print("Scheduler is running. Waiting for tasks...")
# # Keep the script running to execute scheduled tasks
# while True:
#     schedule.run_pending()
#     time.sleep(1)
# Make notes in paysheets. Example: Account 1 and Account 2. Account 1 wins. Account 1 owes Account 2: Bet 2 + Profit/2

