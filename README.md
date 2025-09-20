# LXR Bot

Telegram + PayPal webhook integracija.

## Paleidimas

1. Įkelk šiuos failus į savo GitHub repo.
2. Deploy per [Render](https://render.com).
3. Pridėk **Environment Variables**:

```
BOT_TOKEN= tavo telegram bot token
CHAT_ID= tavo telegram chat id
PAYPAL_CLIENT_ID= tavo paypal client id
PAYPAL_CLIENT_SECRET= tavo paypal client secret
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID= tavo webhook id
```

## Testavimas

Naudok PayPal Sandbox webhook simulatorių su adresu:

```
https://tavoservisas.onrender.com/webhook
```
