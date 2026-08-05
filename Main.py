import os
import time
import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import pytz

# ================= 1. FAKE WEB SERVER (For Render Port Binding) =================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"JACK VIP MODS BOT RUNNING 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

# Background thread mein server chalayenge
threading.Thread(target=run_web_server, daemon=True).start()

# ================= 2. CONFIGURATION =================
BOT_TOKEN = "8474361108:AAHkJ4K73zE_vxqJDiDcjfs-58GSZs0Vb08"  
CHAT_ID = "@damanwolf022"  # Aapka Telegram Channel Handle

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
IST = pytz.timezone('Asia/Kolkata')

# Scheduled Times: "07:00", "09:00", "11:00", "12:00", "19:00"
SCHEDULED_TIMES = ["07:00", "09:00", "11:00", "12:00", "19:00"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

# State Variables
current_step = 1
consecutive_losses = 0
last_id = None
saved_pred = None

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print("Telegram Log Status:", res.status_code)
    except Exception as e:
        print(f"Telegram Send Error: {e}")

def get_latest_history():
    try:
        res = requests.get(API_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict) and "data" in data:
                return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return []

# Exact Logic from your HTML/JS Code
def calculate_prediction(history_list):
    if len(history_list) < 5:
        return "BIG"

    # Convert last 5 results to BIG/SMALL
    trend = ["BIG" if int(x["number"]) >= 5 else "SMALL" for x in history_list[:5]]
    r1, r2, r3, r4, r5 = trend[0], trend[1], trend[2], trend[3], trend[4]

    is_strict_ping_pong = (r1 != r2 and r2 != r3 and r3 != r4 and r4 != r5)
    is_big_dragon = (r1 == "BIG" and r2 == "BIG" and r3 == "BIG")
    is_small_dragon = (r1 == "SMALL" and r2 == "SMALL" and r3 == "SMALL")

    if is_strict_ping_pong:
        return "SMALL" if r1 == "BIG" else "BIG"
    elif is_big_dragon:
        return "BIG"
    elif is_small_dragon:
        return "SMALL"
    else:
        small_count = trend.count("SMALL")
        return "SMALL" if small_count >= 3 else "BIG"

def run_session_round():
    global current_step, consecutive_losses, last_id, saved_pred

    history = get_latest_history()
    if not history:
        return

    current = history[0]
    current_issue = current["issueNumber"]

    if last_id != current_issue:
        
        # Win/Loss Calculation if previous prediction exists
        if last_id is not None:
            actual_num = int(current["number"])
            actual_size = "BIG" if actual_num >= 5 else "SMALL"
            win = (saved_pred == actual_size)

            if win:
                current_step = 1
                consecutive_losses = 0
                status_msg = f"✅ *SUCCESS* (Issue: `{current_issue[-3:]}`)\nActual: *{actual_size}* ({actual_num})"
            else:
                current_step += 1
                consecutive_losses += 1
                status_msg = f"❌ *FAILED* (Issue: `{current_issue[-3:]}`)\nActual: *{actual_size}* ({actual_num})"

            send_telegram_msg(status_msg)

        # Calculate new prediction
        final_prediction = calculate_prediction(history)

        if current_step > 6:
            current_step = 1

        last_id = current_issue
        saved_pred = final_prediction
        next_period = str(int(current_issue) + 1)

        nums_str = "5, 6, 7, 8, 9" if final_prediction == "BIG" else "0, 1, 2, 3, 4"

        msg = (
            f"👑 *JACK VIP MODS | ELITE HACK*\n\n"
            f"📌 *PERIOD:* `{next_period}`\n"
            f"🎯 *PREDICTION:* *{final_prediction}*\n"
            f"📊 *STEP:* `{current_step}`\n"
            f"🎲 *NUMBERS:* `{nums_str}`"
        )
        send_telegram_msg(msg)

# ================= 3. MAIN SCHEDULER LOOP =================
print("Starting Engine...")
send_telegram_msg("⚡ *JACK VIP MODS ENGINE ONLINE*\nWaiting for Scheduled Session Times...")

last_executed_minute = ""

while True:
    now = datetime.now(IST)
    current_time_str = now.strftime("%H:%M")
    
    # Check if current time matches scheduled session times
    if current_time_str in SCHEDULED_TIMES:
        if last_executed_minute != current_time_str:
            send_telegram_msg(f"🚀 *SCHEDULED SESSION STARTED ({current_time_str} IST)*")
            last_executed_minute = current_time_str
            
            # Reset levels at start of new time session
            current_step = 1
            last_id = None
            
            # Run session active loop for 20 minutes
            start_time = time.time()
            while time.time() - start_time < 1200:  # 20 Minutes active time
                run_session_round()
                time.sleep(3)
                
            send_telegram_msg(f"🛑 *SESSION ENDED FOR {current_time_str}*")
            
    time.sleep(5)
