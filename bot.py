from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

import orm

import consts
import pdf_parser
import os

app = Client("my_account", api_hash=consts.API_HASH, api_id=consts.API_ID, bot_token=consts.BOT_TOKEN)

def get_file_path(file_id: str) -> str:
    file_link = app.get_file(file_id)
    download_link = f"https://api.telegram.org/file/bot{consts.BOT_TOKEN}/{file_link}"
    return download_link

@app.on_message(filters.command("start"))
async def hello(client, message):
    schedule_button = KeyboardButton("Расписание")
    update_schedule_button = KeyboardButton("Обновить расписание")
    buttons = [[schedule_button], [update_schedule_button]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await app.send_message(message.chat.id, "Welcome to Webster Scheduler bot!", reply_markup=reply_markup)

@app.on_message(filters.text & filters.regex("Расписание"))
async def schedule_button_handler(client, message):
    file_path = os.path.abspath(".") + "\\" + orm.select_file_id(message.chat.id) + ".pdf"
    schedule = pdf_parser.get_schedule_from_pdf(file_path)
    await app.send_message(message.chat.id, schedule)

@app.on_message(filters.text & filters.regex("Обновить расписание"))
async def receive_pdf(client, message):
    document = message.document
    if document.mime_type == "application/pdf":
        file_path = os.path.join("./downloads", document.file_id + ".pdf")
        await message.download(file_name=file_path)

        data = pdf_parser.get_data_from_pdf(file_path)
        headers = data[1]

        text = f"""Classification: {headers.classification}
Major: {headers.major}
Advisor: {headers.advisor}
Program: {headers.program}"""
        
        await message.reply(text)

        insertion_status:bool = orm.insert(message.from_user.id, message.from_user.username, document.file_id)

        if insertion_status:
            await message.reply("Расписание обновлено")
        else:
            await message.reply("Расписание добавлено")
        
if __name__=="__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        orm.conn.close()
        app.stop()

