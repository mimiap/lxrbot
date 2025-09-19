import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    if text == "/start":
        bot.send_message(chat_id=chat_id, text="Sveikas! 👋 Botas veikia.")
    elif text == "/buy":
        bot.send_message(chat_id=chat_id, text="Test buy funkcija ✅")
    else:
        bot.send_message(chat_id=chat_id, text=f"Gavai žinutę: {text}")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
