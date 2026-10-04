from flask import Flask
import telebot
import json
import os
import random
import string

BOT_TOKEN = "8549403715:AAEKjfFtr3ZzepoJxrXYKpCyBOzGVsjquGw"
ADMIN_ID = 8362233224

app = Flask(__name__)

# Remove any existing webhook first
temp_bot = telebot.TeleBot(BOT_TOKEN)
temp_bot.remove_webhook()

# Now create main bot
bot = telebot.TeleBot(BOT_TOKEN)

DB_FILE = "/tmp/codes.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"codes": {}}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

def generate_code():
    p1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    p2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{p1}-{p2}"

@app.route('/')
def home():
    return "WalkSafe Bot OK"

@app.route('/check/<code>')
def check(code):
    code = code.upper().strip()
    db = load_db()
    if code not in db["codes"]:
        return "INVALID"
    if db["codes"][code]["status"] == "used":
        return "ALREADY_USED"
    db["codes"][code]["status"] = "used"
    save_db(db)
    return "VALID"

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, "WalkSafe Bot\n\n/generate - New code\n/list - All codes")

@bot.message_handler(commands=['generate'])
def cmd_generate(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Unauthorized")
    db = load_db()
    code = generate_code()
    while code in db["codes"]:
        code = generate_code()
    db["codes"][code] = {"status": "unused"}
    save_db(db)
    bot.reply_to(message, f"✅ Code: `{code}`", parse_mode='Markdown')

@bot.message_handler(commands=['list'])
def cmd_list(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Unauthorized")
    db = load_db()
    unused = [c for c, d in db["codes"].items() if d["status"] == "unused"]
    msg = f"📊 Available: {len(unused)}"
    if unused:
        msg += f"\n" + "\n".join([f"`{c}`" for c in list(unused)[:10]])
    bot.reply_to(message, msg, parse_mode='Markdown')

# Run bot polling in main thread
if __name__ == '__main__':
    import threading
    
    def run_bot():
        bot.polling(none_stop=True)
    
    # Start bot in background
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask
    app.run(host='0.0.0.0', port=10000)