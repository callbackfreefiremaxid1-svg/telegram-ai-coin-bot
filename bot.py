import json, os
import telebot, openai
from datetime import datetime

# ================= TOKENS (ENV VARS) =================
BOT_TOKEN = os.getenv("8083623048:AAG57-sIGPTPebTnQdtwFdIo_licRBW6Vkw")
OPENAI_KEY = os.getenv("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")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_KEY

# ================= OWNER =================
OWNER_ID = 6445948135  # @Galaxyboy369

# ================= COINS CONFIG =================
DEFAULT_COINS = 20
MAX_COINS = 100
IMAGE_COST = 5
DAILY_COIN = 1
REF_COIN = 5
DATA_FILE = "coins.json"

# ================= HELPERS =================
def is_owner(uid):
    return uid == OWNER_ID

def load():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f)

def get_user(uid):
    d = load()
    if str(uid) not in d["users"]:
        d["users"][str(uid)] = {"coins": DEFAULT_COINS, "last": ""}
        save(d)
    return d["users"][str(uid)]

def add_coins(uid, amt):
    if is_owner(uid):
        return
    d = load()
    u = get_user(uid)
    u["coins"] = min(MAX_COINS, u["coins"] + amt)
    d["users"][str(uid)] = u
    save(d)

def deduct(uid, amt):
    if is_owner(uid):
        return True
    u = get_user(uid)
    if u["coins"] >= amt:
        add_coins(uid, -amt)
        return True
    return False

def daily(uid):
    if is_owner(uid):
        return 0
    u = get_user(uid)
    today = datetime.now().strftime("%Y-%m-%d")
    if u["last"] != today:
        u["last"] = today
        add_coins(uid, DAILY_COIN)
        d = load()
        d["users"][str(uid)] = u
        save(d)
        return DAILY_COIN
    return 0

# ================= COMMANDS =================
@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    bonus = daily(uid)
    if is_owner(uid):
        bot.reply_to(m, "👑 Owner Access\n♾️ Unlimited Coins")
    else:
        c = get_user(uid)["coins"]
        msg = f"👋 Welcome\n💰 Coins: {c}/{MAX_COINS}"
        if bonus:
            msg += f"\n🎁 Daily +{bonus}"
        bot.reply_to(m, msg)

@bot.message_handler(commands=['balance'])
def balance(m):
    uid = m.from_user.id
    if is_owner(uid):
        bot.reply_to(m, "👑 Balance: ♾️ Unlimited")
    else:
        bot.reply_to(m, f"💰 Coins: {get_user(uid)['coins']}/{MAX_COINS}")

@bot.message_handler(commands=['addcoins'])
def addcoins(m):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "❌ Owner only")
        return
    try:
        _, uid, amt = m.text.split()
        add_coins(int(uid), int(amt))
        bot.reply_to(m, "✅ Coins added")
    except:
        bot.reply_to(m, "Use: /addcoins user_id amount")

@bot.message_handler(commands=['stats'])
def stats(m):
    if not is_owner(m.from_user.id):
        bot.reply_to(m, "❌ Owner only")
        return
    d = load()["users"]
    text = f"👥 Total users: {len(d)}\n\n"
    for k, v in d.items():
        text += f"{k} → {v['coins']}\n"
    bot.reply_to(m, text)

# ================= CHAT & IMAGE =================
@bot.message_handler(func=lambda m: True)
def chat(m):
    uid = m.from_user.id
    text = m.text.strip()

    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if deduct(uid, IMAGE_COST):
            img = f"https://image.pollinations.ai/prompt/{prompt}"
            bot.send_photo(m.chat.id, img)
        else:
            bot.reply_to(m, "❌ Coins kam hai")
    else:
        r = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        bot.reply_to(m, r.choices[0].message.content)

bot.polling()
