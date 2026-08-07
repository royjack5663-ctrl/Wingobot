import os
import time
import threading
import requests
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 1. FAKE WEB SERVER FOR RENDER (PORT FIX)
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"DAMAN WOLF SCHEDULER ACTIVE")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# ==========================================
# 2. CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = "8474361108:AAHkJ4K73zE_vxqJDiDcjfs-58GSZs0Vb08"
TELEGRAM_CHAT_ID = "@damanwolf022" 
CHANNEL_LINK = "https://t.me/damanwolf022"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# IST Timezone (+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Scheduled Hours (IST 24-Hour Format): 07:00, 09:00, 11:00, 19:00, 21:00
SCHEDULED_HOURS = [7, 9, 11, 19, 21]

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
# SESSION ENGINE
# ==========================================
def run_session():
    send_telegram_message(
        f"🟢 <b>NEW PREDICTION SESSION STARTED</b> 🟢\n"
        f"📢 <b>Channel:</b> <a href='{CHANNEL_LINK}'>Daman Wolf Official</a>"
    )

    predictions_made = 0
    total_wins = 0
    total_losses = 0
    current_win_streak = 0
    current_loss_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    
    pending_period = None
    pending_prediction = None

    while True:
        history_list = get_api_data()
        
        if not history_list:
            time.sleep(10)
            continue

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
                total_wins += 1
                current_win_streak += 1
                current_loss_streak = 0
                if current_win_streak > max_win_streak: max_win_streak = current_win_streak
                
                send_telegram_message(
                    f"✅ <b>WIN!</b> Period {pending_period} was {actual_result}\n"
                    f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                )
                is_last_win = True
            else:
                total_losses += 1
                current_loss_streak += 1
                current_win_streak = 0
                if current_loss_streak > max_loss_streak: max_loss_streak = current_loss_streak
                
                send_telegram_message(
                    f"❌ <b>LOSS!</b> Period {pending_period} was {actual_result}\n"
                    f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                )
                is_last_win = False

            if predictions_made >= 10 and is_last_win:
                break
                
            pending_period = None 

        next_period, prediction = calculate_next_prediction(history_list, current_loss_streak)
        
        pending_period = next_period
        pending_prediction = prediction
        predictions_made += 1
        
        send_telegram_message(
            f"📊 <b>PREDICTION #{predictions_made}</b>\n"
            f"🔹 <b>Period:</b> {next_period}\n"
            f"🎯 <b>Result:</b> {prediction}\n\n"
            f"📢 <b>Official Channel:</b> <a href='{CHANNEL_LINK}'>@damanwolf022</a>"
        )

        time.sleep(50) 

    send_telegram_message(
        f"🏆 <b>SESSION COMPLETE REPORT</b> 🏆\n\n"
        f"🔹 <b>Total Predictions:</b> {predictions_made}\n"
        f"✅ <b>Total Wins:</b> {total_wins}\n"
        f"❌ <b>Total Losses:</b> {total_losses}\n\n"
        f"👑 <b>Join Us:</b> <a href='{CHANNEL_LINK}'>Daman Wolf Official Channel</a>"
    )

# ==========================================
# MAIN LOOP
# ==========================================
if __name__ == "__main__":
    send_telegram_message("⚡ <b>DAMAN WOLF SCHEDULER ENGINE ONLINE</b>")

    executed_hours = set()

    while True:
        now_ist = datetime.now(IST)
        current_hour = now_ist.hour
        current_minute = now_ist.minute

        if current_hour in SCHEDULED_HOURS and current_minute < 5:
            if current_hour not in executed_hours:
                executed_hours.add(current_hour)
                run_session()

        if current_minute >= 10:
            executed_hours.discard(current_hour)

        time.sleep(15)

    
