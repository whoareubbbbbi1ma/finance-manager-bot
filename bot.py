import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Токен от BotFather
TOKEN = "8786044864:AAFOjZnfVwbYrHOAy4eGzCdSX5m78wMnXhI"

# База данных
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    note TEXT,
    date TEXT
)
""")
conn.commit()

# Функции
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я твой финансовый бот.\n"
        "Пример добавления расхода: 12 food lunch\n"
        "Команды: /today /week /month"
    )

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        parts = text.split(" ", 2)
        amount = float(parts[0])
        category = parts[1]
        note = parts[2] if len(parts) > 2 else ""
        date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
                       (amount, category, note, date))
        conn.commit()
        await update.message.reply_text(f"Расход {amount}₽ в категории '{category}' сохранен")
    except:
        await update.message.reply_text("Неверный формат. Пример: 12 food lunch")

async def show_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date=?", (today,))
    total = cursor.fetchone()[0] or 0
    await update.message.reply_text(f"Расходы за сегодня: {total}₽")

async def show_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    week_ago = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?", (week_ago, today_str))
    total = cursor.fetchone()[0] or 0
    await update.message.reply_text(f"Расходы за неделю: {total}₽")

async def show_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    month_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?", (month_ago, today_str))
    total = cursor.fetchone()[0] or 0
    await update.message.reply_text(f"Расходы за месяц: {total}₽")

# Настройка бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", show_today))
app.add_handler(CommandHandler("week", show_week))
app.add_handler(CommandHandler("month", show_month))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense))

# Запуск
if __name__ == "__main__":
    print("Бот запущен")
    app.run_polling()