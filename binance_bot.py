import requests
import time
import threading
import os
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = 60  # giây
CHANGE_THRESHOLD = 1.0  # %

last_prices = {}

def get_all_symbols():
    url = "https://api.binance.com/api/v3/ticker/price"
    res = requests.get(url).json()
    return [item for item in res if item["symbol"].endswith("USDT")]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': msg}
    requests.post(url, data=payload)

def run_bot():
    global last_prices
    while True:
        try:
            current_data = get_all_symbols()
            changes = []
            for item in current_data:
                symbol = item["symbol"]
                price = float(item["price"])
                old_price = last_prices.get(symbol)
                if old_price:
                    change_percent = abs((price - old_price) / old_price) * 100
                    if change_percent >= CHANGE_THRESHOLD:
                        changes.append(f"🔄 {symbol}: {old_price:.4f} → {price:.4f} ({change_percent:.2f}%)")
                last_prices[symbol] = price

            if changes:
                msg = "📈 Biến động giá coin:\n" + "\n".join(changes)
                send_telegram(msg)

            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print("Error:", e)
            time.sleep(CHECK_INTERVAL)

# 🟢 Khởi động bot trong thread riêng
threading.Thread(target=run_bot).start()

# 🟢 Fake web server cho Render (bắt buộc)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))