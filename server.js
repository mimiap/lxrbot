import express from "express";
import bodyParser from "body-parser";
import fetch from "node-fetch";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(bodyParser.json());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// >>> pridėta eilutė, kad galėtum atidaryti test.html
app.use(express.static(__dirname));

// PayPal webhook
app.post("/paypal-webhook", async (req, res) => {
  console.log("Webhook gautas:", req.body);

  try {
    await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: process.env.TELEGRAM_CHAT_ID,
        text: "✅ Naujas mokėjimas gautas per PayPal!"
      })
    });
    res.sendStatus(200);
  } catch (err) {
    console.error("Klaida siunčiant į Telegram:", err);
    res.sendStatus(500);
  }
});

const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Serveris paleistas ant porto ${PORT}`);
});
