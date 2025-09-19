import os
import logging
from flask import Flask, request, jsonify
import telegram
from imgurpython import ImgurClient

# ---- CONFIG ----
BOT_TOKEN = os.getenv("BOT_TOKEN")  # iš Render Environment
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # tavo ID (ar grupės ID)
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")  # jei reikia PayPal validacijai

# Telegram Bot
bot = telegram.Bot(token=BOT_TOKEN)

# Flask app
app = Flask(__name__)

# Logger (kad matytum Render loguose)
logging.basicConfig(level=logging.INFO)


# ---- ROUTES ----

@app.route("/")
def home():
    return "Bot is running!", 200


# Telegram webhook
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # Pvz.: vartotojas parašo /start
        if text == "/start":
            bot.send_message(chat_id=chat_id, text="Sveikas! Botas veikia 🚀")

        # Pvz.: /buy
        elif text == "/buy":
            bot.send_message(
                chat_id=chat_id,
                text="Paspausk nuorodą apmokėjimui: https://www.paypal.com/paypalme/tavovardas/5"
            )

    return "ok", 200


# PayPal webhook (čia ateina signalai iš PayPal API)
@app.route("/paypal-webhook", methods=["POST"])
def paypal_webhook():
    data = request.get_json()
    logging.info(f"PayPal data: {data}")

    # pvz., patikrinti apmokėjimo statusą
    if data and data.get("event_type") == "PAYMENT.CAPTURE.COMPLETED":
        payer = data["resource"]["payer"]["email_address"]
        amount = data["resource"]["amount"]["value"]

        # siunčiam pranešimą į Telegram
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"Gautas mokėjimas ✅\nSuma: {amount} EUR\nNuo: {payer}"
        )

    return jsonify({"status": "success"}), 200


# ---- RUN LOCAL (tik testams, Render naudoja gunicorn) ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
