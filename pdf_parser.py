import pdfplumber
from pyrogram import Client
from pyrogram.types import Message

import os
from typing import Dict

import texts
import orm

class table_row:
    def __init__(self, row: list):
        self.crs_sec = row[0]
        self.hrs = row[1]
        self.title = row[2]
        self.instructor:str = row[3].replace("Email", "")
        self.room = row[6]
        self._days = row[7]
        self.building = row[5]
        self.time = row[8][:6] + " " + row[8][6:]
        self.date = row[9][:10] + " " + row[9][10:]
        self.tm = row[10]
        self.type = row[11]
    
    day_to_full = {
        "-M-----": "Monday",
        "--T----": "Tuesday",
        "---W---": "Wednesday",
        "----R--": "Thursday",
        "-----F-": "Friday"
    }

    @property
    def day(self):
        return self.day_to_full.get(self._days, "Unknown")

    def __str__(self):
        return f"{self.crs_sec} / {self.hrs} / {self.title} / {self.instructor} / {self.building} / {self.room} / {self.time} / {self.date} / {self.tm} / {self.type} \n\n"

class table_header:
    def __init__(self, headers: list):
        self.name_surname = headers[0]
        self.classification = headers[0].replace("Classification: ", "")
        self.major = headers[1].replace("Major: ", "")
        self.advisor = headers[2].replace("Advisor: ", "")
        self.program = headers[3]    

    def __str__(self):
        return f"{self.name_surname} {self.classification} {self.major} {self.advisor} {self.program}"

def parse_notification(text: str) -> table_row:
    data = text.split(" / ")
    result = table_row
    result.crs_sec = data[0]
    result.hrs = data[1]
    result.title = data[2]
    result.instructor = data[3]
    result.building = data[4]
    result.room = data[5]
    result.time = data[6]
    result.date = data[7]
    return result

def get_header_from_pdf(pdf_path) -> list:
    with pdfplumber.open(pdf_path) as pdf:
        headers = []
        for page in pdf.pages:
            table = page.extract_tables()[0]
            for row in table[0:4]:  
                headers.append(row[0])
        
    return table_header(headers)

def get_schedule_from_pdf(pdf_path: str) -> list:
    table_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_tables()[0]  
            for row in table[5:-1]:
                print(row)
                trow = [item for item in row if item is not None] 
                trow = [str(item).replace("\n", "") for item in trow]
                if trow != ['']:
                    
                    table_rows.append(table_row(trow))
                    
    return table_rows

def prepare_for_schedule_table(pdf_path: str) -> Dict[str, str]:
    result = {"monday": "",
            "tuesday": "",
            "wednesday": "",
            "thursday": "",
            "friday": ""}
    
    schedule = get_schedule_from_pdf(pdf_path=pdf_path)
    for i in schedule:
        result[i.day.lower()] += str(i)

    return result
    
async def receive_pdf(app: Client, message: Message) -> str:
    """
    Принимает pdf-документ с объекта Message, сохраняет в памяти, добавляет запись в бд
    """
    document = message.document
    if document.mime_type == "application/pdf":
        reply_message = await message.reply("Loading")

        file_path = os.path.join("./downloads", document.file_id + ".pdf")
        await message.download(file_name=file_path) # сохраняет

        headers = get_header_from_pdf(file_path)

        await app.delete_messages(message.chat.id, reply_message.id)
        await message.reply(texts.headers.format(headers.classification, 
                                                headers.major, 
                                                headers.advisor, 
                                                headers.program))

        schedule: dict = prepare_for_schedule_table(file_path)

        insertion_status:bool = orm.insert(message.from_user.id, 
                                        message.from_user.username, 
                                        document.file_id,
                                        schedule) # запись в бд
        

        if insertion_status:
            return "Schedule updated"
        else:
            return "Schedule added"
    else:
        return """Please make sure it is a readable PDF, not JPG, PNG, CGI or whatever else.
Also check if PDF does not contain image, so text can be copied from the file.

Contacts: @om1ji"""
        
def compare_days(day1: table_row, day2: table_row):
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    return days_order.index(day1) - days_order.index(day2)