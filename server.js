const express = require("express");
const bodyParser = require("body-parser");
const path = require("path");
require("dotenv").config();

const app = express();
app.use(bodyParser.json());

// testinis HTML
app.get("/test.html", (req, res) => {
  res.sendFile(path.join(__dirname, "test.html"));
});

// Telegram webhook (placeholder)
app.post("/webhook", (req, res) => {
  console.log("Telegram update:", req.body);
  res.sendStatus(200);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveris paleistas ant porto ${PORT}`);
});