from datetime import datetime

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlite3 import ProgrammingError

from orm import get_job, save_job, delete_job

def ampm_to_string(input_str: str) -> int:
    """Переводит строку типа "9am", "7pm" в число часа
    9pm -> 21
    7am -> 7

    :param input_str: Время вида XX (p/a)m
    :type input_str: str
    :return: Час вида XX
    :rtype: int
    """
    try:
        dt = datetime.strptime(input_str, '%I%p')
        return dt.hour - 2 # Timezone correction
    except ValueError:
        return None
    
def string_to_datetime(hour: int):
    """Переводит число часа в datetime-объект

    Args:
        hour (int): Целое число часа вида X/XX

    Returns:
        _type_: datetime-объект
    """
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    if now >= target_time:
        target_time += datetime.timedelta(days=1)  # Установка времени на следующий день

    return target_time

def form_inline_keyboard(user_id: int, text: str, is_button_call: bool = None) -> InlineKeyboardButton:
    button_7am = InlineKeyboardButton("7am", callback_data="7am")
    button_9pm = InlineKeyboardButton("9pm", callback_data="9pm")
    buttons = [[button_7am, button_9pm]]

    if is_button_call:
        text = text.split("\n\n")[1]

    result = get_job(user_id, text)

    if result is None:
        return InlineKeyboardMarkup(buttons)
    else:
        for i in result:
            if 5 in i:
                buttons[0][0] = InlineKeyboardButton("7am ✅", callback_data="7am")
            if 19 in i:
                buttons[0][1] = InlineKeyboardButton("9pm ✅", callback_data="9pm")
        return InlineKeyboardMarkup(buttons)

def convert_9pm(day_of_week: str) -> str:
    days = ["sun", "mon", "tue", "wed", "thu", "fri"]
    return days[days.index(day_of_week)-1]
    
def convert_letter_to_day_of_week(letter: str) -> str:
    return {"M": "Monday", 
            "T": "Tuesday", 
            "W": "Wednesday", 
            "R": "Thursday",
            "F": "Friday"
            }[letter]

def set_notification(callback_query: CallbackQuery, notify_function, scheduler: AsyncIOScheduler) -> str:
    time = ampm_to_string(callback_query.data)
    user_id = callback_query.from_user.id
    text = callback_query.message.text.split("\n\n")
    course = text[1]
    day_of_week = text[0].lower()[0:3]

    if callback_query.data == "9pm":
        day_of_week = convert_9pm(day_of_week)

    try:
        if get_job(user_id, course, day_of_week, time):
            delete_job(user_id, course, day_of_week, time)
            text = f"Notification unset"
        else:
            save_job(user_id, course, day_of_week, time)
            text = f"Notification set to {callback_query.data}"
            scheduler.add_job(notify_function, CronTrigger(hour=time, day_of_week=day_of_week), 
                    args=[user_id, text])
    except ProgrammingError as e:
        e.add_note("Поменяй text в orm-функциях на course")
        
    return text
