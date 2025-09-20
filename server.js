import express from "express";
import bodyParser from "body-parser";
import dotenv from "dotenv";
import axios from "axios";

dotenv.config();

const app = express();
app.use(bodyParser.json());

const TELEGRAM_API = `https://api.telegram.org/bot${process.env.BOT_TOKEN}`;

// PayPal webhook handler
app.post("/paypal/webhook", async (req, res) => {
  try {
    const event = req.body;

    console.log("PayPal event:", event);

    // Siųsti pranešimą į Telegram
    await axios.post(`${TELEGRAM_API}/sendMessage`, {
      chat_id: process.env.TEST_CHAT_ID,
      text: `Gautas PayPal įvykis: ${event.event_type}`
    });

    res.sendStatus(200);
  } catch (error) {
    console.error("Webhook klaida:", error.message);
    res.sendStatus(500);
  }
});

app.get("/", (req, res) => {
  res.send("LXRBOT veikia ✅");
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveris paleistas ant porto ${PORT}`);
});
