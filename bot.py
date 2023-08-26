"""
Pyrogram framework for Telegram bot
Custom modules and pdf worker
"""
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram_patch.fsm.storages import MemoryStorage
from pyrogram_patch.fsm.filter import StateFilter
from pyrogram.types import CallbackQuery
from pyrogram_patch.fsm import State
from pyrogram_patch import patch

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

messages = {}

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
    
    messages[message.chat.id] = []

@app.on_message((filters.text & filters.regex("Меню")) | filters.command("start"))
async def main(client, message: Message, state: State) -> None:
    await app.delete_messages(message.chat.id, messages[message.chat.id])
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
async def get_day_schedule(client, message: Message, state: State) -> None:
    result = orm.get_day_schedule(message.from_user.id, message.text.lower())
    await app.delete_messages(message.chat.id, message.id)
    if result != [('',)]:
        try:
            result = result[0][0].split("\n\n")
            for i in result[:-1]: # Ответ с fetchall приходит в виде (obj, obj,)
                message = await message.reply(message.text + "\n\n" + i, reply_markup=keyboards.notification_menu)
                messages[message.chat.id].append(message.id) # For bulk deleting messages after "Меню" button
        except TypeError:
            await state.set_state(Parameters.has_no_schedule)
            await app.send_message(message.chat.id, "У тебя нет расписания")
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

    time: int = utils.ampm_to_string(callback_query.data)
    user_id: int = callback_query.from_user.id
    text: str = callback_query.message.text
    day_of_week: str = text.lower().split("\n\n")[0][0:3]

    scheduler.add_job(notify, 
                      CronTrigger(hour=time, day_of_week=day_of_week), 
                      args=[user_id, text]
                      )
    
    orm.save_job(user_id, text, day_of_week, time)
    
    await app.delete_messages(callback_query.from_user.id, callback_query.message.id)
    
    await app.answer_callback_query(callback_query.id,
                                    text=f"Notification set to {callback_query.data}",
                                    show_alert=True)
    
def start_saved_jobs() -> None:
    for job in orm.get_jobs():
        scheduler.add_job(notify, 
                      CronTrigger(hour=job[4], day_of_week=job[3]), 
                      args=[job[1], job[2]]
                      )

def main() -> None:
    try:  
        orm.create_tables()
        start_saved_jobs()
        scheduler.start()
        app.run()
    except KeyboardInterrupt:
        orm.conn.close()
        scheduler.shutdown()
        app.stop()

if __name__=="__main__":
    main()

#
# Feedback support
# Leave Feedback -> Выходит список из кнопок учителей, 
# которых взяли из расписания. Нажимаем на кнопку учителя -> 
# Сообщение-приглашение написать фидбек. Пользователь пишет 
# фидбек. отправляет боту, бот сохраняет в базе данных.
# 
# Check feedback -> Пишут имя учителя, как в расписании ->
# 
