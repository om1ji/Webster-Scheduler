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

@app.on_message(filters.command("start") | (filters.text & filters.regex("Menu")))
async def hello(client, message: Message, state: State) -> None:
    if orm.check_user_for_presence(message.from_user.id):
        await app.send_message(message.chat.id, 
                            "Main menu", 
                            reply_markup=keyboards.main_menu)
    else:
        await app.send_message(message.chat.id, 
                            texts.hello, 
                            reply_markup=keyboards.main_menu)
        await state.set_state(Parameters.has_no_schedule)

@app.on_message(filters.document & StateFilter(Parameters.has_no_schedule))
async def receive_schedule(client, message: Message, state: State) -> None:
    status = await receive_pdf(app, message)
    await app.send_message(message.chat.id, status)
    await state.set_state("has_schedule")

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
    await message.reply("Upload PDF")

# Get current schedule

@app.on_message(filters.text & filters.regex("Schedule"))
async def schedule_button_handler(client, message: Message, state: State) -> None:
    await app.send_message(message.chat.id,
                           "Choose day",
                           reply_markup=keyboards.week_menu)
    
    messages[message.chat.id] = []

# Get daily schedule 

@app.on_message(filters.text & filters.regex(r"^[MTWRF]$"))
async def get_day_schedule(client, message: Message, state: State) -> None:
    day_of_week = utils.convert_letter_to_day_of_week(message.text)
    result = orm.get_day_schedule(message.from_user.id, day_of_week)
    await app.delete_messages(message.chat.id, message.id)
    if result != [('',)]:
        try:
            result = result[0][0].split("\n\n")
            for i in result[:-1]: # Ответ с fetchall приходит в виде (obj, obj,)

                reply_markup = utils.form_inline_keyboard(message.from_user.id, i)
                i = i[:-1] # Убрать пробел в конце

                message_to_delete = await message.reply(day_of_week + "\n\n" + i, 
                                                        reply_markup=reply_markup)
                
                try:
                    messages[message.chat.id].append(message_to_delete.id) # For bulk deleting messages after "Меню" button
                except KeyError:
                    pass

        except TypeError as e:
            print(e.with_traceback())
            await state.set_state(Parameters.has_no_schedule)
            await app.send_message(message.chat.id, "You have no schedule. Upload a PDF")
    else:
        message_to_delete = await message.reply(message.text + "\n\n" + "No courses this day")
        try:
            messages[message.chat.id].append(message_to_delete.id) # For bulk deleting messages after "Меню" button
        except KeyError:
            pass

# Update schedule

@app.on_message(filters.text & filters.regex("Update schedule"))
async def update_schedule_message(client, message: Message, state: State) -> None:
    await state.set_state(Parameters.updating_schedule)
    await message.reply("Upload PDF", reply_markup=keyboards.update_menu)

# Feedback

@app.on_message(filters.text & filters.regex("Feedback"))
async def feedback_menu(client, message: Message) -> None:
    await message.reply(texts.feedback, reply_markup=keyboards.feedback_menu)

@app.on_message(filters.text & filters.regex("Check feedback"))
async def show_link(client, message: Message) -> None:
    await message.reply("https://docs.google.com/spreadsheets/d/1RumzCUn7BHCv7TsHnYo5nWCqfBmZ2OTw3il0wdpQCvE/edit?resourcekey#gid=1751046026")

@app.on_message(filters.text & filters.regex("Leave feedback"))
async def show_link(client, message: Message) -> None:
    await message.reply("https://docs.google.com/forms/d/e/1FAIpQLSfq8wxX5t4LA92VFhiTgRa037xLN6nWtToClYb0RCa1PNgjCw/viewform")

# Receive pdf

@app.on_message(filters.document & StateFilter(Parameters.updating_schedule))
async def update_schedule(client, message: Message, state: State) -> None:
    status = await receive_pdf(app, message)
    orm.delete_all_jobs(message.from_user.id)
    print(f"All jobs of {message.from_user.id} are deleted")
    await app.send_message(message.chat.id, status, reply_markup=keyboards.main_menu)
    await state.finish()

@app.on_message(filters.text & filters.regex("Cancel") & StateFilter(Parameters.updating_schedule))
async def cancel(client, message: Message, state: State) -> None:
    await app.send_message(message.chat.id,
                            "Canceled",
                            reply_markup=keyboards.main_menu)
    
# Inline buttons

@app.on_callback_query(filters.regex("9pm") | filters.regex("7am"))
async def notify_handler(client, callback_query: CallbackQuery):

    time: int = utils.ampm_to_string(callback_query.data)
    user_id: int = callback_query.from_user.id
    text: str = callback_query.message.text.split("\n\n")
    course: str = text[1]
    day_of_week: str = text[0].lower()[0:3]

    if callback_query.data == "9pm":
        day_of_week = utils.convert_9pm(day_of_week)

    scheduler.add_job(notify, 
                      CronTrigger(hour=time, day_of_week=day_of_week), 
                      args=[user_id, text]
                      )
    
    orm.save_job(user_id, course, day_of_week, time)
    
    await app.delete_messages(callback_query.from_user.id, callback_query.message.id)
    
    await app.answer_callback_query(callback_query.id,
                                    text=f"Notification set to {callback_query.data}",
                                    show_alert=True)
        
def start_saved_jobs() -> None:
    jobs = orm.get_jobs()
    if jobs is not None:
        for job in jobs:
            scheduler.add_job(notify, 
                        CronTrigger(hour=job[4], day_of_week=job[3]), 
                        args=[job[1], job[2]]
                        )
    else:
        print("No jobs found :)")

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
