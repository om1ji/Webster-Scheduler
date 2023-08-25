from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import CallbackQuery
from pyrogram import filters

import orm

main_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Расписание", callback_data="schedule")],
        [InlineKeyboardButton("Notifications", callback_data="notifications")]
    ]
)

notification_menu = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("9pm evening before class", callback_data="notify_9pm")],
        [InlineKeyboardButton("7am on class day", callback_data="notify_7am")],
    ]
)
