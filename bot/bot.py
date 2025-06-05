import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Weather, Currency
from dotenv import load_dotenv
from contextlib import contextmanager
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Формирование строки подключения к PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

if not all([BOT_TOKEN, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
    raise ValueError("❌ Не заданы необходимые переменные окружения")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()

bot = telebot.TeleBot(BOT_TOKEN)

cities = [
    "Новосибирск", "Томск", "Красноярск",
    "Барнаул", "Иркутск", "Омск", "Улан-Удэ"
]

currencies = ["Доллар", "Евро", "Юань", "Тенге"]

def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌆 Погода", callback_data="choose_city"),
        InlineKeyboardButton("💱 Валюты", callback_data="choose_currency")
    )
    return markup

def get_city_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=city, callback_data=f"city_{city}") for city in cities]
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    return markup

def get_currency_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=cur, callback_data=f"currency_{cur}") for cur in currencies]
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    return markup

def get_back_to_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    return markup

@bot.message_handler(commands=["start", "menu"])
def send_menu(message):
    bot.send_message(message.chat.id, "🔘 Выберите действие:", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def handle_main_menu(call):
    bot.edit_message_text("🔘 Выберите действие:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_main_menu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("choose_"))
def handle_choose_mode(call):
    if call.data == "choose_city":
        bot.edit_message_text("📍 Выберите город:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_city_keyboard())
    elif call.data == "choose_currency":
        bot.edit_message_text("💱 Выберите валюту:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_currency_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("city_"))
def handle_city(call):
    city = call.data.replace("city_", "")
    with get_session() as session:
        entry = session.query(Weather).filter_by(city=city).order_by(Weather.created_at.desc()).first()

    if entry:
        bot.send_message(call.message.chat.id, f"🌆 {entry.city}\n\n{entry.info}", reply_markup=get_back_to_menu_keyboard())
    else:
        bot.send_message(call.message.chat.id, "❌ Нет данных по городу.", reply_markup=get_back_to_menu_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("currency_"))
def handle_currency(call):
    cur = call.data.replace("currency_", "")
    with get_session() as session:
        entry = session.query(Currency).filter_by(name=cur).order_by(Currency.created_at.desc()).first()

    if entry:
        bot.send_message(call.message.chat.id, f"💱 {entry.name} → {entry.rate}", reply_markup=get_back_to_menu_keyboard())
    else:
        bot.send_message(call.message.chat.id, "❌ Нет данных по валюте.", reply_markup=get_back_to_menu_keyboard())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def handle_text_city_query(message):
    city = message.text.strip().capitalize()
    with get_session() as session:
        entry = session.query(Weather).filter_by(city=city).order_by(Weather.created_at.desc()).first()

    if entry:
        bot.send_message(message.chat.id, f"🌆 {entry.city}\n\n{entry.info}", reply_markup=get_back_to_menu_keyboard())
    else:
        bot.send_message(message.chat.id, "❌ Не удалось найти город. Попробуйте ещё раз или нажмите меню.", reply_markup=get_back_to_menu_keyboard())

if __name__ == "__main__":
    print("🚀 Бот запущен...")
    bot.polling(none_stop=True, interval=0)
