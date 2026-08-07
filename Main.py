import os
import time
import threading
import requests
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
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
IST = timezone('Asia/Kolkata')

# ==========================================
# TELEGRAM NOTIFICATION HELPER
# ==========================================
def send_telegram_message(message):
    """Sends a formatted message to your Telegram channel using HTML mode."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if not response.ok:
            print(f"Telegram API Error: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# ==========================================
# PREDICTION ENGINE
# ==========================================
def get_api_data():
    """Fetches the latest game history from the server."""
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {}).get("list", [])
    except Exception as e:
        print(f"API Fetch Error: {e}")
    return []

def calculate_next_prediction(history_list, consecutive_misses):
    """Calculates the BIG or SMALL prediction based on game history."""
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

    next_period_id = str(int(issue_number) + 1)
    return next_period_id, final_prediction

# ==========================================
# SESSION LOGIC
# ==========================================
def run_session():
    """Runs a complete prediction session (10+ predictions until final win)."""
    start_msg = (
        f"🟢 <b>NEW PREDICTION SESSION STARTED</b> 🟢\n"
        f"📢 <b>Channel:</b> <a href='{CHANNEL_LINK}'>Daman Wolf Official</a>"
    )
    send_telegram_message(start_msg)
    print(f"[{datetime.now(IST)}] Session started.")

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
                if current_win_streak > max_win_streak: 
                    max_win_streak = current_win_streak
                
                send_telegram_message(
                    f"✅ <b>WIN!</b> Period {pending_period} was {actual_result}\n"
                    f"🔗 <a href='{CHANNEL_LINK}'>Join Daman Wolf Channel</a>"
                )
                is_last_win = True
            else:
                total_losses += 1
                current_loss_streak += 1
                current_win_streak = 0
                if current_loss_streak > max_loss_streak: 
                    max_loss_streak = current_loss_streak
                
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

    # REPORT
    try:
        jobs = scheduler.get_jobs()
        jobs.sort(key=lambda j: j.next_run_time)
        
        next_time_str = "Unknown"
        for job in jobs:
            if job.next_run_time > datetime.now(IST):
                next_time_str = job.next_run_time.strftime("%I:%M %p")
                break
    except Exception:
        next_time_str = "Next Scheduled Time"

    report = (
        f"🏆 <b>SESSION COMPLETE REPORT</b> 🏆\n\n"
        f"🔹 <b>Total Predictions:</b> {predictions_made}\n"
        f"✅ <b>Total Wins:</b> {total_wins}\n"
        f"❌ <b>Total Losses:</b> {total_losses}\n\n"
        f"🔥 <b>Max Continuous Win:</b> {max_win_streak}\n"
        f"📉 <b>Max Continuous Loss:</b> {max_loss_streak}\n\n"
        f"⏰ <b>Next Session Schedule:</b> {next_time_str}\n\n"
        f"👑 <b>Join Us:</b> <a href='{CHANNEL_LINK}'>Daman Wolf Official Channel</a>"
    )
    send_telegram_message(report)
    print(f"[{datetime.now(IST)}] Session ended. Report sent.")

# ==========================================
# SCHEDULER SETUP
# ==========================================
if __name__ == "__main__":
    global scheduler
    scheduler = BlockingScheduler(timezone=IST)

    # Clean startup notification
    send_telegram_message("⚡ <b>DAMAN WOLF SCHEDULER ENGINE ONLINE</b>")

    # Morning Schedule: 07:00 AM, 09:00 AM, 11:00 AM
    scheduler.add_job(run_session, 'cron', hour=7, minute=0)
    scheduler.add_job(run_session, 'cron', hour=9, minute=0)
    scheduler.add_job(run_session, 'cron', hour=11, minute=0)

    # Evening Schedule: 07:00 PM (19:00), 09:00 PM (21:00)
    scheduler.add_job(run_session, 'cron', hour=19, minute=0)
    scheduler.add_job(run_session, 'cron', hour=21, minute=0)

    print("Bot is running and scheduled...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    
