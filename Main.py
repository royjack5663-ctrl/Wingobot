import requests
import time
import json

# ================= CONFIGURATION =================
BOT_TOKEN = "8474361108:AAHkJ4K73zE_vxqJDiDcjfs-58GSZs0Vb08"  
CHAT_ID = "@damanwolf022"  # Public Channel Handle

# Direct Game API (Render par koi proxy restriction nahi hoti)
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

MAX_ROUNDS = 10
MAX_LEVEL_CAP = 3  

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

session_active = False
predictions_count = 0
current_level = 1
max_level_reached = 1
total_wins = 0
total_losses = 0
consecutive_strategy_misses = 0
current_strategy = "BIG_TREND"  

last_processed_issue = None
window_saved_pred = None

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        print("Telegram Log:", res.json())
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
        print(f"Fetch Error: {e}")

    return []

def analyze_prediction(history):
    global current_strategy, consecutive_strategy_misses

    if len(history) < 5:
        return "BIG"

    trend = ["BIG" if int(x["number"]) >= 5 else "SMALL" for x in history[:5]]
    r1, r2, r3 = trend[0], trend[1], trend[2]

    is_dragon_big = (r1 == "BIG" and r2 == "BIG" and r3 == "BIG")
    is_dragon_small = (r1 == "SMALL" and r2 == "SMALL" and r3 == "SMALL")

    if is_dragon_big:
        current_strategy = "DRAGON"
        return "BIG"
    elif is_dragon_small:
        current_strategy = "DRAGON"
        return "SMALL"

    if consecutive_strategy_misses >= 2:
        current_strategy = "SMALL_TREND" if current_strategy == "BIG_TREND" else "BIG_TREND"
        consecutive_strategy_misses = 0

    if current_strategy == "BIG_TREND":
        return "BIG" if r1 == "SMALL" else "SMALL"
    else: 
        return "SMALL" if r1 == "BIG" else "BIG"

def start_continuous_session():
    global session_active, predictions_count, current_level, max_level_reached
    global total_wins, total_losses, consecutive_strategy_misses, last_processed_issue
    global window_saved_pred

    session_active = True
    predictions_count = 0
    current_level = 1
    max_level_reached = 1
    total_wins = 0
    total_losses = 0
    consecutive_strategy_misses = 0
    last_processed_issue = None

    send_telegram_msg("🚀 *LIVE TEST SESSION STARTED (RENDER 24/7 MODE)*\nTarget: Win or Max 10 Rounds")

    history = []
    while not history:
        history = get_latest_history()
        if not history:
            time.sleep(3)

    predictions_count += 1
    pred = analyze_prediction(history)
    window_saved_pred = pred
    last_processed_issue = history[0]["issueNumber"]
    next_period = str(int(last_processed_issue) + 1)
    
    send_telegram_msg(
        f"🎯 *PREDICTION #{predictions_count}*\n"
        f"Period: `{next_period}`\n"
        f"Predict: *{pred}*\n"
        f"Current Level: {current_level}"
    )

    while session_active and predictions_count < MAX_ROUNDS:
        history = get_latest_history()
        if not history:
            time.sleep(3)
            continue

        latest_issue = history[0]["issueNumber"]
        
        if last_processed_issue != latest_issue:
            actual_num = int(history[0]["number"])
            actual_res = "BIG" if actual_num >= 5 else "SMALL"
            
            is_win = (window_saved_pred == actual_res)

            if is_win:
                total_wins += 1
                send_telegram_msg(f"✅ *WIN / SUCCESS!* (Issue: {latest_issue[-3:]})\nResult: {actual_res}")
                session_active = False
                break
            else:
                total_losses += 1
                consecutive_strategy_misses += 1
                current_level += 1
                if current_level > max_level_reached:
                    max_level_reached = current_level

                if current_level > MAX_LEVEL_CAP:
                    current_level = 1 

                send_telegram_msg(f"❌ *MISSED!* (Level {current_level - 1})\nActual: {actual_res}")

            if session_active and predictions_count < MAX_ROUNDS:
                predictions_count += 1
                pred = analyze_prediction(history)
                window_saved_pred = pred
                last_processed_issue = latest_issue
                
                next_period = str(int(latest_issue) + 1)
                
                send_telegram_msg(
                    f"🎯 *PREDICTION #{predictions_count}*\n"
                    f"Period: `{next_period}`\n"
                    f"Predict: *{pred}*\n"
                    f"Current Level: {current_level}"
                )

        time.sleep(3)

    send_telegram_msg(
        f"🛑 *SESSION COMPLETED*\n\n"
        f"📊 *Summary:*\n"
        f"• Total Wins: {total_wins}\n"
        f"• Max Level Reached: Level {max_level_reached}\n"
        f"• Status: {'SUCCESS (WIN)' if total_wins > 0 else 'MAX ROUNDS REACHED'}\n\n"
        f"🔄 *Starting Next Session in 10 seconds...*"
    )

print("Starting Clean Render Bot...")
send_telegram_msg("⚙️ *SYSTEM ONLINE:* Render Deployment Active!")

while True:
    start_continuous_session()
    time.sleep(10)

