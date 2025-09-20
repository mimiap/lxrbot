import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

// Saugo apdorotus PayPal event'us
const processedEvents = new Set();

const TELEGRAM_BOT_TOKEN = process.env.BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.CHAT_ID;

async function sendTelegramMessage(text) {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text,
    }),
  });
}

app.post("/webhook", async (req, res) => {
  try {
    const event = req.body;

    // Patikrinam ar jau apdorotas
    if (processedEvents.has(event.id)) {
      console.log(`⚠️ Dubliuotas event praleistas: ${event.id}`);
      return res.sendStatus(200);
    }

    // Įtraukiam į processed sąrašą
    processedEvents.add(event.id);

    if (event.event_type === "PAYMENT.SALE.COMPLETED") {
      const amount = event.resource.amount.total;
      const currency = event.resource.amount.currency;
      await sendTelegramMessage(`✅ Naujas apmokėjimas gautas: ${amount} ${currency}`);
      console.log("Telegram pranešimas išsiųstas.");
    }

    if (event.event_type === "PAYMENT.SALE.REFUNDED") {
      const amount = event.resource.amount.total;
      const currency = event.resource.amount.currency;
      await sendTelegramMessage(`↩️ Grąžintas mokėjimas: ${amount} ${currency}`);
    }

    if (event.event_type === "BILLING.SUBSCRIPTION.CANCELLED") {
      await sendTelegramMessage("⚠️ Klientas atšaukė prenumeratą.");
    }

    res.sendStatus(200);
  } catch (err) {
    console.error("Webhook klaida:", err);
    res.sendStatus(500);
  }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`🚀 Serveris paleistas ant porto ${PORT}`));
