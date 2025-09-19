import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    if text.lower() == "/start":
        bot.sendMessage(chat_id=chat_id, text="Sveikas! Botas veikia 🚀")
    else:
        bot.sendMessage(chat_id=chat_id, text=f"Gavai žinutę: {text}")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
