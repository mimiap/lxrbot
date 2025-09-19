import os
import logging
from flask import Flask, request, jsonify
import telegram
from telegram import InputFile
import requests

# ==== CONFIG ====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # iš Render Environment
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # tavo ID arba grupės ID
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")  # jei reikia PayPal validacijai

# Telegram Bot
bot = telegram.Bot(token=BOT_TOKEN)

# Flask app
app = Flask(__name__)

# Logger (kad matytum Render loguose)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "Bot is running!", 200

# --- Telegram Webhook ---
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        if update.message and update.message.photo:
            # paimti didžiausią nuotraukos variantą
            file_id = update.message.photo[-1].file_id
            file = bot.get_file(file_id)

            # atsisiųsti į atmintį
            response = requests.get(file.file_path)

            # nusiųsti atgal kaip failą
            bot.send_document(
                chat_id=TELEGRAM_CHAT_ID,
                document=InputFile(
                    path_or_bytesio=response.content,
                    filename="photo.jpg"
                )
            )

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logging.error(f"Error in telegram_webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- PayPal Webhook ---
@app.route('/paypal-webhook', methods=['POST'])
def paypal_webhook():
    data = request.json
    logging.info(f"PayPal webhook received: {data}")

    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"💳 Naujas PayPal įvykis:\n{data}"
    )

    return jsonify({"status": "received"}), 200

# Startas (naudojamas tik development, Render paleidžia per gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
