import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "counter": 0, "excluded": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.effective_user.id)

    if user_id not in data["users"]:
        data["counter"] += 1
        while data["counter"] in data["excluded"]:
            data["counter"] += 1
        data["users"][user_id] = data["counter"]
        save_data(data)

    number = data["users"][user_id]

    keyboard = [
        [InlineKeyboardButton("📌 Мой номерок", callback_data="my_number")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")]
    ]

    await update.message.reply_text(
        f"🎉 Ты участвуешь!\nТвой номерок: {number}\n\n📲 WhatsApp: https://wa.me/ВАШ_НОМЕР",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    user_id = str(query.from_user.id)

    if query.data == "my_number":
        number = data["users"].get(user_id, "❌ Нет номера")
        await query.edit_message_text(f"📌 Твой номерок: {number}")

    if query.data == "stats":
        total = len(data["users"])
        await query.edit_message_text(f"📊 Всего участников: {total}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
