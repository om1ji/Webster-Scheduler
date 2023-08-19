import pdfplumber

class table_row:
    def __init__(self, row: list):
        self.crs_sec = row[0]
        self.hrs = row[1]
        self.title = row[2]
        self.instructor:str = row[3].replace("Email", "")
        self.room = row[6]
        self.days = row[7]
        self.time = row[8][:6] + " " + row[8][6:]
        self.date = row[9][:10] + " " + row[9][10:]
        self.tm = row[10]
        self.type = row[11]

    day_mapping = {
        "-M-----": "Monday",
        "--T----": "Tuesday",
        "---W---": "Wednesday",
        "----R--": "Thursday",
        "-----F-": "Friday",
    }

    def convert(self, short_day):
        return self.day_mapping.get(short_day, "Unknown")
    
    def __str__(self):
        return f"{self.convert(self.days)} \n{self.crs_sec} {self.hrs} {self.title} {self.instructor} {self.room} {self.time} {self.date} {self.tm} {self.type} \n\n"

class table_header:
    def __init__(self, headers: list):
        self.name_surname = headers[0]
        self.classification = headers[0].replace("Classification: ", "")
        self.major = headers[1].replace("Major: ", "")
        self.advisor = headers[2].replace("Advisor: ", "")
        self.program = headers[3]    

def get_data_from_pdf(pdf_path) -> list:
    with pdfplumber.open(pdf_path) as pdf:
        headers = []
        for page in pdf.pages:
            table = page.extract_tables()[0]
            for row in table[0:4]:  
                headers.append(row[0])

        table_rows = []
        for page in pdf.pages:
            table = page.extract_tables()[0]  
            for row in table[5:-1]:
                trow = [item for item in row if item is not None] 
                trow = [str(item).replace("\n", "") for item in trow]
                if trow != ['']:
                    table_rows.append(str(table_row(trow)))

    return table_rows, table_header(headers)

def get_schedule_from_pdf(pdf_path) -> str:
    table_rows = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_tables()[0]  
            for row in table[5:-1]:
                trow = [item for item in row if item is not None] 
                trow = [str(item).replace("\n", "") for item in trow]
                if trow != ['']:
                    tmp = table_row(trow)
                    table_rows += str(tmp)
    return table_rows
    