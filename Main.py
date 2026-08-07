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
        self.wfile.write(b"DAMAN WOLF 24/7 ENGINE ACTIVE")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"Web server started on port {port}")
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
        print(f"Telegram Error: {e}")

def get_api_data():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            return res.json().get("data", {}).get("list", [])
    except Exception as e:
        print(f"API Error: {e}")
    return []

# ==========================================
# 24/7 CONTINUOUS ENGINE
# ==========================================
if __name__ == "__main__":
    send_telegram_message("⚡ <b>DAMAN WOLF 24/7 TEST ENGINE ONLINE</b>")

    prediction_count = 0
    pending_period = None
    pending_prediction = None

    while True:
        try:
            history_list = get_api_data()
            
            if not history_list:
                print("No history data found, retrying...")
                time.sleep(10)
                continue

            current_issue = history_list[0]
            latest_period = current_issue.get("issueNumber")

            # 1. Result Check for Pending Period
            if pending_period:
                if latest_period == pending_period:
                    num = int(current_issue.get("number", 0))
                    actual_result = "BIG" if num >= 5 else "SMALL"

                    if actual_result == pending_prediction:
                        send_telegram_message(
                            f"✅ <b>WIN!</b> Period {pending_period} was {actual_result}\n"
                            f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                        )
                    else:
                        send_telegram_message(
                            f"❌ <b>LOSS!</b> Period {pending_period} was {actual_result}\n"
                            f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                        )
                    
                    pending_period = None

            # 2. Generate Prediction if not already pending
            if not pending_period:
                next_period = str(int(latest_period) + 1)
                
                # Simple Alternate/Trend Predictor for test mode
                num = int(current_issue.get("number", 0))
                prediction = "SMALL" if num >= 5 else "BIG"

                pending_period = next_period
                pending_prediction = prediction
                prediction_count += 1

                send_telegram_message(
                    f"📊 <b>PREDICTION #{prediction_count}</b>\n"
                    f"🔹 <b>Period:</b> {next_period}\n"
                    f"🎯 <b>Result:</b> {prediction}\n\n"
                    f"📢 <b>Official Channel:</b> <a href='{CHANNEL_LINK}'>@damanwolf022</a>"
                )

            time.sleep(15)

        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(10)
