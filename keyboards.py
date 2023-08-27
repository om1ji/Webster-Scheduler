from pyrogram.types import ReplyKeyboardMarkup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_keyboard = [
                    "Schedule",
                    "Feedback",
                    "QR",
                    "Update QR"
                ]

main_menu = ReplyKeyboardMarkup([main_keyboard],resize_keyboard=True)

week_keyboard = ["M", "T", "W", "R", "F"]

week_menu = ReplyKeyboardMarkup([week_keyboard, ["Update schedule", "Menu"]], resize_keyboard=True)
update_menu = ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)

feedback_menu = ReplyKeyboardMarkup([["Leave feedback", "Check feedback"], ["Menu"]], resize_keyboard=True)