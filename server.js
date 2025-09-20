import express from "express";
import bodyParser from "body-parser";
import fetch from "node-fetch";

const app = express();
app.use(bodyParser.json());

const TELEGRAM_TOKEN = process.env.BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const PORT = process.env.PORT || 10000;

// PayPal webhook
app.post("/paypal/webhook", async (req, res) => {
  try {
    const event = req.body;

    if (event.event_type === "PAYMENT.SALE.COMPLETED") {
      const amount = event.resource.amount.total;
      const currency = event.resource.amount.currency;
      const message = `✅ Naujas apmokėjimas gautas: ${amount} ${currency}`;

      await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: message,
        }),
      });
    }

    res.sendStatus(200);
  } catch (err) {
    console.error("Klaida webhooke:", err);
    res.sendStatus(500);
  }
});

app.get("/", (req, res) => res.send("Botas gyvas ✅"));

app.listen(PORT, () =>
  console.log(`Serveris paleistas ant porto ${PORT}`)
);
