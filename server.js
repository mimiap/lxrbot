import express from "express";
import fetch from "node-fetch";
import path from "path";

const app = express();
app.use(express.json());

// ✅ Čia pataisymas — leis pasiekti failus iš šaknies (root)
app.use(express.static(process.cwd()));

// Saugo apdorotus PayPal event’us
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
  const event = req.body;
  if (processedEvents.has(event.id)) {
    return res.sendStatus(200);
  }
  processedEvents.add(event.id);

  await sendTelegramMessage(`Naujas PayPal įvykis: ${JSON.stringify(event)}`);
  res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveris veikia ant porto ${PORT}`);
});
