# Telegram PayPal Bot (ready for Render)

This project includes:
- `app.py` — Flask app that creates PayPal orders, verifies PayPal webhook signatures, and sends a secure download link to users via Telegram.
- `static/productivity_bundle.zip` — the product bundle (Weekly Planner, Budget Tracker, Habit Tracker).

IMPORTANT: **This project does NOT contain any secret keys**. Set the necessary environment variables in Render or locally.

## Environment variables (required)
- `TELEGRAM_TOKEN` = your Telegram bot token (from @BotFather)
- `PAYPAL_CLIENT_ID` = PayPal REST app client id
- `PAYPAL_CLIENT_SECRET` = PayPal REST app client secret
- `PAYPAL_MODE` = `sandbox` or `live` (default: sandbox)
- `PAYPAL_WEBHOOK_ID` = the webhook ID you get after creating a webhook in PayPal dashboard (used for signature verification)
- `BASE_URL` = your public app URL (e.g. https://your-app.onrender.com)

## Deploy steps (quick)
1. Push this repo to GitHub.
2. On Render.com, create a new Web Service and connect the repo.
   - Build command: leave empty (Render uses pip install from requirements.txt) or set to: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Add env vars above in Render Environment settings.
3. Deploy and copy the public URL (this will be your `BASE_URL`).
4. In PayPal Developer Dashboard (REST app):
   - Create a Webhook and set the URL to: `https://<your-base-url>/paypal-webhook`
   - Select relevant events: `CHECKOUT.ORDER.APPROVED`, `PAYMENT.CAPTURE.COMPLETED`, `CHECKOUT.ORDER.COMPLETED`
   - After creating the webhook, note the **Webhook ID** and set it to `PAYPAL_WEBHOOK_ID` env var in Render.
5. Set Telegram webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook" -d "url=$BASE_URL/telegram-webhook"
   ```

## How it works
- User messages the bot `/buy`.
- Server creates a PayPal Order and replies with the approval URL.
- User completes payment on PayPal.
- PayPal calls your webhook `/paypal-webhook`.
- Server verifies webhook signature with PayPal's `verify-webhook-signature` API using `PAYPAL_WEBHOOK_ID`.
- If verification succeeds and event is a completed payment, server generates a one-time download token and sends the secure download link to the buyer via Telegram.

## Security notes (read carefully)
- **Do not** store secrets in code. Use Render environment variables.
- Webhook verification is mandatory — do not skip it.
- The in-memory `DOWNLOAD_STORE` is for demo/testing only. Use a persistent DB in production.
- Consider expiring tokens and limiting downloads per token.

## Local testing (with ngrok)
- Run the app locally and expose via `ngrok http 5000`
- Set `BASE_URL` to your ngrok HTTPS URL.
- Create a PayPal sandbox REST app and webhook (use the sandbox API base).
- Add your sandbox webhook ID and sandbox client credentials to env vars.
- Set Telegram webhook to `<ngrok-url>/telegram-webhook`.

## Questions
If you want, I can also:
- Add database support (Postgres on Render).
- Add GitHub Actions workflow for CI / auto-deploy to Render.
- Harden security (rate limiting, signed download tokens in DB, logging).
