import os
from flask import Flask, request
import telegram

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)

@app.route('/')
def index():
    return "Bot is running!", 200

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    if text == "/start":
        bot.sendMessage(chat_id=chat_id, text="Labas! 👋 Boto testas veikia.")
    else:
        bot.sendMessage(chat_id=chat_id, text=f"Gavai žinutę: {text}")

    return 'ok'

if __name__ == '__main__':
    app.run(port=10000)
