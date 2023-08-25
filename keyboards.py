from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_keyboard = [
                    KeyboardButton("Расписание"),
                    KeyboardButton("Feedback")
                ]

main_menu = ReplyKeyboardMarkup([main_keyboard],resize_keyboard=True)

week_keyboard = [ 
                    KeyboardButton("Monday"), 
                    KeyboardButton("Tuesday"),
                    KeyboardButton("Wednesday"),
                    KeyboardButton("Thursday"),
                    KeyboardButton("Friday")
                ]

week_menu = ReplyKeyboardMarkup([week_keyboard, [KeyboardButton("Обновить расписание"), KeyboardButton("Меню")]], resize_keyboard=True)
update_menu = ReplyKeyboardMarkup([[KeyboardButton("Отмена")]], resize_keyboard=True)

notification_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("9pm", callback_data="9pm")],
        [InlineKeyboardButton("7am", callback_data="7am")],
    ]
)

feedback_menu = ReplyKeyboardMarkup([KeyboardButton("")])