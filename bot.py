"""
os library for paths
Pyrogram framework for Telegram bot
Custom modules and pdf worker
"""
import os
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram_patch.fsm.storages import MemoryStorage
from pyrogram_patch.fsm.filter import StateFilter
from pyrogram.types import CallbackQuery
from pyrogram_patch.fsm import State
from pyrogram_patch import patch
from pyrogram.errors.exceptions.bad_request_400 import MessageEmpty

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import orm
import keyboards
import consts
from pdf_parser import receive_pdf, parse_notification
from states import Parameters
import utils
import texts

app = Client(
                name="webster",
                api_hash=consts.API_HASH,
                api_id=consts.API_ID,
                bot_token=consts.BOT_TOKEN
            )

patch_manager = patch(app)
patch_manager.set_storage(MemoryStorage())

scheduler = AsyncIOScheduler()

async def notify(user_id: int, text: str) -> None:
    result = parse_notification(text)
    message_text = texts.notification.format(result.crs_sec, 
                                             result.hrs,
                                             result.title,
                                             result.instructor,
                                             result.time,
                                             result.building,
                                             result.room)
    print(message_text)
    await app.send_message(user_id, message_text)

# Initial

@app.on_message(filters.command("start") & StateFilter())
async def hello(client, message: Message, state: State):
    await app.send_message(message.chat.id, 
                           "Welcome to Webster Scheduler bot", 
                           reply_markup=keyboards.main_menu)
    
    await state.set_state(Parameters.has_no_schedule)

@app.on_message(filters.document & StateFilter(Parameters.has_no_schedule))
async def receive_schedule(client, message: Message, state: State) -> None:
    status = await receive_pdf(app, message)
    await app.send_message(message.chat.id, status)
    await state.finish()

# Main menu

@app.on_message(filters.command("start"))
async def hello(client, message: Message, state: State) -> None:
    await app.send_message(message.chat.id, 
                           "Welcome to Webster Scheduler bot", 
                           reply_markup=keyboards.main_menu)

# Debug
@app.on_message(filters.command("debug"))
async def debug(client, message: Message) -> None:
    response = [job for job in scheduler.get_jobs()]
    await app.send_message(message.chat.id, 
                            str(response),
                           reply_markup=keyboards.main_menu)

# Require schedule if not provided

@app.on_message(filters.text & StateFilter(Parameters.has_no_schedule))
async def require_schedule(client, message: Message, state: State) -> None:
    await message.reply("Загрузи PDF")

# Get current schedule

@app.on_message(filters.text & filters.regex("Расписание"))
async def schedule_button_handler(client, message: Message, state: State) -> None:
    await app.send_message(message.chat.id,
                           "Выбери день bruh",
                           reply_markup=keyboards.week_menu)
    

@app.on_message((filters.text & filters.regex("Меню")) | filters.command("start"))
async def main(client, message: Message, state: State) -> None:
    await app.send_message(message.chat.id,
                            "Welcome to Webster Scheduler bot", 
                            reply_markup=keyboards.main_menu)

# Get daily schedule 

@app.on_message(filters.text & (filters.regex("Monday") | \
                                filters.regex("Tuesday") | \
                                filters.regex("Wednesday") | \
                                filters.regex("Thursday") | \
                                filters.regex("Friday"))
                )
async def get_day_schedule(client, message: Message) -> None:
    result = orm.get_day_schedule(message.from_user.id, message.text.lower())
    if result:
        try:
            for i in result:
                await message.reply(i, reply_markup=keyboards.notification_menu)
        except MessageEmpty:
            print("Message empty error, а так всё норм")
    else:
        await message.reply("На этот день нет занятий")

# Update schedule

@app.on_message(filters.text & filters.regex("Обновить расписание"))
async def update_schedule_message(client, message: Message, state: State) -> None:
    await state.set_state(Parameters.updating_schedule)
    await message.reply("Загрузи PDF", reply_markup=keyboards.update_menu)

@app.on_message(filters.document & StateFilter(Parameters.updating_schedule))
async def update_schedule(client, message: Message, state: State) -> None:
    status = await receive_pdf(app, message)
    await app.send_message(message.chat.id, status, reply_markup=keyboards.main_menu)
    await state.finish()

@app.on_message(filters.text & filters.regex("Отмена") & StateFilter(Parameters.updating_schedule))
async def cancel(client, message: Message, state: State) -> None:
    await app.send_message(message.chat.id,
                            "Отменено",
                            reply_markup=keyboards.main_menu)
    
# Inline buttons

@app.on_callback_query(filters.regex("9pm") | filters.regex("7am"))
async def notify_handler(client, callback_query: CallbackQuery):
    time = utils.ampm_to_string(callback_query.data)
    scheduler.add_job(notify, CronTrigger(hour=time), args=[callback_query.from_user.id, callback_query.message.text])

if __name__=="__main__":
    try:
        orm.create()
        scheduler.start()
        app.run()
    except KeyboardInterrupt:
        orm.conn.close()
        app.stop()

# приходит сообщение расписание грядущего дня
# Уведомления - When to notify - Две инлайн кнопки, два варианта
#
# Feedback support
#Leave Feedback -> Выходит список из кнопок учителей, 
# которых взяли из расписания. Нажимаем на кнопку учителя -> 
# Сообщение-приглашение написать фидбек. Пользователь пишет 
# фидбек. отправляет боту, бот сохраняет в базе данных.
# 
# Check feedback -> Пишут имя учителя, как в расписании ->
# 
