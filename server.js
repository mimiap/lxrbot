const express = require("express");
const bodyParser = require("body-parser");
const fetch = require("node-fetch");
require("dotenv").config();

const app = express();
app.use(bodyParser.json());

// PayPal Webhook handler
app.post("/webhook", async (req, res) => {
  console.log("Webhook event:", req.body);

  if (req.body.event_type === "CHECKOUT.ORDER.APPROVED") {
    const amount = req.body.resource.purchase_units[0].amount.value;
    const currency = req.body.resource.purchase_units[0].amount.currency_code;

    const message = `✅ Naujas mokėjimas gautas: ${amount} ${currency}`;

    // Siunčiam į Telegram
    await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: process.env.TELEGRAM_CHAT_ID,
        text: message
      })
    });
  }

  res.sendStatus(200);
});

app.get("/", (req, res) => {
  res.send("PayPal + Telegram botas veikia!");
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Serveris paleistas ant ${PORT}`));
