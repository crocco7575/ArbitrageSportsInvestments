from telegram.ext import Application, MessageHandler
from telegram.ext.filters import TEXT
import requests

messages_to_send = ["Message 1", "Message 2", "Message 3"] # LIST OF OPEN BET MESSAGES THAT NEED AN OUTCOME
user_responses = []  # To store user responses
message_index = {"value": 1}  # Using a mutable object to allow modification within handler

BOT_TOKEN = '7357326085:AAGruL07kqq15YhfH4vWOHrZiRaXmM2jfK8'

# IF WE WANT WE CAN ALSO SEND A MESSAGE LIKE "IT'S 10:00PM! Respond to the following outcomes with 1 or 2:"

# send the initial message
CHAT_ID = "8133083076" # CHANGE CHAT ID IF YOU WANT TO TEST

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

# Add the MessageHandler to the application
app.add_handler(MessageHandler(TEXT, handle_message))

# Start the bot
app.run_polling()

# REST OF LOGIC WITH USER RESPONSES GOES HERE: