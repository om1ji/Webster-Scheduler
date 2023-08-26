from pyrogram.types import ReplyKeyboardMarkup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_keyboard = [
                    "Schedule",
                    "Feedback"
                ]

main_menu = ReplyKeyboardMarkup([main_keyboard],resize_keyboard=True)

week_keyboard = ["M", "T", "W", "R", "F"]

week_menu = ReplyKeyboardMarkup([week_keyboard, ["Update schedule", "Menu"]], resize_keyboard=True)
update_menu = ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)

notification_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("9pm", callback_data="9pm"),
        InlineKeyboardButton("7am", callback_data="7am")]
    ]
)

feedback_menu = ReplyKeyboardMarkup([["Leave feedback", "Check feedback"], ["Menu"]], resize_keyboard=True)