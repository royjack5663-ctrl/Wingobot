import os
import time
import datetime
import requests

# ==========================================
# CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8474361108:AAHkJ4K73zE_vxqJDiDcjfs-58GSZs0Vb08")
TELEGRAM_CHAT_ID = "@damanwolf022" 
CHANNEL_LINK = "https://t.me/damanwolf022"
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

SCHEDULED_HOURS = [7, 9, 11, 16, 20] # 07:00 AM, 09:00 AM, 11:00 AM, 04:00 PM, 08:00 PM
MAX_STANDARD_PREDICTIONS = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

is_session_active = False
current_session_hour = None
prediction_count = 0
wins = 0
losses = 0
waiting_for_recovery = False

pending_full_period = None
pending_prediction = None
last_processed_period = None
consecutive_misses = 0

def get_ist_time():
    now_utc = datetime.datetime.utcnow()
    return now_utc + datetime.timedelta(hours=5, minutes=30)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_api_data():
    try:
        res = requests.get(API_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                d = data.get("data")
                if isinstance(d, dict):
                    return d.get("list", [])
                elif isinstance(d, list):
                    return d
    except Exception as e:
        print(f"API Error: {e}")
    return []

def calculate_jack_roy_prediction(history_list, misses):
    obs_len = 5
    if misses == 1: obs_len = 4
    elif misses >= 2: obs_len = 3

    obs_data = history_list[:obs_len]
    obs_history = ["BIG" if int(x.get("number", 0)) >= 5 else "SMALL" for x in obs_data]

    r1 = obs_history[0]
    r2 = obs_history[1] if len(obs_history) > 1 else r1
    r3 = obs_history[2] if len(obs_history) > 2 else r2

    is_chopping = (r1 != r2 and r2 != r3)
    is_streak = (r1 == r2 and r2 == r3)

    if is_chopping:
        return "SMALL" if r1 == "BIG" else "BIG"
    elif is_streak:
        return r1
    else:
        big_cnt = sum(1 for x in obs_history if x == "BIG")
        small_cnt = sum(1 for x in obs_history if x == "SMALL")
        if r1 == "BIG": big_cnt += 0.5
        if r1 == "SMALL": small_cnt += 0.5
        return "BIG" if big_cnt > small_cnt else "SMALL"

if __name__ == "__main__":
    send_telegram("🚀 <b>JACK ROY VIP TIMED ENGINE ONLINE</b>")
    print("Engine Running...")
    processed_hours_today = []

    while True:
        try:
            ist = get_ist_time()
            curr_hour = ist.hour
            curr_min = ist.minute
            today_str = ist.strftime("%Y-%m-%d")

            if 'last_day' not in locals() or last_day != today_str:
                processed_hours_today = []
                last_day = today_str

            # Start Scheduled Session
            if not is_session_active and curr_hour in SCHEDULED_HOURS and curr_min < 5:
                session_key = f"{today_str}_{curr_hour}"
                if session_key not in processed_hours_today:
                    is_session_active = True
                    current_session_hour = curr_hour
                    prediction_count = 0
                    wins = 0
                    losses = 0
                    waiting_for_recovery = False
                    consecutive_misses = 0
                    pending_full_period = None
                    processed_hours_today.append(session_key)

                    t_format = f"{curr_hour % 12 or 12}:00 {'PM' if curr_hour >= 12 else 'AM'}"
                    send_telegram(f"🔥 <b>JACK ROY VIP SESSION STARTED</b>\n⏰ <b>Time:</b> {t_format}")

            if is_session_active:
                history = get_api_data()
                if history:
                    latest_item = history[0]
                    latest_full_p = str(latest_item.get("issueNumber"))
                    latest_num = int(latest_item.get("number", 0))
                    actual_res = "BIG" if latest_num >= 5 else "SMALL"

                    if pending_full_period and latest_full_p == pending_full_period:
                        short_p = pending_full_period[-3:]
                        if actual_res == pending_prediction:
                            wins += 1
                            consecutive_misses = 0
                            send_telegram(f"✅ <b>WIN!</b> Period {short_p} was <b>{actual_res}</b>")
                            
                            if waiting_for_recovery:
                                waiting_for_recovery = False
                                is_session_active = False
                                total = wins + losses
                                acc = round((wins / total) * 100, 1) if total > 0 else 0
                                send_telegram(f"📊 <b>SESSION COMPLETE (RECOVERY WIN)</b>\nTotal: {total} | Wins: {wins} | Losses: {losses} | Accuracy: {acc}%")
                                pending_full_period = None
                                continue
                        else:
                            losses += 1
                            consecutive_misses += 1
                            send_telegram(f"❌ <b>LOSS!</b> Period {short_p} was <b>{actual_res}</b>")

                        pending_full_period = None

                    if prediction_count >= MAX_STANDARD_PREDICTIONS and not pending_full_period:
                        if consecutive_misses > 0 and not waiting_for_recovery:
                            waiting_for_recovery = True
                            send_telegram("⚠️ <b>10th Loss!</b> Session extended until 1 WIN.")
                        elif not waiting_for_recovery:
                            is_session_active = False
                            total = wins + losses
                            acc = round((wins / total) * 100, 1) if total > 0 else 0
                            send_telegram(f"📊 <b>SESSION COMPLETE REPORT</b>\nTotal: {total} | Wins: {wins} | Losses: {losses} | Accuracy: {acc}%")
                            continue

                    if not pending_full_period and last_processed_period != latest_full_p and is_session_active:
                        next_full_period = str(int(latest_full_p) + 1)
                        pred_val = calculate_jack_roy_prediction(history, consecutive_misses)

                        prediction_count += 1
                        pending_full_period = next_full_period
                        pending_prediction = pred_val
                        last_processed_period = latest_full_p

                        short_next = next_full_period[-3:]
                        send_telegram(
                            f"📊 <b>PREDICTION #{prediction_count}</b>\n"
                            f"🔹 <b>Period:</b> {short_next}\n"
                            f"🎯 <b>Result:</b> {pred_val}\n\n"
                            f"📢 <a href='{CHANNEL_LINK}'>Jack Roy VIP Channel</a>"
                        )

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(10)
