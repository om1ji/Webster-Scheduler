from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from orm import get_job

def ampm_to_string(input_str: str) -> int:
    """Переводит строку типа "9am", "7pm" в число часа
    9pm -> 21
    7am -> 7

    :param input_str: Время вида XX(p/a)m
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

def form_inline_keyboard(user_id: int, text: str) -> InlineKeyboardMarkup:
    button_7am = InlineKeyboardButton("7am", callback_data="7am")
    button_9pm = InlineKeyboardButton("9pm", callback_data="9pm")
    buttons = [[button_7am, button_9pm]]

    result = get_job(user_id, text[:-1]) # [:-1] чтобы убрать пробел в конце
    if result == [] or result is None:
        return InlineKeyboardMarkup(buttons)
    else:
        for i in result:
            if 5 in i:
                buttons[0][0] = InlineKeyboardButton("7am ✅", callback_data="7am")
            if 19 in i:
                buttons[0][1] = InlineKeyboardButton("9pm ✅", callback_data="9pm")
        return InlineKeyboardMarkup(buttons)

def convert_9pm(day_of_week: str) -> str:
    if day_of_week == "mon":
        return "sun"
    elif day_of_week == "tue":
        return "mon"
    elif day_of_week == "wed":
        return "tue"
    elif day_of_week == "thu":
        return "wed"
    elif day_of_week == "fri":
        return "thu"