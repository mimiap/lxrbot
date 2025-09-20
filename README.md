# LXRBot PayPal + Telegram

## Diegimas
1. Įkelk failus į GitHub repozitoriją.
2. Deploy Render.com su nustatymais:
   - Build Command: `npm install`
   - Start Command: `node server.js`
3. Render Settings -> Environment Variables įrašyk:
   - PAYPAL_CLIENT_ID
   - PAYPAL_SECRET
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID

4. Testuok `https://tavo-app.onrender.com/html/test.html`
