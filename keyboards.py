from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup

main_keyboard = [
                    KeyboardButton("Расписание"), 
                    KeyboardButton("Обновить расписание"),
                ]

main_menu = ReplyKeyboardMarkup([main_keyboard])

week_keyboard = [ 
                    KeyboardButton("Monday"), 
                    KeyboardButton("Tuesday"),
                    KeyboardButton("Wednesday"),
                    KeyboardButton("Thursday"),
                    KeyboardButton("Friday")
                ]

week_menu = ReplyKeyboardMarkup([week_keyboard, [KeyboardButton("Меню")]], resize_keyboard=True)
update_menu = ReplyKeyboardMarkup([[KeyboardButton("Отмена")]])