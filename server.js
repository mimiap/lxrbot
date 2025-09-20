require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const fetch = require('node-fetch');

const app = express();
app.use(bodyParser.json());

// PayPal
const PAYPAL_CLIENT_ID = process.env.PAYPAL_CLIENT_ID;
const PAYPAL_SECRET = process.env.PAYPAL_SECRET;
const PAYPAL_API = "https://api-m.paypal.com";

// Telegram
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

// Test route
app.get('/', (req, res) => {
  res.send('LXRBOT is running.');
});

// PayPal webhook
app.post('/webhook', async (req, res) => {
  console.log('Webhook received:', req.body);
  try {
    if (req.body.event_type === "CHECKOUT.ORDER.APPROVED") {
      const amount = req.body.resource.purchase_units[0].amount.value;
      const currency = req.body.resource.purchase_units[0].amount.currency_code;
      const message = `💳 Naujas apmokėjimas: ${amount} ${currency}`;

      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: message
        })
      });
    }
    res.sendStatus(200);
  } catch (err) {
    console.error("Klaida webhook apdorojant:", err);
    res.sendStatus(500);
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Serveris veikia ant porto ${PORT}`));
