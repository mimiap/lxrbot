import express from "express";
import fetch from "node-fetch";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

// static files
app.use(express.static(path.join(__dirname, "html")));

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

// PayPal webhook handler
app.post("/webhook", async (req, res) => {
  const event = req.body;

  try {
    if (event.event_type === "CHECKOUT.ORDER.APPROVED" || event.event_type === "PAYMENT.CAPTURE.COMPLETED") {
      const payerName = event.resource?.payer?.name?.given_name || "Vartotojas";
      const amount = event.resource?.purchase_units?.[0]?.amount?.value || "???";

      const message = `✅ Naujas mokėjimas!\n👤 ${payerName}\n💵 ${amount} ${event.resource?.purchase_units?.[0]?.amount?.currency_code}`;
      await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: TELEGRAM_CHAT_ID, text: message })
      });
    }

    res.sendStatus(200);
  } catch (err) {
    console.error("Webhook klaida:", err);
    res.sendStatus(500);
  }
});

// start server
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`Serveris paleistas ant ${PORT}`));
