import os
import json
import uuid
import time
import requests
from flask import Flask, request, jsonify, send_file, abort, url_for

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # required
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")  # required
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")  # required
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")  # 'sandbox' or 'live'
PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID")  # required for webhook signature verification
BASE_URL = os.environ.get("BASE_URL")  # https://your-render-url.onrender.com - required

if not (TELEGRAM_TOKEN and PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET and PAYPAL_WEBHOOK_ID and BASE_URL):
    raise RuntimeError("Set TELEGRAM_TOKEN, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_WEBHOOK_ID and BASE_URL env variables before running.")

app = Flask(__name__)
app.config['DOWNLOAD_STORE'] = {}  # token -> file path (demo only). Use DB in production.

# === PayPal client setup ===
if PAYPAL_MODE == "live":
    paypal_env = LiveEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
    PAYPAL_API_BASE = "https://api-m.paypal.com"
else:
    paypal_env = SandboxEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
    PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

paypal_client = PayPalHttpClient(paypal_env)

# === Helpers ===
def telegram_send_message(chat_id: int, text: str, parse_mode=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    r = requests.post(url, json=payload, timeout=15)
    return r.ok, r.json() if r.headers.get('Content-Type','').startswith('application/json') else r.text

def telegram_send_document(chat_id: int, file_url: str, filename: str):
    # Telegram will fetch file from file_url (must be publicly reachable)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    payload = {"chat_id": chat_id, "document": file_url, "caption": filename}
    r = requests.post(url, data=payload, timeout=30)
    return r.ok, r.json() if r.headers.get('Content-Type','').startswith('application/json') else r.text

# === Create PayPal order endpoint ===
@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.json or {}
    chat_id = data.get('chat_id')
    if not chat_id:
        return jsonify({"error": "chat_id required"}), 400

    # Create order via PayPal SDK (one-time purchase)
    request_order = OrdersCreateRequest()
    request_order.prefer('return=representation')
    request_order.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "EUR",
                "value": "6.00"   # price (change if needed)
            },
            "description": "Productivity Bundle (Weekly Planner + Budget + Habit Tracker)"
        }],
        "application_context": {
            "return_url": f"{BASE_URL}/paypal-return?chat_id={chat_id}",
            "cancel_url": f"{BASE_URL}/paypal-cancel?chat_id={chat_id}"
        }
    })
    try:
        response = paypal_client.execute(request_order)
        order = response.result
        approval_url = None
        for link in order.links:
            if link.rel == "approve":
                approval_url = link.href
        # store mapping from order id -> chat_id to identify user on webhook (demo store)
        app.config['DOWNLOAD_STORE'][order.id] = {"chat_id": int(chat_id), "status": "CREATED", "created": time.time()}
        return jsonify({"approval_url": approval_url, "order_id": order.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === PayPal return pages (optional) ===
@app.route('/paypal-return', methods=['GET'])
def paypal_return():
    chat_id = request.args.get('chat_id')
    return f"<h3>Thank you. Payment approved in PayPal. Please wait — you'll receive a Telegram message when payment is completed.</h3>"

@app.route('/paypal-cancel', methods=['GET'])
def paypal_cancel():
    return "<h3>Payment cancelled.</h3>"

# === Download endpoint (serves the bundle file) ===
@app.route('/download/<token>', methods=['GET'])
def download_file(token):
    store = app.config['DOWNLOAD_STORE']
    entry = store.get(token)
    if not entry:
        abort(404)
    # simple expiration: 24h
    if time.time() - entry.get('created',0) > 24*3600:
        abort(404)
    filepath = entry.get('file')
    if not filepath or not os.path.exists(filepath):
        abort(404)
    return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

# === PayPal webhook verification helper ===
def get_paypal_access_token():
    token_url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    r = requests.post(token_url, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data={'grant_type':'client_credentials'}, timeout=15)
    r.raise_for_status()
    return r.json()['access_token']

def verify_paypal_webhook(headers, body_json):
    # PayPal expects a POST to /v1/notifications/verify-webhook-signature
    verify_url = f"{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature"
    access_token = get_paypal_access_token()
    payload = {
        "auth_algo": headers.get("PAYPAL-AUTH-ALGO"),
        "cert_url": headers.get("PAYPAL-CERT-URL"),
        "transmission_id": headers.get("PAYPAL-TRANSMISSION-ID"),
        "transmission_sig": headers.get("PAYPAL-TRANSMISSION-SIG"),
        "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME"),
        "webhook_id": PAYPAL_WEBHOOK_ID,
        "webhook_event": body_json
    }
    r = requests.post(verify_url, json=payload, headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}, timeout=15)
    r.raise_for_status()
    return r.json()  # contains verification_status field

# === PayPal webhook endpoint ===
@app.route('/paypal-webhook', methods=['POST'])
def paypal_webhook():
    body = request.get_json()
    headers = request.headers
    try:
        verification = verify_paypal_webhook(headers, body)
    except Exception as e:
        # verification call failed
        return jsonify({"error": "verification failed", "detail": str(e)}), 400

    if verification.get('verification_status') != 'SUCCESS':
        return jsonify({"error": "invalid webhook signature", "verification": verification}), 400

    event_type = body.get('event_type')
    resource = body.get('resource', {})
    # Handle order capture / payment completed
    if event_type in ("CHECKOUT.ORDER.APPROVED", "PAYMENT.CAPTURE.COMPLETED", "CHECKOUT.ORDER.COMPLETED"):
        # Try to locate order id
        order_id = resource.get('id') or resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id') or resource.get('order_id')
        found_key = None
        store = app.config['DOWNLOAD_STORE']
        if order_id and order_id in store:
            found_key = order_id
        else:
            # fallback: check if any stored key appears in the resource json
            s = json.dumps(resource)
            for k in store:
                if k in s:
                    found_key = k
                    break
        if found_key:
            rec = store[found_key]
            chat_id = rec.get('chat_id')
            # create a download token
            token = str(uuid.uuid4())
            # map token -> static/productivity_bundle.zip (demo)
            filepath = os.path.join(os.path.dirname(__file__), 'static', 'productivity_bundle.zip')
            store[token] = {"chat_id": chat_id, "file": filepath, "created": time.time()}
            # send secure download link to user
            download_url = f"{BASE_URL}/download/{token}"
            telegram_send_message(chat_id, f"✅ Payment received. Download your bundle here: {download_url}")
            # optionally, send as document so Telegram stores the file
            telegram_send_document(chat_id, download_url, "productivity_bundle.zip")
            # mark original order as paid
            store[found_key]['status'] = 'PAID'
            return jsonify({"status":"delivered"}), 200
    # Return 200 for other events
    return jsonify({"status":"ignored"}), 200

# === Telegram webhook endpoint (receives updates from Telegram) ===
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.json or {}
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text','').strip()
        if text.startswith('/start'):
            telegram_send_message(chat_id, "Welcome! Send /buy to purchase the Productivity Bundle (6 EUR)." )
        elif text.startswith('/buy'):
            # Create PayPal order server-side and return approval link
            # Use POST /create-order via internal request to keep one endpoint
            resp = requests.post(url_for('create_order', _external=True), json={'chat_id': chat_id})
            if resp.status_code == 200:
                data = resp.json()
                approval_url = data.get('approval_url') or data.get('approval_url') or data.get('approval_url') or data.get('approval_url')
                # the SDK returns 'approval_url' as 'approval_url' in our create_order response; handle fallback
                approval = data.get('approval_url') or next((l['href'] for l in data.get('links',[]) if l.get('rel')=='approve'), None)
                # our create_order returns approval_url field
                approval = data.get('approval_url') or data.get('approval_url')
                # if not found, use full resp json to extract
                if not approval:
                    # fallback: try order_id lookup via store
                    approval = data.get('approval_url') or ''
                telegram_send_message(chat_id, f"Please approve payment here: {approval}")
            else:
                telegram_send_message(chat_id, "Failed to create payment. Try again later.")
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
