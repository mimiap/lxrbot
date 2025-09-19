import os
from flask import Flask, request, jsonify
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.getenv("BOT_TOKEN")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# /start komanda
@app.route(f"/{TOKEN}", methods=["POST"])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    if text == "/start":
        bot.sendMessage(chat_id=chat_id, text="Sveikas! Paspausk /buy kad įsigytum produktą.")
    elif text == "/buy":
        keyboard = [
            [InlineKeyboardButton("💳 Mokėti per PayPal", url="https://www.sandbox.paypal.com/checkoutnow?token=FAKE_TOKEN")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.sendMessage(chat_id=chat_id, text="Spausk mygtuką ir atlik mokėjimą:", reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id=chat_id, text="Nežinau tokios komandos 🤔")

    return "ok"


# PayPal webhook endpoint
@app.route("/paypal-webhook", methods=["POST"])
def paypal_webhook():
    data = request.json

    # Čia reikėtų patikrinti PayPal signature (kol kas minimaliai darom)
    if data and "event_type" in data:
        if data["event_type"] == "CHECKOUT.ORDER.APPROVED":
            # Ištraukiam pirkėjo info
            payer_email = data["resource"]["payer"]["email_address"]
            # Siunčiam produktą (čia galima padaryti DB lookup ir pan.)
            # Pvz.: siunčiam nuorodą į PDF
            bot.sendMessage(chat_id=os.getenv("TEST_CHAT_ID"), text=f"✅ Mokėjimas gautas iš {payer_email}\nŠtai tavo produktas: https://tavo-domenas.lt/download.zip")

    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return "Botas gyvas!"

if __name__ == "__main__":
    app.run(port=10000)

print("Chat ID:", chat_id)
