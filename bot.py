from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram_patch.fsm.storages import MemoryStorage
from pyrogram_patch.fsm.filter import StateFilter
from pyrogram_patch.fsm import State
from pyrogram_patch import patch

import orm
import keyboards
import consts
from pdf_parser import *
from states import Parameters
import texts


import os

app = Client(
                name="webster", 
                api_hash=consts.API_HASH, 
                api_id=consts.API_ID, 
                bot_token=consts.BOT_TOKEN
            )

patch_manager = patch(app)
patch_manager.set_storage(MemoryStorage())

async def receive_pdf(message: Message) -> str:
    """
    Принимает pdf-документ с объекта Message, сохраняет в памяти, добавляет запись в бд
    """
    document = message.document
    if document.mime_type == "application/pdf":
        reply_message = await message.reply("Загрузка")

        file_path = os.path.join("./downloads", document.file_id + ".pdf")
        await message.download(file_name=file_path) # сохраняет

        headers: table_header = get_data_from_pdf(file_path)[1]

        await app.delete_messages(message.chat.id, reply_message.id)
        await message.reply(texts.headers.format(headers.classification, 
                                                 headers.major, 
                                                 headers.advisor, 
                                                 headers.program))

        insertion_status:bool = orm.insert(message.from_user.id, 
                                           message.from_user.username, 
                                           document.file_id) # запись в бд

        if insertion_status:
            return "Расписание обновлено"
        else:
            return "Расписание добавлено"

@app.on_message(filters.command("start") & StateFilter())
async def hello(client, message: Message, state: State):
    await app.send_message(message.chat.id, 
                           "Welcome to Webster Scheduler bot", 
                           reply_markup=keyboards.main_menu)
    
    await state.set_state(Parameters.has_no_schedule)

@app.on_message(filters.command("start"))
async def hello(client, message: Message, state: State):
    await app.send_message(message.chat.id, 
                           "Welcome to Webster Scheduler bot", 
                           reply_markup=keyboards.main_menu)
    
@app.on_message(filters.command("states") & StateFilter())
async def states_data(client, message: Message, state: State):
    states = await state.get_data()
    print(states)
    await message.reply(str(states))

@app.on_message(filters.document & StateFilter(Parameters.has_no_schedule))
async def receive_schedule(client, message: Message, state: State):
    status = await receive_pdf(message)
    await app.send_message(message.chat.id, status)
    await state.finish()

@app.on_message(filters.text & StateFilter(Parameters.has_no_schedule))
async def require_schedule(client, message: Message, state: State):
    await message.reply("Загрузи PDF")

@app.on_message(filters.text & filters.regex("Расписание"))
async def schedule_button_handler(client, message: Message, state: State):
    file_path = os.path.abspath("downloads") + "\\" + orm.select_file_id(message.from_user.id) + ".pdf"
    schedule = get_schedule_from_pdf(file_path)

    await app.send_message(message.chat.id, 
                           schedule, 
                           reply_markup=keyboards.week_menu)
    
@app.on_message(filters.text & filters.regex("Меню"))
async def hello(client, message: Message, state: State):
    await app.send_message(message.chat.id, 
                            "Welcome to Webster Scheduler bot", 
                            reply_markup=keyboards.main_menu)

@app.on_message(filters.text & filters.regex("Обновить расписание"))
async def update_schedule(client, message: Message, state: State):
    await state.set_state(Parameters.updating_schedule)
    await message.reply("Загрузи PDF", reply_markup=keyboards.update_menu)

@app.on_message(filters.document & StateFilter(Parameters.updating_schedule))
async def update_schedule(client, message: Message, state: State):
    status = await receive_pdf(message)
    await app.send_message(message.chat.id, status, reply_markup=keyboards.main_menu)
    await state.finish()    

@app.on_message(filters.text & filters.regex("Отмена") & StateFilter(Parameters.updating_schedule))
async def hello(client, message: Message, state: State):
    await app.send_message(message.chat.id, 
                            "Отменено", 
                            reply_markup=keyboards.main_menu)


if __name__=="__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        orm.conn.close()
        app.stop()