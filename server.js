import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

// PayPal webhook listener
app.post("/webhook", async (req, res) => {
  console.log("Webhook received:", req.body);
  
  // Telegram message
  const message = "✅ Mokėjimas gautas, ačiū už jūsų pirkimą!";
  const telegramUrl = `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  
  await fetch(telegramUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: process.env.TELEGRAM_CHAT_ID,
      text: message
    })
  });

  res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Serveris paleistas ant porto ${PORT}`));
