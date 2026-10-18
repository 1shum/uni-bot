import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
import pytz
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === СЮДА ВПИШИ СВОИ ДАННЫЕ ===
BOT_TOKEN = "8970456575:AAHvSbWVL3CSri_lrOmapCRcPsbmZyul3FY" # Вместо этого текста вставь токен от BotFather в кавычках
MY_TELEGRAM_ID = 1087118817 # Вместо этого текста вставь свой ID (просто число, без кавычек)
TIMEZONE = pytz.timezone("Asia/Yekaterinburg")
# ===============================

# Твоё расписание (оно автоматически запишется в файл при первом запуске)
SCHEDULE_DATA = {
"monday": [
{"time": "08:30 - 10:00", "name": "Информационные системы и технологии", "room": "Ауд. 556", "type": "Лабораторная работа"},
{"time": "10:10 - 11:40", "name": "Информационные системы и технологии", "room": "Ауд. 556", "type": "Лабораторная работа"},
{"time": "12:10 - 13:40", "name": "Физкультура", "room": "Спортзал", "type": "Практика"},
{"time": "13:50 - 15:20", "name": "Экономика", "room": "Ауд. 262", "type": "Лекция"}
],
"tuesday": [
{"time": "13:50 - 15:20", "name": "Русский язык", "room": "Ауд. 215", "type": "Занятие"},
{"time": "15:30 - 17:00", "name": "Безопасность жизнедеятельности", "room": "Ауд. 421", "type": "Занятие"},
{"time": "18:10 - 18:40", "name": "Алгебра и геометрия", "room": "Ауд. 453", "type": "Занятие"}
],
"wednesday": [
{"time": "10:10 - 11:40", "name": "ОБЖ", "room": "Ауд. 608", "type": "Занятие"},
{"time": "12:10 - 13:40", "name": "Физкультура", "room": "Спортзал", "type": "Практика"},
{"time": "13:50 - 15:20", "name": "Основы российской государственности", "room": "Ауд. 505", "type": "Занятие"},
{"time": "15:30 - 17:00", "name": "Основы российской государственности", "room": "Ауд. 505", "type": "Практика"}
],
"thursday": [],
"friday": [
{"time": "10:10 - 11:40", "name": "Информационные системы и технологии", "room": "Ауд. 262", "type": "Лекция"},
{"time": "12:10 - 13:40", "name": "Основы российской государственности", "room": "Ауд. 608", "type": "Лекция"},
{"time": "13:50 - 15:20", "name": "Английский язык", "room": "Ауд. 111", "type": "Практика"},
{"time": "15:30 - 17:00", "name": "Алгебра и геометрия", "room": "Ауд. 258", "type": "Занятие"}
],
"saturday": [
{"time": "12:10 - 13:40", "name": "Информатика и языки программирования", "room": "Ауд. 103", "type": "Лабораторная работа"},
{"time": "13:50 - 15:20", "name": "Информатика и языки программирования", "room": "Ауд. 103", "type": "Занятие"}
],
"sunday": []
}

if not os.path.exists("schedule.json"):
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(SCHEDULE_DATA, f, ensure_ascii=False, indent=2)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def load_schedule():
    with open("schedule.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_tomorrow_schedule_text():
    schedule = load_schedule()
    tomorrow = datetime.now(TIMEZONE) + timedelta(days=1)
    day_key = tomorrow.strftime("%A").lower()

    days_ru = {
        "monday": "Понедельник", "tuesday": "Вторник", "wednesday": "Среда",
        "thursday": "Четверг", "friday": "Пятница", "saturday": "Суббота", "sunday": "Воскресенье"
    }

    day_name = days_ru.get(day_key, day_key)
    date_str = tomorrow.strftime("%d.%m.%Y")
    lessons = schedule.get(day_key, [])

    if not lessons:
        return f"📅 *Расписание на завтра* ({day_name}, {date_str}):\n\n🎉 Пар нет, отдыхаем!"

    text = f"📅 *Расписание на завтра* ({day_name}, {date_str}):\n\n"
    for i, lesson in enumerate(lessons, 1):
        text += f"{i}. *{lesson['name']}* ({lesson['type']})\n"
        text += f"  ⏰ Время: `{lesson['time']}`\n"
        text += f"  📍 Кабинет: `{lesson['room']}`\n\n"

    return text

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📅 Расписание на завтра")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я твой бот-помощник с расписанием.\nКаждый день в 00:00 я буду присылать расписание пар на завтра.",
        reply_markup=keyboard
    )

@dp.message(F.text == "📅 Расписание на завтра")
async def manual_schedule(message: types.Message):
    text = get_tomorrow_schedule_text()
    await message.answer(text, parse_mode="Markdown")

async def send_midnight_schedule():
    text = get_tomorrow_schedule_text()
    try:
        await bot.send_message(chat_id=MY_TELEGRAM_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Не удалось отправить полночное сообщение: {e}")

async def main():
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(send_midnight_schedule, "cron", hour=0, minute=0)
    scheduler.start()

    logging.info("Бот запущен и ждет полуночи...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
