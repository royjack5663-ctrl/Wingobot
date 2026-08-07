import os
import time
import threading
import requests
from datetime import datetime, timedelta
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
        requests.post(url, json=payload, timeout=10)
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

def calculate_next_prediction(history_list, consecutive_misses):
    if not history_list:
        return None, None

    current_issue = history_list[0]
    issue_number = current_issue.get("issueNumber")

    observation_length = 5
    if consecutive_misses == 1:
        observation_length = 4
    elif consecutive_misses >= 2:
        observation_length = 3

    observed_history = []
    for x in history_list[:observation_length]:
        num = int(x.get("number", 0))
        observed_history.append("BIG" if num >= 5 else "SMALL")

    if len(observed_history) < 3:
        return str(int(issue_number) + 1), "BIG"

    r1, r2, r3 = observed_history[0], observed_history[1], observed_history[2]
    is_chopping = (r1 != r2) and (r2 != r3)
    is_streak = (r1 == r2) and (r2 == r3)

    if is_chopping:
        final_prediction = "SMALL" if r1 == "BIG" else "BIG"
    elif is_streak:
        final_prediction = r1
    else:
        big_count = observed_history.count("BIG")
        small_count = observed_history.count("SMALL")
        if r1 == "BIG": big_count += 0.5
        else: small_count += 0.5
        final_prediction = "BIG" if big_count > small_count else "SMALL"

    return str(int(issue_number) + 1), final_prediction

# ==========================================
# 24/7 CONTINUOUS ENGINE
# ==========================================
if __name__ == "__main__":
    send_telegram_message("⚡ <b>DAMAN WOLF 24/7 CONTINUOUS ENGINE STARTED</b>")

    prediction_count = 0
    consecutive_misses = 0
    pending_period = None
    pending_prediction = None

    while True:
        try:
            history_list = get_api_data()
            
            if not history_list:
                time.sleep(10)
                continue

            # 1. Verification of previous prediction result
            if pending_period:
                actual_result = None
                for item in history_list:
                    if item.get("issueNumber") == pending_period:
                        num = int(item.get("number", 0))
                        actual_result = "BIG" if num >= 5 else "SMALL"
                        break
                
                if actual_result is None:
                    time.sleep(10)
                    continue

                if actual_result == pending_prediction:
                    consecutive_misses = 0
                    send_telegram_message(
                        f"✅ <b>WIN!</b> Period {pending_period} was {actual_result}\n"
                        f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                    )
                else:
                    consecutive_misses += 1
                    send_telegram_message(
                        f"❌ <b>LOSS!</b> Period {pending_period} was {actual_result}\n"
                        f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                    )

                pending_period = None

            # 2. Generate Next Period Prediction
            next_period, prediction = calculate_next_prediction(history_list, consecutive_misses)
            
            if next_period:
                pending_period = next_period
                pending_prediction = prediction
                prediction_count += 1

                send_telegram_message(
                    f"📊 <b>PREDICTION #{prediction_count}</b>\n"
                    f"🔹 <b>Period:</b> {next_period}\n"
                    f"🎯 <b>Result:</b> {prediction}\n\n"
                    f"📢 <b>Official Channel:</b> <a href='{CHANNEL_LINK}'>@damanwolf022</a>"
                )

            # Wait 50 seconds before next issue result
            time.sleep(50)

        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(10)
            
