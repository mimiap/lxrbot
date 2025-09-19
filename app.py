import os
import logging
from flask import Flask, request, jsonify
import telegram
from telegram import InputFile

# ---- CONFIG ----
BOT_TOKEN = os.getenv("BOT_TOKEN")  # iš Render Environment
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # tavo ID arba grupės ID
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")  # jei reikia PayPal validacijai

# Telegram Bot
bot = telegram.Bot(token=BOT_TOKEN)

# Flask app
app = Flask(__name__)

# Logger (kad matytum Render loguose)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    logging.info(f"Got update: {data}")

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            bot.send_message(chat_id=chat_id, text="Sveikas! Botas veikia 🚀")
        else:
            bot.send_message(chat_id=chat_id, text=f"Gavai žinutę: {text}")

    return jsonify({"status": "ok"})

@app.route("/paypal", methods=["POST"])
def paypal_webhook():
    # Čia gali pridėti PayPal validaciją pagal savo logiką
    secret = request.headers.get("Paypal-Secret")
    if secret == PAYPAL_SECRET:
        logging.info("PayPal įvykis gautas")
        return jsonify({"status": "paypal ok"})
    else:
        return jsonify({"error": "Unauthorized"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
