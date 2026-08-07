import os
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 1. FAKE WEB SERVER FOR RENDER (PORT FIX)
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"DAMAN WOLF ENGINE ACTIVE")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Web server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Web server error: {e}")

threading.Thread(target=run_web_server, daemon=True).start()

# ==========================================
# 2. CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = "8474361108:AAHkJ4K73zE_vxqJDiDcjfs-58GSZs0Vb08"
TELEGRAM_CHAT_ID = "@damanwolf022" 
CHANNEL_LINK = "https://t.me/damanwolf022"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Sent Status: {res.status_code}")
    except Exception as e:
        print(f"Telegram Send Error: {e}")

def get_api_data():
    """ Robust API Fetching & Extraction """
    try:
        res = requests.get(API_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                data_field = data.get("data")
                if isinstance(data_field, dict):
                    return data_field.get("list", [])
                elif isinstance(data_field, list):
                    return data_field
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return []

def get_short_period(full_period_str):
    """ Period number ke last 3 digits extract karta hai """
    period_str = str(full_period_str)
    return period_str[-3:] if len(period_str) >= 3 else period_str

# ==========================================
# MAIN PREDICTION ENGINE
# ==========================================
if __name__ == "__main__":
    # Updated Engine Startup Message
    send_telegram_message("🚀 <b>DAMAN WOLF PREDICTION ENGINE ONLINE</b>\n<i>Syncing with 1-Minute Wingo Stream...</i>")

    prediction_count = 0
    last_processed_full_period = None
    
    pending_full_period = None
    pending_prediction = None

    while True:
        try:
            history = get_api_data()
            if not history:
                print("API data empty, retrying in 10s...")
                time.sleep(10)
                continue

            latest_item = history[0]
            latest_full_period = str(latest_item.get("issueNumber"))
            latest_num = int(latest_item.get("number", 0))
            actual_res = "BIG" if latest_num >= 5 else "SMALL"

            # 1. Result Check for Previous Prediction
            if pending_full_period and latest_full_period == pending_full_period:
                short_p = get_short_period(pending_full_period)
                if actual_res == pending_prediction:
                    send_telegram_message(
                        f"✅ <b>WIN!</b> Period {short_p} was <b>{actual_res}</b>\n"
                        f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                    )
                else:
                    send_telegram_message(
                        f"❌ <b>LOSS!</b> Period {short_p} was <b>{actual_res}</b>\n"
                        f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                    )
                pending_full_period = None

            # 2. Generate Next Period Prediction
            if not pending_full_period and last_processed_full_period != latest_full_period:
                next_full_period = str(int(latest_full_period) + 1)
                
                # Dynamic Logic
                predicted_val = "SMALL" if latest_num >= 5 else "BIG"

                prediction_count += 1
                pending_full_period = next_full_period
                pending_prediction = predicted_val
                last_processed_full_period = latest_full_period

                short_next_period = get_short_period(next_full_period)

                send_telegram_message(
                    f"📊 <b>PREDICTION #{prediction_count}</b>\n"
                    f"🔹 <b>Period:</b> {short_next_period}\n"
                    f"🎯 <b>Result:</b> {predicted_val}\n\n"
                    f"📢 <b>Official Channel:</b> <a href='{CHANNEL_LINK}'>@damanwolf022</a>"
                )

        except Exception as e:
            print(f"Runtime Engine Error: {e}")

        # Checking frequency every 10 seconds for 1-minute issue sync
        time.sleep(10)
