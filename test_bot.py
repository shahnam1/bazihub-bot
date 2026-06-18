import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ================== ⚙️ تنظیمات ==================
TOKEN = "8187715324:AAEfVuuYLNY0l1SuKE-hEJv5uC2wtMuBeok"
MERCHANT_ID = "1253538e-6521-11ea-8511-000c295eb8fc"
CALLBACK_URL = "https://yourdomain.com/zarinpal/callback"  # لینک بازگشت پرداخت

ADMIN_USERNAME = "@capitan_6ah"
INSTAGRAM = "https://instagram.com/yourpage"
SUPPORT_PHONE = "+989397793979"

# نرخ پیش‌فرض
DEFAULT_USDT_TMN = 150_000

# محصولات MLBB
MLBB_PRODUCTS = {
    "mlbb_weekly": {"name": "Weekly Pass", "usd": 1.35},
    "mlbb_257": {"name": "257 جم", "usd": 5.0},
    "mlbb_514": {"name": "514 جم", "usd": 10.0},
    "mlbb_1412": {"name": "1412 جم", "usd": 27.0},
    "mlbb_2398": {"name": "2398 جم", "usd": 45.0},
}

# ================== 📡 گرفتن نرخ ==================
def fetch_usdt_rate():
    try:
        resp = requests.get("https://api.bitpin.org/v1/mkt/markets/")
        data = resp.json()
        for m in data.get("results", []):
            if m.get("code") == "USDT_IRT":
                return float(m["price"])
    except Exception as e:
        print("Error fetching rate:", e)
    return DEFAULT_USDT_TMN

def fetch_mlbb_price(product_key: str, usdt: float):
    """محاسبه قیمت تومانی محصول"""
    usd = MLBB_PRODUCTS[product_key]["usd"]
    return int(round(usd * usdt))

# ================== 💳 زرین‌پال ==================
def create_payment_link(amount_tmn: int, description: str):
    url = "https://api.zarinpal.com/pg/v4/payment/request.json"
    payload = {
        "merchant_id": MERCHANT_ID,
        "amount": amount_tmn,
        "callback_url": CALLBACK_URL,
        "description": description,
    }
    resp = requests.post(url, json=payload)
    data = resp.json()
    if data.get("data") and data["data"].get("authority"):
        authority = data["data"]["authority"]
        return f"https://www.zarinpal.com/pg/StartPay/{authority}"
    return None

# ================== 🟢 منو ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Mobile Legends: Bang Bang", callback_data="menu_mlbb")],
        [InlineKeyboardButton("Call of Duty Mobile", callback_data="menu_codm")],
        [InlineKeyboardButton("PUBG Mobile", callback_data="menu_pubg")],
        [InlineKeyboardButton("📞 پشتیبانی", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM)],
    ]
    await update.message.reply_text(
        "🎮 به BaziHub خوش اومدی!\nیک بازی رو انتخاب کن:", 
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    usdt = context.application.bot_data.get("usdt_rate", DEFAULT_USDT_TMN)

    if data == "menu_mlbb":
        kb = [
            [InlineKeyboardButton(p["name"], callback_data=k)]
            for k, p in MLBB_PRODUCTS.items()
        ]
        kb.append([InlineKeyboardButton("⬅️ برگشت", callback_data="back_home")])
        await q.edit_message_text("MLBB → یک محصول انتخاب کن:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("mlbb_"):
        price_tmn = fetch_mlbb_price(data, usdt)
        context.user_data["awaiting_mlbb_id"] = True
        context.user_data["product_key"] = data
        context.user_data["price_tmn"] = price_tmn

        text = (
            f"*{MLBB_PRODUCTS[data]['name']}*\n"
            f"💵 قیمت: ~ *{price_tmn:,}* تومان\n\n"
            "لطفاً *User ID* و *Zone ID* بازی رو اینطوری بفرست:\n"
            "`12345678 1234`"
        )
        await q.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ برگشت", callback_data="menu_mlbb")]])
        )

    elif data == "back_home":
        await start(q, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_mlbb_id"):
        parts = update.message.text.strip().split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            await update.message.reply_text(
                "❗ لطفاً دقیقاً این قالب رو بفرست: `UserID ZoneID`", 
                parse_mode=ParseMode.MARKDOWN
            )
            return

        user_id, zone_id = parts
        product_key = context.user_data["product_key"]
        price = context.user_data["price_tmn"]

        # ⚡ چک نیک‌نیم
        nickname = None
        try:
            r = requests.get(
                f"https://api.duniagames.co.id/api/transaction/v1/top-up/inquiry/store",
                params={
                    "productId": "1",
                    "catalogId": "57",
                    "itemId": "2",
                    "paymentId": "352",
                    "gameId": user_id,
                    "zoneId": zone_id,
                }
            )
            nickname = r.json().get("data", {}).get("gameName")
        except:
            pass

        if not nickname:
            await update.message.reply_text("❌ شناسه کاربری پیدا نشد. دوباره چک کن.")
            return

        # ساخت لینک پرداخت
        link = create_payment_link(price, f"خرید {MLBB_PRODUCTS[product_key]['name']} برای {nickname}")
        if not link:
            await update.message.reply_text("❌ خطا در ایجاد لینک پرداخت")
            return

        await update.message.reply_text(
            f"✅ کاربر پیدا شد: *{nickname}*\n"
            f"💳 مبلغ: *{price:,} تومان*\n\n"
            f"برای پرداخت روی لینک زیر بزن:\n{link}",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data["awaiting_mlbb_id"] = False

# ================== 🏁 main ==================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # آپدیت نرخ تتر هر 30 ثانیه
    async def job_update_usdt_rate(context: ContextTypes.DEFAULT_TYPE):
        rate = fetch_usdt_rate()
        if rate:
            context.application.bot_data["usdt_rate"] = rate
            print("🔄 نرخ تتر آپدیت شد:", rate)
    app.job_queue.run_repeating(job_update_usdt_rate, interval=30, first=1)

    print("🤖 Bot is running ...")
    app.run_polling()

if __name__ == "__main__":
    main()
