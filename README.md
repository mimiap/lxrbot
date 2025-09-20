# LXRBot

Telegram + PayPal Webhook integracija.

## Paleidimas lokaliai

1. Nukopijuok `.env.example` į `.env` ir užpildyk reikiamais duomenimis.
2. Įdiek priklausomybes:
   ```bash
   npm install
   ```
3. Paleisk serverį:
   ```bash
   npm start
   ```

## Deploy į Render

- Įkelk šį projektą į GitHub
- Sukurk naują Render Web Service
- Pridėk aplinkos kintamuosius (`Environment` skiltyje)
- Paspausk **Deploy**

Webhook URL bus:
```
https://tavo-app.onrender.com/paypal/webhook
```
