from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

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