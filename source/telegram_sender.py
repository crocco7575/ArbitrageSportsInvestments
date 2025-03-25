import requests
def send_message(person, message):
# Replace with your bot's token and chat ID
    BOT_TOKEN = "7357326085:AAGruL07kqq15YhfH4vWOHrZiRaXmM2jfK8"
    if person == "Cameron":
        chat_ID = "8133083076"  # Your chat ID
    elif person == "Javi": 
        chat_ID =  "7873187454"
    else: raise Exception("MANUAL THROWN ERROR: Invalid Person given in send_message")

    # Send the message
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {"chat_id": chat_ID, "text": message}

    response = requests.get(url, params=params)
    #print("done")
#send_message("Cameron", "Lets go make some money. Place $ here, place $ here")